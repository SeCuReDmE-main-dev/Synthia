import json

import pytest

from synthia_core.biology_graph import (
    CONCENTRIC_HYPERGRAPH_SOURCE_ID,
    HYPERSOFT_GRAPH_SOURCE_ID,
    RESTRICTED_SUPERHYPERGRAPH_SOURCE_ID,
    TREE_TOBACCO_SOURCE_ID,
    BiologyGraphReviewLayer,
    GraphReviewPriority,
    build_tree_tobacco_demo_graph,
    score_biology_graph_review,
)
from synthia_core.cli import main
from synthia_core.safety import HIERARCHY


def test_parser_preserves_formal_values_and_bounds():
    graph = BiologyGraphReviewLayer.from_raw_graph(
        {
            "graph_label": "Parser graph",
            "source_ids": ["source.graph"],
            "nodes": [
                {
                    "id": "node.a",
                    "label": "Node A",
                    "node_type": "criterion",
                    "T": 1.2,
                    "I": 0.4,
                    "F": -0.1,
                    "weight": -5,
                    "source_ids": ["source.node"],
                },
                {"id": "node.b", "label": "Node B", "node_type": "outcome", "T": 0.2, "I": 0.3, "F": 0.4},
            ],
            "edges": [
                {"id": "edge.a", "source": "node.a", "target": "node.b", "edge_type": "evidence", "T": 0.6, "I": 0.2, "F": 0.1}
            ],
        }
    )
    payload = graph.score()

    assert payload["graph_label"] == "Parser graph"
    assert payload["source_ids"][:2] == ["source.graph", "source.node"]
    assert payload["nodes"][0]["formal_value"]["T"] == 1.2
    assert payload["nodes"][0]["operational_tif"]["T"] == 1.0
    assert payload["nodes"][0]["operational_tif"]["F"] == 0.0
    assert payload["nodes"][0]["weight"] == 0.0
    assert payload["human_review_required"] is True
    assert payload["hierarchy"] == HIERARCHY


def test_invalid_edge_reference_is_rejected():
    with pytest.raises(ValueError, match="existing biology graph node id"):
        BiologyGraphReviewLayer.from_raw_graph(
            {
                "nodes": [{"id": "node.a", "T": 0.5, "I": 0.2, "F": 0.1}],
                "edges": [{"id": "edge.bad", "source": "node.a", "target": "missing", "T": 0.5, "I": 0.2, "F": 0.1}],
            }
        )


def test_contradiction_edge_can_force_critical_review():
    payload = score_biology_graph_review(
        {
            "graph_label": "Contradiction graph",
            "nodes": [
                {"id": "node.signal", "label": "Signal", "node_type": "outcome", "T": 0.8, "I": 0.1, "F": 0.05},
                {"id": "node.expert", "label": "Expert disagreement", "node_type": "expert", "T": 0.2, "I": 0.7, "F": 0.4},
            ],
            "edges": [
                {
                    "id": "edge.conflict",
                    "source": "node.signal",
                    "target": "node.expert",
                    "edge_type": "contradiction",
                    "T": 0.2,
                    "I": 0.82,
                    "F": 0.5,
                }
            ],
        }
    )

    assert payload["contradiction_load"] >= 0.75
    assert payload["review_priority"] == GraphReviewPriority.CRITICAL_REVIEW.value
    assert payload["operational_tif"]["G_lex"] == payload["contradiction_load"]


def test_empty_nodes_are_critical_and_bounded():
    payload = score_biology_graph_review({"graph_label": "Empty graph", "nodes": []})

    assert payload["node_count"] == 0
    assert payload["edge_count"] == 0
    assert payload["hyperedge_count"] == 0
    assert payload["supervertex_count"] == 0
    assert payload["dominant_system_node"] is None
    assert payload["contradiction_load"] == 1.0
    assert payload["uncertainty_load"] == 1.0
    assert payload["review_priority"] == GraphReviewPriority.CRITICAL_REVIEW.value
    assert payload["operational_tif"]["T"] == 0.0
    assert payload["operational_tif"]["I"] == 1.0
    assert payload["operational_tif"]["F"] == 0.0


def test_demo_graph_is_public_safe_and_source_linked():
    payload = score_biology_graph_review(build_tree_tobacco_demo_graph())
    serialized = json.dumps(payload, ensure_ascii=False)

    assert payload["graph_label"] == "Synthetic tree tobacco extract review graph"
    assert payload["node_count"] == 5
    assert payload["edge_count"] == 4
    assert payload["hyperedge_count"] == 1
    assert payload["supervertex_count"] == 1
    assert payload["human_review_required"] is True
    assert TREE_TOBACCO_SOURCE_ID in payload["source_ids"]
    assert CONCENTRIC_HYPERGRAPH_SOURCE_ID in payload["source_ids"]
    assert HYPERSOFT_GRAPH_SOURCE_ID in payload["source_ids"]
    assert RESTRICTED_SUPERHYPERGRAPH_SOURCE_ID in payload["source_ids"]
    assert "formal taxonomic act" in payload["authority_boundary"]
    assert "private_thread_subject" not in serialized
    assert "raw_private_gmail_body" not in serialized
    assert "private_message_id" not in serialized


def test_cli_biology_graph_score_and_demo(capsys):
    graph = {
        "graph_label": "CLI graph fixture",
        "nodes": [
            {"id": "node.a", "label": "A", "node_type": "criterion", "T": 0.7, "I": 0.2, "F": 0.1},
            {"id": "node.b", "label": "B", "node_type": "outcome", "T": 0.6, "I": 0.3, "F": 0.1},
        ],
        "edges": [{"id": "edge.a", "source": "node.a", "target": "node.b", "edge_type": "evidence", "T": 0.6, "I": 0.2, "F": 0.1}],
    }

    assert main(["biology-graph", "score", "--graph", json.dumps(graph)]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["graph_label"] == "CLI graph fixture"
    assert payload["human_review_required"] is True

    assert main(["biology-graph", "demo"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["source_anchors"][0]["source_id"] == TREE_TOBACCO_SOURCE_ID
