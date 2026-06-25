import json

from synthia_core.cli import main
from synthia_core.hipporag_bridge import (
    HippoRAGEdgeTrace,
    HippoRAGGraphLocation,
    HippoRAGMemoryBit,
    build_memory_bit_from_cli,
)
from synthia_core.plithogenic import TIF
from synthia_core.safety import HIERARCHY


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
