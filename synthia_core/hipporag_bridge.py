"""HippoRAG-style memory graph trace storage for Synthia.

This module does not vendor HippoRAG. It stores Synthia-compatible graph memory
bits in RethinkDB so HippoRAG-style passage/entity/fact locations can be traced
by lexicon type, selection mechanism, and plithogenic state.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Iterable, Mapping, Protocol
from uuid import uuid4

from .plithogenic import PlithogenicAttribute, PlithogenicMatrix, TIF, clamp01
from .safety import HIERARCHY
from .swarm import RethinkDBBackendConfig, RethinkDBSwarmBackend


class HippoRAGSelectionMechanism(str, Enum):
    DENSE_PASSAGE = "dense_passage"
    FACT_RERANK = "fact_rerank"
    PERSONALIZED_PAGERANK = "personalized_pagerank"
    LEXICON_BRIDGE = "lexicon_bridge"
    PLITHOGENIC_TRACE = "plithogenic_trace"
    MANUAL_REVIEW = "manual_review"


class MemoryLakePort(Protocol):
    """Narrow central-memory contract used by the Synthia adapter."""

    def index_records(self, records: list[dict[str, Any]], mode: str = "incremental") -> dict[str, Any]: ...

    def search(
        self,
        query: str,
        filters: dict[str, Any] | None = None,
        limit: int = 8,
    ) -> dict[str, Any]: ...

    def health(self) -> dict[str, Any]: ...


class HippoRAGRetrieverPort(Protocol):
    def retrieve_dpr(self, queries: list[str], num_to_retrieve: int | None = None) -> object: ...


class HippoRAGGenerationDisabled(RuntimeError):
    """Raised when a caller crosses the retrieval-only production boundary."""


class HippoRAGRetrievalOnlyGateway:
    """Expose HippoRAG evidence retrieval without its answer-generation APIs."""

    SCHEMA = "synthia.hipporag-retrieval.v1"
    GENERATION_OWNER = "codex_or_gemini"

    def __init__(self, retriever: HippoRAGRetrieverPort) -> None:
        self.retriever = retriever

    def retrieve(self, queries: Iterable[str], num_to_retrieve: int = 10) -> dict[str, object]:
        clean_queries = [str(query).strip() for query in queries if str(query).strip()]
        if not clean_queries:
            raise ValueError("At least one non-empty retrieval query is required.")
        if not 1 <= num_to_retrieve <= 50:
            raise ValueError("num_to_retrieve must be between 1 and 50.")

        raw = self.retriever.retrieve_dpr(clean_queries, num_to_retrieve)
        metrics: Mapping[str, object] = {}
        solutions = raw
        if isinstance(raw, tuple):
            solutions = raw[0]
            if len(raw) > 1 and isinstance(raw[1], Mapping):
                metrics = raw[1]
        if not isinstance(solutions, Iterable) or isinstance(solutions, (str, bytes, Mapping)):
            raise TypeError("HippoRAG retrieve returned an unsupported result shape.")

        return {
            "schema": self.SCHEMA,
            "queries": clean_queries,
            "results": [self._serialize_solution(solution) for solution in solutions],
            "metrics": dict(metrics),
            "generation_performed": False,
            "generation_owner": self.GENERATION_OWNER,
            "retrieval_profile": "hipporag_dpr_only",
            "authority": "retrieval_support_only",
            "hierarchy": HIERARCHY,
        }

    def rag_qa(self, *args: object, **kwargs: object) -> None:
        self._deny_generation("rag_qa")

    def rag_qa_dpr(self, *args: object, **kwargs: object) -> None:
        self._deny_generation("rag_qa_dpr")

    def qa(self, *args: object, **kwargs: object) -> None:
        self._deny_generation("qa")

    def generate(self, *args: object, **kwargs: object) -> None:
        self._deny_generation("generate")

    @staticmethod
    def _deny_generation(method: str) -> None:
        raise HippoRAGGenerationDisabled(
            f"HippoRAG method {method} is disabled: generation belongs to Codex or Gemini after retrieval review."
        )

    @staticmethod
    def _serialize_solution(solution: object) -> dict[str, object]:
        if isinstance(solution, Mapping):
            question = solution.get("question", "")
            docs = solution.get("docs", [])
            scores = solution.get("doc_scores", [])
            provenance_ids = solution.get("provenance_ids", [])
        else:
            question = getattr(solution, "question", "")
            docs = getattr(solution, "docs", [])
            scores = getattr(solution, "doc_scores", [])
            provenance_ids = getattr(solution, "provenance_ids", [])
        return {
            "question": str(question),
            "documents": [str(document) for document in docs or []],
            "scores": [float(score) for score in scores or []],
            "provenance_ids": [str(provenance_id) for provenance_id in provenance_ids or []],
        }


@dataclass(frozen=True)
class HippoRAGGraphLocation:
    namespace: str
    node_type: str
    node_id: str
    chunk_id: str | None = None
    entity_id: str | None = None
    fact_id: str | None = None
    edge_id: str | None = None
    hop_depth: int = 0

    def as_dict(self) -> dict[str, object]:
        return {
            "namespace": self.namespace,
            "node_type": self.node_type,
            "node_id": self.node_id,
            "chunk_id": self.chunk_id,
            "entity_id": self.entity_id,
            "fact_id": self.fact_id,
            "edge_id": self.edge_id,
            "hop_depth": self.hop_depth,
        }


@dataclass(frozen=True)
class HippoRAGMemoryBit:
    lexicon_type: str
    content: str
    graph_location: HippoRAGGraphLocation
    selection_mechanism: str
    tif: TIF = field(default_factory=lambda: TIF(T=0.7, I=0.25, F=0.05, I_system=0.25))
    source_ids: tuple[str, ...] = ()
    memory_bit_id: str = field(default_factory=lambda: f"hippo.bit.{uuid4().hex}")
    relevance: float = 0.5
    created_at: float = field(default_factory=time.time)

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> "HippoRAGMemoryBit":
        location_payload = payload.get("graph_location") if isinstance(payload.get("graph_location"), Mapping) else {}
        tif_payload = payload.get("tif") if isinstance(payload.get("tif"), Mapping) else {}
        return cls(
            lexicon_type=str(payload.get("lexicon_type", "general")),
            content=str(payload.get("content", "")),
            graph_location=HippoRAGGraphLocation(
                namespace=str(location_payload.get("namespace", "synthia")),
                node_type=str(location_payload.get("node_type", "memory_bit")),
                node_id=str(location_payload.get("node_id", payload.get("memory_bit_id", "unknown"))),
                chunk_id=_optional_str(location_payload.get("chunk_id")),
                entity_id=_optional_str(location_payload.get("entity_id")),
                fact_id=_optional_str(location_payload.get("fact_id")),
                edge_id=_optional_str(location_payload.get("edge_id")),
                hop_depth=int(location_payload.get("hop_depth", 0)),
            ),
            selection_mechanism=str(payload.get("selection_mechanism", HippoRAGSelectionMechanism.PLITHOGENIC_TRACE.value)),
            tif=TIF(
                T=float(tif_payload.get("T", payload.get("T", 0.7))),
                I=float(tif_payload.get("I", payload.get("I", 0.25))),
                F=float(tif_payload.get("F", payload.get("F", 0.05))),
                I_system=tif_payload.get("I_system^S", payload.get("I_system")),
                H_lex=tif_payload.get("H_lex", payload.get("H_lex")),
                G_lex=tif_payload.get("G_lex", payload.get("G_lex")),
                I_lexicon=tif_payload.get("I_lexicon", payload.get("I_lexicon")),
                D_f=tif_payload.get("D_f", payload.get("D_f")),
                dF=tif_payload.get("dF", payload.get("dF")),
                i_fractal=tif_payload.get("i_fractal", payload.get("i_fractal")),
            ),
            source_ids=tuple(str(item) for item in payload.get("source_ids", []) if item),
            memory_bit_id=str(payload.get("memory_bit_id", payload.get("id", f"hippo.bit.{uuid4().hex}"))),
            relevance=float(payload.get("relevance", 0.5)),
            created_at=float(payload.get("created_at", time.time())),
        )

    def selection_score(self) -> float:
        bounded = self.tif.bounded()
        graph_boost = clamp01(1.0 / (1.0 + max(0, self.graph_location.hop_depth)))
        return clamp01((bounded.T * 0.45) + (self.relevance * 0.35) + (graph_boost * 0.2) - (bounded.F * 0.2))

    def as_dict(self) -> dict[str, object]:
        attribute = PlithogenicAttribute(
            name=self.memory_bit_id,
            value=self.lexicon_type,
            tif=self.tif,
            weight=self.selection_score(),
            source_id=self.source_ids[0] if self.source_ids else None,
        )
        profile = PlithogenicMatrix([attribute]).profile()
        return {
            "id": self.memory_bit_id,
            "memory_bit_id": self.memory_bit_id,
            "lexicon_type": self.lexicon_type,
            "content": self.content,
            "content_sha256": hashlib.sha256(self.content.encode("utf-8")).hexdigest(),
            "graph_location": self.graph_location.as_dict(),
            "selection_mechanism": self.selection_mechanism,
            "selection_score": self.selection_score(),
            "relevance": clamp01(self.relevance),
            "source_ids": list(self.source_ids),
            "tif": self.tif.as_dict(),
            "plithogenic_profile": profile,
            "i_lexicon_trace": profile["indeterminacy_profile"],
            "created_at": self.created_at,
            "hierarchy": HIERARCHY,
        }


@dataclass(frozen=True)
class HippoRAGEdgeTrace:
    left_memory_bit_id: str
    right_memory_bit_id: str
    relation: str
    weight: float = 1.0
    lexicon_type: str = "general"
    edge_id: str = field(default_factory=lambda: f"hippo.edge.{uuid4().hex}")

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.edge_id,
            "edge_id": self.edge_id,
            "left_memory_bit_id": self.left_memory_bit_id,
            "right_memory_bit_id": self.right_memory_bit_id,
            "relation": self.relation,
            "weight": clamp01(self.weight),
            "lexicon_type": self.lexicon_type,
            "hierarchy": HIERARCHY,
        }


class RethinkDBHippoRAGTraceStore:
    MEMORY_BITS_TABLE = "hipporag_memory_bits"
    GRAPH_EDGES_TABLE = "hipporag_graph_edges"
    SELECTION_TRACES_TABLE = "hipporag_selection_traces"

    def __init__(self, config: RethinkDBBackendConfig | None = None) -> None:
        self.backend = RethinkDBSwarmBackend(config)
        self.config = self.backend.config

    def status(self) -> dict[str, object]:
        status = self.backend.status()
        status["hipporag_tables"] = [
            self.MEMORY_BITS_TABLE,
            self.GRAPH_EDGES_TABLE,
            self.SELECTION_TRACES_TABLE,
        ]
        return status

    def ensure_schema(self) -> dict[str, object]:
        base = self.backend.ensure_schema()
        r = self.backend._driver()
        conn = self.backend._connect(r)
        try:
            existing = r.table_list().run(conn)
            created = []
            for table in (self.MEMORY_BITS_TABLE, self.GRAPH_EDGES_TABLE, self.SELECTION_TRACES_TABLE):
                if table not in existing:
                    r.table_create(table).run(conn)
                    created.append(table)
                r.table(table).wait().run(conn)
            return {
                "database": self.config.database,
                "swarm_schema": base,
                "created_tables": created,
                "hipporag_ready": True,
            }
        finally:
            conn.close()

    def store_memory_bit(self, memory_bit: HippoRAGMemoryBit) -> dict[str, object]:
        self.ensure_schema()
        r = self.backend._driver()
        conn = self.backend._connect(r)
        try:
            document = memory_bit.as_dict()
            result = r.table(self.MEMORY_BITS_TABLE).insert(document, conflict="replace").run(conn)
            trace = {
                "id": f"selection.{memory_bit.memory_bit_id}",
                "memory_bit_id": memory_bit.memory_bit_id,
                "lexicon_type": memory_bit.lexicon_type,
                "selection_mechanism": memory_bit.selection_mechanism,
                "selection_score": memory_bit.selection_score(),
                "graph_location": memory_bit.graph_location.as_dict(),
                "created_at": time.time(),
                "hierarchy": HIERARCHY,
            }
            trace_result = r.table(self.SELECTION_TRACES_TABLE).insert(trace, conflict="replace").run(conn)
            return {
                "stored": True,
                "memory_bit_id": memory_bit.memory_bit_id,
                "result": result,
                "selection_trace_result": trace_result,
            }
        finally:
            conn.close()

    def store_edge(self, edge: HippoRAGEdgeTrace) -> dict[str, object]:
        self.ensure_schema()
        r = self.backend._driver()
        conn = self.backend._connect(r)
        try:
            result = r.table(self.GRAPH_EDGES_TABLE).insert(edge.as_dict(), conflict="replace").run(conn)
            return {"stored": True, "edge_id": edge.edge_id, "result": result}
        finally:
            conn.close()

    def select_memory_bits(
        self,
        lexicon_type: str | None = None,
        selection_mechanism: str | None = None,
        limit: int = 10,
    ) -> dict[str, object]:
        r = self.backend._driver()
        conn = self.backend._connect(r)
        try:
            query = r.table(self.MEMORY_BITS_TABLE)
            if lexicon_type:
                query = query.filter({"lexicon_type": lexicon_type})
            if selection_mechanism:
                query = query.filter({"selection_mechanism": selection_mechanism})
            rows = list(query.order_by(r.desc("selection_score")).limit(limit).run(conn))
            return {
                "lexicon_type": lexicon_type,
                "selection_mechanism": selection_mechanism,
                "count": len(rows),
                "memory_bits": rows,
                "hierarchy": HIERARCHY,
            }
        finally:
            conn.close()


class MemoryLakeHippoRAGTraceStore:
    """Persist Synthia HippoRAG traces in the central MemoryLake."""

    PRODUCT = "scholarium-central-knowledge-gateway"
    LANE = "preparation"

    def __init__(self, lake: MemoryLakePort) -> None:
        self.lake = lake

    def status(self) -> dict[str, object]:
        health = self.lake.health()
        return {
            "backend": "memory_lake",
            "ready": bool(health.get("ready")),
            "partition": self.LANE,
            "product": self.PRODUCT,
            "memory_lake": health,
            "hierarchy": HIERARCHY,
        }

    def store_memory_bit(self, memory_bit: HippoRAGMemoryBit) -> dict[str, object]:
        payload = memory_bit.as_dict()
        selection_trace = {
            "id": f"selection.{memory_bit.memory_bit_id}",
            "memory_bit_id": memory_bit.memory_bit_id,
            "lexicon_type": memory_bit.lexicon_type,
            "selection_mechanism": memory_bit.selection_mechanism,
            "selection_score": memory_bit.selection_score(),
            "graph_location": memory_bit.graph_location.as_dict(),
            "created_at": time.time(),
            "hierarchy": HIERARCHY,
        }
        result = self.lake.index_records(
            [
                self._record(
                    "memory-bit",
                    memory_bit.memory_bit_id,
                    memory_bit.content,
                    payload,
                    memory_bit.lexicon_type,
                    memory_bit.source_ids,
                ),
                self._record(
                    "selection-trace",
                    str(selection_trace["id"]),
                    (
                        f"Selected {memory_bit.memory_bit_id} with "
                        f"{memory_bit.selection_mechanism} at score "
                        f"{memory_bit.selection_score():.6f}."
                    ),
                    selection_trace,
                    memory_bit.lexicon_type,
                    memory_bit.source_ids,
                ),
            ]
        )
        return {
            "stored": result.get("failed", 0) == 0,
            "memory_bit_id": memory_bit.memory_bit_id,
            "partition": self.LANE,
            "result": result,
        }

    def store_edge(self, edge: HippoRAGEdgeTrace) -> dict[str, object]:
        result = self.lake.index_records(
            [
                self._record(
                    "graph-edge",
                    edge.edge_id,
                    f"{edge.left_memory_bit_id} {edge.relation} {edge.right_memory_bit_id}",
                    edge.as_dict(),
                    edge.lexicon_type,
                    (edge.left_memory_bit_id, edge.right_memory_bit_id),
                )
            ]
        )
        return {
            "stored": result.get("failed", 0) == 0,
            "edge_id": edge.edge_id,
            "partition": self.LANE,
            "result": result,
        }

    def select_memory_bits(
        self,
        lexicon_type: str | None = None,
        selection_mechanism: str | None = None,
        limit: int = 10,
    ) -> dict[str, object]:
        filters: dict[str, Any] = {"source_type": "hipporag-memory-bit"}
        if lexicon_type:
            filters["tag"] = f"lexicon:{lexicon_type}"
        query = selection_mechanism or lexicon_type or "HippoRAG memory graph trace"
        result = self.lake.search(query, filters=filters, limit=limit)
        return {
            "lexicon_type": lexicon_type,
            "selection_mechanism": selection_mechanism,
            "count": int(result.get("count", 0)),
            "memory_bits": result.get("results", []),
            "partition": self.LANE,
            "hierarchy": HIERARCHY,
        }

    def _record(
        self,
        record_type: str,
        record_id: str,
        text: str,
        payload: Mapping[str, object],
        lexicon_type: str,
        source_ids: Iterable[str],
    ) -> dict[str, Any]:
        return {
            "path": f"synthia-hipporag:{record_type}:{record_id}",
            "text": text,
            "source_type": f"hipporag-{record_type}",
            "product": self.PRODUCT,
            "lane": self.LANE,
            "sensitivity": "private",
            "uncertainty": "human-review-required",
            "approval_state": "pending",
            "subject": f"Synthia HippoRAG {record_type}",
            "claim": "Trace candidate stored for retrieval and human review.",
            "confidence_label": "tentative due to conflicting or missing evidence",
            "provenance_id": record_id,
            "artifact_targets": ["internal-note"],
            "connector_source_subtype": "synthia-hipporag-trace",
            "tags": [
                "hipporag",
                "synthia",
                f"record:{record_type}",
                f"lexicon:{lexicon_type}",
                f"partition:{self.LANE}",
            ],
            "metadata": {
                "schema": "synthia.hipporag-trace.v1",
                "record_type": record_type,
                "lexicon_type": lexicon_type,
                "source_ids": list(source_ids),
                "payload": dict(payload),
                "hierarchy": HIERARCHY,
            },
        }


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    text = str(value)
    return text or None


def build_memory_bit_from_cli(
    *,
    lexicon_type: str,
    content: str,
    namespace: str,
    node_type: str,
    node_id: str,
    selection_mechanism: str,
    relevance: float,
    source_ids: Iterable[str],
    tif: TIF,
) -> HippoRAGMemoryBit:
    return HippoRAGMemoryBit(
        lexicon_type=lexicon_type,
        content=content,
        graph_location=HippoRAGGraphLocation(namespace=namespace, node_type=node_type, node_id=node_id),
        selection_mechanism=selection_mechanism,
        tif=tif,
        source_ids=tuple(source_ids),
        relevance=relevance,
    )
