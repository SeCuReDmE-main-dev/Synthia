import json

from synthia_core.cli import main
from synthia_core.phylo_plithogenic import (
    PhyloPlithogenicReviewPacket,
    ReviewStatus,
    build_tilapia_style_demo_packet,
    score_phylo_plithogenic_packet,
)
from synthia_core.safety import HIERARCHY


def test_parser_preserves_source_ids_and_review_status():
    packet = PhyloPlithogenicReviewPacket.from_raw_packet(
        {
            "taxon_label": "Synthetic candidate",
            "taxon_type": "candidate_taxon",
            "phylo_context": "public-safe fixture",
            "review_status": ReviewStatus.DRAFT.value,
            "source_ids": ["source.a", "source.b"],
            "dimensions": [
                {"name": "phylogeny", "value": "anchor", "T": 1.2, "I": 0.1, "F": -0.1, "weight": -5, "dominant": True}
            ],
        }
    )

    payload = packet.score()

    assert payload["source_ids"] == ["source.a", "source.b"]
    assert payload["review_status"] == "draft"
    assert payload["dimensions"][0]["formal_value"]["T"] == 1.2
    assert payload["dimensions"][0]["operational_tif"]["T"] == 1.0
    assert payload["dimensions"][0]["weight"] == 0.0
    assert payload["human_review_required"] is True
    assert payload["hierarchy"] == HIERARCHY


def test_dominant_dimension_controls_contradiction_comparison():
    payload = score_phylo_plithogenic_packet(
        {
            "taxon_label": "Synthetic species",
            "taxon_type": "species",
            "phylo_context": "dominant dimension fixture",
            "dimensions": [
                {"name": "morphology", "value": "variant", "T": 0.1, "I": 0.1, "F": 0.8},
                {"name": "phylogeny", "value": "anchor", "T": 0.9, "I": 0.05, "F": 0.0, "dominant": True},
            ],
        }
    )

    assert payload["dominant_dimension"]["name"] == "phylogeny"
    assert payload["contradictions"][0]["name"] == "morphology"
    assert payload["contradictions"][0]["degree"] > payload["contradictions"][1]["degree"]


def test_high_contradiction_produces_high_review_priority():
    payload = score_phylo_plithogenic_packet(
        {
            "taxon_label": "Conflicted synthetic taxon",
            "taxon_type": "species",
            "phylo_context": "high contradiction fixture",
            "dimensions": [
                {"name": "phylogeny", "value": "anchor", "T": 1.0, "I": 0.0, "F": 0.0, "dominant": True},
                {"name": "expert_disagreement", "value": "strong_conflict", "T": 0.0, "I": 1.0, "F": 1.0},
            ],
        }
    )

    assert payload["review_priority"] == "high"
    assert payload["contradiction_load"] >= 0.6
    assert payload["operational_tif"]["I_lexicon"] == payload["contradiction_load"]


def test_empty_dimensions_are_max_indeterminacy_and_bounded():
    payload = score_phylo_plithogenic_packet(
        {
            "taxon_label": "Empty candidate",
            "taxon_type": "candidate_taxon",
            "phylo_context": "empty dimension fixture",
            "dimensions": [],
        }
    )

    assert payload["dominant_dimension"] is None
    assert payload["contradiction_load"] == 1.0
    assert payload["operational_tif"]["T"] == 0.0
    assert payload["operational_tif"]["I"] == 1.0
    assert payload["operational_tif"]["F"] == 0.0
    assert payload["human_review_required"] is True


def test_demo_packet_is_public_safe_and_review_bounded():
    payload = build_tilapia_style_demo_packet().score()
    serialized = json.dumps(payload, ensure_ascii=False)

    assert payload["taxon_label"] == "Oreochromis niloticus review candidate"
    assert payload["taxon_type"] == "species"
    assert payload["human_review_required"] is True
    assert "formal nomenclatural act" in payload["authority_boundary"]
    assert "drive.aguilar.wiley_mayden_species_speciation_1985" in payload["source_ids"]
    assert "nss.tilapia_tilv_plithogenic_fuzzy_soft_set_2025" in payload["source_ids"]
    assert "raw_private_gmail_body" not in serialized
    assert "private_thread_subject" not in serialized
    assert "private_message_id" not in serialized


def test_cli_phylo_plithogenic_score_and_demo(capsys):
    packet = {
        "taxon_label": "CLI synthetic candidate",
        "taxon_type": "species",
        "phylo_context": "cli fixture",
        "dimensions": [
            {"name": "phylogeny", "value": "anchor", "T": 0.9, "I": 0.05, "F": 0.0, "dominant": True},
            {"name": "ecology", "value": "variant", "T": 0.6, "I": 0.3, "F": 0.1},
        ],
    }

    assert main(["taxonomy", "phylo-plithogenic", "score", "--packet", json.dumps(packet)]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["human_review_required"] is True
    assert payload["taxon_label"] == "CLI synthetic candidate"

    assert main(["taxonomy", "phylo-plithogenic", "demo"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["source_pair_hint"]["plithogenic_anchor"] == "nss.tilapia_tilv_plithogenic_fuzzy_soft_set_2025"
