import json
from pathlib import Path

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


def test_chapter3_valid_muon_flavor_mass_phase_event_is_profiled():
    event = _valid_event()
    event.update(
        {
            "created_flavor": "mu",
            "flavor_basis": {"e": 0.0, "mu": 1.0, "tau": 0.0},
            "mass_basis": {"nu1": 0.17, "nu2": 0.33, "nu3": 0.50},
            "distance_km": 295,
            "energy_gev": 0.6,
            "secondary_products": ["muon_like_track", "proton_like_activity"],
            "detector_signature": "toy muon-like indirect projection",
        }
    )

    payload = classify_neutrino_observation(event)
    chapter3 = payload["LexPacket_neutrino"]["chapter3_profile"]

    assert payload["Adm_lex"] is True
    assert chapter3["flavor_profile"]["I_flavor"]["created_flavor"] == "nu_mu"
    assert chapter3["mass_profile"]["I_mass"]["mass_weights_status"] == "toy_simulation"
    assert chapter3["phase_profile"]["I_phase"]["L_over_E"] == 491.66666667
    assert chapter3["interaction_profile"]["I_interaction"]["channel"] == "weak_CC"
    assert chapter3["detector_profile"]["I_detector"]["detector_projection_status"] == "indirect"
    assert not _json_has_key(payload, "dF")


def test_unknown_flavor_claim_as_truth_is_rejected():
    event = _valid_event()
    event["created_flavor"] = "sterile"

    payload = classify_neutrino_observation(event)

    assert payload["Adm_lex"] is False
    assert payload["decision"]["status"] == "rejected"
    assert "unknown_flavor_as_truth" in payload["refusal_packet"]["reason_codes"]


def test_declared_unknown_flavor_is_profiled_without_inventing_truth():
    event = _valid_event()
    event["created_flavor"] = "sterile"
    event["flavor_status"] = "unknown"

    payload = classify_neutrino_observation(event)
    chapter3 = payload["LexPacket_neutrino"]["chapter3_profile"]

    assert payload["Adm_lex"] is True
    assert chapter3["flavor_profile"]["I_flavor"]["created_flavor"] == "unknown"
    assert "unknown_flavor_as_truth" not in payload["refusal_packet"]["reason_codes"]


def test_flavor_mass_collapse_is_rejected():
    event = _valid_event()
    event["notes"] = "flavor_weak_state = mass_propagation_state"

    payload = classify_neutrino_observation(event)

    assert payload["Adm_lex"] is False
    assert payload["decision"]["status"] == "rejected"
    assert "flavor_mass_collapse" in payload["refusal_packet"]["reason_codes"]


def test_equal_flavor_and_mass_basis_vectors_are_rejected():
    event = _valid_event()
    event["flavor_basis"] = {"e": 0.0, "mu": 1.0, "tau": 0.0}
    event["mass_basis"] = {"nu1": 0.0, "nu2": 1.0, "nu3": 0.0}

    payload = classify_neutrino_observation(event)

    assert payload["Adm_lex"] is False
    assert "mass_basis_equals_flavor_basis" in payload["refusal_packet"]["reason_codes"]


def test_pmns_measured_and_phase_tension_proof_language_reruns_synthia():
    event = _valid_event()
    event["notes"] = "this is the measured PMNS and phase tension proves new physics"

    payload = classify_neutrino_observation(event)

    assert payload["Adm_lex"] is False
    assert payload["decision"]["status"] == "corrected"
    assert "pmns_measured_claim" in payload["refusal_packet"]["reason_codes"]
    assert "phase_tension_as_new_physics" in payload["refusal_packet"]["reason_codes"]


def test_invalid_energy_is_suspended():
    event = _valid_event()
    event["distance_km"] = 295
    event["energy_gev"] = 0

    payload = classify_neutrino_observation(event)

    assert payload["Adm_lex"] is False
    assert payload["decision"]["status"] == "suspended"
    assert "invalid_energy_gev" in payload["refusal_packet"]["reason_codes"]


def test_weak_nc_is_admitted_without_direct_flavor_readout_claim():
    event = _valid_event()
    event["interaction_channel"] = "neutral_current"
    event["detector_signature"] = "toy neutral-current indirect projection"

    payload = classify_neutrino_observation(event)
    chapter3 = payload["LexPacket_neutrino"]["chapter3_profile"]

    assert payload["Adm_lex"] is True
    assert chapter3["interaction_profile"]["I_interaction"]["channel"] == "weak_NC"


def test_visible_neutrino_and_simulated_detection_claims_are_rejected():
    event = _valid_event()
    event["notes"] = "visible_neutrino = true and simulated trace is real detection"

    payload = classify_neutrino_observation(event)

    assert payload["Adm_lex"] is False
    assert "visible_neutrino_claim" in payload["refusal_packet"]["reason_codes"]
    assert "simulation_trace_as_detection" in payload["refusal_packet"]["reason_codes"]


def test_secondary_response_force_overclaims_are_rejected():
    event = _valid_event()
    event["notes"] = "hadronic trace proves strong force primary and nuclear activity proves new force"

    payload = classify_neutrino_observation(event)

    assert payload["Adm_lex"] is False
    assert "secondary_response_as_primary_force" in payload["refusal_packet"]["reason_codes"]
    assert "new_force_from_nuclear_activity" in payload["refusal_packet"]["reason_codes"]


def test_gravity_detection_channel_claim_is_rejected():
    event = _valid_event()
    event["notes"] = "gravity_detection_channel = true"

    payload = classify_neutrino_observation(event)

    assert payload["Adm_lex"] is False
    assert "gravity_detection_channel_claim" in payload["refusal_packet"]["reason_codes"]


def test_chapter4_valid_event_returns_lex_neutrino_profile():
    event = json.loads(Path("tests/fixtures/neutrino_chapter4_valid_event.json").read_text(encoding="utf-8"))

    payload = classify_neutrino_observation(event)
    packet = payload["LexPacket_neutrino"]
    chapter4 = packet["chapter4_profile"]

    assert payload["Adm_lex"] is True
    assert packet["decision"]["status"] == "accepted"
    assert chapter4["profile_version"] == "chapter4.lex_neutrino_public_safe.v1"
    assert "p_neutrino_profile" in chapter4
    assert "lex_neutrino_profile" in chapter4
    assert "lex_metrics" in chapter4
    assert chapter4["lex_metrics"]["dL_lex"] == packet["dL_lex"]
    assert 0.0 <= chapter4["lex_metrics"]["H_lex"] <= 1.0
    assert 0.0 <= chapter4["lex_metrics"]["G_lex"] <= 1.0
    assert chapter4["protection_profile"]["SynthiaGuard_neutrino"]["approved_for_fnp"] is True
    assert not _json_has_key(payload, "dF")
    assert not _json_has_key(payload, "D_f")
    assert not _json_has_key(payload, "i_fractal")


def test_chapter4_cantor_metaphor_is_partitioned_for_allowed_payload_only():
    event = _valid_event()
    event["notes"] = (
        "Cantor gaps and quasicrystal phason flips are conceptual metaphor only "
        "for the book image, not detector evidence."
    )

    payload = classify_neutrino_observation(event)
    guard = payload["LexPacket_neutrino"]["chapter4_profile"]["protection_profile"]["SynthiaGuard_neutrino"]

    assert payload["Adm_lex"] is True
    assert payload["decision"]["status"] == "accepted_with_partition"
    assert "metaphor_as_physics" in payload["refusal_packet"]["reason_codes"]
    assert guard["approved_for_fnp"] is True
    assert guard["approval_scope"] == "allowed_payload_only"
    assert guard["allowed_payload"]
    assert guard["excluded_payload"]["metaphor_payload"] == "conceptual_language_only"


def test_chapter4_simulation_as_real_detection_is_rejected():
    event = _valid_event()
    event["notes"] = "the simulation detected real neutrino evidence"

    payload = classify_neutrino_observation(event)

    assert payload["Adm_lex"] is False
    assert payload["decision"]["status"] == "rejected"
    assert "real_detection_claim" in payload["refusal_packet"]["reason_codes"]


def test_chapter4_trace_as_neutrino_total_is_rejected():
    event = _valid_event()
    event["notes"] = "trace is neutrino total"

    payload = classify_neutrino_observation(event)

    assert payload["Adm_lex"] is False
    assert payload["decision"]["status"] == "rejected"
    assert "trace_as_neutrino_total" in payload["refusal_packet"]["reason_codes"]


def test_chapter4_substrate_proof_language_reruns_synthia():
    event = _valid_event()
    event["notes"] = "the fractal substrate proves the physical conclusion"

    payload = classify_neutrino_observation(event)
    guard = payload["LexPacket_neutrino"]["chapter4_profile"]["protection_profile"]["SynthiaGuard_neutrino"]

    assert payload["Adm_lex"] is False
    assert payload["decision"]["status"] == "corrected"
    assert "metaphor_as_physics" in payload["refusal_packet"]["reason_codes"]
    assert "speculation_as_physical_conclusion" in payload["refusal_packet"]["reason_codes"]
    assert guard["approved_for_fnp"] is False


def test_chapter4_missing_source_for_physical_claim_is_suspended():
    event = _valid_event()
    event.pop("source_truth")
    event["notes"] = "physical claim proves a detector conclusion"

    payload = classify_neutrino_observation(event)

    assert payload["Adm_lex"] is False
    assert payload["decision"]["status"] == "suspended"
    assert "missing_source_for_physical_claim" in payload["refusal_packet"]["reason_codes"]


def test_chapter4_cli_accepts_fixture(capsys):
    assert main(
        [
            "neutrino",
            "guardrail-check",
            "--input",
            "tests/fixtures/neutrino_chapter4_valid_event.json",
            "--json",
        ]
    ) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["Adm_lex"] is True
    assert payload["LexPacket_neutrino"]["chapter4_profile"]["profile_version"] == "chapter4.lex_neutrino_public_safe.v1"


def test_cli_guardrail_check_accepts_chapter3_fixture(capsys):
    input_path = Path("tests/fixtures/neutrino_chapter3_valid_event.json")

    assert main(["neutrino", "guardrail-check", "--input", str(input_path), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)

    chapter3 = payload["LexPacket_neutrino"]["chapter3_profile"]
    assert payload["Adm_lex"] is True
    assert chapter3["flavor_profile"]["I_flavor"]["created_flavor"] == "nu_mu"
    assert chapter3["interaction_profile"]["I_interaction"]["channel"] == "weak_CC"


def _chapter5_event():
    return json.loads(Path("tests/fixtures/neutrino_chapter5_valid_event.json").read_text(encoding="utf-8"))


def test_chapter5_valid_event_returns_fnp_intake_profile():
    payload = classify_neutrino_observation(_chapter5_event())
    packet = payload["LexPacket_neutrino"]
    chapter5 = packet["chapter5_intake_profile"]

    assert payload["Adm_lex"] is True
    assert chapter5["profile_version"] == "chapter5.fnp_intake_public_safe.v1"
    assert chapter5["E_FNP_neutrino_request"]["allowed_payload_status"] == "present"
    assert chapter5["carrier_request_policy"]["requested_family"] == "phase_carrier"
    assert chapter5["guard_state"]["approved_for_fnp_intake"] is True
    assert chapter5["Adm_FNP_required"] is True
    assert not _json_has_key(payload, "D_f")
    assert not _json_has_key(payload, "D_f_hat")
    assert not _json_has_key(payload, "dF")
    assert not _json_has_key(payload, "i_fractal")
    assert not _json_has_key(payload, "i_fractal_candidate")


def test_chapter5_missing_allowed_payload_is_suspended():
    event = _chapter5_event()
    event.pop("source_truth")

    payload = classify_neutrino_observation(event)

    assert payload["Adm_lex"] is False
    assert payload["decision"]["status"] == "suspended"
    assert "missing_allowed_payload_for_chapter5" in payload["refusal_packet"]["reason_codes"]
    assert payload["LexPacket_neutrino"]["chapter5_intake_profile"]["guard_state"]["approved_for_fnp_intake"] is False


def test_chapter5_dl_lex_used_as_fractal_carrier_is_rejected():
    event = _chapter5_event()
    event["notes"] = "dL_lex = D_f"

    payload = classify_neutrino_observation(event)

    assert payload["Adm_lex"] is False
    assert payload["decision"]["status"] == "rejected"
    assert "dL_lex_used_as_D_f" in payload["refusal_packet"]["reason_codes"]


def test_chapter5_bounded_carrier_as_indeterminacy_is_rejected():
    event = _chapter5_event()
    event["notes"] = "D_f_hat = I and D_f_hat = i_fractal"

    payload = classify_neutrino_observation(event)

    assert payload["Adm_lex"] is False
    assert payload["decision"]["status"] == "rejected"
    assert "D_f_hat_as_I_claim" in payload["refusal_packet"]["reason_codes"]
    assert "D_f_hat_as_i_fractal_claim" in payload["refusal_packet"]["reason_codes"]


def test_chapter5_invalid_carrier_family_is_suspended():
    event = _chapter5_event()
    event["carrier_request"]["carrier_family"] = "blackhole_vortex_carrier"

    payload = classify_neutrino_observation(event)

    assert payload["Adm_lex"] is False
    assert payload["decision"]["status"] == "suspended"
    assert "invalid_carrier_family" in payload["refusal_packet"]["reason_codes"]


def test_chapter5_synthia_normalization_claim_is_rejected():
    event = _chapter5_event()
    event["notes"] = "Synthia normalizes and calculates D_f_hat"

    payload = classify_neutrino_observation(event)

    assert payload["Adm_lex"] is False
    assert payload["decision"]["status"] == "rejected"
    assert "normalization_claim_in_synthia" in payload["refusal_packet"]["reason_codes"]


def _chapter6_event():
    return json.loads(Path("tests/fixtures/neutrino_chapter6_valid_event.json").read_text(encoding="utf-8"))


def _chapter7_event():
    return json.loads(Path("tests/fixtures/neutrino_chapter7_valid_event.json").read_text(encoding="utf-8"))


def _chapter8_event():
    return json.loads(Path("tests/fixtures/neutrino_chapter8_valid_event.json").read_text(encoding="utf-8"))


def _chapter9_event():
    return json.loads(Path("tests/fixtures/neutrino_chapter9_valid_event.json").read_text(encoding="utf-8"))


def _chapter10_event():
    return json.loads(Path("tests/fixtures/neutrino_chapter10_valid_event.json").read_text(encoding="utf-8"))


def test_chapter6_valid_event_returns_complete_i_neutrino_vector():
    payload = classify_neutrino_observation(_chapter6_event())
    packet = payload["LexPacket_neutrino"]
    chapter6 = packet["chapter6_vector_profile"]
    vector = chapter6["I_neutrino_vec"]

    assert payload["Adm_lex"] is True
    assert chapter6["profile_version"] == "chapter6.i_neutrino_vector_public_safe.v1"
    assert vector["carrier_order"] == [
        "I_source",
        "I_flavor",
        "I_mass",
        "I_mix",
        "I_phase",
        "I_medium",
        "I_interaction",
        "I_secondary",
        "I_detector",
        "I_uncertainty",
    ]
    assert set(vector["carriers"]) == set(vector["carrier_order"])
    assert vector["missing_carriers"] == []
    assert vector["carriers"]["I_uncertainty"]["FNP_pending_status"] == "no_FNP_before_admission"
    assert chapter6["GuardrailCheck"]["ready_for_Synthia"] is True
    assert chapter6["GuardrailCheck"]["ready_for_FNP"] == "false_before_Synthia"
    assert not _json_has_key(payload, "D_f")
    assert not _json_has_key(payload, "D_f_hat")
    assert not _json_has_key(payload, "dF")
    assert not _json_has_key(payload, "i_fractal")
    assert not _json_has_key(payload, "i_fractal_candidate")


def test_chapter6_supplied_vector_missing_carrier_is_suspended():
    event = _chapter6_event()
    event["I_neutrino_vec"] = {
        "carriers": {
            "I_source": {"source_type": "toy_simulation"},
            "I_flavor": {"created_flavor": "nu_mu"},
        }
    }

    payload = classify_neutrino_observation(event)

    assert payload["Adm_lex"] is False
    assert payload["decision"]["status"] == "suspended"
    assert "missing_i_neutrino_vector_carrier" in payload["refusal_packet"]["reason_codes"]
    assert "i_uncertainty_missing" in payload["refusal_packet"]["reason_codes"]


def test_chapter6_vector_collapse_claims_are_rejected():
    event = _chapter6_event()
    event["notes"] = "I_neutrino_vec = dL_lex and I_neutrino_vec = dF and I_neutrino_vec = detector_signature"

    payload = classify_neutrino_observation(event)

    assert payload["Adm_lex"] is False
    assert payload["decision"]["status"] == "rejected"
    assert "i_neutrino_vec_equals_dL_lex" in payload["refusal_packet"]["reason_codes"]
    assert "i_neutrino_vec_equals_dF" in payload["refusal_packet"]["reason_codes"]
    assert "i_neutrino_vec_equals_detector_signature" in payload["refusal_packet"]["reason_codes"]


def test_chapter6_ready_for_fnp_before_synthia_is_rejected():
    event = _chapter6_event()
    event["ready_for_FNP"] = True

    payload = classify_neutrino_observation(event)

    assert payload["Adm_lex"] is False
    assert payload["decision"]["status"] == "rejected"
    assert "ready_for_fnp_before_synthia" in payload["refusal_packet"]["reason_codes"]


def test_chapter6_uncertainty_cannot_collapse_to_zero():
    event = _chapter6_event()
    event["notes"] = "I_uncertainty = 0"

    payload = classify_neutrino_observation(event)

    assert payload["Adm_lex"] is False
    assert payload["decision"]["status"] == "rejected"
    assert "uncertainty_collapsed_to_zero" in payload["refusal_packet"]["reason_codes"]


def test_chapter7_valid_event_returns_transition_profile_without_fnp_fields():
    payload = classify_neutrino_observation(_chapter7_event())
    packet = payload["LexPacket_neutrino"]
    chapter7 = packet["chapter7_transition_profile"]

    assert payload["Adm_lex"] is True
    assert packet["dL_lex"] == 0.31927681
    assert chapter7["profile_version"] == "chapter7.synthia_transition_public_safe.v1"
    assert chapter7["I_neutrino_definition"] == "I_neutrino := I_neutrino_vec"
    assert chapter7["passage_test"]["I_neutrino_vec_status"] == "assembled"
    assert chapter7["passage_test"]["L_over_E"] == 491.66666667
    assert chapter7["passage_test"]["ready_for_Synthia"] is True
    assert chapter7["passage_test"]["ready_for_FNP"] == "false_before_Synthia"
    assert chapter7["synthia_reading"]["selected_observation_lexicon"] == "phase_evolution"
    assert chapter7["synthia_reading"]["secondary_observation_lexicon"] == "weak_interaction"
    assert chapter7["synthia_reading"]["dL_lex"] == 0.31927681
    assert chapter7["synthia_reading"]["approved_for_fnp"] is True
    assert chapter7["chapter7_gate"]["ready_for_FNP"] == "true_after_Synthia"
    assert not _json_has_key(payload, "D_f")
    assert not _json_has_key(payload, "D_f_hat")
    assert not _json_has_key(payload, "dF")
    assert not _json_has_key(payload, "i_fractal")
    assert not _json_has_key(payload, "i_fractal_candidate")


def test_chapter7_physical_proof_and_candidate_claims_are_rejected():
    event = _chapter7_event()
    event["notes"] = "L_over_E_as_physical_proof and i_fractal_candidate proves final truth"

    payload = classify_neutrino_observation(event)

    assert payload["Adm_lex"] is False
    assert payload["decision"]["status"] == "rejected"
    assert "l_over_e_as_physical_proof" in payload["refusal_packet"]["reason_codes"]
    assert "i_fractal_candidate_as_proof" in payload["refusal_packet"]["reason_codes"]


def test_chapter7_ready_for_fnp_before_synthia_is_rejected_with_chapter7_code():
    event = _chapter7_event()
    event["ready_for_FNP"] = True

    payload = classify_neutrino_observation(event)

    assert payload["Adm_lex"] is False
    assert payload["decision"]["status"] == "rejected"
    assert "ready_for_fnp_before_synthia" in payload["refusal_packet"]["reason_codes"]
    assert "chapter7_ready_for_fnp_without_synthia" in payload["refusal_packet"]["reason_codes"]


def test_chapter8_valid_event_returns_first_run_profile_without_fnp_fields():
    payload = classify_neutrino_observation(_chapter8_event())
    packet = payload["LexPacket_neutrino"]
    chapter8 = packet["chapter8_run_profile"]

    assert payload["Adm_lex"] is True
    assert chapter8["profile_version"] == "chapter8.first_run_public_safe.v1"
    assert chapter8["run_input"]["I_neutrino_vec_status"] == "assembled"
    assert chapter8["run_input"]["ready_for_Synthia"] is True
    assert chapter8["run_input"]["ready_for_FNP"] == "false_before_Synthia"
    assert chapter8["synthia_gate"]["Adm_lex"] is True
    assert chapter8["synthia_gate"]["approved_for_fnp"] is True
    assert chapter8["synthia_gate"]["ready_for_FNP"] == "true_after_Synthia"
    assert chapter8["run_decision"]["run_status"] == "admissible_under_guardrails"
    assert chapter8["run_permission"]["permission_to_continue"] is True
    assert chapter8["run_permission"]["allowed_next_step"] == "FNP_QNN_readout"
    assert chapter8["run_permission"]["can_continue_to_chapter9"] is True
    assert not _json_has_key(payload, "D_f")
    assert not _json_has_key(payload, "D_f_hat")
    assert not _json_has_key(payload, "dF")
    assert not _json_has_key(payload, "i_fractal")
    assert not _json_has_key(payload, "i_fractal_candidate")


def test_chapter8_ready_for_fnp_before_synthia_is_rejected():
    event = _chapter8_event()
    event["ready_for_FNP"] = True

    payload = classify_neutrino_observation(event)

    assert payload["Adm_lex"] is False
    assert payload["decision"]["status"] == "rejected"
    assert "ready_for_fnp_before_synthia" in payload["refusal_packet"]["reason_codes"]
    assert "chapter8_fnp_before_synthia" in payload["refusal_packet"]["reason_codes"]
    assert payload["LexPacket_neutrino"]["chapter8_run_profile"]["run_decision"]["run_status"] == "rejected"


def test_chapter8_permission_and_candidate_proof_claims_are_rejected():
    event = _chapter8_event()
    event["notes"] = "permission_to_continue is proof and chapter8 candidate as proof"

    payload = classify_neutrino_observation(event)

    assert payload["Adm_lex"] is False
    assert payload["decision"]["status"] == "rejected"
    assert "chapter8_permission_as_proof" in payload["refusal_packet"]["reason_codes"]
    assert "chapter8_candidate_as_proof" in payload["refusal_packet"]["reason_codes"]


def test_chapter8_missing_simulation_status_is_suspended():
    event = _chapter8_event()
    event.pop("source_truth")

    payload = classify_neutrino_observation(event)

    assert payload["Adm_lex"] is False
    assert payload["decision"]["status"] == "suspended"
    assert "missing_source_truth" in payload["refusal_packet"]["reason_codes"]
    assert "chapter8_simulation_status_missing" in payload["refusal_packet"]["reason_codes"]
    assert payload["LexPacket_neutrino"]["chapter8_run_profile"]["run_decision"]["run_status"] == "suspended"


def test_chapter8_suspended_or_rejected_as_numeric_shortcut_is_rejected():
    event = _chapter8_event()
    event["notes"] = "suspended = 0 and rejected as noise"

    payload = classify_neutrino_observation(event)

    assert payload["Adm_lex"] is False
    assert payload["decision"]["status"] == "rejected"
    assert "chapter8_suspended_as_zero" in payload["refusal_packet"]["reason_codes"]
    assert "chapter8_rejected_as_noise" in payload["refusal_packet"]["reason_codes"]


def test_chapter9_valid_event_returns_source_choice_profile_without_fnp_fields():
    payload = classify_neutrino_observation(_chapter9_event())
    packet = payload["LexPacket_neutrino"]
    chapter9 = packet["chapter9_source_choice_profile"]

    assert payload["Adm_lex"] is True
    assert chapter9["profile_version"] == "chapter9.source_choice_public_safe.v1"
    assert chapter9["chapter9_status"] == "selected_for_container"
    assert chapter9["source_visibility"]["registry_status"] == "present"
    assert set(chapter9["source_visibility"]["required_source_ids"]) == {
        "SB60-002",
        "CH9-T2K-OSC-001",
        "SB60-052",
    }
    assert chapter9["central_experiment"]["experiment_id"] == (
        "chapter11_t2k_like_flavor_antiflavor_phase_projection"
    )
    assert chapter9["central_experiment"]["status"] == "selected_for_simulation"
    assert chapter9["central_experiment"]["reproduction_status"] == "not_T2K_reproduction"
    assert chapter9["central_experiment"]["detection_status"] == "no_real_detection_claim"
    assert chapter9["central_experiment"]["ready_for_container"] is True
    assert chapter9["central_experiment"]["ready_for_physical_claim"] is False
    assert chapter9["paths"]["Path_A"]["initial_flavor"] == "nu_mu"
    assert chapter9["paths"]["Path_B"]["initial_flavor"] == "anti_nu_mu"
    assert chapter9["synthia_gate"]["approved_for_container_validation"] is True
    assert chapter9["synthia_gate"]["ready_for_FNP"] == "true_after_Synthia_for_container_validation"
    assert not _json_has_key(payload, "D_f")
    assert not _json_has_key(payload, "D_f_hat")
    assert not _json_has_key(payload, "dF")
    assert not _json_has_key(payload, "i_fractal")
    assert not _json_has_key(payload, "i_fractal_candidate")


def test_chapter9_missing_source_registry_is_suspended():
    event = _chapter9_event()
    event.pop("chapter9_source_registry")

    payload = classify_neutrino_observation(event)

    assert payload["Adm_lex"] is False
    assert payload["decision"]["status"] == "suspended"
    assert "chapter9_missing_source_registry" in payload["refusal_packet"]["reason_codes"]
    assert payload["LexPacket_neutrino"]["chapter9_source_choice_profile"]["chapter9_status"] == (
        "blocked_or_suspended"
    )


def test_chapter9_missing_or_unbounded_experiment_choice_is_suspended_or_rejected():
    missing = _chapter9_event()
    missing.pop("chapter9_experiment_choice")

    payload = classify_neutrino_observation(missing)

    assert payload["Adm_lex"] is False
    assert payload["decision"]["status"] == "suspended"
    assert "chapter9_missing_central_experiment" in payload["refusal_packet"]["reason_codes"]

    unbounded = _chapter9_event()
    unbounded["chapter9_experiment_choice"]["experiment_id"] = "all_neutrino_physics"

    payload = classify_neutrino_observation(unbounded)

    assert payload["Adm_lex"] is False
    assert payload["decision"]["status"] == "rejected"
    assert "chapter9_unbounded_experiment_choice" in payload["refusal_packet"]["reason_codes"]


def test_chapter9_t2k_cp_detection_and_source_proof_claims_are_rejected():
    event = _chapter9_event()
    event["notes"] = (
        "T2K reproduced and CP violation measured and selected experiment is real detection "
        "and mathematical source proves physical and background missing equals zero and source stack proves"
    )

    payload = classify_neutrino_observation(event)

    assert payload["Adm_lex"] is False
    assert payload["decision"]["status"] == "rejected"
    reasons = payload["refusal_packet"]["reason_codes"]
    assert "chapter9_t2k_reproduction_claim" in reasons
    assert "chapter9_cp_measurement_claim" in reasons
    assert "chapter9_experiment_choice_as_detection" in reasons
    assert "chapter9_math_source_as_physical_proof" in reasons
    assert "chapter9_background_missing_as_zero" in reasons
    assert "chapter9_source_stack_as_proof" in reasons


def test_chapter10_valid_event_returns_chamber_container_profile_without_fnp_fields():
    payload = classify_neutrino_observation(_chapter10_event())
    packet = payload["LexPacket_neutrino"]
    chapter10 = packet["chapter10_chamber_profile"]

    assert payload["Adm_lex"] is True
    assert chapter10["profile_version"] == "chapter10.chamber_container_public_safe.v1"
    assert chapter10["chapter10_status"] == "run_prepared_for_chapter11"
    assert chapter10["source_visibility"]["registry_status"] == "present"
    assert chapter10["Chamber_10"]["not_detector"] is True
    assert chapter10["EventContainer_10"]["schema_version"] == "chamber.event_container.v1"
    assert chapter10["EventContainer_10"]["required_fields_present"] is True
    assert chapter10["SimulatedNeutrinoEvent_10"]["event_status"] == "educational_simulation"
    assert chapter10["SimulatedNeutrinoEvent_10"]["detection_status"] == "no_real_detection_claim"
    assert chapter10["SimulatedNeutrinoEvent_10"]["L_over_E_context"]["L_over_E"] == 491.66666667
    assert chapter10["RunContract_10"]["run_contract_status"] == "declared"
    assert chapter10["SynthiaGate_10"]["ready_for_FNP"] == "true_after_Synthia_for_run_contract_validation"
    assert chapter10["RunPrepared_10"]["chapter11_execution_ready"] is True
    assert chapter10["RunPrepared_10"]["physical_claim_allowed"] is False
    assert not _json_has_key(payload, "D_f")
    assert not _json_has_key(payload, "D_f_hat")
    assert not _json_has_key(payload, "dF")
    assert not _json_has_key(payload, "i_fractal")
    assert not _json_has_key(payload, "i_fractal_candidate")


def test_chapter10_missing_source_registry_is_suspended():
    event = _chapter10_event()
    event.pop("chapter10_source_registry")

    payload = classify_neutrino_observation(event)

    assert payload["Adm_lex"] is False
    assert payload["decision"]["status"] == "suspended"
    assert "chapter10_missing_source_registry" in payload["refusal_packet"]["reason_codes"]
    assert payload["LexPacket_neutrino"]["chapter10_chamber_profile"]["chapter10_status"] == "suspended"


def test_chapter10_missing_container_event_or_run_contract_is_suspended():
    for key, code in (
        ("chapter10_container", "chapter10_missing_container_contract"),
        ("chapter10_simulated_event", "chapter10_missing_simulated_event"),
        ("chapter10_run_contract", "chapter10_missing_run_contract"),
    ):
        event = _chapter10_event()
        event.pop(key)

        payload = classify_neutrino_observation(event)

        assert payload["Adm_lex"] is False
        assert payload["decision"]["status"] == "suspended"
        assert code in payload["refusal_packet"]["reason_codes"]


def test_chapter10_overclaim_language_is_rejected():
    event = _chapter10_event()
    event["notes"] = (
        "chamber = detector and container valid is proof and simulated event is detection "
        "and T2K reproduced and path_comparison = CP_measurement and background missing equals zero "
        "and prepared_tension_slot = dF"
    )

    payload = classify_neutrino_observation(event)

    assert payload["Adm_lex"] is False
    assert payload["decision"]["status"] == "rejected"
    reasons = payload["refusal_packet"]["reason_codes"]
    assert "chapter10_chamber_as_detector" in reasons
    assert "chapter10_container_as_proof" in reasons
    assert "chapter10_event_as_detection" in reasons
    assert "chapter10_t2k_reproduction_claim" in reasons
    assert "chapter10_cp_measurement_claim" in reasons
    assert "chapter10_background_missing_as_zero" in reasons
    assert "chapter10_prepared_tension_as_df" in reasons


def test_chapter10_ready_for_fnp_before_synthia_is_rejected():
    event = _chapter10_event()
    event["ready_for_FNP"] = True

    payload = classify_neutrino_observation(event)

    assert payload["Adm_lex"] is False
    assert payload["decision"]["status"] == "rejected"
    assert "ready_for_fnp_before_synthia" in payload["refusal_packet"]["reason_codes"]
    assert "chapter10_fnp_before_synthia" in payload["refusal_packet"]["reason_codes"]
