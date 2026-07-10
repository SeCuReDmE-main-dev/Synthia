from __future__ import annotations

import copy
import json
from pathlib import Path

from synthia_core.chapter14_threshold_gate import classify_chapter14_threshold
from synthia_core.cli import main

ROOT = Path(__file__).resolve().parents[1]


def event():
    return json.loads((ROOT / "tests/fixtures/neutrino_chapter14_valid_event.json").read_text(encoding="utf-8"))


def assert_no_fractal_fields(value):
    forbidden = {"D_f", "D_f_hat", "dF", "i_fractal", "i_fractal_candidate"}
    if isinstance(value, dict):
        assert forbidden.isdisjoint(value)
        for nested in value.values(): assert_no_fractal_fields(nested)
    elif isinstance(value, list):
        for nested in value: assert_no_fractal_fields(nested)


def test_valid_threshold_profile_is_additive_and_admitted():
    result = classify_chapter14_threshold(event())
    profile = result["LexPacket_neutrino"]["chapter14_threshold_profile"]
    assert result["Adm_lex"] is True
    assert profile["chapter14_status"] == "ready_for_fnp_threshold_calculation"
    assert profile["carrier_policy"] == {"exact_ten_carrier_set": True, "provided_count": 10}
    assert profile["capability_boundary"]["physical_model_validated"] is False
    assert result["schema_version"] == "synthia.lex_neutrino.v1"
    assert_no_fractal_fields(result)


def test_missing_source_and_missing_carrier_suspend():
    payload = event(); contract = payload["chapter14_threshold_contract"]
    contract["sources"] = []; contract["i_quasicrystal_vec"]["carriers"].pop()
    result = classify_chapter14_threshold(payload)
    assert result["decision"]["status"] == "suspended"
    assert "chapter14_missing_primary_sources" in result["decision"]["reason_codes"]
    assert "chapter14_invalid_ten_carrier_vector" in result["decision"]["reason_codes"]


def test_substrate_detection_and_biology_claims_reject():
    for flag in ("substrate_as_established_fact", "real_detection_claim", "penrose_as_physical_proof", "quasicrystal_proves_neutrino", "biological_validation_claim"):
        payload = event(); payload["chapter14_threshold_contract"]["claim_flags"][flag] = True
        result = classify_chapter14_threshold(payload)
        assert result["decision"]["status"] == "rejected"
        assert result["Adm_lex"] is False


def test_unbounded_phason_suspends_and_fnp_output_rejects():
    payload = event(); payload["chapter14_threshold_contract"]["phason_transition"].pop("scale")
    assert classify_chapter14_threshold(payload)["decision"]["status"] == "suspended"
    payload = event(); payload["chapter14_threshold_contract"]["D_f"] = 1.4
    result = classify_chapter14_threshold(payload)
    assert result["decision"]["status"] == "rejected"
    assert "chapter14_fnp_output_in_synthia" in result["decision"]["reason_codes"]


def test_cli_emits_profile(capsys):
    code = main(["neutrino", "chapter14-threshold-check", "--input", str(ROOT / "tests/fixtures/neutrino_chapter14_valid_event.json"), "--json"])
    result = json.loads(capsys.readouterr().out)
    assert code == 0
    assert result["chapter14_threshold_profile"]["chapter14_status"] == "ready_for_fnp_threshold_calculation"
