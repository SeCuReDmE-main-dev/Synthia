import json

from synthia_core.cli import main
from synthia_core.safety import HIERARCHY
from synthia_core.scientific_governance import (
    DATASHEETS_SOURCE_ID,
    FAIR_PRINCIPLES_SOURCE_ID,
    MODEL_CARDS_SOURCE_ID,
    NIST_AI_RMF_SOURCE_ID,
    TRIPOD_AI_SOURCE_ID,
    GovernancePriority,
    GovernanceStandard,
    ScientificGovernanceCase,
    ValidationStatus,
    build_synthia_governance_demo_case,
    score_scientific_governance_case,
)


def test_parser_preserves_source_ids_formal_values_and_bounds():
    case = ScientificGovernanceCase.from_raw_case(
        {
            "case_label": "Parser governance case",
            "review_subject": "Synthetic review subject",
            "intended_use": "Review support",
            "out_of_scope_use": "Certification",
            "source_ids": ["source.case"],
            "evidence_sources": [
                {
                    "source_id": "source.record",
                    "standard": GovernanceStandard.MODEL_CARD.value,
                    "title": "Synthetic model card source",
                    "url": "https://example.test/model-card",
                    "coverage_T": 1.4,
                    "coverage_I": 0.4,
                    "coverage_F": -0.3,
                    "weight": -2.0,
                }
            ],
        }
    )
    payload = score_scientific_governance_case(case)
    source = payload["evidence_sources"][0]

    assert payload["source_ids"][:2] == ["source.case", "source.record"]
    assert source["formal_value"]["T"] == 1.4
    assert source["formal_value"]["F"] == -0.3
    assert source["operational_tif"]["T"] == 1.0
    assert source["operational_tif"]["F"] == 0.0
    assert source["weight"] == 0.0
    assert payload["validation_status"] == ValidationStatus.SPECIALIST_REVIEW_REQUIRED.value
    assert payload["human_review_required"] is True
    assert payload["hierarchy"] == HIERARCHY


def test_rejects_non_object_case_non_array_sources_and_bad_related_payload():
    try:
        ScientificGovernanceCase.from_raw_case([])
    except ValueError as exc:
        assert "must be a JSON object" in str(exc)
    else:
        raise AssertionError("non-object case should be rejected")

    try:
        ScientificGovernanceCase.from_raw_case({"evidence_sources": {"source_id": "bad"}})
    except ValueError as exc:
        assert "evidence_sources must be a JSON array" in str(exc)
    else:
        raise AssertionError("non-array evidence_sources should be rejected")

    try:
        ScientificGovernanceCase.from_raw_case({"evidence_sources": [], "related_taxon_packet": []})
    except ValueError as exc:
        assert "related_taxon_packet must be a JSON object" in str(exc)
    else:
        raise AssertionError("non-object related payload should be rejected")


def test_empty_evidence_is_critical_and_bounded():
    payload = score_scientific_governance_case({"case_label": "Empty governance case", "evidence_sources": []})

    assert payload["reporting_standard_coverage"] == {
        standard.value: 0.0 for standard in GovernanceStandard
    }
    assert payload["evidence_gap_load"] == 1.0
    assert payload["contradiction_load"] == 1.0
    assert payload["uncertainty_load"] == 1.0
    assert payload["governance_priority"] == GovernancePriority.CRITICAL_REVIEW.value
    assert payload["operational_tif"]["T"] == 0.0
    assert payload["operational_tif"]["I"] == 1.0
    assert payload["operational_tif"]["F"] == 0.0
    assert payload["model_card"]["human_review_required"] is True
    assert payload["dataset_sheet"]["fair_metadata_status"] == "missing"


def test_missing_standards_and_high_indeterminacy_drive_priority():
    payload = score_scientific_governance_case(
        {
            "case_label": "Gap governance case",
            "review_subject": "Synthetic model output",
            "evidence_sources": [
                {
                    "source_id": "source.only",
                    "standard": GovernanceStandard.MODEL_CARD.value,
                    "title": "Only model card",
                    "url": "https://example.test/only",
                    "coverage_T": 0.92,
                    "coverage_I": 0.84,
                    "coverage_F": 0.66,
                    "weight": 1.0,
                }
            ],
        }
    )

    assert payload["reporting_standard_coverage"][GovernanceStandard.MODEL_CARD.value] == 1.0
    assert payload["evidence_gap_load"] >= 0.75
    assert payload["governance_priority"] == GovernancePriority.CRITICAL_REVIEW.value
    assert payload["operational_tif"]["G_lex"] == payload["contradiction_load"]


def test_related_phase_payloads_are_preserved_and_reported():
    related_taxon = {"taxon_label": "Synthetic taxon", "human_review_required": True}
    related_risk = {"case_label": "Synthetic risk", "human_review_required": True}
    related_graph = {"graph_label": "Synthetic graph", "human_review_required": True}
    related_molecular = {"case_label": "Synthetic molecular", "human_review_required": True}
    related_algorithm = {"case_label": "Synthetic algorithm", "human_review_required": True}
    payload = score_scientific_governance_case(
        {
            "case_label": "Linked governance case",
            "review_subject": "Linked synthetic review",
            "related_taxon_packet": related_taxon,
            "related_risk_case": related_risk,
            "related_biology_graph": related_graph,
            "related_molecular_review": related_molecular,
            "related_algorithm_behavior": related_algorithm,
            "evidence_sources": [
                {
                    "source_id": MODEL_CARDS_SOURCE_ID,
                    "standard": GovernanceStandard.MODEL_CARD.value,
                    "title": "Model card anchor",
                    "coverage_T": 0.8,
                    "coverage_I": 0.2,
                    "coverage_F": 0.1,
                }
            ],
        }
    )

    assert payload["related_taxon_packet"] == related_taxon
    assert payload["related_risk_case"] == related_risk
    assert payload["related_biology_graph"] == related_graph
    assert payload["related_molecular_review"] == related_molecular
    assert payload["related_algorithm_behavior"] == related_algorithm
    assert payload["model_card"]["linked_phase_payloads"] == [
        "phase_1_taxon_packet",
        "phase_2_risk_case",
        "phase_3_biology_graph",
        "phase_4_molecular_review",
        "phase_5_algorithm_behavior",
    ]
    assert "no scientific certification" in payload["authority_boundary"]
    assert "no autonomous scientific conclusion" in payload["authority_boundary"]


def test_demo_case_is_public_safe_and_links_all_standards():
    payload = score_scientific_governance_case(build_synthia_governance_demo_case())
    serialized = json.dumps(payload, ensure_ascii=False).lower()

    assert payload["case_label"] == "Synthetic Synthia governance reporting case"
    assert set(payload["source_ids"]) == {
        NIST_AI_RMF_SOURCE_ID,
        TRIPOD_AI_SOURCE_ID,
        MODEL_CARDS_SOURCE_ID,
        DATASHEETS_SOURCE_ID,
        FAIR_PRINCIPLES_SOURCE_ID,
    }
    assert set(payload["reporting_standard_coverage"]) == {standard.value for standard in GovernanceStandard}
    assert payload["dataset_sheet"]["fair_metadata_status"] == "source_linked"
    assert payload["model_card"]["human_review_required"] is True
    forbidden_terms = (
        "raw_" + "private_" + "gmail_" + "body",
        "private_" + "message_" + "id",
        "h" + "2" + "o",
        "auto" + "ml",
    )
    for term in forbidden_terms:
        assert term not in serialized


def test_cli_scientific_governance_score_and_demo(capsys):
    case = {
        "case_label": "CLI governance fixture",
        "review_subject": "CLI review",
        "evidence_sources": [
            {
                "source_id": FAIR_PRINCIPLES_SOURCE_ID,
                "standard": GovernanceStandard.FAIR_DATA.value,
                "title": "FAIR fixture",
                "coverage_T": 0.72,
                "coverage_I": 0.2,
                "coverage_F": 0.08,
            }
        ],
    }

    assert main(["scientific-governance", "score", "--case", json.dumps(case)]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["case_label"] == "CLI governance fixture"
    assert payload["human_review_required"] is True

    assert main(["scientific-governance", "demo"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert NIST_AI_RMF_SOURCE_ID in payload["source_ids"]
