from pathlib import Path

import numpy as np

from synthia_core.retrieval_benchmark import (
    BenchmarkDocument,
    DPRGatewayBenchmarkEngine,
    SentenceTransformerDPRRetriever,
    evaluate_engine,
    load_benchmark_spec,
)


FIXTURE = Path(__file__).parent / "fixtures" / "education_retrieval_benchmark.v1.json"


class DeterministicModel:
    vocabulary = ("soccer", "geometry", "spanish", "deaf", "autism", "tic", "music")

    def encode(self, texts, **kwargs):
        rows = []
        for text in texts:
            lower = text.lower()
            vector = np.array([float(term in lower) for term in self.vocabulary], dtype=float)
            norm = np.linalg.norm(vector)
            rows.append(vector / norm if norm else vector)
        return np.asarray(rows)


def test_load_benchmark_spec_has_traceable_synthetic_ground_truth():
    spec = load_benchmark_spec(FIXTURE)

    assert spec.name == "scholarium-teach-synthetic-education-v1"
    assert len(spec.documents) == 10
    assert len(spec.queries) == 6
    assert spec.top_k == 3
    assert spec.deletion_provenance_id == "source-spatial-soccer"


def test_dpr_gateway_benchmark_measures_provenance_suppression_and_reconstruction():
    spec = load_benchmark_spec(FIXTURE)
    retriever = SentenceTransformerDPRRetriever("deterministic-test-model", model=DeterministicModel())
    engine = DPRGatewayBenchmarkEngine(retriever)

    result = evaluate_engine(engine, spec)

    assert result["metrics"]["provenance_coverage"] == 1.0
    assert result["metrics"]["suppression_leakage"] == 0.0
    assert result["metrics"]["reconstruction_recovery"] == 1.0
    assert "source-spatial-soccer" in result["lifecycle"]["before_delete"]
    assert "source-spatial-soccer" not in result["lifecycle"]["after_delete"]
    assert "source-spatial-soccer" in result["lifecycle"]["after_reconstruction"]


def test_document_record_marks_fixture_as_synthetic_and_preserves_hierarchy():
    record = BenchmarkDocument("doc", "text", "source-doc").as_memory_record()

    assert record["sensitivity"] == "synthetic"
    assert record["provenance_id"] == "source-doc"
    assert record["metadata"]["synthetic"] is True
    assert "H_lex" in record["metadata"]["hierarchy"]
