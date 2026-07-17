import json

import pytest

from synthia_core.cli import main
from synthia_core.hipporag_bridge import (
    HippoRAGEdgeTrace,
    HippoRAGGenerationDisabled,
    HippoRAGGraphLocation,
    HippoRAGMemoryBit,
    HippoRAGRetrievalOnlyGateway,
    MemoryLakeHippoRAGTraceStore,
    build_memory_bit_from_cli,
)
from synthia_core.plithogenic import TIF
from synthia_core.safety import HIERARCHY


class FakeMemoryLake:
    def __init__(self):
        self.batches = []
        self.searches = []

    def index_records(self, records, mode="incremental"):
        self.batches.append((records, mode))
        return {"status": "success", "indexed": len(records), "skipped": 0, "deduped": 0, "failed": 0}

    def search(self, query, filters=None, limit=8):
        self.searches.append((query, filters, limit))
        return {"status": "success", "count": 1, "results": [{"id": "chunk-1"}]}

    def health(self):
        return {"status": "success", "ready": True, "database": "test-memory.sqlite"}


class FakeQuerySolution:
    def __init__(self, question, docs, doc_scores, provenance_ids=()):
        self.question = question
        self.docs = docs
        self.doc_scores = doc_scores
        self.provenance_ids = provenance_ids


class FakeHippoRAG:
    def __init__(self):
        self.retrieve_dpr_calls = []
        self.generation_calls = []

    def retrieve_dpr(self, queries, num_to_retrieve=None):
        self.retrieve_dpr_calls.append((queries, num_to_retrieve))
        return (
            [FakeQuerySolution(queries[0], ["Approved source passage"], [0.94], ["source-card-1"])],
            {"recall@5": 1.0},
        )

    def rag_qa(self, *args, **kwargs):
        self.generation_calls.append("rag_qa")

    def qa(self, *args, **kwargs):
        self.generation_calls.append("qa")


def test_hipporag_memory_bit_preserves_lexicon_graph_and_tif():
    memory_bit = HippoRAGMemoryBit(
        lexicon_type="taxonomy",
        content="Aburria aburri redescription repairs diagnostic context.",
        graph_location=HippoRAGGraphLocation(
            namespace="hipporag.case.study",
            node_type="fact",
            node_id="fact-1",
            chunk_id="chunk-1",
            entity_id="entity-aburria",
            fact_id="fact-redescription",
            hop_depth=2,
        ),
        selection_mechanism="fact_rerank",
        tif=TIF(T=0.86, I=0.12, F=0.02, I_system=0.12, D_f=0.12, dF=0.03, i_fractal=0.12),
        source_ids=("hipporag-case-study",),
        relevance=0.91,
    )

    payload = memory_bit.as_dict()

    assert payload["lexicon_type"] == "taxonomy"
    assert payload["graph_location"]["fact_id"] == "fact-redescription"
    assert payload["selection_mechanism"] == "fact_rerank"
    assert payload["selection_score"] > 0.0
    assert payload["tif"]["hierarchy"] == HIERARCHY
    assert payload["plithogenic_profile"]["hierarchy"] == HIERARCHY
    assert payload["i_lexicon_trace"]["plithogenic_classified_as"] == "I_system^S"


def test_hipporag_memory_bit_round_trips_mapping():
    original = HippoRAGMemoryBit(
        lexicon_type="physics",
        content="Thermal anomaly is a physics signal candidate.",
        graph_location=HippoRAGGraphLocation("swarm", "entity", "thermal"),
        selection_mechanism="personalized_pagerank",
        relevance=0.75,
    )

    loaded = HippoRAGMemoryBit.from_mapping(original.as_dict())

    assert loaded.memory_bit_id == original.memory_bit_id
    assert loaded.lexicon_type == "physics"
    assert loaded.graph_location.node_id == "thermal"
    assert loaded.selection_mechanism == "personalized_pagerank"


def test_build_memory_bit_from_cli_defaults_to_plithogenic_trace():
    memory_bit = build_memory_bit_from_cli(
        lexicon_type="biology",
        content="Unknown leaf candidate.",
        namespace="synthia",
        node_type="chunk",
        node_id="chunk-leaf",
        selection_mechanism="plithogenic_trace",
        relevance=0.6,
        source_ids=["cli"],
        tif=TIF(T=0.6, I=0.35, F=0.05, I_system=0.35),
    )

    assert memory_bit.lexicon_type == "biology"
    assert memory_bit.graph_location.node_type == "chunk"
    assert memory_bit.source_ids == ("cli",)


def test_hipporag_edge_trace_payload():
    edge = HippoRAGEdgeTrace(
        left_memory_bit_id="hippo.bit.left",
        right_memory_bit_id="hippo.bit.right",
        relation="lexicon_bridge",
        lexicon_type="phylocode_nomenclature",
        weight=0.8,
    ).as_dict()

    assert edge["left_memory_bit_id"] == "hippo.bit.left"
    assert edge["relation"] == "lexicon_bridge"
    assert edge["weight"] == 0.8
    assert edge["hierarchy"] == HIERARCHY


def test_memory_lake_store_indexes_bit_and_selection_trace_in_preparation():
    lake = FakeMemoryLake()
    store = MemoryLakeHippoRAGTraceStore(lake)
    memory_bit = HippoRAGMemoryBit(
        lexicon_type="education",
        content="Spatial reasoning can support a geometry learning strategy.",
        graph_location=HippoRAGGraphLocation("scholarium", "strength", "spatial-1"),
        selection_mechanism="plithogenic_trace",
        source_ids=("growth-story-1",),
    )

    result = store.store_memory_bit(memory_bit)

    assert result["stored"] is True
    records, mode = lake.batches[0]
    assert mode == "incremental"
    assert len(records) == 2
    assert {record["source_type"] for record in records} == {
        "hipporag-memory-bit",
        "hipporag-selection-trace",
    }
    assert all(record["lane"] == "preparation" for record in records)
    assert all(record["approval_state"] == "pending" for record in records)
    assert records[0]["metadata"]["payload"]["graph_location"]["node_id"] == "spatial-1"
    assert records[0]["metadata"]["hierarchy"] == HIERARCHY


def test_memory_lake_store_indexes_edge_and_delegates_retrieval():
    lake = FakeMemoryLake()
    store = MemoryLakeHippoRAGTraceStore(lake)
    edge = HippoRAGEdgeTrace(
        left_memory_bit_id="hippo.bit.left",
        right_memory_bit_id="hippo.bit.right",
        relation="learning_bridge",
        lexicon_type="education",
    )

    stored = store.store_edge(edge)
    selected = store.select_memory_bits("education", "plithogenic_trace", 5)

    assert stored["stored"] is True
    assert lake.batches[0][0][0]["source_type"] == "hipporag-graph-edge"
    assert selected["count"] == 1
    assert selected["partition"] == "preparation"
    assert lake.searches == [
        ("plithogenic_trace", {"source_type": "hipporag-memory-bit", "tag": "lexicon:education"}, 5)
    ]


def test_memory_lake_store_status_exposes_central_backend_without_local_memory():
    status = MemoryLakeHippoRAGTraceStore(FakeMemoryLake()).status()

    assert status["backend"] == "memory_lake"
    assert status["ready"] is True
    assert status["partition"] == "preparation"
    assert status["hierarchy"] == HIERARCHY


def test_retrieval_only_gateway_returns_sourced_results_without_generation():
    hipporag = FakeHippoRAG()
    gateway = HippoRAGRetrievalOnlyGateway(hipporag)

    result = gateway.retrieve(["How can spatial reasoning support geometry?"], 5)

    assert hipporag.retrieve_dpr_calls == [(["How can spatial reasoning support geometry?"], 5)]
    assert hipporag.generation_calls == []
    assert result["schema"] == "synthia.hipporag-retrieval.v1"
    assert result["results"][0] == {
        "question": "How can spatial reasoning support geometry?",
        "documents": ["Approved source passage"],
        "scores": [0.94],
        "provenance_ids": ["source-card-1"],
    }
    assert result["metrics"] == {"recall@5": 1.0}
    assert result["generation_performed"] is False
    assert result["generation_owner"] == "codex_or_gemini"
    assert result["retrieval_profile"] == "hipporag_dpr_only"
    assert result["hierarchy"] == HIERARCHY


@pytest.mark.parametrize("method", ["rag_qa", "rag_qa_dpr", "qa", "generate"])
def test_retrieval_only_gateway_rejects_generation_before_upstream_call(method):
    hipporag = FakeHippoRAG()
    gateway = HippoRAGRetrievalOnlyGateway(hipporag)

    with pytest.raises(HippoRAGGenerationDisabled, match="generation belongs to Codex or Gemini"):
        getattr(gateway, method)(["query"])

    assert hipporag.generation_calls == []


@pytest.mark.parametrize("queries, limit", [([], 5), (["   "], 5), (["valid"], 0), (["valid"], 51)])
def test_retrieval_only_gateway_rejects_invalid_requests(queries, limit):
    gateway = HippoRAGRetrievalOnlyGateway(FakeHippoRAG())

    with pytest.raises(ValueError):
        gateway.retrieve(queries, limit)


def test_cli_hipporag_backend_status_smoke(capsys):
    code = main(["hipporag", "backend", "status", "--rethinkdb-port", "1"])

    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["backend"] == "rethinkdb"
    assert payload["hipporag_tables"] == [
        "hipporag_memory_bits",
        "hipporag_graph_edges",
        "hipporag_selection_traces",
    ]
