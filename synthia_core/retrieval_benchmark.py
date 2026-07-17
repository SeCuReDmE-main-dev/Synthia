"""Reproducible retrieval lifecycle benchmark for Synthia education traces.

The benchmark compares the central MemoryLake retrieval surface with a local
dense retriever that implements HippoRAG's ``retrieve_dpr`` port. It does not
instantiate HippoRAG's graph, OpenIE, reranker, or answer-generation pipeline.
"""

from __future__ import annotations

import argparse
import json
import platform
import sys
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Protocol, Sequence

from .hipporag_bridge import HippoRAGRetrievalOnlyGateway
from .safety import HIERARCHY


SCHEMA = "synthia.education-retrieval-benchmark.v1"


@dataclass(frozen=True)
class BenchmarkDocument:
    document_id: str
    text: str
    provenance_id: str
    tags: tuple[str, ...] = ("education", "synthetic-benchmark")

    def as_memory_record(self) -> dict[str, Any]:
        return {
            "path": f"synthetic-education-benchmark:{self.document_id}",
            "text": self.text,
            "source_type": "education-benchmark",
            "product": "scholarium-teach",
            "lane": "benchmark",
            "sensitivity": "synthetic",
            "uncertainty": "benchmark-ground-truth",
            "approval_state": "approved",
            "subject": self.document_id,
            "claim": "Synthetic benchmark evidence; not a claim about a student.",
            "confidence_label": "synthetic benchmark fixture",
            "citation_text": self.provenance_id,
            "provenance_id": self.provenance_id,
            "artifact_targets": ["internal-note"],
            "connector_source_subtype": "synthia-education-benchmark",
            "tags": list(self.tags),
            "metadata": {
                "schema": SCHEMA,
                "document_id": self.document_id,
                "synthetic": True,
                "hierarchy": HIERARCHY,
            },
        }


@dataclass(frozen=True)
class BenchmarkQuery:
    query_id: str
    text: str
    relevant_provenance_ids: tuple[str, ...]


@dataclass(frozen=True)
class BenchmarkSpec:
    name: str
    documents: tuple[BenchmarkDocument, ...]
    queries: tuple[BenchmarkQuery, ...]
    top_k: int
    deletion_query_id: str
    deletion_provenance_id: str


@dataclass(frozen=True)
class EvidenceHit:
    provenance_id: str
    document: str
    score: float


class BenchmarkEngine(Protocol):
    name: str

    def index(self, documents: Sequence[BenchmarkDocument]) -> Mapping[str, Any]: ...

    def retrieve(self, query: str, top_k: int) -> list[EvidenceHit]: ...

    def delete(self, provenance_id: str) -> Mapping[str, Any]: ...


class MemoryLakeBenchmarkEngine:
    """Adapter over the real central MemoryLake public contract."""

    name = "memory_lake_only"

    def __init__(self, lake: object) -> None:
        self.lake = lake

    def index(self, documents: Sequence[BenchmarkDocument]) -> Mapping[str, Any]:
        return self.lake.index_records([document.as_memory_record() for document in documents])

    def retrieve(self, query: str, top_k: int) -> list[EvidenceHit]:
        payload = self.lake.search(
            query,
            filters={"source_type": "education-benchmark", "lane": "benchmark"},
            limit=top_k,
        )
        hits: list[EvidenceHit] = []
        seen: set[str] = set()
        for item in payload.get("results", []):
            provenance_id = str(item.get("provenance_id") or "")
            if provenance_id in seen:
                continue
            seen.add(provenance_id)
            hits.append(
                EvidenceHit(
                    provenance_id=provenance_id,
                    document=str(item.get("snippet") or ""),
                    score=float(item.get("score") or 0.0),
                )
            )
        return hits[:top_k]

    def delete(self, provenance_id: str) -> Mapping[str, Any]:
        return self.lake.delete_sources(provenance_ids=[provenance_id])


class SentenceTransformerDPRRetriever:
    """Local dense retriever implementing the narrow ``retrieve_dpr`` port.

    This reproduces the dense dot-product retrieval profile used by the
    upstream HippoRAG DPR method. It is intentionally not labelled as a full
    HippoRAG graph execution.
    """

    profile = "hipporag_retrieve_dpr_compatible_local_sentence_transformer"

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        model: object | None = None,
    ) -> None:
        import numpy as np

        if model is None:
            from sentence_transformers import SentenceTransformer

            model = SentenceTransformer(model_name, local_files_only=True)
        self.model_name = model_name
        self.model = model
        self._np = np
        self._documents: dict[str, BenchmarkDocument] = {}
        self._ordered: list[BenchmarkDocument] = []
        self._embeddings = np.empty((0, 0), dtype=float)

    def index_documents(self, documents: Sequence[BenchmarkDocument]) -> dict[str, Any]:
        for document in documents:
            self._documents[document.provenance_id] = document
        self._rebuild_embeddings()
        return {"status": "success", "indexed": len(documents), "total": len(self._ordered)}

    def delete_provenance(self, provenance_id: str) -> dict[str, Any]:
        deleted = int(self._documents.pop(provenance_id, None) is not None)
        self._rebuild_embeddings()
        return {"status": "success", "deleted_sources": deleted, "provenance_ids": [provenance_id]}

    def retrieve_dpr(self, queries: list[str], num_to_retrieve: int | None = None) -> list[dict[str, Any]]:
        top_k = int(num_to_retrieve or 10)
        if not self._ordered:
            return [
                {"question": query, "docs": [], "doc_scores": [], "provenance_ids": []}
                for query in queries
            ]
        query_vectors = self._encode(queries)
        solutions: list[dict[str, Any]] = []
        for query, query_vector in zip(queries, query_vectors):
            scores = self._embeddings @ query_vector
            order = self._np.argsort(scores)[::-1][:top_k]
            selected = [self._ordered[int(index)] for index in order]
            solutions.append(
                {
                    "question": query,
                    "docs": [document.text for document in selected],
                    "doc_scores": [float(scores[int(index)]) for index in order],
                    "provenance_ids": [document.provenance_id for document in selected],
                }
            )
        return solutions

    def _rebuild_embeddings(self) -> None:
        self._ordered = sorted(self._documents.values(), key=lambda item: item.provenance_id)
        if not self._ordered:
            self._embeddings = self._np.empty((0, 0), dtype=float)
            return
        self._embeddings = self._encode([document.text for document in self._ordered])

    def _encode(self, texts: Sequence[str]):
        embeddings = self.model.encode(
            list(texts),
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        return self._np.asarray(embeddings, dtype=float)


class DPRGatewayBenchmarkEngine:
    """Benchmark adapter that exercises Synthia's retrieval-only gateway."""

    name = "hipporag_dpr_compatible_adapter"

    def __init__(self, retriever: SentenceTransformerDPRRetriever) -> None:
        self.retriever = retriever
        self.gateway = HippoRAGRetrievalOnlyGateway(retriever)

    def index(self, documents: Sequence[BenchmarkDocument]) -> Mapping[str, Any]:
        return self.retriever.index_documents(documents)

    def retrieve(self, query: str, top_k: int) -> list[EvidenceHit]:
        payload = self.gateway.retrieve([query], top_k)
        result = payload["results"][0]
        return [
            EvidenceHit(provenance_id=provenance_id, document=document, score=score)
            for provenance_id, document, score in zip(
                result["provenance_ids"], result["documents"], result["scores"]
            )
        ]

    def delete(self, provenance_id: str) -> Mapping[str, Any]:
        return self.retriever.delete_provenance(provenance_id)


def load_benchmark_spec(path: Path) -> BenchmarkSpec:
    payload = json.loads(path.read_text(encoding="utf-8"))
    documents = tuple(
        BenchmarkDocument(
            document_id=str(item["document_id"]),
            text=str(item["text"]),
            provenance_id=str(item["provenance_id"]),
            tags=tuple(item.get("tags") or ("education", "synthetic-benchmark")),
        )
        for item in payload["documents"]
    )
    queries = tuple(
        BenchmarkQuery(
            query_id=str(item["query_id"]),
            text=str(item["text"]),
            relevant_provenance_ids=tuple(str(value) for value in item["relevant_provenance_ids"]),
        )
        for item in payload["queries"]
    )
    spec = BenchmarkSpec(
        name=str(payload["name"]),
        documents=documents,
        queries=queries,
        top_k=int(payload.get("top_k", 3)),
        deletion_query_id=str(payload["deletion_case"]["query_id"]),
        deletion_provenance_id=str(payload["deletion_case"]["provenance_id"]),
    )
    _validate_spec(spec)
    return spec


def _validate_spec(spec: BenchmarkSpec) -> None:
    if not spec.documents or not spec.queries:
        raise ValueError("Benchmark requires documents and queries.")
    if spec.top_k < 1:
        raise ValueError("top_k must be positive.")
    provenance_ids = [document.provenance_id for document in spec.documents]
    if len(set(provenance_ids)) != len(provenance_ids):
        raise ValueError("Document provenance_ids must be unique.")
    known = set(provenance_ids)
    for query in spec.queries:
        if not query.relevant_provenance_ids or not set(query.relevant_provenance_ids) <= known:
            raise ValueError(f"Query {query.query_id} has invalid relevance ground truth.")
    query_by_id = {query.query_id: query for query in spec.queries}
    if spec.deletion_query_id not in query_by_id:
        raise ValueError("Deletion query is not present in the query set.")
    if spec.deletion_provenance_id not in query_by_id[spec.deletion_query_id].relevant_provenance_ids:
        raise ValueError("Deletion provenance must be relevant to the deletion query.")


def evaluate_engine(engine: BenchmarkEngine, spec: BenchmarkSpec) -> dict[str, Any]:
    started = time.perf_counter()
    index_result = dict(engine.index(spec.documents))
    baseline_rows: list[dict[str, Any]] = []
    all_hits: list[EvidenceHit] = []
    precision_values: list[float] = []
    recall_values: list[float] = []
    for query in spec.queries:
        hits = engine.retrieve(query.text, spec.top_k)
        all_hits.extend(hits)
        retrieved = [hit.provenance_id for hit in hits[: spec.top_k]]
        relevant = set(query.relevant_provenance_ids)
        relevant_retrieved = relevant.intersection(retrieved)
        precision = len(relevant_retrieved) / spec.top_k
        recall = len(relevant_retrieved) / len(relevant)
        precision_values.append(precision)
        recall_values.append(recall)
        baseline_rows.append(
            {
                "query_id": query.query_id,
                "retrieved_provenance_ids": retrieved,
                "relevant_provenance_ids": list(query.relevant_provenance_ids),
                "precision_at_k": round(precision, 6),
                "recall_at_k": round(recall, 6),
            }
        )

    deletion_query = next(query for query in spec.queries if query.query_id == spec.deletion_query_id)
    before_delete = engine.retrieve(deletion_query.text, spec.top_k)
    delete_result = dict(engine.delete(spec.deletion_provenance_id))
    after_delete = engine.retrieve(deletion_query.text, spec.top_k)
    leakage = any(hit.provenance_id == spec.deletion_provenance_id for hit in after_delete)
    target_document = next(
        document for document in spec.documents if document.provenance_id == spec.deletion_provenance_id
    )
    reconstruction_result = dict(engine.index([target_document]))
    after_reconstruction = engine.retrieve(deletion_query.text, spec.top_k)
    recovered = any(hit.provenance_id == spec.deletion_provenance_id for hit in after_reconstruction)
    provenance_count = sum(bool(hit.provenance_id) for hit in all_hits)

    return {
        "engine": engine.name,
        "index": index_result,
        "metrics": {
            "precision_at_k": round(sum(precision_values) / len(precision_values), 6),
            "recall_at_k": round(sum(recall_values) / len(recall_values), 6),
            "provenance_coverage": round(provenance_count / len(all_hits), 6) if all_hits else 0.0,
            "suppression_leakage": 1.0 if leakage else 0.0,
            "reconstruction_recovery": 1.0 if recovered else 0.0,
        },
        "queries": baseline_rows,
        "lifecycle": {
            "target_provenance_id": spec.deletion_provenance_id,
            "before_delete": [hit.provenance_id for hit in before_delete],
            "delete_result": delete_result,
            "after_delete": [hit.provenance_id for hit in after_delete],
            "reconstruction_result": reconstruction_result,
            "after_reconstruction": [hit.provenance_id for hit in after_reconstruction],
        },
        "elapsed_seconds": round(time.perf_counter() - started, 6),
    }


def run_benchmark(spec: BenchmarkSpec, memory_lake: object, dpr_retriever: SentenceTransformerDPRRetriever) -> dict[str, Any]:
    engines: list[BenchmarkEngine] = [
        MemoryLakeBenchmarkEngine(memory_lake),
        DPRGatewayBenchmarkEngine(dpr_retriever),
    ]
    return {
        "schema": SCHEMA,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "benchmark": {
            "name": spec.name,
            "synthetic_data_only": True,
            "document_count": len(spec.documents),
            "query_count": len(spec.queries),
            "top_k": spec.top_k,
            "metric_definitions": {
                "precision_at_k": "mean relevant retrieved divided by k",
                "recall_at_k": "mean relevant retrieved divided by relevant ground-truth count",
                "provenance_coverage": "retrieved hits with non-empty provenance divided by retrieved hits",
                "suppression_leakage": "1 if deleted provenance remains retrievable, otherwise 0",
                "reconstruction_recovery": "1 if controlled reindex restores target retrieval, otherwise 0",
            },
        },
        "runtime": {
            "python": platform.python_version(),
            "dpr_model": dpr_retriever.model_name,
            "dpr_profile": dpr_retriever.profile,
            "full_hipporag_graph_executed": False,
            "openie_executed": False,
            "generation_performed": False,
            "generation_owner": "codex_or_gemini_after_human_review",
            "authority": "retrieval_measurement_support_only",
            "hierarchy": HIERARCHY,
        },
        "engines": [evaluate_engine(engine, spec) for engine in engines],
    }


def render_markdown(result: Mapping[str, Any]) -> str:
    benchmark = result["benchmark"]
    lines = [
        "# Mission 060 - Retrieval Benchmark",
        "",
        f"Generated: `{result['generated_at']}`",
        "",
        "This benchmark uses synthetic education data only. The dense lane implements the ",
        "HippoRAG `retrieve_dpr` port with a local SentenceTransformer; it does not execute ",
        "the full HippoRAG graph, OpenIE, reranking, or answer generation.",
        "",
        f"Corpus: {benchmark['document_count']} documents, {benchmark['query_count']} queries, `k={benchmark['top_k']}`.",
        "",
        "| Engine | Precision@k | Recall@k | Provenance | Suppression leakage | Reconstruction |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for engine in result["engines"]:
        metrics = engine["metrics"]
        lines.append(
            "| {engine} | {precision:.3f} | {recall:.3f} | {provenance:.3f} | {leakage:.3f} | {recovery:.3f} |".format(
                engine=engine["engine"],
                precision=metrics["precision_at_k"],
                recall=metrics["recall_at_k"],
                provenance=metrics["provenance_coverage"],
                leakage=metrics["suppression_leakage"],
                recovery=metrics["reconstruction_recovery"],
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation Boundary",
            "",
            "These measurements compare retrieval profiles on a small controlled fixture. They do not prove educational efficacy, student classification quality, or production readiness.",
            "",
            "## Metric Definitions",
            "",
        ]
    )
    for name, definition in benchmark["metric_definitions"].items():
        lines.append(f"- `{name}`: {definition}.")
    return "\n".join(lines) + "\n"


def _build_memory_lake(memory_plugin_root: Path, data_dir: Path) -> object:
    sys.path.insert(0, str(memory_plugin_root))
    from memory_lake.config import MemoryConfig
    from memory_lake.store import MemoryLake

    return MemoryLake(
        MemoryConfig(
            plugin_root=memory_plugin_root,
            data_dir=data_dir,
            allowed_roots=(data_dir,),
            obsidian_vault_dir=data_dir / "obsidian-vault",
            enable_chroma=False,
        )
    )


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the Synthia mission-060 retrieval benchmark.")
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--memory-plugin-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--model", default="sentence-transformers/all-MiniLM-L6-v2")
    args = parser.parse_args(list(argv) if argv is not None else None)

    spec = load_benchmark_spec(args.corpus.resolve())
    with tempfile.TemporaryDirectory(prefix="synthia-mission-060-") as temporary_dir:
        memory_lake = _build_memory_lake(args.memory_plugin_root.resolve(), Path(temporary_dir) / "memory")
        retriever = SentenceTransformerDPRRetriever(args.model)
        result = run_benchmark(spec, memory_lake, retriever)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(render_markdown(result), encoding="utf-8")
    print(
        json.dumps(
            {"schema": result["schema"], "output": str(args.output), "engines": result["engines"]},
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
