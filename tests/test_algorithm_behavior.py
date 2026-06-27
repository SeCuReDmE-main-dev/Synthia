import json

from synthia_core.algorithm_behavior import (
    ALGORITHMIC_BEHAVIOR_SEED_SOURCE_ID,
    ALGORITHMIC_PARAMETER_CORPUS_SOURCE_ID,
    AlgorithmBehaviorCase,
    AlgorithmReviewPriority,
    BehaviorFamily,
    build_algorithmic_bioinformatics_demo_case,
    score_algorithm_behavior_case,
)
from synthia_core.cli import main
from synthia_core.safety import HIERARCHY


def test_parser_preserves_sources_metadata_and_bounds():
    case = AlgorithmBehaviorCase.from_raw_case(
        {
            "case_label": "Parser algorithm case",
            "algorithm_context": "Synthetic review context",
            "source_ids": ["source.case"],
            "parameter_records": [
                {
                    "name": "alpha",
                    "algorithm_family": "regularization_family",
                    "behavior_families": [BehaviorFamily.REGULARIZATION_CONSTRAINTS.value],
                    "hyperparameter": "yes",
                    "T": 1.4,
                    "I": 0.4,
                    "F": -0.2,
                    "weight": -2.0,
                    "source_ids": ["source.record"],
                    "configured_value": {"grid": [0.1, 0.5]},
                    "expected_role": "capacity constraint",
                    "validation_status": "reviewed",
                    "bioinformatics_relevance": 1.3,
                }
            ],
        }
    )
    payload = score_algorithm_behavior_case(case)
    record = payload["parameter_records"][0]

    assert payload["source_ids"][:2] == ["source.case", "source.record"]
    assert record["formal_value"]["T"] == 1.4
    assert record["formal_value"]["F"] == -0.2
    assert record["operational_tif"]["T"] == 1.0
    assert record["operational_tif"]["F"] == 0.0
    assert record["configured_value"] == {"grid": [0.1, 0.5]}
    assert record["operational_bioinformatics_relevance"] == 1.0
    assert record["weight"] == 0.0
    assert payload["human_review_required"] is True
    assert payload["hierarchy"] == HIERARCHY


def test_rejects_non_object_case_and_non_array_parameters():
    try:
        AlgorithmBehaviorCase.from_raw_case([])
    except ValueError as exc:
        assert "must be a JSON object" in str(exc)
    else:
        raise AssertionError("non-object case should be rejected")

    try:
        AlgorithmBehaviorCase.from_raw_case({"parameter_records": {"name": "bad"}})
    except ValueError as exc:
        assert "parameter_records must be a JSON array" in str(exc)
    else:
        raise AssertionError("non-array parameter_records should be rejected")


def test_empty_parameters_are_critical_and_bounded():
    payload = score_algorithm_behavior_case({"case_label": "Empty algorithm case", "parameter_records": []})

    assert payload["parameter_count"] == 0
    assert payload["algorithm_count"] == 0
    assert payload["dominant_behavior_family"] is None
    assert payload["behavior_family_loads"] == {}
    assert payload["algorithmic_risk_signal"] == 1.0
    assert payload["contradiction_load"] == 1.0
    assert payload["uncertainty_load"] == 1.0
    assert payload["review_priority"] == AlgorithmReviewPriority.CRITICAL_REVIEW.value
    assert payload["operational_tif"]["T"] == 0.0
    assert payload["operational_tif"]["I"] == 1.0
    assert payload["operational_tif"]["F"] == 0.0


def test_dominant_family_and_high_uncertainty_drive_priority():
    payload = score_algorithm_behavior_case(
        {
            "case_label": "Contradicted algorithm case",
            "algorithm_context": "Synthetic review context",
            "parameter_records": [
                {
                    "name": "distribution",
                    "algorithm_family": "objective_family",
                    "behavior_families": [BehaviorFamily.LOSS_DISTRIBUTION_LINK.value],
                    "hyperparameter": "yes",
                    "T": 0.96,
                    "I": 0.78,
                    "F": 0.72,
                    "weight": 2.0,
                    "validation_status": "failed",
                    "bioinformatics_relevance": 1.0,
                },
                {
                    "name": "seed",
                    "algorithm_family": "reproducibility_family",
                    "behavior_families": [BehaviorFamily.REPRODUCIBILITY_RESOURCE_CONTROL.value],
                    "hyperparameter": "yes",
                    "T": 0.8,
                    "I": 0.1,
                    "F": 0.05,
                    "weight": 0.1,
                    "validation_status": "reviewed",
                    "bioinformatics_relevance": 0.4,
                },
            ],
        }
    )

    assert payload["dominant_behavior_family"] == BehaviorFamily.LOSS_DISTRIBUTION_LINK.value
    assert payload["algorithmic_risk_signal"] >= 0.75
    assert payload["review_priority"] == AlgorithmReviewPriority.CRITICAL_REVIEW.value
    assert payload["operational_tif"]["G_lex"] == payload["contradiction_load"]


def test_related_payloads_are_preserved_without_authority_expansion():
    related_molecular = {"case_label": "Synthetic molecular", "human_review_required": True}
    related_graph = {"graph_label": "Synthetic graph", "human_review_required": True}
    payload = score_algorithm_behavior_case(
        {
            "case_label": "Linked algorithm case",
            "related_molecular_review": related_molecular,
            "related_biology_graph": related_graph,
            "parameter_records": [
                {
                    "name": "validation_frame",
                    "algorithm_family": "validation_family",
                    "behavior_families": [BehaviorFamily.VALIDATION_STOPPING_CHECKPOINTING.value],
                    "hyperparameter": "no",
                    "T": 0.7,
                    "I": 0.25,
                    "F": 0.1,
                    "validation_status": "partially_reviewed",
                }
            ],
        }
    )

    assert payload["related_molecular_review"] == related_molecular
    assert payload["related_biology_graph"] == related_graph
    assert "no model-performance guarantee" in payload["authority_boundary"]
    assert "no biological conclusion" in payload["authority_boundary"]


def test_demo_case_is_public_safe_and_synthia_native():
    payload = score_algorithm_behavior_case(build_algorithmic_bioinformatics_demo_case())
    serialized = json.dumps(payload, ensure_ascii=False).lower()

    assert payload["case_label"] == "Synthetic bioinformatics algorithm behavior review"
    assert payload["parameter_count"] == 6
    assert ALGORITHMIC_PARAMETER_CORPUS_SOURCE_ID in payload["source_ids"]
    assert ALGORITHMIC_BEHAVIOR_SEED_SOURCE_ID in payload["source_ids"]
    assert payload["source_anchor"]["vendor_terms_admitted"] is False
    forbidden_terms = (
        "auto" + "ml",
        "xg" + "boost",
        "h" + "2" + "o",
        "raw_" + "private_" + "gmail_" + "body",
        "private_" + "message_" + "id",
    )
    for term in forbidden_terms:
        assert term not in serialized


def test_cli_algorithm_behavior_score_and_demo(capsys):
    case = {
        "case_label": "CLI algorithm fixture",
        "algorithm_context": "CLI review",
        "parameter_records": [
            {
                "name": "nfolds",
                "algorithm_family": "validation_family",
                "behavior_families": [BehaviorFamily.VALIDATION_STOPPING_CHECKPOINTING.value],
                "hyperparameter": "no",
                "T": 0.68,
                "I": 0.22,
                "F": 0.1,
                "validation_status": "reviewed",
            }
        ],
    }

    assert main(["algorithm-behavior", "score", "--case", json.dumps(case)]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["case_label"] == "CLI algorithm fixture"
    assert payload["human_review_required"] is True

    assert main(["algorithm-behavior", "demo"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["source_anchor"]["source_id"] == ALGORITHMIC_BEHAVIOR_SEED_SOURCE_ID
