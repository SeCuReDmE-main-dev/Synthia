import json

from synthia_core.cli import main
from synthia_core.neutrino_lexical_gate import classify_neutrino_observation


def _valid_event():
    return {
        "event_id": "public-safe-neutrino-001",
        "claim_class": "simulation",
        "interaction_channel": "weak_CC",
        "detector_signature": "toy electron-like secondary trace",
        "source_truth": {"phase1_reference": "public physics reference"},
    }


def _json_has_key(payload, key):
    if isinstance(payload, dict):
        return key in payload or any(_json_has_key(value, key) for value in payload.values())
    if isinstance(payload, list):
        return any(_json_has_key(value, key) for value in payload)
    return False


def test_valid_simulation_event_is_admitted():
    payload = classify_neutrino_observation(_valid_event())

    assert payload["schema_version"] == "synthia.lex_neutrino.v1"
    assert payload["Adm_lex"] is True
    assert payload["decision"]["status"] == "accepted"
    assert 0.0 <= payload["dL_lex"] <= 1.0
    assert payload["LexPacket_neutrino"]["source_layer"] == "lexical"
    assert not _json_has_key(payload, "dF")
    assert not _json_has_key(payload, "D_f")
    assert not _json_has_key(payload, "i_fractal")


def test_real_detection_claim_is_rejected():
    event = _valid_event()
    event["detector_signature"] = "real neutrino detected by this chamber"
    payload = classify_neutrino_observation(event)

    assert payload["Adm_lex"] is False
    assert payload["decision"]["status"] == "rejected"
    assert payload["decision"]["next_action"] == "block_fnp"
    assert "real_detection_claim" in payload["refusal_packet"]["reason_codes"]


def test_strong_primary_claim_is_rejected():
    event = _valid_event()
    event["interaction_channel"] = "strong"
    payload = classify_neutrino_observation(event)

    assert payload["Adm_lex"] is False
    assert payload["decision"]["status"] == "rejected"
    assert "strong_primary_interaction_claim" in payload["refusal_packet"]["reason_codes"]


def test_correctable_internal_mechanism_language_reruns_synthia():
    event = _valid_event()
    event["interpretation"] = "the neutrino chooses fusion and decay while it gains mass"
    payload = classify_neutrino_observation(event)

    assert payload["Adm_lex"] is False
    assert payload["decision"]["status"] == "corrected"
    assert payload["decision"]["next_action"] == "rerun_synthia"
    assert "choice_or_intention_language" in payload["refusal_packet"]["reason_codes"]
    assert "fusion_as_internal_flavor_mechanism" in payload["refusal_packet"]["reason_codes"]
    assert "decay_as_internal_flavor_mechanism" in payload["refusal_packet"]["reason_codes"]
    assert "literal_mass_gain_loss_claim" in payload["refusal_packet"]["reason_codes"]


def test_missing_source_truth_is_suspended():
    event = _valid_event()
    event.pop("source_truth")
    payload = classify_neutrino_observation(event)

    assert payload["Adm_lex"] is False
    assert payload["decision"]["status"] == "suspended"
    assert payload["decision"]["next_action"] == "hold_for_review"
    assert "missing_source_truth" in payload["refusal_packet"]["reason_codes"]


def test_collapse_claims_are_rejected():
    event = _valid_event()
    event["dL_lex"] = 0.5
    event["dF"] = 0.5
    event["I_lexicon"] = 0.4
    event["i_fractal"] = 0.4
    payload = classify_neutrino_observation(event)

    assert payload["Adm_lex"] is False
    assert payload["decision"]["status"] == "rejected"
    assert "dL_lex_equals_dF" in payload["refusal_packet"]["reason_codes"]
    assert "I_lexicon_equals_i_fractal" in payload["refusal_packet"]["reason_codes"]


def test_detector_trace_and_candidate_proof_claims_are_rejected():
    event = _valid_event()
    event["notes"] = "detector trace is the neutrino and candidate is proof"
    payload = classify_neutrino_observation(event)

    assert payload["Adm_lex"] is False
    assert payload["decision"]["status"] == "rejected"
    assert "detector_trace_confused_with_particle" in payload["refusal_packet"]["reason_codes"]
    assert "candidate_confused_with_proof" in payload["refusal_packet"]["reason_codes"]


def test_cli_guardrail_check_returns_same_contract(tmp_path, capsys):
    input_path = tmp_path / "event.json"
    input_path.write_text(json.dumps(_valid_event()), encoding="utf-8")

    assert main(["neutrino", "guardrail-check", "--input", str(input_path), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["schema_version"] == "synthia.lex_neutrino.v1"
    assert payload["LexPacket_neutrino"]["Adm_lex"] is True
