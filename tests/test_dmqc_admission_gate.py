from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from synthia_core.cli import main
from synthia_core.dmqc_admission_gate import (
    FORBIDDEN_FNP_FIELDS,
    canonical_sha256,
    evaluate_dmqc_admission,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "dmqc_admission"


def fixture(name: str) -> dict[str, object]:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def assert_no_forbidden_fnp_keys(value: object) -> None:
    if isinstance(value, dict):
        assert FORBIDDEN_FNP_FIELDS.isdisjoint(map(str, value))
        for nested in value.values():
            assert_no_forbidden_fnp_keys(nested)
    elif isinstance(value, list):
        for nested in value:
            assert_no_forbidden_fnp_keys(nested)


def test_complete_provenance_is_accepted_and_ready_for_fnp():
    result = evaluate_dmqc_admission(fixture("admitted_complete.json"))
    assert result["decision"] == {
        "status": "accepted",
        "normalized_state": "admitted",
        "next_action": "route_to_fnp",
        "reason_codes": [],
    }
    assert result["ready_for_fnp"] is True
    assert result["permitted_claims"] == ["synthetic_case_may_be_processed_by_fnp"]
    assert result["reproducibility_status"] == "deterministic_fixture"


def test_missing_provenance_suspends():
    result = evaluate_dmqc_admission(fixture("missing_provenance.json"))
    assert result["decision"]["status"] == "suspended"
    assert result["decision"]["normalized_state"] == "suspended"
    assert result["ready_for_fnp"] is False
    assert "dmqc_missing_provenance" in result["decision"]["reason_codes"]


def test_impossible_formation_energy_unit_rejects():
    result = evaluate_dmqc_admission(fixture("impossible_unit.json"))
    assert result["decision"]["status"] == "rejected"
    assert result["decision"]["next_action"] == "block_fnp"
    assert "dmqc_impossible_unit" in result["decision"]["reason_codes"]
    assert result["evidence_profile"]["H"] == 1.0


def test_recoverable_source_contradiction_suspends_and_increases_i():
    result = evaluate_dmqc_admission(fixture("recoverable_contradiction.json"))
    assert result["decision"]["status"] == "suspended"
    assert "dmqc_recoverable_source_contradiction" in result["decision"]["reason_codes"]
    assert result["evidence_profile"]["C"] > 0.0
    assert result["I"] >= result["evidence_profile"]["C"]


def test_validated_material_overclaim_rejects():
    result = evaluate_dmqc_admission(fixture("claim_overreach.json"))
    assert result["decision"]["status"] == "rejected"
    assert "dmqc_validated_material_claim_without_evidence" in result["decision"]["reason_codes"]
    assert "validated_material_discovery" in result["forbidden_claims"]
    assert result["F"] == 1.0


def test_injected_fnp_field_rejects_recursively():
    result = evaluate_dmqc_admission(fixture("fnp_field_injection.json"))
    assert result["decision"]["status"] == "rejected"
    assert "dmqc_fnp_output_in_synthia" in result["decision"]["reason_codes"]

    payload = fixture("admitted_complete.json")
    payload["nested"] = {"deeper": [{"D_f": 1.49}]}
    assert evaluate_dmqc_admission(payload)["decision"]["status"] == "rejected"


def test_output_contains_no_forbidden_fnp_keys():
    result = evaluate_dmqc_admission(fixture("admitted_complete.json"))
    assert_no_forbidden_fnp_keys(result)
    assert result["boundary"]["forbidden_output_fields"] == sorted(FORBIDDEN_FNP_FIELDS)


def test_json_key_order_does_not_change_decision_or_hash():
    payload = fixture("admitted_complete.json")
    reordered = dict(reversed(list(payload.items())))
    direct = evaluate_dmqc_admission(payload)
    reordered_result = evaluate_dmqc_admission(reordered)
    assert reordered_result == direct
    assert canonical_sha256(reordered_result) == canonical_sha256(direct)


def test_cli_and_python_function_emit_the_same_packet(capsys: pytest.CaptureFixture[str]):
    path = FIXTURES / "admitted_complete.json"
    expected = evaluate_dmqc_admission(fixture("admitted_complete.json"))
    code = main(["dmqc", "admission-check", "--input", str(path), "--json"])
    actual = json.loads(capsys.readouterr().out)
    assert code == 0
    assert actual == expected


def test_three_runs_produce_the_same_canonical_sha256():
    payload = fixture("admitted_complete.json")
    hashes = [canonical_sha256(evaluate_dmqc_admission(copy.deepcopy(payload))) for _ in range(3)]
    assert len(set(hashes)) == 1
    assert len(hashes[0]) == 64


def test_invalid_raw_reference_hash_rejects():
    payload = fixture("admitted_complete.json")
    payload["raw_result_reference"]["sha256"] = "REPLACE_AFTER_CANONICALIZATION"
    result = evaluate_dmqc_admission(payload)
    assert result["decision"]["status"] == "rejected"
    assert "dmqc_raw_reference_hash_mismatch" in result["decision"]["reason_codes"]


def test_non_object_input_is_rejected_by_contract():
    with pytest.raises(ValueError, match="JSON object"):
        evaluate_dmqc_admission(["not", "an", "object"])
