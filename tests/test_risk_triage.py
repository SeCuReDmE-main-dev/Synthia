import json

from synthia_core.cli import main
from synthia_core.risk_triage import (
    P2NRS_SOURCE_URL,
    RiskDomain,
    RiskPriority,
    RiskTriageCase,
    RoughRegion,
    build_food_safety_demo_case,
    score_risk_triage_case,
)
from synthia_core.safety import HIERARCHY


def test_risk_case_parser_preserves_formal_values_and_bounds():
    case = RiskTriageCase.from_raw_case(
        {
            "case_label": "Parser fixture",
            "domain": RiskDomain.ENVIRONMENT.value,
            "source_ids": ["source.risk"],
            "criteria": [
                {
                    "name": "sensor",
                    "value": "uncertain",
                    "T": 1.2,
                    "I": 0.4,
                    "F": -0.1,
                    "probability": 1.4,
                    "weight": -2,
                    "source_ids": ["source.risk"],
                }
            ],
        }
    )
    payload = score_risk_triage_case(case)

    assert payload["case_label"] == "Parser fixture"
    assert payload["domain"] == "environment"
    assert payload["source_ids"] == ["source.risk"]
    assert payload["criteria"][0]["formal_value"]["T"] == 1.2
    assert payload["criteria"][0]["formal_value"]["probability"] == 1.4
    assert payload["criteria"][0]["operational_tif"]["T"] == 1.0
    assert payload["criteria"][0]["operational_probability"] == 1.0
    assert payload["criteria"][0]["weight"] == 0.0
    assert payload["human_review_required"] is True
    assert payload["hierarchy"] == HIERARCHY


def test_lower_approximation_maps_to_critical_review():
    payload = score_risk_triage_case(
        {
            "case_label": "Clear high risk",
            "criteria": [
                {"name": "microbial", "value": "high", "T": 0.9, "I": 0.05, "F": 0.02, "probability": 0.9, "weight": 2},
                {"name": "temperature", "value": "high", "T": 0.86, "I": 0.06, "F": 0.03, "probability": 0.84},
            ],
        }
    )

    assert payload["rough_region"] == RoughRegion.LOWER_APPROXIMATION.value
    assert payload["risk_priority"] == RiskPriority.CRITICAL_REVIEW.value
    assert payload["risk_signal"] >= 0.70


def test_boundary_region_maps_to_elevated_review():
    payload = score_risk_triage_case(
        {
            "case_label": "Uncertain case",
            "criteria": [
                {"name": "sensor_uncertainty", "value": "missing", "T": 0.45, "I": 0.7, "F": 0.1, "probability": 0.55},
                {"name": "expert_disagreement", "value": "conflict", "T": 0.42, "I": 0.65, "F": 0.2, "probability": 0.50},
            ],
        }
    )

    assert payload["rough_region"] == RoughRegion.BOUNDARY_REGION.value
    assert payload["risk_priority"] == RiskPriority.ELEVATED.value
    assert payload["uncertainty_load"] > 0.35


def test_empty_criteria_are_critical_and_bounded():
    payload = score_risk_triage_case({"case_label": "Empty case", "criteria": []})

    assert payload["rough_region"] == RoughRegion.BOUNDARY_REGION.value
    assert payload["risk_priority"] == RiskPriority.CRITICAL_REVIEW.value
    assert payload["probability_load"] == 1.0
    assert payload["contradiction_load"] == 1.0
    assert payload["operational_tif"]["T"] == 0.0
    assert payload["operational_tif"]["I"] == 1.0
    assert payload["operational_tif"]["F"] == 0.0


def test_related_taxon_packet_is_preserved_without_authority_claim():
    related = {"taxon_label": "Synthetic taxon", "human_review_required": True}
    payload = score_risk_triage_case(
        {
            "case_label": "Conservation bridge",
            "domain": "conservation",
            "related_taxon_packet": related,
            "criteria": [
                {"name": "habitat", "value": "degraded", "T": 0.7, "I": 0.2, "F": 0.1, "probability": 0.65}
            ],
        }
    )

    assert payload["related_taxon_packet"] == related
    assert "no public-health" in payload["decision_boundary"]
    assert "taxonomic authority" in payload["decision_boundary"]


def test_food_safety_demo_is_public_safe_and_source_linked():
    payload = score_risk_triage_case(build_food_safety_demo_case())
    serialized = json.dumps(payload, ensure_ascii=False)

    assert payload["case_label"] == "Synthetic milk batch review case"
    assert payload["domain"] == RiskDomain.FOOD_SAFETY.value
    assert payload["source_anchor"]["url"] == P2NRS_SOURCE_URL
    assert payload["human_review_required"] is True
    assert "private_thread_subject" not in serialized
    assert "raw_private_gmail_body" not in serialized
    assert "private_message_id" not in serialized


def test_cli_risk_triage_score_and_demo(capsys):
    case = {
        "case_label": "CLI risk fixture",
        "criteria": [
            {"name": "microbial", "value": "watch", "T": 0.6, "I": 0.2, "F": 0.1, "probability": 0.55}
        ],
    }

    assert main(["risk-triage", "score", "--case", json.dumps(case)]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["case_label"] == "CLI risk fixture"
    assert payload["human_review_required"] is True

    assert main(["risk-triage", "demo"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["source_anchor"]["source_id"] == "nss.p2nrs_food_safety_2025"

