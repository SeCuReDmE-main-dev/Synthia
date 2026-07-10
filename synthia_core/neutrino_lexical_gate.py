"""Public-safe neutrino lexical admission gate for Synthia.

This module classifies the language of a neutrino-like simulation event before
any downstream FNP-QNN computation. It is educational simulation infrastructure:
it does not detect neutrinos and it does not compute D_f, dF, or i_fractal.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import json
import math
from typing import Any, Mapping


SCHEMA_VERSION = "synthia.lex_neutrino.v1"
BOUNDARY = "simulation_not_detection"
SOURCE_LAYER = "lexical"

REFUSAL_CATEGORIES = (
    "real_detection_claim",
    "strong_primary_interaction_claim",
    "literal_mass_gain_loss_claim",
    "literal_mass_change_claim",
    "decay_as_internal_flavor_mechanism",
    "fusion_as_internal_flavor_mechanism",
    "choice_or_intention_language",
    "dL_lex_equals_dF",
    "I_lexicon_equals_i_fractal",
    "missing_source_truth",
    "missing_interaction_channel",
    "detector_trace_confused_with_particle",
    "candidate_confused_with_proof",
    "unknown_flavor_as_truth",
    "flavor_mass_collapse",
    "mass_basis_equals_flavor_basis",
    "pmns_measured_claim",
    "invalid_energy_gev",
    "phase_tension_as_new_physics",
    "visible_neutrino_claim",
    "simulation_trace_as_detection",
    "trace_as_neutrino_total",
    "secondary_response_as_primary_force",
    "new_force_from_nuclear_activity",
    "gravity_detection_channel_claim",
    "metaphor_as_physics",
    "speculation_as_physical_conclusion",
    "missing_source_for_physical_claim",
    "missing_allowed_payload_for_chapter5",
    "blocked_payload_used_for_carrier",
    "dL_lex_used_as_D_f",
    "D_f_hat_as_I_claim",
    "D_f_hat_as_dF_claim",
    "D_f_hat_as_i_fractal_claim",
    "missing_scale_context",
    "missing_carrier_request",
    "invalid_carrier_family",
    "normalization_claim_in_synthia",
    "missing_i_neutrino_vector_carrier",
    "i_neutrino_vec_equals_dL_lex",
    "i_neutrino_vec_equals_dF",
    "i_neutrino_vec_equals_detector_signature",
    "i_uncertainty_missing",
    "uncertainty_collapsed_to_zero",
    "ready_for_fnp_before_synthia",
    "guardrail_check_missing",
    "vector_claim_as_physical_detection",
    "vector_claim_as_physical_proof",
    "missing_chapter7_vector_profile",
    "l_over_e_as_physical_proof",
    "chapter7_ready_for_fnp_without_synthia",
    "i_neutrino_load_as_primary_object",
    "i_fractal_candidate_as_proof",
    "chapter7_result_claim_as_detection",
    "chapter8_missing_run_vector",
    "chapter8_fnp_before_synthia",
    "chapter8_permission_as_proof",
    "chapter8_admissible_as_detection",
    "chapter8_suspended_as_zero",
    "chapter8_rejected_as_noise",
    "chapter8_unbounded_next_step",
    "chapter8_candidate_as_proof",
    "chapter8_simulation_status_missing",
    "chapter8_invalid_run_status",
    "chapter9_missing_source_registry",
    "chapter9_missing_central_experiment",
    "chapter9_fnp_before_synthia",
    "chapter9_t2k_reproduction_claim",
    "chapter9_cp_measurement_claim",
    "chapter9_experiment_choice_as_detection",
    "chapter9_math_source_as_physical_proof",
    "chapter9_background_missing_as_zero",
    "chapter9_source_stack_as_proof",
    "chapter9_unbounded_experiment_choice",
    "chapter10_missing_source_registry",
    "chapter10_missing_container_contract",
    "chapter10_missing_simulated_event",
    "chapter10_missing_run_contract",
    "chapter10_fnp_before_synthia",
    "chapter10_chamber_as_detector",
    "chapter10_container_as_proof",
    "chapter10_event_as_detection",
    "chapter10_t2k_reproduction_claim",
    "chapter10_cp_measurement_claim",
    "chapter10_background_missing_as_zero",
    "chapter10_prepared_tension_as_df",
    "chapter10_unbounded_manipulation",
    "chapter11_missing_passage_contract",
    "chapter11_missing_injection_packet",
    "chapter11_path_pair_missing",
    "chapter11_path_container_mismatch",
    "chapter11_path_admission_route_mismatch",
    "chapter11_t2k_reproduction_claim",
    "chapter11_cp_measurement_claim",
    "chapter11_path_comparison_as_cp_measurement",
    "chapter11_background_missing_as_zero",
    "chapter11_fnp_before_synthia",
    "chapter11_dl_lex_as_df",
    "chapter11_fnp_output_in_synthia",
    "chapter11_candidate_as_proof",
    "chapter12_missing_validation_contract",
    "chapter12_missing_reference_run",
    "chapter12_incomplete_carrier_policy",
    "chapter12_incomplete_matter_model",
    "chapter12_incomplete_detector_response",
    "chapter12_hidden_randomness",
    "chapter12_invalid_repeat_protocol",
    "chapter12_invalid_proof_upgrade",
    "chapter12_msw_as_measurement",
    "chapter12_trace_as_neutrino",
    "chapter12_secondary_as_primary_interaction",
    "chapter12_repetition_as_experimental_evidence",
    "chapter12_fnp_before_synthia",
    "chapter12_fnp_output_in_synthia",
)

CRITICAL_REJECTION_CODES = {
    "real_detection_claim",
    "strong_primary_interaction_claim",
    "dL_lex_equals_dF",
    "I_lexicon_equals_i_fractal",
    "detector_trace_confused_with_particle",
    "candidate_confused_with_proof",
    "unknown_flavor_as_truth",
    "flavor_mass_collapse",
    "mass_basis_equals_flavor_basis",
    "visible_neutrino_claim",
    "simulation_trace_as_detection",
    "trace_as_neutrino_total",
    "secondary_response_as_primary_force",
    "new_force_from_nuclear_activity",
    "gravity_detection_channel_claim",
    "blocked_payload_used_for_carrier",
    "dL_lex_used_as_D_f",
    "D_f_hat_as_I_claim",
    "D_f_hat_as_dF_claim",
    "D_f_hat_as_i_fractal_claim",
    "normalization_claim_in_synthia",
    "i_neutrino_vec_equals_dL_lex",
    "i_neutrino_vec_equals_dF",
    "i_neutrino_vec_equals_detector_signature",
    "uncertainty_collapsed_to_zero",
    "ready_for_fnp_before_synthia",
    "vector_claim_as_physical_detection",
    "vector_claim_as_physical_proof",
    "l_over_e_as_physical_proof",
    "chapter7_ready_for_fnp_without_synthia",
    "i_neutrino_load_as_primary_object",
    "i_fractal_candidate_as_proof",
    "chapter7_result_claim_as_detection",
    "chapter8_fnp_before_synthia",
    "chapter8_permission_as_proof",
    "chapter8_admissible_as_detection",
    "chapter8_suspended_as_zero",
    "chapter8_rejected_as_noise",
    "chapter8_unbounded_next_step",
    "chapter8_candidate_as_proof",
    "chapter9_fnp_before_synthia",
    "chapter9_t2k_reproduction_claim",
    "chapter9_cp_measurement_claim",
    "chapter9_experiment_choice_as_detection",
    "chapter9_math_source_as_physical_proof",
    "chapter9_background_missing_as_zero",
    "chapter9_source_stack_as_proof",
    "chapter9_unbounded_experiment_choice",
    "chapter10_fnp_before_synthia",
    "chapter10_chamber_as_detector",
    "chapter10_container_as_proof",
    "chapter10_event_as_detection",
    "chapter10_t2k_reproduction_claim",
    "chapter10_cp_measurement_claim",
    "chapter10_background_missing_as_zero",
    "chapter10_prepared_tension_as_df",
    "chapter10_unbounded_manipulation",
    "chapter11_t2k_reproduction_claim",
    "chapter11_cp_measurement_claim",
    "chapter11_path_comparison_as_cp_measurement",
    "chapter11_background_missing_as_zero",
    "chapter11_fnp_before_synthia",
    "chapter11_dl_lex_as_df",
    "chapter11_fnp_output_in_synthia",
    "chapter11_candidate_as_proof",
    "chapter12_invalid_proof_upgrade",
    "chapter12_msw_as_measurement",
    "chapter12_trace_as_neutrino",
    "chapter12_secondary_as_primary_interaction",
    "chapter12_repetition_as_experimental_evidence",
    "chapter12_fnp_before_synthia",
    "chapter12_fnp_output_in_synthia",
}
CORRECTION_CODES = {
    "literal_mass_gain_loss_claim",
    "literal_mass_change_claim",
    "decay_as_internal_flavor_mechanism",
    "fusion_as_internal_flavor_mechanism",
    "choice_or_intention_language",
    "pmns_measured_claim",
    "phase_tension_as_new_physics",
    "speculation_as_physical_conclusion",
}
PARTITION_CODES = {"metaphor_as_physics"}
SUSPENSION_CODES = {
    "missing_source_truth",
    "missing_interaction_channel",
    "invalid_energy_gev",
    "missing_source_for_physical_claim",
    "missing_allowed_payload_for_chapter5",
    "missing_scale_context",
    "missing_carrier_request",
    "invalid_carrier_family",
    "missing_i_neutrino_vector_carrier",
    "i_uncertainty_missing",
    "guardrail_check_missing",
    "missing_chapter7_vector_profile",
    "chapter8_missing_run_vector",
    "chapter8_simulation_status_missing",
    "chapter8_invalid_run_status",
    "chapter9_missing_source_registry",
    "chapter9_missing_central_experiment",
    "chapter10_missing_source_registry",
    "chapter10_missing_container_contract",
    "chapter10_missing_simulated_event",
    "chapter10_missing_run_contract",
    "chapter11_missing_passage_contract",
    "chapter11_missing_injection_packet",
    "chapter11_path_pair_missing",
    "chapter11_path_container_mismatch",
    "chapter11_path_admission_route_mismatch",
    "chapter12_missing_validation_contract",
    "chapter12_missing_reference_run",
    "chapter12_incomplete_carrier_policy",
    "chapter12_incomplete_matter_model",
    "chapter12_incomplete_detector_response",
    "chapter12_hidden_randomness",
    "chapter12_invalid_repeat_protocol",
}
VALID_INTERACTION_CHANNELS = {"weak_CC", "weak_NC"}
VALID_FLAVORS = {"nu_e", "nu_mu", "nu_tau", "unknown"}
FLAVOR_KEYS = ("e", "mu", "tau")
MASS_KEYS = ("nu_1", "nu_2", "nu_3")
CHAPTER4_LEXICONS = (
    "source_lex",
    "flavor_lex",
    "mass_lex",
    "mix_lex",
    "phase_lex",
    "medium_lex",
    "interaction_lex",
    "secondary_lex",
    "detector_lex",
    "uncertainty_lex",
    "metaphor_lex",
    "overclaim_lex",
)
CHAPTER5_CARRIER_FAMILIES = (
    "phase_carrier",
    "detector_projection_carrier",
    "secondary_trace_carrier",
    "plithogenic_contradiction_carrier",
    "multi_attribute_tension_carrier",
    "scale_transition_carrier",
    "null_carrier",
)
CHAPTER6_REQUIRED_CARRIERS = (
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
)
CHAPTER6_FORBIDDEN_PROFILE_KEYS = {"D_f", "D_f_hat", "dF", "i_fractal", "i_fractal_candidate"}
CHAPTER9_REQUIRED_SOURCE_IDS = ("SB60-002", "CH9-T2K-OSC-001", "SB60-052")
CHAPTER9_EXPERIMENT_ID = "chapter11_t2k_like_flavor_antiflavor_phase_projection"
CHAPTER10_REQUIRED_SOURCE_IDS = ("CH10-GEANT4-001", "CH10-SCHEMA-001")
CHAPTER10_CONTAINER_SCHEMA_VERSION = "chamber.event_container.v1"
CHAPTER10_EVENT_SCHEMA_VERSION = "chamber.simulated_neutrino_event.v1"
CHAPTER10_RUN_CONTRACT_VERSION = "chamber.run_contract.v1"
CHAPTER11_PASSAGE_CONTRACT_VERSION = "chamber.chapter11_passage_contract.v1"
CHAPTER11_INJECTION_PACKET_VERSION = "chamber.chapter11_injection_packet.v1"
CHAPTER12_VALIDATION_CONTRACT_VERSION = "chamber.chapter12_validation_contract.v1"
CHAPTER11_FORBIDDEN_OUTPUT_KEYS = {
    "D_f",
    "D_f_hat",
    "dF",
    "i_fractal",
    "i_fractal_candidate",
    "D_f_11",
    "D_f_hat_11",
    "dF_11",
    "i_fractal_candidate_11",
}
CHAPTER12_FORBIDDEN_OUTPUT_KEYS = CHAPTER11_FORBIDDEN_OUTPUT_KEYS | {
    "effective_matter_potential",
    "reconstructed_detector_output",
}


class DecisionStatus(str, Enum):
    ACCEPTED = "accepted"
    ACCEPTED_WITH_PARTITION = "accepted_with_partition"
    CORRECTED = "corrected"
    SUSPENDED = "suspended"
    REJECTED = "rejected"


@dataclass(frozen=True)
class RefusalPacket:
    blocked: bool
    reason_codes: tuple[str, ...]
    next_action: str
    source_layer: str = SOURCE_LAYER
    human_message: str = ""

    def as_dict(self) -> dict[str, object]:
        return {
            "blocked": self.blocked,
            "reason_codes": list(self.reason_codes),
            "next_action": self.next_action,
            "source_layer": self.source_layer,
            "human_message": self.human_message,
        }


@dataclass(frozen=True)
class NeutrinoObservationInput:
    event_id: str
    claim_class: str
    interaction_channel: str
    source_truth: Mapping[str, object]
    detector_signature: str
    created_flavor: str
    flavor_status: str
    flavor_basis: Mapping[str, float]
    mass_basis: Mapping[str, float]
    distance_km: float | None
    energy_gev: float | None
    secondary_products: tuple[str, ...]
    text: str
    raw_payload: Mapping[str, Any]

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "NeutrinoObservationInput":
        if not isinstance(payload, Mapping):
            raise ValueError("neutrino lexical gate input must be a JSON object")
        source_truth = payload.get("source_truth")
        if source_truth is None and isinstance(payload.get("sources"), Mapping):
            source_truth = payload.get("sources")
        return cls(
            event_id=str(payload.get("event_id", "neutrino-simulation-event")).strip()
            or "neutrino-simulation-event",
            claim_class=str(payload.get("claim_class", "simulation")).strip() or "simulation",
            interaction_channel=_normalize_interaction_channel(payload.get("interaction_channel")),
            source_truth=source_truth if isinstance(source_truth, Mapping) else {},
            detector_signature=str(payload.get("detector_signature", "")).strip(),
            created_flavor=_normalize_flavor(payload.get("created_flavor")),
            flavor_status=str(payload.get("flavor_status", "")).strip().lower(),
            flavor_basis=_normalize_flavor_basis(payload),
            mass_basis=_normalize_mass_basis(payload),
            distance_km=_optional_float(payload.get("distance_km")),
            energy_gev=_optional_float(payload.get("energy_gev")),
            secondary_products=tuple(_secondary_products(payload)),
            text=_payload_text(payload),
            raw_payload=payload,
        )


@dataclass(frozen=True)
class LexPacketNeutrino:
    event_id: str
    Adm_lex: bool
    dL_lex: float
    decision_status: DecisionStatus
    refusal_packet: RefusalPacket
    chapter3_profile: Mapping[str, object]
    chapter4_profile: Mapping[str, object]
    chapter5_intake_profile: Mapping[str, object]
    chapter6_vector_profile: Mapping[str, object]
    chapter7_transition_profile: Mapping[str, object]
    chapter8_run_profile: Mapping[str, object]
    chapter9_source_choice_profile: Mapping[str, object]
    chapter10_chamber_profile: Mapping[str, object]
    chapter11_passage_profile: Mapping[str, object]
    chapter12_validation_profile: Mapping[str, object]

    def as_dict(self) -> dict[str, object]:
        decision = {
            "status": self.decision_status.value,
            "next_action": self.refusal_packet.next_action,
            "reason_codes": list(self.refusal_packet.reason_codes),
        }
        return {
            "schema_version": SCHEMA_VERSION,
            "event_id": self.event_id,
            "Adm_lex": self.Adm_lex,
            "dL_lex": self.dL_lex,
            "decision": decision,
            "refusal_packet": self.refusal_packet.as_dict(),
            "source_layer": SOURCE_LAYER,
            "boundary": BOUNDARY,
            "chapter3_profile": dict(self.chapter3_profile),
            "chapter4_profile": dict(self.chapter4_profile),
            "chapter5_intake_profile": dict(self.chapter5_intake_profile),
            "chapter6_vector_profile": dict(self.chapter6_vector_profile),
            "chapter7_transition_profile": dict(self.chapter7_transition_profile),
            "chapter8_run_profile": dict(self.chapter8_run_profile),
            "chapter9_source_choice_profile": dict(self.chapter9_source_choice_profile),
            "chapter10_chamber_profile": dict(self.chapter10_chamber_profile),
            "chapter11_passage_profile": dict(self.chapter11_passage_profile),
            "chapter12_validation_profile": dict(self.chapter12_validation_profile),
            "guardrail_categories": list(REFUSAL_CATEGORIES),
            "metric_definition": "dL_lex is lexical admission load only; downstream FNP friction is separate.",
        }


def classify_neutrino_observation(payload: Mapping[str, Any]) -> dict[str, object]:
    """Return the public-safe Synthia lexical admission contract."""

    observation = NeutrinoObservationInput.from_mapping(payload)
    reason_codes = tuple(_reason_codes(observation))
    status = _decision_status(reason_codes)
    adm_lex = status in {DecisionStatus.ACCEPTED, DecisionStatus.ACCEPTED_WITH_PARTITION}
    d_l_lex = _d_l_lex(observation, reason_codes)
    chapter3_profile = _chapter3_profile(observation, reason_codes)
    chapter4_profile = _chapter4_profile(observation, reason_codes, status, d_l_lex, chapter3_profile)
    chapter5_intake_profile = _chapter5_intake_profile(observation, reason_codes, status, chapter3_profile, chapter4_profile)
    chapter6_vector_profile = _chapter6_vector_profile(
        observation,
        reason_codes,
        status,
        d_l_lex,
        chapter3_profile,
        chapter4_profile,
        chapter5_intake_profile,
    )
    chapter7_transition_profile = _chapter7_transition_profile(
        observation,
        reason_codes,
        status,
        d_l_lex,
        chapter4_profile,
        chapter6_vector_profile,
    )
    chapter8_run_profile = _chapter8_run_profile(
        observation,
        reason_codes,
        status,
        d_l_lex,
        chapter6_vector_profile,
        chapter7_transition_profile,
    )
    chapter9_source_choice_profile = _chapter9_source_choice_profile(
        observation,
        reason_codes,
        status,
        chapter8_run_profile,
    )
    chapter10_chamber_profile = _chapter10_chamber_profile(
        observation,
        reason_codes,
        status,
        chapter9_source_choice_profile,
    )
    chapter11_passage_profile = _chapter11_passage_profile(
        observation,
        reason_codes,
        status,
        d_l_lex,
        chapter10_chamber_profile,
    )
    chapter12_validation_profile = _chapter12_validation_profile(
        observation,
        reason_codes,
        status,
        chapter11_passage_profile,
    )
    refusal_packet = RefusalPacket(
        blocked=not adm_lex,
        reason_codes=reason_codes,
        next_action=_next_action(status),
        human_message=_human_message(status),
    )
    packet = LexPacketNeutrino(
        event_id=observation.event_id,
        Adm_lex=adm_lex,
        dL_lex=d_l_lex,
        decision_status=status,
        refusal_packet=refusal_packet,
        chapter3_profile=chapter3_profile,
        chapter4_profile=chapter4_profile,
        chapter5_intake_profile=chapter5_intake_profile,
        chapter6_vector_profile=chapter6_vector_profile,
        chapter7_transition_profile=chapter7_transition_profile,
        chapter8_run_profile=chapter8_run_profile,
        chapter9_source_choice_profile=chapter9_source_choice_profile,
        chapter10_chamber_profile=chapter10_chamber_profile,
        chapter11_passage_profile=chapter11_passage_profile,
        chapter12_validation_profile=chapter12_validation_profile,
    ).as_dict()
    return {
        "success": True,
        "type": "synthia_neutrino_lexical_gate",
        "schema_version": SCHEMA_VERSION,
        "LexPacket_neutrino": packet,
        "Adm_lex": packet["Adm_lex"],
        "dL_lex": packet["dL_lex"],
        "decision": packet["decision"],
        "refusal_packet": packet["refusal_packet"],
        "source_layer": SOURCE_LAYER,
        "boundary": BOUNDARY,
        "public_safe": True,
        "claim_boundary": (
            "educational simulation; simulation is not detection; Synthia classifies before "
            "FNP-QNN computes; dL_lex != downstream fractal friction; I_lexicon remains lexical."
        ),
    }


def _reason_codes(observation: NeutrinoObservationInput) -> list[str]:
    text = observation.text
    reasons: list[str] = []

    if observation.claim_class != "simulation" or _contains_any(
        text,
        ("real neutrino detected", "real detection", "detected real neutrino", "detector data claim"),
    ):
        reasons.append("real_detection_claim")

    if not observation.interaction_channel:
        reasons.append("missing_interaction_channel")
    elif observation.interaction_channel not in VALID_INTERACTION_CHANNELS or _contains_any(
        text,
        ("strong primary", "strong force primary", "strong-force primary", "primary strong interaction"),
    ):
        reasons.append("strong_primary_interaction_claim")

    if _contains_any(text, ("mass gain", "mass loss", "gain mass", "lose mass", "gains mass", "loses mass")):
        reasons.append("literal_mass_gain_loss_claim")
    if _contains_any(text, ("change mass", "changes mass", "changing mass", "mass changes", "masse change")):
        reasons.append("literal_mass_change_claim")
    if "decay" in text:
        reasons.append("decay_as_internal_flavor_mechanism")
    if "fusion" in text:
        reasons.append("fusion_as_internal_flavor_mechanism")
    if _contains_any(
        text,
        (
            "neutrino chooses",
            "neutrino choose",
            "neutrino decides",
            "neutrino decide",
            "neutrino intention",
            "voluntary choice",
            "voluntary intention",
            "particle chooses",
            "particle decides",
        ),
    ):
        reasons.append("choice_or_intention_language")

    if _numeric_equal(observation.raw_payload.get("dL_lex"), observation.raw_payload.get("dF")) or _contains_any(
        text,
        ("dl_lex = df", "dl_lex equals df", "dl_lex==df", "dL_lex = dF".lower()),
    ):
        reasons.append("dL_lex_equals_dF")

    if _numeric_equal(observation.raw_payload.get("I_lexicon"), observation.raw_payload.get("i_fractal")) or _contains_any(
        text,
        ("i_lexicon = i_fractal", "i_lexicon equals i_fractal", "i_lexicon==i_fractal"),
    ):
        reasons.append("I_lexicon_equals_i_fractal")

    if not observation.source_truth:
        reasons.append("missing_source_truth")
        if _contains_any(
            text,
            (
                "physical claim",
                "claim physique",
                "proves",
                "proof",
                "prouve",
                "demontre",
                "validated physics",
                "conclusion physique",
            ),
        ):
            reasons.append("missing_source_for_physical_claim")

    if _invalid_declared_flavor(observation):
        reasons.append("unknown_flavor_as_truth")

    if _contains_any(
        text,
        (
            "flavor is mass",
            "flavour is mass",
            "saveur est la masse",
            "flavor_weak_state = mass_propagation_state",
            "flavor_weak_state equals mass_propagation_state",
        ),
    ):
        reasons.append("flavor_mass_collapse")

    if _basis_vectors_equal(observation.flavor_basis, observation.mass_basis) or _contains_any(
        text,
        ("flavor_basis = mass_basis", "flavor_basis equals mass_basis", "flavor_basis==mass_basis"),
    ):
        reasons.append("mass_basis_equals_flavor_basis")

    if _contains_any(
        text,
        ("measured pmns", "true pmns", "real pmns", "pmns measured", "matrice pmns mesuree"),
    ):
        reasons.append("pmns_measured_claim")

    if observation.energy_gev is not None and observation.energy_gev <= 0.0:
        reasons.append("invalid_energy_gev")

    if _contains_any(
        text,
        (
            "phase tension proves",
            "phase_tension proves",
            "phase tension is proof",
            "phase_tension = proof",
            "tension de phase prouve",
        ),
    ):
        reasons.append("phase_tension_as_new_physics")

    if _contains_any(
        text,
        ("detector trace is the neutrino", "trace equals neutrino", "secondary particle is the neutrino"),
    ):
        reasons.append("detector_trace_confused_with_particle")

    if _contains_any(
        text,
        ("visible_neutrino = true", "neutrino seen directly", "neutrino_seen_directly", "visible neutrino"),
    ):
        reasons.append("visible_neutrino_claim")

    if _contains_any(
        text,
        (
            "simulation trace is detection",
            "simulated trace is real detection",
            "simulation de trace = detection",
        ),
    ):
        reasons.append("simulation_trace_as_detection")

    if _contains_any(
        text,
        ("trace is neutrino total", "trace_as_neutrino_total", "i_detector = i_neutrino"),
    ):
        reasons.append("trace_as_neutrino_total")

    if _contains_any(
        text,
        (
            "secondary response is primary force",
            "secondary_response = primary_force",
            "hadronic trace proves strong force primary",
            "gerbe hadronique prouve force forte",
        ),
    ):
        reasons.append("secondary_response_as_primary_force")

    if _contains_any(
        text,
        (
            "nuclear activity proves new force",
            "new force from nuclear activity",
            "activite nucleaire nouvelle force",
        ),
    ):
        reasons.append("new_force_from_nuclear_activity")

    if _contains_any(
        text,
        (
            "gravity detection channel",
            "gravity_detection_channel = true",
            "gravite canal de detection",
        ),
    ):
        reasons.append("gravity_detection_channel_claim")

    if _contains_any(
        text,
        ("candidate is proof", "candidate proves", "proof of mapped neutrino", "i_fractal_candidate proves"),
    ):
        reasons.append("candidate_confused_with_proof")

    if _contains_any(
        text,
        (
            "cantor",
            "koch",
            "quasicrystal",
            "quasicristal",
            "substrat fractal",
            "fractal substrate",
            "phason",
            "phason flip",
        ),
    ):
        reasons.append("metaphor_as_physics")

    if _contains_any(
        text,
        (
            "substrat fractal prouve",
            "fractal substrate proves",
            "proves the fractal substrate",
            "quasicrystal substrate is proven",
            "quasicristal prouve",
            "physical proof of substrate",
            "new physics proof",
            "validated physical conclusion",
        ),
    ):
        reasons.append("speculation_as_physical_conclusion")

    if _chapter5_requested(observation):
        carrier_request = observation.raw_payload.get("carrier_request")
        scale_context = observation.raw_payload.get("scale_context")
        family = _carrier_family(carrier_request)
        if not isinstance(carrier_request, Mapping):
            reasons.append("missing_carrier_request")
        elif family not in CHAPTER5_CARRIER_FAMILIES:
            reasons.append("invalid_carrier_family")
        if not isinstance(scale_context, Mapping):
            reasons.append("missing_scale_context")
        if _contains_any(text, ("excluded_payload used for carrier", "use excluded_payload for carrier", "blocked payload used")):
            reasons.append("blocked_payload_used_for_carrier")

    if _contains_any(
        text,
        (
            "dl_lex = d_f",
            "dl_lex equals d_f",
            "dl_lex used as d_f",
            "dl_lex is d_f",
            "dl_lex = df carrier",
        ),
    ):
        reasons.append("dL_lex_used_as_D_f")

    if _contains_any(text, ("d_f_hat = i", "d_f_hat equals i", "d_f_hat is i", "df_hat = i")):
        reasons.append("D_f_hat_as_I_claim")
    if _contains_any(text, ("d_f_hat = df", "d_f_hat equals df", "d_f_hat is df", "df_hat = df")):
        reasons.append("D_f_hat_as_dF_claim")
    if _contains_any(
        text,
        (
            "d_f_hat = i_fractal",
            "d_f_hat equals i_fractal",
            "d_f_hat is i_fractal",
            "df_hat = i_fractal",
        ),
    ):
        reasons.append("D_f_hat_as_i_fractal_claim")

    if _contains_any(
        text,
        (
            "synthia normalizes",
            "synthia calculates d_f_hat",
            "synthia computes d_f_hat",
            "normalization in synthia",
            "synthia normalization",
        ),
    ):
        reasons.append("normalization_claim_in_synthia")

    supplied_vector = _supplied_chapter6_vector(observation.raw_payload)
    if supplied_vector is not None:
        missing_carriers = _missing_chapter6_carriers(supplied_vector)
        if missing_carriers:
            reasons.append("missing_i_neutrino_vector_carrier")
        if "I_uncertainty" in missing_carriers:
            reasons.append("i_uncertainty_missing")
    supplied_chapter6 = observation.raw_payload.get("chapter6_vector_profile")
    if isinstance(supplied_chapter6, Mapping) and not isinstance(supplied_chapter6.get("GuardrailCheck"), Mapping):
        reasons.append("guardrail_check_missing")

    ready_for_fnp = observation.raw_payload.get("ready_for_FNP")
    if ready_for_fnp is True or _contains_any(text, ("ready_for_fnp = true", "ready_for_fnp=true")):
        reasons.append("ready_for_fnp_before_synthia")
    if _contains_any(
        text,
        (
            "i_neutrino_vec = dl_lex",
            "i_neutrino_vec equals dl_lex",
            "i_neutrino_vec==dl_lex",
        ),
    ):
        reasons.append("i_neutrino_vec_equals_dL_lex")
    if _contains_any(
        text,
        (
            "i_neutrino_vec = df",
            "i_neutrino_vec equals df",
            "i_neutrino_vec==df",
        ),
    ):
        reasons.append("i_neutrino_vec_equals_dF")
    if _contains_any(
        text,
        (
            "i_neutrino_vec = detector_signature",
            "i_neutrino_vec equals detector_signature",
            "i_neutrino_vec = detector signature",
        ),
    ):
        reasons.append("i_neutrino_vec_equals_detector_signature")
    if _contains_any(text, ("i_uncertainty = 0", "i_uncertainty collapsed to zero", "uncertainty collapsed to zero")):
        reasons.append("uncertainty_collapsed_to_zero")
    if _contains_any(text, ("i_neutrino_vec proves detection", "vector proves detection", "vecteur prouve detection")):
        reasons.append("vector_claim_as_physical_detection")
    if _contains_any(
        text,
        ("i_neutrino_vec proves physical proof", "vector proves physics", "vecteur prouve physique"),
    ):
        reasons.append("vector_claim_as_physical_proof")

    if _chapter7_requested(observation):
        if not _nested_mapping(_chapter6_vector_profile_preview(observation), "I_neutrino_vec"):
            reasons.append("missing_chapter7_vector_profile")
        if ready_for_fnp is True or _contains_any(
            text,
            (
                "ready_for_fnp = true before synthia",
                "ready_for_fnp=true before synthia",
                "chapter7 ready for fnp without synthia",
            ),
        ):
            reasons.append("chapter7_ready_for_fnp_without_synthia")
    if _contains_any(
        text,
        (
            "l_over_e_as_physical_proof",
            "l/e proves fractality",
            "l_over_e proves physical proof",
            "l_over_e = proof",
        ),
    ):
        reasons.append("l_over_e_as_physical_proof")
    if _contains_any(
        text,
        (
            "i_neutrino_load = i_neutrino",
            "i_neutrino_load as primary object",
            "i_neutrino_load is the primary object",
        ),
    ):
        reasons.append("i_neutrino_load_as_primary_object")
    if _contains_any(
        text,
        (
            "i_fractal_candidate proves",
            "i_fractal_candidate is proof",
            "candidate_as_proof",
            "candidate is physical proof",
        ),
    ):
        reasons.append("i_fractal_candidate_as_proof")
    if _contains_any(
        text,
        (
            "chapter7 result is detection",
            "chapter7_result_claim_as_detection",
            "chapter 7 detected neutrino",
        ),
    ):
        reasons.append("chapter7_result_claim_as_detection")

    if _chapter8_requested(observation):
        preview = _chapter6_vector_profile_preview(observation)
        if not _nested_mapping(preview, "I_neutrino_vec"):
            reasons.append("chapter8_missing_run_vector")
        if ready_for_fnp is True or _contains_any(
            text,
            (
                "chapter8 fnp before synthia",
                "chapter 8 fnp before synthia",
                "first run skips synthia",
                "run bypasses synthia",
                "ready_for_fnp before synthia",
            ),
        ):
            reasons.append("chapter8_fnp_before_synthia")
        if _contains_any(
            text,
            (
                "permission_to_continue is proof",
                "permission to continue is proof",
                "permission_to_continue = proof",
                "first run proves",
            ),
        ):
            reasons.append("chapter8_permission_as_proof")
        if _contains_any(
            text,
            (
                "admissible means detection",
                "admissible_as_detection",
                "admissible_under_guardrails proves detection",
                "run_status is real detection",
            ),
        ):
            reasons.append("chapter8_admissible_as_detection")
        if _contains_any(text, ("suspended = 0", "suspended as zero", "suspendu = 0", "suspendu as zero")):
            reasons.append("chapter8_suspended_as_zero")
        if _contains_any(text, ("rejected as noise", "rejected = noise", "rejete = bruit", "rejet as noise")):
            reasons.append("chapter8_rejected_as_noise")
        if _contains_any(
            text,
            (
                "unbounded_next_step",
                "unbounded next step",
                "permission without guardrails",
                "continue without guardrails",
            ),
        ):
            reasons.append("chapter8_unbounded_next_step")
        if _contains_any(
            text,
            (
                "chapter8 candidate as proof",
                "chapter 8 candidate as proof",
                "candidate_as_proof",
                "candidate is proof",
            ),
        ):
            reasons.append("chapter8_candidate_as_proof")
        if not observation.source_truth and _contains_any(
            text,
            ("chapter8", "chapter 8", "first run", "run_status"),
        ):
            reasons.append("chapter8_simulation_status_missing")
        supplied_status = _normalize_token(observation.raw_payload.get("run_status", ""))
        if supplied_status and supplied_status not in {
            "admissible_under_guardrails",
            "suspended",
            "rejected",
        }:
            reasons.append("chapter8_invalid_run_status")

    if _chapter9_requested(observation):
        source_ids = set(_chapter9_source_ids(observation.raw_payload))
        if not set(CHAPTER9_REQUIRED_SOURCE_IDS) <= source_ids:
            reasons.append("chapter9_missing_source_registry")
        experiment = _chapter9_experiment_choice(observation.raw_payload)
        if not experiment:
            reasons.append("chapter9_missing_central_experiment")
        elif str(experiment.get("experiment_id", "")).strip() != CHAPTER9_EXPERIMENT_ID:
            reasons.append("chapter9_unbounded_experiment_choice")
        if ready_for_fnp is True or _contains_any(
            text,
            (
                "chapter9 fnp before synthia",
                "chapter 9 fnp before synthia",
                "central experiment skips synthia",
                "chapter9 direct fnp",
            ),
        ):
            reasons.append("chapter9_fnp_before_synthia")
        if _contains_any(
            text,
            (
                "t2k reproduced",
                "t2k reproduction claim",
                "t2k_like = t2k",
                "t2k-like proves t2k",
            ),
        ):
            reasons.append("chapter9_t2k_reproduction_claim")
        if _contains_any(
            text,
            (
                "cp measurement claim",
                "cp violation measured",
                "measures cp violation",
                "chapter9 cp measurement",
            ),
        ):
            reasons.append("chapter9_cp_measurement_claim")
        if _contains_any(
            text,
            (
                "experiment choice is detection",
                "chosen experiment detects",
                "selected experiment is real detection",
                "central experiment proves detection",
            ),
        ):
            reasons.append("chapter9_experiment_choice_as_detection")
        if _contains_any(
            text,
            (
                "mathematical source proves physical",
                "math source as physical proof",
                "source_mathematical -> physical_property_claim",
                "plithogenic reading is physical structure",
            ),
        ):
            reasons.append("chapter9_math_source_as_physical_proof")
        if _contains_any(
            text,
            (
                "background missing equals zero",
                "background_model_missing = background_zero",
                "missing background is zero",
            ),
        ):
            reasons.append("chapter9_background_missing_as_zero")
        if _contains_any(
            text,
            (
                "source stack proves",
                "source_physical + source_mathematical = proof",
                "sources prove the experiment",
            ),
        ):
            reasons.append("chapter9_source_stack_as_proof")

    if _chapter10_requested(observation):
        source_ids = set(_chapter10_source_ids(observation.raw_payload))
        if not set(CHAPTER10_REQUIRED_SOURCE_IDS) <= source_ids:
            reasons.append("chapter10_missing_source_registry")
        if not _chapter10_container(observation.raw_payload):
            reasons.append("chapter10_missing_container_contract")
        if not _chapter10_event(observation.raw_payload):
            reasons.append("chapter10_missing_simulated_event")
        if not _chapter10_run_contract(observation.raw_payload):
            reasons.append("chapter10_missing_run_contract")
        if ready_for_fnp is True or _contains_any(
            text,
            (
                "chapter10 fnp before synthia",
                "chapter 10 fnp before synthia",
                "run contract skips synthia",
                "chapter10 direct fnp",
                "event_to_fnp_direct",
            ),
        ):
            reasons.append("chapter10_fnp_before_synthia")
        if _contains_any(
            text,
            (
                "chamber is detector",
                "chamber = detector",
                "chambre = detecteur",
                "chamber detects neutrinos",
            ),
        ):
            reasons.append("chapter10_chamber_as_detector")
        if _contains_any(
            text,
            (
                "container valid is proof",
                "container_valid = physical_proof",
                "schema valid is physical truth",
                "container proves",
            ),
        ):
            reasons.append("chapter10_container_as_proof")
        if _contains_any(
            text,
            (
                "simulated event is detection",
                "simulatedneutrinoevent_10 = real_neutrino_event",
                "event is real detection",
                "detected neutrino event",
            ),
        ):
            reasons.append("chapter10_event_as_detection")
        if _contains_any(
            text,
            (
                "t2k reproduced",
                "t2k reproduction claim",
                "t2k_like = t2k",
                "not_t2k_reproduction = false",
            ),
        ):
            reasons.append("chapter10_t2k_reproduction_claim")
        if _contains_any(
            text,
            (
                "cp measurement claim",
                "cp violation measured",
                "path_comparison = cp_measurement",
                "measures cp violation",
            ),
        ):
            reasons.append("chapter10_cp_measurement_claim")
        if _contains_any(
            text,
            (
                "background missing equals zero",
                "background_missing = background_zero",
                "background_model_missing = background_zero",
                "missing background is zero",
            ),
        ):
            reasons.append("chapter10_background_missing_as_zero")
        if _contains_any(
            text,
            (
                "prepared_tension_slot = df",
                "prepared tension is df",
                "prepared tension slot is dF".lower(),
                "chapter10 computes df",
            ),
        ):
            reasons.append("chapter10_prepared_tension_as_df")
        if _contains_any(
            text,
            (
                "unbounded manipulation",
                "manipulation without guardrails",
                "compare all neutrino physics",
                "chapter10 physical claim allowed",
            ),
        ):
            reasons.append("chapter10_unbounded_manipulation")

    if _chapter11_requested(observation):
        contract = _chapter11_passage_contract(observation.raw_payload)
        injection = _chapter11_injection_packet(observation.raw_payload)
        path_a = _chapter11_path_event(injection, "Path_A_event", "path_A_neutrino")
        path_b = _chapter11_path_event(injection, "Path_B_event", "path_B_antineutrino")
        if not contract:
            reasons.append("chapter11_missing_passage_contract")
        if not injection:
            reasons.append("chapter11_missing_injection_packet")
        if not path_a or not path_b:
            reasons.append("chapter11_path_pair_missing")
        if path_a and path_b and _chapter11_path_container_mismatch(path_a, path_b):
            reasons.append("chapter11_path_container_mismatch")
        if path_a and path_b and _chapter11_path_route_mismatch(path_a, path_b):
            reasons.append("chapter11_path_admission_route_mismatch")
        if ready_for_fnp is True or _contains_any(
            text,
            (
                "chapter11 fnp before synthia",
                "chapter 11 fnp before synthia",
                "chapter11 direct fnp",
                "passage skips synthia",
                "ready_for_fnp before synthia",
            ),
        ):
            reasons.append("chapter11_fnp_before_synthia")
        if _contains_any(
            text,
            (
                "t2k reproduced",
                "t2k reproduction claim",
                "t2k_like = t2k",
                "t2k-like reproduces t2k",
                "chapter11 t2k reproduction",
            ),
        ):
            reasons.append("chapter11_t2k_reproduction_claim")
        if _contains_any(
            text,
            (
                "cp measurement claim",
                "cp violation measured",
                "measures cp violation",
                "chapter11 cp measurement",
            ),
        ):
            reasons.append("chapter11_cp_measurement_claim")
        if _contains_any(
            text,
            (
                "path_comparison = cp_measurement",
                "pathcomparison_11 = cp_measurement",
                "path comparison measures cp",
                "two_path_contrast = cp_measurement",
            ),
        ):
            reasons.append("chapter11_path_comparison_as_cp_measurement")
        if _contains_any(
            text,
            (
                "background missing equals zero",
                "background_missing = background_zero",
                "background_model_missing = background_zero",
                "missing background is zero",
            ),
        ):
            reasons.append("chapter11_background_missing_as_zero")
        if _contains_any(
            text,
            (
                "dl_lex = df_11",
                "dl_lex equals df_11",
                "dl_lex = df",
                "dl_lex as df_11",
                "dL_lex = dF_11".lower(),
            ),
        ):
            reasons.append("chapter11_dl_lex_as_df")
        if _contains_any(
            text,
            (
                "candidate_as_proof",
                "i_fractal_candidate_11 proves",
                "candidate proves",
                "candidate is proof",
            ),
        ):
            reasons.append("chapter11_candidate_as_proof")
        if _contains_forbidden_chapter11_output(observation.raw_payload):
            reasons.append("chapter11_fnp_output_in_synthia")

    if _chapter12_requested(observation):
        contract = _chapter12_validation_contract(observation.raw_payload)
        if not contract:
            reasons.append("chapter12_missing_validation_contract")
        else:
            if not str(contract.get("reference_run_id", "")).strip():
                reasons.append("chapter12_missing_reference_run")
            supplied_carriers = contract.get("required_carriers", [])
            if not isinstance(supplied_carriers, list) or set(map(str, supplied_carriers)) != set(CHAPTER6_REQUIRED_CARRIERS):
                reasons.append("chapter12_incomplete_carrier_policy")

            medium_policy = contract.get("medium_policy")
            if not isinstance(medium_policy, Mapping) or medium_policy.get("explicit_matter_potential_required") is not True:
                reasons.append("chapter12_incomplete_matter_model")

            detector_policy = contract.get("detector_policy")
            if not isinstance(detector_policy, Mapping) or detector_policy.get("response_matrix_required") is not True:
                reasons.append("chapter12_incomplete_detector_response")
            elif str(detector_policy.get("background_policy", "")) != "explicit_or_none_by_model":
                reasons.append("chapter12_incomplete_detector_response")

            repeat_protocol = contract.get("repeat_protocol")
            if not isinstance(repeat_protocol, Mapping):
                reasons.append("chapter12_invalid_repeat_protocol")
            else:
                deterministic_runs = _optional_float(repeat_protocol.get("deterministic_runs"))
                stochastic_runs = _optional_float(repeat_protocol.get("stochastic_runs"))
                maximum_runs = _optional_float(repeat_protocol.get("maximum_runs"))
                delta_tolerance = _optional_float(repeat_protocol.get("delta_max_tolerance"))
                rmse_tolerance = _optional_float(repeat_protocol.get("rmse_tolerance"))
                if (
                    deterministic_runs is None
                    or stochastic_runs is None
                    or maximum_runs is None
                    or not 1 <= deterministic_runs <= maximum_runs <= 1000
                    or not 1 <= stochastic_runs <= maximum_runs
                    or delta_tolerance is None
                    or rmse_tolerance is None
                    or delta_tolerance < 0
                    or rmse_tolerance < 0
                ):
                    reasons.append("chapter12_invalid_repeat_protocol")
                if repeat_protocol.get("hidden_randomness") is not False or not str(
                    repeat_protocol.get("seed_policy", "")
                ).strip():
                    reasons.append("chapter12_hidden_randomness")

            if str(contract.get("proof_state_requested", "")) not in {
                "P0_structural",
                "P1_software_execution",
                "P2_internal_repeatability",
            } or contract.get("physical_model_validated") is not False:
                reasons.append("chapter12_invalid_proof_upgrade")
            if isinstance(medium_policy, Mapping) and medium_policy.get("MSW_measurement_claim") is True:
                reasons.append("chapter12_msw_as_measurement")
            if isinstance(detector_policy, Mapping) and detector_policy.get("trace_is_neutrino") is True:
                reasons.append("chapter12_trace_as_neutrino")
            if isinstance(detector_policy, Mapping) and detector_policy.get("secondary_is_primary_interaction") is True:
                reasons.append("chapter12_secondary_as_primary_interaction")
            if contract.get("repetition_is_experimental_evidence") is True:
                reasons.append("chapter12_repetition_as_experimental_evidence")
            if contract.get("ready_for_FNP") is True or ready_for_fnp is True:
                reasons.append("chapter12_fnp_before_synthia")
        if _contains_forbidden_chapter12_output(observation.raw_payload):
            reasons.append("chapter12_fnp_output_in_synthia")

    if _chapter5_requested(observation) and set(reasons) & (
        CRITICAL_REJECTION_CODES | CORRECTION_CODES | SUSPENSION_CODES
    ):
        reasons.append("missing_allowed_payload_for_chapter5")

    return [code for code in REFUSAL_CATEGORIES if code in set(reasons)]


def _decision_status(reason_codes: tuple[str, ...]) -> DecisionStatus:
    reason_set = set(reason_codes)
    if reason_set & CRITICAL_REJECTION_CODES:
        return DecisionStatus.REJECTED
    if reason_set and reason_set <= PARTITION_CODES:
        return DecisionStatus.ACCEPTED_WITH_PARTITION
    if reason_set & CORRECTION_CODES:
        return DecisionStatus.CORRECTED
    if reason_set & SUSPENSION_CODES:
        return DecisionStatus.SUSPENDED
    return DecisionStatus.ACCEPTED


def _next_action(status: DecisionStatus) -> str:
    return {
        DecisionStatus.ACCEPTED: "admit_to_fnp",
        DecisionStatus.ACCEPTED_WITH_PARTITION: "admit_to_fnp",
        DecisionStatus.CORRECTED: "rerun_synthia",
        DecisionStatus.SUSPENDED: "hold_for_review",
        DecisionStatus.REJECTED: "block_fnp",
    }[status]


def _human_message(status: DecisionStatus) -> str:
    return {
        DecisionStatus.ACCEPTED: "Lexical admission passed for educational simulation.",
        DecisionStatus.ACCEPTED_WITH_PARTITION: "Only the admitted lexical partition may continue.",
        DecisionStatus.CORRECTED: "Correct the wording and rerun Synthia before FNP-QNN.",
        DecisionStatus.SUSPENDED: "Missing context requires review before FNP-QNN.",
        DecisionStatus.REJECTED: "The claim crosses a public safety boundary and must not enter FNP-QNN.",
    }[status]


def _d_l_lex(observation: NeutrinoObservationInput, reason_codes: tuple[str, ...]) -> float:
    if not reason_codes:
        chapter7_d_l_lex = _chapter7_metric(observation, "dL_lex")
        if _chapter7_requested(observation) and chapter7_d_l_lex is not None:
            return round(_clamp01(chapter7_d_l_lex), 8)
        return 0.12
    load = 0.12
    load += 0.45 * bool(set(reason_codes) & CRITICAL_REJECTION_CODES)
    load += 0.25 * bool(set(reason_codes) & CORRECTION_CODES)
    load += 0.18 * bool(set(reason_codes) & SUSPENSION_CODES)
    load += min(0.20, 0.025 * len(reason_codes))
    return round(_clamp01(load), 8)


def _chapter3_profile(observation: NeutrinoObservationInput, reason_codes: tuple[str, ...]) -> dict[str, object]:
    l_over_e = None
    if observation.distance_km is not None and observation.energy_gev is not None and observation.energy_gev > 0.0:
        l_over_e = round(observation.distance_km / observation.energy_gev, 8)
    created_flavor = observation.created_flavor if observation.created_flavor in VALID_FLAVORS else "unknown"
    flavor_status = "unknown" if created_flavor == "unknown" else "declared"
    mass_status = "unknown" if not observation.mass_basis else "toy_simulation"
    detector_projection_status = _detector_projection_status(observation)
    return {
        "profile_version": "chapter3.neutrino_public_safe.v1",
        "physical_minimum_profile": {
            "particle_family": "neutral_lepton",
            "claim_class": observation.claim_class,
            "boundary": BOUNDARY,
            "direct_detection_claim": False,
        },
        "flavor_profile": {
            "I_flavor": {
                "created_flavor": created_flavor,
                "flavor_basis": dict(observation.flavor_basis),
                "flavor_status": flavor_status,
                "allowed_flavors": ["nu_e", "nu_mu", "nu_tau"],
                "guardrail": "flavor_weak_state != mass_propagation_state",
            }
        },
        "mass_profile": {
            "I_mass": {
                "mass_basis": dict(observation.mass_basis),
                "mass_status": mass_status,
                "mass_weights_status": "toy_simulation" if observation.mass_basis else "unknown",
                "guardrail": "mass_propagation_state != flavor_weak_state",
            }
        },
        "phase_profile": {
            "I_phase": {
                "distance_km": observation.distance_km,
                "energy_gev": observation.energy_gev,
                "L_over_E": l_over_e,
                "phase_evolution_status": "available" if l_over_e is not None else "not_available",
                "guardrail": "phase_evolution != literal_mass_change",
            }
        },
        "interaction_profile": {
            "I_interaction": {
                "channel": observation.interaction_channel or "unknown",
                "primary_interaction": "weak" if observation.interaction_channel in VALID_INTERACTION_CHANNELS else "unknown",
                "allowed_channels": sorted(VALID_INTERACTION_CHANNELS),
                "guardrail": "weak_CC != strong_interaction",
            }
        },
        "secondary_profile": {
            "I_secondary": {
                "products": list(observation.secondary_products),
                "secondary_status": "declared" if observation.secondary_products else "unknown",
                "guardrail": "secondary_response != primary_neutrino_force",
            }
        },
        "detector_profile": {
            "I_detector": {
                "projection": observation.detector_signature or "unknown",
                "detector_projection_status": detector_projection_status,
                "visibility_status": "indirect" if detector_projection_status != "none" else "none",
                "guardrail": "I_detector != I_neutrino",
            }
        },
        "chapter3_guardrail_summary": {
            "reason_codes": list(reason_codes),
            "no_downstream_fractal_fields": True,
            "simulation_not_detection": True,
        },
    }


def _chapter4_profile(
    observation: NeutrinoObservationInput,
    reason_codes: tuple[str, ...],
    status: DecisionStatus,
    d_l_lex: float,
    chapter3_profile: Mapping[str, object],
) -> dict[str, object]:
    lex_scores = _chapter4_lexicon_scores(observation, reason_codes)
    lex_metrics = _chapter4_lex_metrics(lex_scores, reason_codes, d_l_lex)
    protection_profile = _chapter4_protection_profile(observation, reason_codes, status, chapter3_profile, lex_metrics)
    return {
        "profile_version": "chapter4.lex_neutrino_public_safe.v1",
        "p_neutrino_profile": _p_neutrino_profile(observation, reason_codes, lex_scores),
        "lex_neutrino_profile": {
            "profile_name": "lex_neutrino",
            "lexicons": lex_scores,
            "taxonomy_chain": "P_neutrino -> Synthia -> P_lex_neutrino -> H_lex -> G_lex -> I_lexicon -> dL_lex -> Adm_lex",
            "lexicon_count": len(CHAPTER4_LEXICONS),
        },
        "lex_metrics": lex_metrics,
        "protection_profile": protection_profile,
        "chapter4_guardrail_summary": {
            "reason_codes": list(reason_codes),
            "schema_additive": True,
            "synthia_only_lexical": True,
            "no_downstream_fractal_fields": True,
        },
    }


def _chapter5_intake_profile(
    observation: NeutrinoObservationInput,
    reason_codes: tuple[str, ...],
    status: DecisionStatus,
    chapter3_profile: Mapping[str, object],
    chapter4_profile: Mapping[str, object],
) -> dict[str, object]:
    guard = _nested_mapping(chapter4_profile, "protection_profile", "SynthiaGuard_neutrino")
    protection_packet = _nested_mapping(chapter4_profile, "protection_profile", "ProtectionPacket_neutrino")
    lex_metrics = _nested_mapping(chapter4_profile, "lex_metrics")
    p_profile = _nested_mapping(chapter4_profile, "p_neutrino_profile")
    allowed_payload = guard.get("allowed_payload") if isinstance(guard.get("allowed_payload"), Mapping) else {}
    if not allowed_payload and status is DecisionStatus.ACCEPTED:
        allowed_payload = {
            "event_id": observation.event_id,
            "payload_status": "full_lexical_payload_admitted",
            "approved_scope": "full_lexical_payload",
        }
    excluded_payload = guard.get("excluded_payload") if isinstance(guard.get("excluded_payload"), Mapping) else {}
    scale_context = observation.raw_payload.get("scale_context")
    scale_context = scale_context if isinstance(scale_context, Mapping) else {}
    carrier_request = observation.raw_payload.get("carrier_request")
    carrier_family = _carrier_family(carrier_request)
    guard_state = _chapter5_guard_state(reason_codes, status, allowed_payload, carrier_family)
    return {
        "profile_version": "chapter5.fnp_intake_public_safe.v1",
        "E_FNP_neutrino_request": {
            "event_id": observation.event_id,
            "source_trace_status": "present" if observation.source_truth else "missing",
            "simulation_status": observation.claim_class,
            "allowed_payload_status": "present" if allowed_payload else "missing",
            "excluded_payload_status": "present" if excluded_payload else "none",
            "input_object_boundary": "lexically_admitted_event_request_only",
        },
        "C_FNP_request": {
            "S": "neutrino_public_safe_simulation_chamber",
            "Omega": "chapter5_fnp_intake",
            "A": "allowed_payload_only",
            "R": "public_guardrail_relations",
            "M": "deterministic_local_mapping_required",
            "Theta": "chapter5_5_1_to_5_4",
            "Adm": "requires_fnp_validation",
        },
        "TIF_seed_request": {
            "source": "chapter4_p_neutrino_profile",
            "T/I/F": dict(p_profile.get("T/I/F", {})) if isinstance(p_profile.get("T/I/F"), Mapping) else {},
            "lexical_metrics": {
                "H_lex": lex_metrics.get("H_lex"),
                "G_lex": lex_metrics.get("G_lex"),
                "I_lexicon": lex_metrics.get("I_lexicon"),
                "dL_lex": lex_metrics.get("dL_lex"),
            },
            "seed_boundary": "lexical_seed_not_fractal_friction",
        },
        "scale_context_request": {
            "status": "present" if scale_context else "missing",
            "domain": str(scale_context.get("domain", "unspecified")) if scale_context else "unspecified",
            "scale": str(scale_context.get("scale", "unspecified")) if scale_context else "unspecified",
            "measurement_method": str(scale_context.get("measurement_method", "unspecified")) if scale_context else "unspecified",
        },
        "carrier_request_policy": {
            "requested_family": carrier_family or "unspecified",
            "allowed_families": list(CHAPTER5_CARRIER_FAMILIES),
            "status": "valid" if carrier_family in CHAPTER5_CARRIER_FAMILIES else "missing_or_invalid",
            "fnp_must_supply_numeric_carrier_values": True,
        },
        "guard_state": {
            **guard_state,
            "chapter4_protection_actions": {
                key: value.get("action")
                for key, value in protection_packet.items()
                if isinstance(value, Mapping) and "action" in value
            },
        },
        "Adm_FNP_required": True,
        "boundary": {
            "synthia_role": "lexical_intake_only",
            "no_fractal_computation": True,
            "invariants": [
                "dL_lex != downstream fractal carrier",
                "bounded carrier != downstream friction",
                "bounded carrier != fractal indeterminacy candidate",
            ],
        },
    }


def _chapter6_vector_profile(
    observation: NeutrinoObservationInput,
    reason_codes: tuple[str, ...],
    status: DecisionStatus,
    d_l_lex: float,
    chapter3_profile: Mapping[str, object],
    chapter4_profile: Mapping[str, object],
    chapter5_intake_profile: Mapping[str, object],
) -> dict[str, object]:
    source_truth = dict(observation.source_truth)
    source_type = str(observation.raw_payload.get("source_type", "")).strip() or (
        "toy_simulation" if observation.claim_class == "simulation" else "unknown"
    )
    source_status = str(observation.raw_payload.get("source_status", "")).strip() or (
        "simulation_input" if observation.claim_class == "simulation" else "unknown"
    )
    p_profile = _nested_mapping(chapter4_profile, "p_neutrino_profile")
    tif_profile = dict(p_profile.get("T/I/F", {})) if isinstance(p_profile.get("T/I/F"), Mapping) else {}
    lexical_metrics = _nested_mapping(chapter4_profile, "lex_metrics")
    chapter5_guard = _nested_mapping(chapter5_intake_profile, "guard_state")
    source_profile = {
        "source_type": source_type,
        "source_status": source_status,
        "evidence_level": str(observation.raw_payload.get("evidence_level", "simulation_reference")),
        "provenance": str(observation.raw_payload.get("provenance", "source_truth" if source_truth else "missing")),
        "source_truth_status": "present" if source_truth else "missing",
        "boundary": str(observation.raw_payload.get("boundary", "no_real_detection_claim")),
    }
    carriers = {
        "I_source": source_profile,
        "I_flavor": dict(_nested_mapping(chapter3_profile, "flavor_profile", "I_flavor")),
        "I_mass": dict(_nested_mapping(chapter3_profile, "mass_profile", "I_mass")),
        "I_mix": _chapter6_mix_carrier(observation),
        "I_phase": dict(_nested_mapping(chapter3_profile, "phase_profile", "I_phase")),
        "I_medium": _chapter6_medium_carrier(observation),
        "I_interaction": dict(_nested_mapping(chapter3_profile, "interaction_profile", "I_interaction")),
        "I_secondary": dict(_nested_mapping(chapter3_profile, "secondary_profile", "I_secondary")),
        "I_detector": dict(_nested_mapping(chapter3_profile, "detector_profile", "I_detector")),
        "I_uncertainty": _chapter6_uncertainty_carrier(
            observation,
            reason_codes,
            status,
            tif_profile,
            lexical_metrics,
            chapter5_guard,
        ),
    }
    missing_carriers = [name for name in CHAPTER6_REQUIRED_CARRIERS if not carriers.get(name)]
    guardrail_check = _chapter6_guardrail_check(observation, reason_codes, carriers, d_l_lex)
    return {
        "profile_version": "chapter6.i_neutrino_vector_public_safe.v1",
        "vector_definition": "I_neutrino = I_neutrino_vec within chamber frame only",
        "I_neutrino_vec": {
            "carrier_order": list(CHAPTER6_REQUIRED_CARRIERS),
            "carriers": carriers,
            "missing_carriers": missing_carriers,
            "vector_status": "assembled" if not missing_carriers else "incomplete",
        },
        "GuardrailCheck": guardrail_check,
        "readiness": {
            "ready_for_Synthia": guardrail_check["ready_for_Synthia"],
            "ready_for_FNP": guardrail_check["ready_for_FNP"],
            "next_required_gate": "Synthia lexical admission before FNP friction",
        },
        "projection_policy": {
            "lexical_projection": "dL_lex = Pi_lex(I_neutrino_vec)",
            "friction_policy": "FNP friction only after admission",
            "lexical_load_value": round(_clamp01(d_l_lex), 8),
        },
        "vector_invariants": [
            "I_neutrino_vec != dL_lex",
            "I_neutrino_vec != downstream friction",
            "I_neutrino_vec != detector_signature",
            "dL_lex != downstream friction",
            "I_lexicon != downstream fractal admission",
            "simulation != real_detection",
        ],
        "boundary": {
            "synthia_role": "assemble_and_classify_vector_only",
            "no_fractal_computation": True,
            "no_real_detection_claim": True,
            "chamber_frame_only": True,
        },
    }


def _chapter6_mix_carrier(observation: NeutrinoObservationInput) -> dict[str, object]:
    mixing_matrix = observation.raw_payload.get("mixing_matrix_or_weights", observation.raw_payload.get("mixing_matrix"))
    return {
        "mixing_model": str(observation.raw_payload.get("mixing_model", "PMNS_like_toy")),
        "mixing_matrix_or_weights": mixing_matrix if isinstance(mixing_matrix, Mapping) else "symbolic",
        "mixing_status": str(observation.raw_payload.get("mixing_status", "toy_simulation")),
        "mixing_source": str(observation.raw_payload.get("mixing_source", "local_payload")),
        "mixing_guardrail": "PMNS_like_toy != experimental_PMNS_fit",
    }


def _chapter6_medium_carrier(observation: NeutrinoObservationInput) -> dict[str, object]:
    medium_type = str(
        observation.raw_payload.get("medium_type", observation.raw_payload.get("medium", "vacuum"))
    ).strip() or "vacuum"
    density_status = str(observation.raw_payload.get("density_status", "not_applicable")).strip() or "not_applicable"
    matter_status = str(observation.raw_payload.get("matter_effect_status", "ignored_in_phase1")).strip()
    msw_status = str(observation.raw_payload.get("MSW_status", observation.raw_payload.get("msw_status", "not_used"))).strip()
    if medium_type.lower() != "vacuum" and density_status == "not_applicable":
        density_status = "unknown"
    return {
        "medium_type": _normalize_token(medium_type),
        "density_status": _normalize_token(density_status),
        "matter_effect_status": _normalize_token(matter_status or "ignored_in_phase1"),
        "MSW_status": _normalize_token(msw_status or "not_used"),
        "medium_source": str(observation.raw_payload.get("medium_source", "local_payload")),
        "medium_guardrail": "matter_effect_named != matter_effect_computed",
    }


def _chapter6_uncertainty_carrier(
    observation: NeutrinoObservationInput,
    reason_codes: tuple[str, ...],
    status: DecisionStatus,
    tif_profile: Mapping[str, object],
    lexical_metrics: Mapping[str, object],
    chapter5_guard: Mapping[str, object],
) -> dict[str, object]:
    return {
        "TIF_profile": dict(tif_profile),
        "source_gap": "none" if observation.source_truth else "missing_source_truth",
        "model_gap": "phase1_toy",
        "detector_gap": "high_for_real_detection" if observation.detector_signature else "missing_detector_projection",
        "simulation_gap": "declared" if observation.claim_class == "simulation" else "invalid_claim_class",
        "lexical_gap": {
            "status": status.value,
            "I_lexicon": lexical_metrics.get("I_lexicon"),
            "lexical_load": lexical_metrics.get("dL_lex"),
        },
        "plithogenic_contradiction": {
            "reason_codes": list(reason_codes),
            "contradiction_count": len(reason_codes),
        },
        "FNP_pending_status": "no_FNP_before_admission",
        "unknown_fields": _chapter6_unknown_fields(observation),
        "guardrail_residuals": list(reason_codes)
        or ["no_real_detection_claim", "no_strong_primary_claim", "no_literal_mass_change_claim"],
        "chapter5_intake_state": dict(chapter5_guard),
    }


def _chapter6_guardrail_check(
    observation: NeutrinoObservationInput,
    reason_codes: tuple[str, ...],
    carriers: Mapping[str, object],
    d_l_lex: float,
) -> dict[str, object]:
    reason_set = set(reason_codes)
    return {
        "source_declared": bool(observation.source_truth),
        "simulation_status_declared": observation.claim_class == "simulation",
        "no_real_detection_claim": "real_detection_claim" not in reason_set,
        "flavor_mass_separated": not bool(reason_set & {"flavor_mass_collapse", "mass_basis_equals_flavor_basis"}),
        "mass_weights_marked_toy": _nested_mapping(carriers, "I_mass").get("mass_weights_status") == "toy_simulation",
        "weak_channel_declared": observation.interaction_channel in VALID_INTERACTION_CHANNELS,
        "strong_primary_claim": "strong_primary_interaction_claim" in reason_set,
        "detector_trace_not_object": not bool(
            reason_set & {"detector_trace_confused_with_particle", "trace_as_neutrino_total"}
        ),
        "phase_not_choice": "choice_or_intention_language" not in reason_set,
        "dL_lex_not_downstream_friction": not bool(
            reason_set & {"dL_lex_equals_dF", "dL_lex_used_as_D_f"}
        ),
        "lexical_load": round(_clamp01(d_l_lex), 8),
        "ready_for_Synthia": True,
        "ready_for_FNP": "false_before_Synthia",
    }


def _chapter7_transition_profile(
    observation: NeutrinoObservationInput,
    reason_codes: tuple[str, ...],
    status: DecisionStatus,
    d_l_lex: float,
    chapter4_profile: Mapping[str, object],
    chapter6_vector_profile: Mapping[str, object],
) -> dict[str, object]:
    vector = _nested_mapping(chapter6_vector_profile, "I_neutrino_vec")
    carriers = _nested_mapping(vector, "carriers")
    phase = _nested_mapping(carriers, "I_phase")
    guardrail = _nested_mapping(chapter6_vector_profile, "GuardrailCheck")
    synthia_reading = _chapter7_synthia_reading(observation, d_l_lex, chapter4_profile)
    admitted = status in {DecisionStatus.ACCEPTED, DecisionStatus.ACCEPTED_WITH_PARTITION}
    return {
        "profile_version": "chapter7.synthia_transition_public_safe.v1",
        "I_neutrino_definition": "I_neutrino := I_neutrino_vec",
        "passage_test": {
            "I_neutrino_vec_status": vector.get("vector_status", "unknown"),
            "L_over_E": phase.get("L_over_E"),
            "ready_for_Synthia": guardrail.get("ready_for_Synthia") is True,
            "ready_for_FNP": "false_before_Synthia",
            "passage_boundary": "assembled_vector_before_fnp_friction",
        },
        "synthia_reading": synthia_reading,
        "chapter7_gate": {
            "ready_for_FNP": "true_after_Synthia" if admitted else "false",
            "approved_for_fnp": admitted and synthia_reading["approved_for_fnp"] is True,
            "reason_codes": list(reason_codes),
            "next_required_gate": "FNP chapter7 readout",
        },
        "transition_invariants": [
            "I_neutrino_vec != dL_lex",
            "I_neutrino_vec != downstream friction",
            "dL_lex != downstream friction",
            "I_lexicon != downstream fractal admission",
            "candidate is not proof",
            "simulation is not detection",
        ],
        "boundary": {
            "synthia_role": "lexical_transition_only",
            "no_fractal_computation": True,
            "no_real_detection_claim": True,
        },
    }


def _chapter7_synthia_reading(
    observation: NeutrinoObservationInput,
    d_l_lex: float,
    chapter4_profile: Mapping[str, object],
) -> dict[str, object]:
    supplied = observation.raw_payload.get("chapter7_synthia_reading")
    supplied = supplied if isinstance(supplied, Mapping) else {}
    lex_metrics = _nested_mapping(chapter4_profile, "lex_metrics")
    return {
        "selected_observation_lexicon": str(
            supplied.get("selected_observation_lexicon", "phase_evolution")
        ),
        "secondary_observation_lexicon": str(
            supplied.get("secondary_observation_lexicon", "weak_interaction")
        ),
        "H_lex": _chapter7_float(supplied, "H_lex", lex_metrics.get("H_lex", 0.0)),
        "G_lex": _chapter7_float(supplied, "G_lex", lex_metrics.get("G_lex", 0.0)),
        "I_lexicon": _chapter7_float(supplied, "I_lexicon", lex_metrics.get("I_lexicon", 0.0)),
        "C_lex": _chapter7_float(supplied, "C_lex", lex_metrics.get("C_lex", 0.0)),
        "E_gap": _chapter7_float(supplied, "E_gap", lex_metrics.get("E_gap", 0.0)),
        "dL_lex": round(_clamp01(d_l_lex), 8),
        "classification_status": str(supplied.get("classification_status", "stable")),
        "approved_for_fnp": bool(supplied.get("approved_for_fnp", True)),
        "reading_boundary": "dL_lex is lexical transition load only",
    }


def _chapter7_float(supplied: Mapping[str, object], key: str, default: object) -> float:
    value = _optional_float(supplied.get(key, default))
    return round(_clamp01(value if value is not None else 0.0), 8)


def _chapter8_run_profile(
    observation: NeutrinoObservationInput,
    reason_codes: tuple[str, ...],
    status: DecisionStatus,
    d_l_lex: float,
    chapter6_vector_profile: Mapping[str, object],
    chapter7_transition_profile: Mapping[str, object],
) -> dict[str, object]:
    vector = _nested_mapping(chapter6_vector_profile, "I_neutrino_vec")
    guardrail = _nested_mapping(chapter6_vector_profile, "GuardrailCheck")
    passage = _nested_mapping(chapter7_transition_profile, "passage_test")
    reading = _nested_mapping(chapter7_transition_profile, "synthia_reading")
    gate = _nested_mapping(chapter7_transition_profile, "chapter7_gate")
    run_status = _chapter8_run_status(reason_codes, status, gate)
    permission = run_status == "admissible_under_guardrails"
    return {
        "profile_version": "chapter8.first_run_public_safe.v1",
        "run_input": {
            "I_neutrino_vec_status": vector.get("vector_status", "unknown"),
            "L_over_E": passage.get("L_over_E"),
            "ready_for_Synthia": guardrail.get("ready_for_Synthia") is True,
            "ready_for_FNP": "false_before_Synthia",
            "source_status": _nested_mapping(vector, "carriers", "I_source").get("source_status", "unknown"),
            "simulation_status": "declared" if observation.claim_class == "simulation" else "invalid",
            "boundary": BOUNDARY,
        },
        "synthia_gate": {
            "Adm_lex": status in {DecisionStatus.ACCEPTED, DecisionStatus.ACCEPTED_WITH_PARTITION},
            "approved_for_fnp": gate.get("approved_for_fnp") is True,
            "ready_for_FNP": gate.get("ready_for_FNP", "false"),
            "selected_observation_lexicon": reading.get("selected_observation_lexicon"),
            "secondary_observation_lexicon": reading.get("secondary_observation_lexicon"),
            "dL_lex": round(_clamp01(d_l_lex), 8),
            "classification_status": reading.get("classification_status", status.value),
        },
        "run_decision": {
            "run_status": run_status,
            "decision_basis": _chapter8_decision_basis(run_status),
            "missing_requirements": _chapter8_missing_requirements(reason_codes),
            "refusal_codes": _chapter8_refusal_codes(reason_codes),
            "source_decision_status": status.value,
        },
        "run_permission": {
            "permission_to_continue": permission,
            "allowed_next_step": "FNP_QNN_readout" if permission else _chapter8_blocked_next_step(run_status),
            "can_continue_to_chapter9": permission,
            "forbidden_upgrades": [
                "permission_to_continue_as_proof",
                "admissible_as_detection",
                "simulation_as_real_detection",
                "candidate_as_proof",
                "FNP_before_Synthia",
            ],
            "claim_boundary": "educational simulation; permission is not proof; simulation is not detection",
        },
        "invariants": [
            "I_neutrino_vec remains the chamber object",
            "dL_lex remains lexical load",
            "FNP computes only after Synthia admission",
            "suspended is not zero",
            "rejected is not noise",
            "candidate is not proof",
        ],
    }


def _chapter8_run_status(
    reason_codes: tuple[str, ...],
    status: DecisionStatus,
    gate: Mapping[str, object],
) -> str:
    reason_set = set(reason_codes)
    if reason_set & CRITICAL_REJECTION_CODES:
        return "rejected"
    approved = gate.get("approved_for_fnp") is True and gate.get("ready_for_FNP") == "true_after_Synthia"
    if status in {DecisionStatus.ACCEPTED, DecisionStatus.ACCEPTED_WITH_PARTITION} and approved:
        return "admissible_under_guardrails"
    return "suspended"


def _chapter8_decision_basis(run_status: str) -> str:
    return {
        "admissible_under_guardrails": "Synthia admitted the lexical gate and preserved the first-run boundaries.",
        "suspended": "Missing or incomplete context prevents first-run continuation.",
        "rejected": "A critical guardrail was triggered; the run cannot continue.",
    }.get(run_status, "unknown first-run status")


def _chapter8_missing_requirements(reason_codes: tuple[str, ...]) -> list[str]:
    return [code for code in reason_codes if code in SUSPENSION_CODES]


def _chapter8_refusal_codes(reason_codes: tuple[str, ...]) -> list[str]:
    return [code for code in reason_codes if code in CRITICAL_REJECTION_CODES]


def _chapter8_blocked_next_step(run_status: str) -> str:
    if run_status == "rejected":
        return "stop_and_repair_claim"
    return "repair_payload"


def _chapter9_source_choice_profile(
    observation: NeutrinoObservationInput,
    reason_codes: tuple[str, ...],
    status: DecisionStatus,
    chapter8_run_profile: Mapping[str, object],
) -> dict[str, object]:
    requested = _chapter9_requested(observation)
    source_ids = _chapter9_source_ids(observation.raw_payload)
    source_set = set(source_ids)
    experiment = _chapter9_experiment_choice(observation.raw_payload)
    run_permission = _nested_mapping(chapter8_run_profile, "run_permission")
    can_continue_from_chapter8 = (
        run_permission.get("can_continue_to_chapter9") is True
        and _nested_mapping(chapter8_run_profile, "run_decision").get("run_status")
        == "admissible_under_guardrails"
    )
    admitted = status in {DecisionStatus.ACCEPTED, DecisionStatus.ACCEPTED_WITH_PARTITION}
    required_sources_present = set(CHAPTER9_REQUIRED_SOURCE_IDS) <= source_set
    experiment_id = str(experiment.get("experiment_id", "")).strip()
    central_selected = experiment_id == CHAPTER9_EXPERIMENT_ID
    profile_status = (
        "selected_for_container"
        if requested and admitted and required_sources_present and central_selected and can_continue_from_chapter8
        else "not_requested"
        if not requested
        else "blocked_or_suspended"
    )
    return {
        "profile_version": "chapter9.source_choice_public_safe.v1",
        "chapter9_status": profile_status,
        "source_visibility": {
            "source_visible": requested,
            "registry_status": "present" if required_sources_present else "missing_required_source",
            "required_source_ids": list(CHAPTER9_REQUIRED_SOURCE_IDS),
            "provided_source_ids": source_ids,
            "source_role": "source_as_boundary_not_proof",
        },
        "source_families": {
            "source_physical": ["SB60-002", "CH9-T2K-OSC-001"],
            "source_mathematical": ["SB60-052"],
            "source_boundaries": [
                "source_physical != source_mathematical",
                "source_physical != proof",
                "source_mathematical != physical_proof",
                "citation != total_authority",
            ],
        },
        "central_experiment": {
            "experiment_id": experiment_id or CHAPTER9_EXPERIMENT_ID,
            "status": str(experiment.get("status", "selected_for_simulation")),
            "reproduction_status": str(experiment.get("reproduction_status", "not_T2K_reproduction")),
            "detection_status": str(experiment.get("detection_status", "no_real_detection_claim")),
            "ready_for_container": bool(experiment.get("ready_for_container", central_selected)),
            "ready_for_physical_claim": bool(experiment.get("ready_for_physical_claim", False)),
            "objective": str(experiment.get("objective", "compare_two_flavor_paths_under_guardrails")),
        },
        "paths": {
            "Path_A": {
                "beam_kind": "neutrino",
                "initial_flavor": "nu_mu",
                "target_projection": "nu_e",
                "status": "simulation_path",
            },
            "Path_B": {
                "beam_kind": "antineutrino",
                "initial_flavor": "anti_nu_mu",
                "target_projection": "anti_nu_e",
                "status": "simulation_path",
            },
        },
        "chapter8_dependency": {
            "can_continue_to_chapter9": can_continue_from_chapter8,
            "run_status": _nested_mapping(chapter8_run_profile, "run_decision").get("run_status", "unknown"),
            "permission_boundary": "chapter8_permission_is_not_proof",
        },
        "synthia_gate": {
            "Adm_lex": admitted,
            "approved_for_container_validation": (
                admitted and required_sources_present and central_selected and can_continue_from_chapter8
            ),
            "ready_for_FNP": (
                "true_after_Synthia_for_container_validation"
                if admitted and required_sources_present and central_selected and can_continue_from_chapter8
                else "false"
            ),
            "reason_codes": list(reason_codes),
            "next_required_gate": "FNP chapter9 experiment choice validation",
        },
        "forbidden_upgrades": [
            "T2K_like_as_T2K_reproduction",
            "CP_asymmetry_toy_as_CP_measurement",
            "central_experiment_as_real_detection",
            "source_stack_as_proof",
            "background_missing_as_zero",
            "FNP_before_Synthia",
        ],
        "boundary": {
            "synthia_role": "source_choice_and_lexical_gate_only",
            "no_fractal_computation": True,
            "no_real_detection_claim": True,
            "chapter10_next": "build_experimental_container",
        },
    }


def _chapter10_chamber_profile(
    observation: NeutrinoObservationInput,
    reason_codes: tuple[str, ...],
    status: DecisionStatus,
    chapter9_source_choice_profile: Mapping[str, object],
) -> dict[str, object]:
    requested = _chapter10_requested(observation)
    source_ids = _chapter10_source_ids(observation.raw_payload)
    source_set = set(source_ids)
    source_ready = set(CHAPTER10_REQUIRED_SOURCE_IDS) <= source_set
    container = _chapter10_container(observation.raw_payload)
    event = _chapter10_event(observation.raw_payload)
    run_contract = _chapter10_run_contract(observation.raw_payload)
    chapter9_ready = (
        _nested_mapping(chapter9_source_choice_profile, "central_experiment").get("ready_for_container") is True
        and _nested_mapping(chapter9_source_choice_profile, "synthia_gate").get("approved_for_container_validation")
        is True
    )
    admitted = status in {DecisionStatus.ACCEPTED, DecisionStatus.ACCEPTED_WITH_PARTITION}
    critical_block = bool(set(reason_codes) & CRITICAL_REJECTION_CODES)
    suspended = bool(set(reason_codes) & SUSPENSION_CODES)
    run_prepared = requested and admitted and source_ready and bool(container) and bool(event) and bool(run_contract) and chapter9_ready
    if not requested:
        profile_status = "not_requested"
    elif critical_block:
        profile_status = "rejected"
    elif suspended or not run_prepared:
        profile_status = "suspended"
    else:
        profile_status = "run_prepared_for_chapter11"

    return {
        "profile_version": "chapter10.chamber_container_public_safe.v1",
        "chapter10_status": profile_status,
        "source_visibility": {
            "source_visible": requested,
            "registry_status": "present" if source_ready else "missing_required_source",
            "required_source_ids": list(CHAPTER10_REQUIRED_SOURCE_IDS),
            "provided_source_ids": source_ids,
            "source_role": "simulation_architecture_and_container_contract_not_proof",
        },
        "Chamber_10": {
            "chamber_status": "declared" if requested else "not_requested",
            "chamber_role": "admission_separation_and_bounded_calculation",
            "not_detector": True,
            "layers": [
                "source_layer",
                "geometry_layer",
                "medium_layer",
                "particle_event_layer",
                "propagation_layer",
                "interaction_layer",
                "detector_projection_layer",
                "uncertainty_layer",
                "lexical_gate_layer",
                "friction_gate_layer",
            ],
            "guardrail": "chamber != detector",
        },
        "EventContainer_10": _chapter10_container_profile(container),
        "SimulatedNeutrinoEvent_10": _chapter10_event_profile(event, observation),
        "RunContract_10": _chapter10_run_contract_profile(run_contract),
        "chapter9_dependency": {
            "chapter9_status": chapter9_source_choice_profile.get("chapter9_status", "unknown"),
            "central_experiment_id": _nested_mapping(chapter9_source_choice_profile, "central_experiment").get(
                "experiment_id", CHAPTER9_EXPERIMENT_ID
            ),
            "ready_for_container": chapter9_ready,
            "dependency_boundary": "chapter9_choice_is_not_experiment_execution",
        },
        "SynthiaGate_10": {
            "Adm_lex": admitted,
            "approved_for_container_validation": run_prepared,
            "ready_for_FNP": "true_after_Synthia_for_run_contract_validation" if run_prepared else "false",
            "reason_codes": list(reason_codes),
            "next_required_gate": "FNP chapter10 run contract validation" if run_prepared else "repair_chapter10_payload",
        },
        "RunPrepared_10": {
            "chamber_ready": run_prepared,
            "container_ready": bool(container) and source_ready,
            "event_ready": bool(event),
            "path_pair_ready": _chapter10_path_pair_ready(event),
            "equality_controls_declared": bool(_nested_mapping(run_contract, "equality_controls")),
            "variable_controls_declared": bool(_nested_mapping(run_contract, "variable_controls")),
            "Synthia_required": True,
            "FNP_after_Synthia_only": True,
            "chapter11_execution_ready": run_prepared,
            "physical_claim_allowed": False,
        },
        "forbidden_upgrades": [
            "chamber_as_detector",
            "container_valid_as_physical_proof",
            "simulated_event_as_detection",
            "T2K_like_as_T2K_reproduction",
            "path_comparison_as_CP_measurement",
            "background_missing_as_zero",
            "prepared_tension_slot_as_dF",
            "FNP_before_Synthia",
        ],
        "boundary": {
            "synthia_role": "chapter10 chamber_container_event_run_contract_gate_only",
            "no_fractal_computation": True,
            "no_real_detection_claim": True,
            "chapter11_next": "execute_first_passage_under_declared_contract",
        },
    }


def _chapter10_container_profile(container: Mapping[str, object]) -> dict[str, object]:
    if not container:
        return {"container_status": "missing"}
    required_fields = [
        "schema_version",
        "container_id",
        "source_packet",
        "experiment_packet",
        "path_packets",
        "simulation_boundary",
        "detector_projection_policy",
        "uncertainty_policy",
        "guard_state",
        "admission_route",
    ]
    missing = [field for field in required_fields if not container.get(field)]
    return {
        "schema_version": str(container.get("schema_version", CHAPTER10_CONTAINER_SCHEMA_VERSION)),
        "container_id": str(container.get("container_id", "chapter10_t2k_like_container_001")),
        "container_status": "declared" if not missing else "incomplete",
        "required_fields_present": not missing,
        "missing_required_fields": missing,
        "simulation_boundary": str(container.get("simulation_boundary", "educational_simulation")),
        "detector_projection_policy": str(
            container.get("detector_projection_policy", "simulated_projection_only")
        ),
        "background_model_status": str(container.get("background_model_status", "missing_or_simplified")),
        "admission_route": str(container.get("admission_route", "container_to_synthia_to_fnp")),
        "container_boundary": "container_valid != physical_proof",
    }


def _chapter10_event_profile(
    event: Mapping[str, object],
    observation: NeutrinoObservationInput,
) -> dict[str, object]:
    if not event:
        return {"event_status": "missing"}
    path_packets = event.get("path_packets")
    paths = path_packets if isinstance(path_packets, list) else []
    return {
        "schema_version": str(event.get("schema_version", CHAPTER10_EVENT_SCHEMA_VERSION)),
        "event_id": str(event.get("event_id", observation.event_id)),
        "event_status": str(event.get("event_status", "educational_simulation")),
        "detection_status": str(event.get("detection_status", "no_real_detection_claim")),
        "reproduction_status": str(event.get("reproduction_status", "not_T2K_reproduction")),
        "measurement_status": str(event.get("measurement_status", "no_CP_measurement_claim")),
        "path_packets": paths,
        "L_over_E_context": {
            "distance_km": observation.distance_km,
            "energy_gev": observation.energy_gev,
            "L_over_E": _l_over_e(observation),
            "guardrail": "L_over_E != proof",
        },
        "interaction_policy": {
            "allowed_channels": ["weak_CC", "weak_NC"],
            "primary_interaction": "weak",
            "strong_primary_allowed": False,
        },
        "detector_projection_policy": {
            "projection_status": "simulated_projection_only",
            "visibility_status": "indirect",
            "detector_data_status": "none",
        },
        "background_model_status": dict(_nested_mapping(event, "background_model_status"))
        if _nested_mapping(event, "background_model_status")
        else {"status": "missing_or_simplified", "background_zero_claim": False},
        "event_boundary": "SimulatedNeutrinoEvent_10 != real_neutrino_event",
    }


def _chapter10_run_contract_profile(run_contract: Mapping[str, object]) -> dict[str, object]:
    if not run_contract:
        return {"run_contract_status": "missing"}
    equality_controls = _nested_mapping(run_contract, "equality_controls")
    variable_controls = _nested_mapping(run_contract, "variable_controls")
    return {
        "schema_version": str(run_contract.get("schema_version", CHAPTER10_RUN_CONTRACT_VERSION)),
        "run_id": str(run_contract.get("run_id", "chapter10_pre_run_contract_001")),
        "run_status": str(run_contract.get("run_status", "preparation_only")),
        "run_contract_status": "declared",
        "path_pair_status": str(run_contract.get("path_pair_status", "prepared_not_interpreted")),
        "equality_controls": dict(equality_controls),
        "variable_controls": dict(variable_controls),
        "prepared_tension_slots": list(run_contract.get("prepared_tension_slots", []))
        if isinstance(run_contract.get("prepared_tension_slots"), list)
        else [],
        "output_boundary": str(run_contract.get("output_boundary", "no_result_before_chapter11")),
        "contract_boundary": "prepared_tension_slot != dF",
    }


def _chapter10_path_pair_ready(event: Mapping[str, object]) -> bool:
    path_packets = event.get("path_packets") if isinstance(event, Mapping) else None
    if not isinstance(path_packets, list) or len(path_packets) < 2:
        return False
    text = _payload_text({"paths": path_packets})
    return all(token in text for token in ("path_a", "path_b", "nu_mu", "anti_nu_mu", "nu_e", "anti_nu_e"))


def _chapter11_passage_profile(
    observation: NeutrinoObservationInput,
    reason_codes: tuple[str, ...],
    status: DecisionStatus,
    d_l_lex: float,
    chapter10_chamber_profile: Mapping[str, object],
) -> dict[str, object]:
    requested = _chapter11_requested(observation)
    contract = _chapter11_passage_contract(observation.raw_payload)
    injection = _chapter11_injection_packet(observation.raw_payload)
    path_a = _chapter11_path_event(injection, "Path_A_event", "path_A_neutrino")
    path_b = _chapter11_path_event(injection, "Path_B_event", "path_B_antineutrino")
    common_controls = _chapter11_common_controls(injection)
    chapter10_ready = _nested_mapping(chapter10_chamber_profile, "RunPrepared_10").get("chapter11_execution_ready") is True
    admitted = status in {DecisionStatus.ACCEPTED, DecisionStatus.ACCEPTED_WITH_PARTITION}
    critical_block = bool(set(reason_codes) & CRITICAL_REJECTION_CODES)
    suspended = bool(set(reason_codes) & SUSPENSION_CODES)
    path_pair_ready = bool(path_a and path_b)
    symmetry_valid = (
        path_pair_ready
        and not _chapter11_path_container_mismatch(path_a, path_b)
        and not _chapter11_path_route_mismatch(path_a, path_b)
    )
    passage_ready = requested and admitted and chapter10_ready and bool(contract) and bool(injection) and symmetry_valid
    if not requested:
        profile_status = "not_requested"
    elif critical_block:
        profile_status = "rejected"
    elif suspended or not passage_ready:
        profile_status = "suspended"
    else:
        profile_status = "ready_for_fnp_passage"

    return {
        "profile_version": "chapter11.passage_public_safe.v1",
        "chapter11_status": profile_status,
        "Chapter11PassageContract": _chapter11_contract_profile(contract, chapter10_ready),
        "Chapter11InjectionPacket": _chapter11_injection_profile(injection, path_pair_ready),
        "Path_A_event": _chapter11_path_profile(path_a, "Path_A_event"),
        "Path_B_event": _chapter11_path_profile(path_b, "Path_B_event"),
        "CommonPathControls": _chapter11_controls_profile(common_controls),
        "ChamberSymmetry_11": {
            "status": "valid" if symmetry_valid else "invalid_or_incomplete",
            "same_container": bool(path_a and path_b and not _chapter11_path_container_mismatch(path_a, path_b)),
            "same_admission_route": bool(path_a and path_b and not _chapter11_path_route_mismatch(path_a, path_b)),
            "same_baseline_policy": str(common_controls.get("baseline_policy", "same")) == "same",
            "same_energy_policy": str(common_controls.get("energy_policy", "same")) == "same",
            "same_boundary": str(common_controls.get("simulation_boundary", BOUNDARY)) == BOUNDARY,
            "comparison_boundary": "PathComparison_11 != CP_measurement",
        },
        "SynthiaReading_11": {
            "selected_observation_lexicon": "t2k_like_path_pair" if requested else "not_requested",
            "secondary_observation_lexicon": "simulation_boundary",
            "active_lexicons": [
                "source_boundary_lex",
                "path_pair_lex",
                "simulation_boundary_lex",
                "cp_measurement_guard_lex",
                "fnp_boundary_lex",
            ],
            "dL_lex": d_l_lex,
            "classification_status": "admitted_under_lexical_guardrails" if passage_ready else profile_status,
            "approved_for_fnp": passage_ready,
            "ready_for_Synthia": requested,
            "ready_for_FNP": "true_after_Synthia" if passage_ready else "false",
            "physical_claim_allowed": False,
            "reason_codes": list(reason_codes),
            "reading_boundary": "dL_lex is lexical friction only; Synthia does not compute FNP outputs",
        },
        "forbidden_upgrades": [
            "T2K_like_as_T2K_reproduction",
            "PathComparison_11_as_CP_measurement",
            "Path_A_event_as_measured_appearance_event",
            "Path_B_event_as_CP_measurement",
            "background_missing_as_zero",
            "dL_lex_as_dF_11",
            "FNP_before_Synthia",
            "candidate_as_proof",
        ],
        "boundary": {
            "synthia_role": "chapter11 passage lexical gate only",
            "no_fractal_computation": True,
            "no_real_detection_claim": True,
            "chapter12_next": "variation_tests_after_conditional_readout",
        },
    }


def _chapter11_contract_profile(contract: Mapping[str, object], chapter10_ready: bool) -> dict[str, object]:
    if not contract:
        return {"status": "missing"}
    return {
        "schema_version": str(contract.get("schema_version", CHAPTER11_PASSAGE_CONTRACT_VERSION)),
        "status": str(contract.get("status", "established")),
        "run_origin": str(contract.get("run_origin", "chapter8_admissible_under_guardrails")),
        "experiment_choice": str(contract.get("experiment_choice", CHAPTER9_EXPERIMENT_ID)),
        "container_status": str(contract.get("container_status", "chapter10_ready")),
        "chapter10_execution_ready": chapter10_ready,
        "Synthia_required": bool(contract.get("Synthia_required", True)),
        "FNP_before_Synthia": bool(contract.get("FNP_before_Synthia", False)),
        "physical_claim_allowed": bool(contract.get("physical_claim_allowed", False)),
        "contract_boundary": str(contract.get("contract_boundary", "T2K_like != T2K_reproduction")),
    }


def _chapter11_injection_profile(injection: Mapping[str, object], path_pair_ready: bool) -> dict[str, object]:
    if not injection:
        return {"status": "missing"}
    return {
        "schema_version": str(injection.get("schema_version", CHAPTER11_INJECTION_PACKET_VERSION)),
        "status": str(injection.get("status", "assembled")),
        "route": str(injection.get("route", "container_to_synthia_to_fnp")),
        "path_pair_ready": path_pair_ready,
        "ready_for_Synthia": bool(injection.get("ready_for_Synthia", True)),
        "ready_for_FNP": str(injection.get("ready_for_FNP", "false_before_Synthia")),
        "injection_boundary": str(injection.get("injection_boundary", "simulation_path_pair_not_measurement")),
    }


def _chapter11_path_profile(path: Mapping[str, object], label: str) -> dict[str, object]:
    if not path:
        return {"path_label": label, "status": "missing"}
    return {
        "path_label": label,
        "path_id": str(path.get("path_id", label)),
        "container_id": str(path.get("container_id", "")),
        "admission_route": str(path.get("admission_route", "container_to_synthia_to_fnp")),
        "beam_kind": str(path.get("beam_kind", "")),
        "initial_flavor": str(path.get("initial_flavor", "")),
        "target_projection": str(path.get("target_projection", "")),
        "path_status": str(path.get("path_status", path.get("status", "simulation_path"))),
        "detection_claim": bool(path.get("detection_claim", False)),
        "measurement_claim": bool(path.get("measurement_claim", False)),
        "reproduction_claim": bool(path.get("reproduction_claim", False)),
        "boundary": str(path.get("boundary", "simulation_path != measured_event")),
    }


def _chapter11_controls_profile(common_controls: Mapping[str, object]) -> dict[str, object]:
    if not common_controls:
        return {"status": "missing"}
    return {
        "status": "declared",
        "container_policy": str(common_controls.get("container_policy", "same")),
        "admission_route_policy": str(common_controls.get("admission_route_policy", "same")),
        "baseline_policy": str(common_controls.get("baseline_policy", "same")),
        "energy_policy": str(common_controls.get("energy_policy", "same")),
        "detector_projection_policy": str(common_controls.get("detector_projection_policy", "same")),
        "background_model_status": str(common_controls.get("background_model_status", "missing_or_simplified")),
        "simulation_boundary": str(common_controls.get("simulation_boundary", BOUNDARY)),
    }


def _chapter12_validation_profile(
    observation: NeutrinoObservationInput,
    reason_codes: tuple[str, ...],
    status: DecisionStatus,
    chapter11_passage_profile: Mapping[str, object],
) -> dict[str, object]:
    requested = _chapter12_requested(observation)
    contract = _chapter12_validation_contract(observation.raw_payload)
    admitted = status in {DecisionStatus.ACCEPTED, DecisionStatus.ACCEPTED_WITH_PARTITION}
    ready = requested and admitted and bool(contract)
    if not requested:
        profile_status = "not_requested"
    elif ready:
        profile_status = "ready_for_fnp_validation"
    elif status is DecisionStatus.REJECTED:
        profile_status = "rejected"
    else:
        profile_status = "suspended"

    required_carriers = contract.get("required_carriers", []) if contract else []
    medium_policy = contract.get("medium_policy", {}) if contract else {}
    detector_policy = contract.get("detector_policy", {}) if contract else {}
    repeat_protocol = contract.get("repeat_protocol", {}) if contract else {}
    invariants = contract.get("invariants", []) if contract else []
    if not isinstance(medium_policy, Mapping):
        medium_policy = {}
    if not isinstance(detector_policy, Mapping):
        detector_policy = {}
    if not isinstance(repeat_protocol, Mapping):
        repeat_protocol = {}
    if not isinstance(required_carriers, list):
        required_carriers = []
    if not isinstance(invariants, list):
        invariants = []

    return {
        "profile_version": "chapter12.validation_public_safe.v1",
        "chapter12_status": profile_status,
        "ValidationContract_12": {
            "schema_version": str(contract.get("schema_version", CHAPTER12_VALIDATION_CONTRACT_VERSION))
            if contract
            else CHAPTER12_VALIDATION_CONTRACT_VERSION,
            "status": str(contract.get("status", "missing")) if contract else "missing",
            "reference_run_id": str(contract.get("reference_run_id", "")) if contract else "",
            "proof_state_requested": str(contract.get("proof_state_requested", "")) if contract else "",
            "physical_model_validated": False,
            "chapter11_dependency": "reference_declared" if contract.get("reference_run_id") else "missing",
            "chapter11_inline_status": str(chapter11_passage_profile.get("chapter11_status", "not_supplied")),
        },
        "carrier_policy": {
            "required_carriers": list(map(str, required_carriers)),
            "required_count": len(CHAPTER6_REQUIRED_CARRIERS),
            "provided_count": len(required_carriers),
            "exact_ten_carrier_set": set(map(str, required_carriers)) == set(CHAPTER6_REQUIRED_CARRIERS),
            "missing_carriers": [name for name in CHAPTER6_REQUIRED_CARRIERS if name not in set(map(str, required_carriers))],
        },
        "medium_policy": dict(medium_policy),
        "detector_policy": dict(detector_policy),
        "repeat_protocol": dict(repeat_protocol),
        "invariants": list(map(str, invariants)),
        "SynthiaReading_12": {
            "ready_for_Synthia": requested,
            "approved_for_fnp_validation": ready,
            "ready_for_FNP": "true_after_Synthia" if ready else "false",
            "reason_codes": list(reason_codes),
            "next_required_gate": "FNP chapter12 validation" if ready else "repair_chapter12_validation_contract",
        },
        "capability_boundary": {
            "requested_claim": "ten-carrier software computation",
            "maximum_proof_state": "P2_internal_repeatability",
            "physical_model_validated": False,
            "simulation_is_detection": False,
            "repetition_is_experimental_evidence": False,
        },
        "boundary": {
            "synthia_role": "chapter12 validation contract and lexical gate only",
            "no_medium_computation": True,
            "no_detector_reconstruction": True,
            "no_fractal_computation": True,
        },
    }


def _l_over_e(observation: NeutrinoObservationInput) -> float | None:
    if observation.distance_km is None or observation.energy_gev is None or observation.energy_gev <= 0.0:
        return None
    return round(observation.distance_km / observation.energy_gev, 8)


def _p_neutrino_profile(
    observation: NeutrinoObservationInput,
    reason_codes: tuple[str, ...],
    lex_scores: Mapping[str, float],
) -> dict[str, object]:
    dominant_lexicon, dominant_value = _dominant_score(lex_scores)
    contradiction_load = _contradiction_load(reason_codes)
    uncertainty_load = _uncertainty_load(reason_codes)
    truth_load = round(_clamp01(1.0 - max(contradiction_load, uncertainty_load)), 8)
    return {
        "A_neutrino": {
            "source": "source_lex",
            "flavor": "flavor_lex",
            "mass": "mass_lex",
            "mix": "mix_lex",
            "phase": "phase_lex",
            "medium": "medium_lex",
            "interaction": "interaction_lex",
            "secondary": "secondary_lex",
            "detector": "detector_lex",
            "uncertainty": "uncertainty_lex",
            "metaphor": "metaphor_lex",
            "overclaim": "overclaim_lex",
        },
        "values": {
            "created_flavor": observation.created_flavor,
            "interaction_channel": observation.interaction_channel or "unknown",
            "detector_signature": observation.detector_signature or "unknown",
            "secondary_products": list(observation.secondary_products),
        },
        "statuses": {
            "source_status": "present" if observation.source_truth else "missing",
            "claim_class": observation.claim_class,
            "metaphor_status": "partition_required" if "metaphor_as_physics" in reason_codes else "none",
            "admission_surface": "lexical_only",
        },
        "dominance": {
            "dominant_lexicon": dominant_lexicon,
            "dominant_value": dominant_value,
        },
        "contradictions": {
            "reason_codes": list(reason_codes),
            "contradiction_load": contradiction_load,
        },
        "weights": dict(lex_scores),
        "T/I/F": {
            "T": truth_load,
            "I": uncertainty_load,
            "F": contradiction_load,
        },
    }


def _chapter4_lexicon_scores(observation: NeutrinoObservationInput, reason_codes: tuple[str, ...]) -> dict[str, float]:
    scores = {key: 0.02 for key in CHAPTER4_LEXICONS}
    scores["source_lex"] += 0.18 if observation.source_truth else 0.08
    scores["flavor_lex"] += 0.18 if observation.created_flavor in VALID_FLAVORS else 0.04
    scores["mass_lex"] += 0.16 if observation.mass_basis else 0.04
    scores["mix_lex"] += 0.10 if observation.flavor_basis and observation.mass_basis else 0.03
    scores["phase_lex"] += 0.14 if observation.distance_km is not None and observation.energy_gev is not None else 0.04
    scores["medium_lex"] += 0.08 if _contains_any(observation.text, ("medium", "vacuum", "matiere", "matter", "msw")) else 0.03
    scores["interaction_lex"] += 0.18 if observation.interaction_channel in VALID_INTERACTION_CHANNELS else 0.05
    scores["secondary_lex"] += 0.12 if observation.secondary_products else 0.04
    scores["detector_lex"] += 0.14 if observation.detector_signature else 0.04
    scores["uncertainty_lex"] += 0.10 if reason_codes else 0.04
    scores["metaphor_lex"] += 0.18 if "metaphor_as_physics" in reason_codes else 0.03
    scores["overclaim_lex"] += 0.18 if set(reason_codes) & (CRITICAL_REJECTION_CODES | CORRECTION_CODES) else 0.03
    return {key: round(_clamp01(value), 8) for key, value in scores.items()}


def _chapter4_lex_metrics(
    lex_scores: Mapping[str, float],
    reason_codes: tuple[str, ...],
    d_l_lex: float,
) -> dict[str, object]:
    normalized = _normalized_distribution(lex_scores)
    sorted_values = sorted(normalized.values(), reverse=True)
    top = sorted_values[0] if sorted_values else 0.0
    second = sorted_values[1] if len(sorted_values) > 1 else 0.0
    m_lex = round(_clamp01(top - second), 8)
    g_lex = round(_clamp01(1.0 - m_lex), 8)
    c_lex = _contradiction_load(reason_codes)
    e_gap = _evidence_gap(reason_codes)
    return {
        "H_lex": _entropy01(normalized),
        "M_lex": m_lex,
        "G_lex": g_lex,
        "C_lex": c_lex,
        "E_gap": e_gap,
        "I_lexicon": round(_clamp01(max(g_lex, c_lex, e_gap)), 8),
        "dL_lex": round(_clamp01(d_l_lex), 8),
        "distribution": normalized,
        "metric_boundary": "lexical_load_only",
    }


def _chapter4_protection_profile(
    observation: NeutrinoObservationInput,
    reason_codes: tuple[str, ...],
    status: DecisionStatus,
    chapter3_profile: Mapping[str, object],
    lex_metrics: Mapping[str, object],
) -> dict[str, object]:
    hard_blocks = [code for code in reason_codes if code in CRITICAL_REJECTION_CODES]
    excluded_payload = _excluded_payload(reason_codes, status)
    approved_for_fnp = status in {DecisionStatus.ACCEPTED, DecisionStatus.ACCEPTED_WITH_PARTITION}
    allowed_payload = {}
    if approved_for_fnp:
        allowed_payload = {
            "event_id": observation.event_id,
            "claim_class": observation.claim_class,
            "source_layer": SOURCE_LAYER,
            "boundary": BOUNDARY,
            "approved_scope": "allowed_payload_only"
            if status is DecisionStatus.ACCEPTED_WITH_PARTITION
            else "full_lexical_payload",
            "chapter3_profile": dict(chapter3_profile),
            "lex_metrics": {
                "H_lex": lex_metrics.get("H_lex"),
                "G_lex": lex_metrics.get("G_lex"),
                "I_lexicon": lex_metrics.get("I_lexicon"),
                "dL_lex": lex_metrics.get("dL_lex"),
            },
        }
    return {
        "ProtectionPacket_neutrino": {
            "simulation_detection_guard": _guard_state(
                reason_codes,
                ("real_detection_claim", "simulation_trace_as_detection", "visible_neutrino_claim"),
            ),
            "flavor_mass_guard": _guard_state(
                reason_codes,
                ("flavor_mass_collapse", "mass_basis_equals_flavor_basis"),
            ),
            "secondary_primary_guard": _guard_state(
                reason_codes,
                ("secondary_response_as_primary_force", "new_force_from_nuclear_activity"),
            ),
            "metaphor_guard": _guard_state(reason_codes, ("metaphor_as_physics",)),
            "speculation_claim_guard": _guard_state(reason_codes, ("speculation_as_physical_conclusion",)),
            "source_trace_guard": _guard_state(
                reason_codes,
                ("missing_source_truth", "missing_source_for_physical_claim"),
            ),
            "hard_block_reason_codes": hard_blocks,
        },
        "SynthiaGuard_neutrino": {
            "approved_for_fnp": approved_for_fnp,
            "approval_scope": "allowed_payload_only"
            if status is DecisionStatus.ACCEPTED_WITH_PARTITION
            else ("none" if not approved_for_fnp else "full_lexical_payload"),
            "allowed_payload": allowed_payload,
            "excluded_payload": excluded_payload,
        },
    }


def _excluded_payload(reason_codes: tuple[str, ...], status: DecisionStatus) -> dict[str, object]:
    excluded: dict[str, object] = {}
    if "metaphor_as_physics" in reason_codes:
        excluded["metaphor_payload"] = "conceptual_language_only"
    if "speculation_as_physical_conclusion" in reason_codes:
        excluded["speculative_physics_claim"] = "requires_correction_before_fnp"
    if status in {DecisionStatus.CORRECTED, DecisionStatus.SUSPENDED, DecisionStatus.REJECTED}:
        excluded["blocked_reason_codes"] = list(reason_codes)
    return excluded


def _guard_state(reason_codes: tuple[str, ...], watched_codes: tuple[str, ...]) -> dict[str, object]:
    matched = [code for code in watched_codes if code in reason_codes]
    if any(code in CRITICAL_REJECTION_CODES for code in matched):
        action = "block"
    elif any(code in SUSPENSION_CODES for code in matched):
        action = "hold"
    elif any(code in CORRECTION_CODES for code in matched):
        action = "correct"
    elif matched:
        action = "partition"
    else:
        action = "pass"
    return {"action": action, "reason_codes": matched}


def _chapter5_guard_state(
    reason_codes: tuple[str, ...],
    status: DecisionStatus,
    allowed_payload: Mapping[str, object],
    carrier_family: str,
) -> dict[str, object]:
    reason_set = set(reason_codes)
    can_request = (
        status in {DecisionStatus.ACCEPTED, DecisionStatus.ACCEPTED_WITH_PARTITION}
        and bool(allowed_payload)
        and carrier_family in CHAPTER5_CARRIER_FAMILIES
        and not reason_set & (CRITICAL_REJECTION_CODES | CORRECTION_CODES | SUSPENSION_CODES)
    )
    if can_request:
        action = "request_fnp_validation"
    elif status is DecisionStatus.REJECTED:
        action = "block"
    elif status is DecisionStatus.CORRECTED:
        action = "correct"
    else:
        action = "hold"
    return {
        "action": action,
        "approved_for_fnp_intake": can_request,
        "reason_codes": list(reason_codes),
    }


def _chapter5_requested(observation: NeutrinoObservationInput) -> bool:
    raw = observation.raw_payload
    if raw.get("chapter5_enabled") is True:
        return True
    if isinstance(raw.get("carrier_request"), Mapping):
        return True
    return _contains_any(observation.text, ("chapter5", "chapter 5", "e_fnp_neutrino", "carrier_request"))


def _chapter7_requested(observation: NeutrinoObservationInput) -> bool:
    raw = observation.raw_payload
    if raw.get("chapter7_enabled") is True:
        return True
    if isinstance(raw.get("chapter7_synthia_reading"), Mapping):
        return True
    return _contains_any(observation.text, ("chapter7", "chapter 7", "chapter7_transition_profile"))


def _chapter8_requested(observation: NeutrinoObservationInput) -> bool:
    raw = observation.raw_payload
    if raw.get("chapter8_enabled") is True:
        return True
    if isinstance(raw.get("chapter8_run_request"), Mapping):
        return True
    return _contains_any(observation.text, ("chapter8", "chapter 8", "first run", "run_status"))


def _chapter9_requested(observation: NeutrinoObservationInput) -> bool:
    raw = observation.raw_payload
    if raw.get("chapter9_enabled") is True:
        return True
    if isinstance(raw.get("chapter9_source_registry"), Mapping):
        return True
    if isinstance(raw.get("chapter9_experiment_choice"), Mapping):
        return True
    return _contains_any(
        observation.text,
        ("chapter9", "chapter 9", "t2k-like", "t2k_like", "central experiment"),
    )


def _chapter10_requested(observation: NeutrinoObservationInput) -> bool:
    raw = observation.raw_payload
    if raw.get("chapter10_enabled") is True:
        return True
    if isinstance(raw.get("chapter10_source_registry"), Mapping):
        return True
    if isinstance(raw.get("chapter10_container"), Mapping):
        return True
    if isinstance(raw.get("chapter10_simulated_event"), Mapping):
        return True
    if isinstance(raw.get("chapter10_run_contract"), Mapping):
        return True
    return _contains_any(
        observation.text,
        (
            "chapter10",
            "chapter 10",
            "chamber_10",
            "eventcontainer_10",
            "simulatedneutrinoevent_10",
            "runcontract_10",
        ),
    )


def _chapter11_requested(observation: NeutrinoObservationInput) -> bool:
    raw = observation.raw_payload
    if raw.get("chapter11_enabled") is True:
        return True
    if isinstance(raw.get("chapter11_passage_contract"), Mapping):
        return True
    if isinstance(raw.get("chapter11_injection_packet"), Mapping):
        return True
    if isinstance(raw.get("SynthiaReading_11"), Mapping):
        return True
    return False


def _chapter12_requested(observation: NeutrinoObservationInput) -> bool:
    raw = observation.raw_payload
    return raw.get("chapter12_enabled") is True or isinstance(raw.get("chapter12_validation_contract"), Mapping)


def _chapter9_source_ids(payload: Mapping[str, Any]) -> list[str]:
    registry = payload.get("chapter9_source_registry")
    if not isinstance(registry, Mapping):
        return []
    raw_ids = registry.get("source_ids", registry.get("sources", []))
    if isinstance(raw_ids, Mapping):
        raw_ids = raw_ids.keys()
    if not isinstance(raw_ids, (list, tuple, set)):
        return []
    return [str(item).strip() for item in raw_ids if str(item).strip()]


def _chapter9_experiment_choice(payload: Mapping[str, Any]) -> Mapping[str, object]:
    choice = payload.get("chapter9_experiment_choice")
    return choice if isinstance(choice, Mapping) else {}


def _chapter10_source_ids(payload: Mapping[str, Any]) -> list[str]:
    registry = payload.get("chapter10_source_registry")
    if not isinstance(registry, Mapping):
        return []
    raw_ids = registry.get("source_ids", registry.get("sources", []))
    if isinstance(raw_ids, Mapping):
        raw_ids = raw_ids.keys()
    if not isinstance(raw_ids, (list, tuple, set)):
        return []
    return [str(item).strip() for item in raw_ids if str(item).strip()]


def _chapter10_container(payload: Mapping[str, Any]) -> Mapping[str, object]:
    container = payload.get("chapter10_container")
    return container if isinstance(container, Mapping) else {}


def _chapter10_event(payload: Mapping[str, Any]) -> Mapping[str, object]:
    event = payload.get("chapter10_simulated_event")
    return event if isinstance(event, Mapping) else {}


def _chapter10_run_contract(payload: Mapping[str, Any]) -> Mapping[str, object]:
    contract = payload.get("chapter10_run_contract")
    return contract if isinstance(contract, Mapping) else {}


def _chapter11_passage_contract(payload: Mapping[str, Any]) -> Mapping[str, object]:
    contract = payload.get("chapter11_passage_contract")
    return contract if isinstance(contract, Mapping) else {}


def _chapter11_injection_packet(payload: Mapping[str, Any]) -> Mapping[str, object]:
    packet = payload.get("chapter11_injection_packet")
    return packet if isinstance(packet, Mapping) else {}


def _chapter12_validation_contract(payload: Mapping[str, Any]) -> Mapping[str, object]:
    contract = payload.get("chapter12_validation_contract")
    return contract if isinstance(contract, Mapping) else {}


def _chapter11_common_controls(injection: Mapping[str, object]) -> Mapping[str, object]:
    controls = injection.get("CommonPathControls") if isinstance(injection, Mapping) else None
    if not isinstance(controls, Mapping):
        controls = injection.get("common_path_controls") if isinstance(injection, Mapping) else None
    return controls if isinstance(controls, Mapping) else {}


def _chapter11_path_event(
    injection: Mapping[str, object],
    key: str,
    expected_path_id: str,
) -> Mapping[str, object]:
    if not isinstance(injection, Mapping):
        return {}
    direct = injection.get(key)
    if isinstance(direct, Mapping):
        return direct
    paths = injection.get("paths")
    if isinstance(paths, Mapping):
        candidate = paths.get(key) or paths.get(expected_path_id)
        if isinstance(candidate, Mapping):
            return candidate
    if isinstance(paths, list):
        for item in paths:
            if not isinstance(item, Mapping):
                continue
            if str(item.get("path_id", "")).strip() == expected_path_id:
                return item
    return {}


def _chapter11_path_container_mismatch(path_a: Mapping[str, object], path_b: Mapping[str, object]) -> bool:
    container_a = str(path_a.get("container_id", "")).strip()
    container_b = str(path_b.get("container_id", "")).strip()
    return not container_a or not container_b or container_a != container_b


def _chapter11_path_route_mismatch(path_a: Mapping[str, object], path_b: Mapping[str, object]) -> bool:
    route_a = str(path_a.get("admission_route", "")).strip()
    route_b = str(path_b.get("admission_route", "")).strip()
    expected = "container_to_synthia_to_fnp"
    return route_a != expected or route_b != expected or route_a != route_b


def _contains_forbidden_chapter11_output(value: object) -> bool:
    if isinstance(value, Mapping):
        return any(
            str(key) in CHAPTER11_FORBIDDEN_OUTPUT_KEYS or _contains_forbidden_chapter11_output(item)
            for key, item in value.items()
        )
    if isinstance(value, list):
        return any(_contains_forbidden_chapter11_output(item) for item in value)
    return False


def _contains_forbidden_chapter12_output(value: object) -> bool:
    if isinstance(value, Mapping):
        for key, item in value.items():
            if str(key) in CHAPTER12_FORBIDDEN_OUTPUT_KEYS:
                return True
            if _contains_forbidden_chapter12_output(item):
                return True
    elif isinstance(value, list):
        return any(_contains_forbidden_chapter12_output(item) for item in value)
    return False


def _chapter7_metric(observation: NeutrinoObservationInput, key: str) -> float | None:
    supplied = observation.raw_payload.get("chapter7_synthia_reading")
    if not isinstance(supplied, Mapping):
        return None
    return _optional_float(supplied.get(key))


def _chapter6_vector_profile_preview(observation: NeutrinoObservationInput) -> Mapping[str, object]:
    supplied = _supplied_chapter6_vector(observation.raw_payload)
    if supplied is not None:
        return {"I_neutrino_vec": supplied}
    if observation.claim_class == "simulation" and observation.interaction_channel in VALID_INTERACTION_CHANNELS:
        return {"I_neutrino_vec": {"vector_status": "will_be_assembled"}}
    return {}


def _supplied_chapter6_vector(payload: Mapping[str, Any]) -> Mapping[str, object] | None:
    direct = payload.get("I_neutrino_vec")
    if isinstance(direct, Mapping):
        return direct
    profile = payload.get("chapter6_vector_profile")
    if isinstance(profile, Mapping):
        vector = profile.get("I_neutrino_vec")
        if isinstance(vector, Mapping):
            return vector
    return None


def _missing_chapter6_carriers(vector: Mapping[str, object]) -> list[str]:
    carriers = vector.get("carriers")
    if isinstance(carriers, Mapping):
        return [name for name in CHAPTER6_REQUIRED_CARRIERS if name not in carriers or not carriers.get(name)]
    return [name for name in CHAPTER6_REQUIRED_CARRIERS if name not in vector or not vector.get(name)]


def _chapter6_unknown_fields(observation: NeutrinoObservationInput) -> list[str]:
    unknown: list[str] = []
    if not observation.source_truth:
        unknown.append("I_source.source_truth")
    if observation.created_flavor == "unknown":
        unknown.append("I_flavor.created_flavor")
    if not observation.mass_basis:
        unknown.append("I_mass.mass_basis")
    if observation.distance_km is None:
        unknown.append("I_phase.distance")
    if observation.energy_gev is None:
        unknown.append("I_phase.energy")
    if not observation.interaction_channel:
        unknown.append("I_interaction.channel")
    if not observation.secondary_products:
        unknown.append("I_secondary.products")
    if not observation.detector_signature:
        unknown.append("I_detector.projection")
    return unknown


def _carrier_family(carrier_request: object) -> str:
    if not isinstance(carrier_request, Mapping):
        return ""
    return _normalize_token(carrier_request.get("carrier_family", carrier_request.get("family", "")))


def _nested_mapping(payload: Mapping[str, object], *path: str) -> Mapping[str, object]:
    current: object = payload
    for key in path:
        if not isinstance(current, Mapping):
            return {}
        current = current.get(key)
    return current if isinstance(current, Mapping) else {}


def _normalized_distribution(scores: Mapping[str, float]) -> dict[str, float]:
    total = sum(max(0.0, float(value)) for value in scores.values())
    if total <= 0.0:
        return {key: 0.0 for key in scores}
    return {key: round(max(0.0, float(value)) / total, 8) for key, value in scores.items()}


def _entropy01(distribution: Mapping[str, float]) -> float:
    values = [float(value) for value in distribution.values() if float(value) > 0.0]
    if not values or len(values) == 1:
        return 0.0
    entropy = -sum(value * math.log(value, 2) for value in values)
    max_entropy = math.log(len(distribution), 2)
    return round(_clamp01(entropy / max_entropy), 8)


def _dominant_score(scores: Mapping[str, float]) -> tuple[str, float]:
    if not scores:
        return "none", 0.0
    key = max(scores, key=lambda item: scores[item])
    return key, round(float(scores[key]), 8)


def _contradiction_load(reason_codes: tuple[str, ...]) -> float:
    if not reason_codes:
        return 0.0
    load = 0.0
    load += 0.55 * bool(set(reason_codes) & CRITICAL_REJECTION_CODES)
    load += 0.35 * bool(set(reason_codes) & CORRECTION_CODES)
    load += 0.15 * bool(set(reason_codes) & PARTITION_CODES)
    return round(_clamp01(load), 8)


def _uncertainty_load(reason_codes: tuple[str, ...]) -> float:
    if not reason_codes:
        return 0.12
    load = 0.18
    load += 0.40 * bool(set(reason_codes) & SUSPENSION_CODES)
    load += 0.10 * bool(set(reason_codes) & PARTITION_CODES)
    load += min(0.20, 0.02 * len(reason_codes))
    return round(_clamp01(load), 8)


def _evidence_gap(reason_codes: tuple[str, ...]) -> float:
    if not (set(reason_codes) & SUSPENSION_CODES):
        return 0.0
    return round(_clamp01(0.30 + 0.08 * len(set(reason_codes) & SUSPENSION_CODES)), 8)


def _normalize_interaction_channel(value: object) -> str:
    raw = str(value or "").strip()
    lowered = raw.lower().replace("-", "_").replace(" ", "_")
    if lowered in {"weak_cc", "charged_current", "weak_charged_current"}:
        return "weak_CC"
    if lowered in {"weak_nc", "neutral_current", "weak_neutral_current"}:
        return "weak_NC"
    return raw


def _normalize_flavor(value: object) -> str:
    raw = str(value or "").strip().lower().replace("-", "_").replace(" ", "_")
    if raw in {"", "unknown", "unk", "symbolic"}:
        return "unknown"
    if raw in {"e", "electron", "electron_neutrino", "nu_e", "ν_e"}:
        return "nu_e"
    if raw in {"mu", "muon", "muon_neutrino", "nu_mu", "ν_mu"}:
        return "nu_mu"
    if raw in {"tau", "tau_neutrino", "nu_tau", "ν_tau"}:
        return "nu_tau"
    return raw


def _invalid_declared_flavor(observation: NeutrinoObservationInput) -> bool:
    if observation.created_flavor in VALID_FLAVORS:
        return False
    return observation.flavor_status not in {"unknown", "symbolic", "suspended"}


def _normalize_flavor_basis(payload: Mapping[str, Any]) -> dict[str, float]:
    basis = payload.get("flavor_basis")
    if isinstance(basis, Mapping):
        return _normalize_basis(basis, FLAVOR_KEYS, _flavor_basis_key)
    created = _normalize_flavor(payload.get("created_flavor"))
    if created == "nu_e":
        return {"e": 1.0, "mu": 0.0, "tau": 0.0}
    if created == "nu_mu":
        return {"e": 0.0, "mu": 1.0, "tau": 0.0}
    if created == "nu_tau":
        return {"e": 0.0, "mu": 0.0, "tau": 1.0}
    return {}


def _normalize_mass_basis(payload: Mapping[str, Any]) -> dict[str, float]:
    basis = payload.get("mass_basis")
    if isinstance(basis, Mapping):
        return _normalize_basis(basis, MASS_KEYS, _mass_basis_key)
    return {}


def _normalize_basis(
    basis: Mapping[str, object],
    expected_keys: tuple[str, ...],
    key_normalizer: Any,
) -> dict[str, float]:
    values = {key: 0.0 for key in expected_keys}
    for raw_key, raw_value in basis.items():
        key = key_normalizer(raw_key)
        if key in values:
            values[key] += max(0.0, _optional_float(raw_value) or 0.0)
    total = sum(values.values())
    if total <= 0.0:
        return {}
    return {key: round(value / total, 8) for key, value in values.items()}


def _flavor_basis_key(value: object) -> str:
    raw = str(value).strip().lower().replace("-", "_").replace(" ", "_")
    if raw in {"e", "nu_e", "electron", "electron_neutrino"}:
        return "e"
    if raw in {"mu", "nu_mu", "muon", "muon_neutrino"}:
        return "mu"
    if raw in {"tau", "nu_tau", "tau_neutrino"}:
        return "tau"
    return raw


def _mass_basis_key(value: object) -> str:
    raw = str(value).strip().lower().replace("-", "_").replace(" ", "_")
    if raw in {"1", "nu1", "nu_1", "m1", "m_1"}:
        return "nu_1"
    if raw in {"2", "nu2", "nu_2", "m2", "m_2"}:
        return "nu_2"
    if raw in {"3", "nu3", "nu_3", "m3", "m_3"}:
        return "nu_3"
    return raw


def _basis_vectors_equal(left: Mapping[str, float], right: Mapping[str, float]) -> bool:
    if not left or not right:
        return False
    left_values = list(left.values())
    right_values = list(right.values())
    if len(left_values) != len(right_values):
        return False
    return all(abs(float(a) - float(b)) < 1e-12 for a, b in zip(left_values, right_values))


def _secondary_products(payload: Mapping[str, Any]) -> list[str]:
    value = payload.get("secondary_products", payload.get("I_secondary", []))
    if isinstance(value, str):
        return [_normalize_token(value)]
    if isinstance(value, list):
        return [_normalize_token(item) for item in value if str(item).strip()]
    return []


def _detector_projection_status(observation: NeutrinoObservationInput) -> str:
    if not observation.detector_signature:
        return "unknown"
    if _contains_any(observation.detector_signature.lower(), ("none", "no_direct_trace")):
        return "none"
    return "indirect"


def _normalize_token(value: object) -> str:
    return str(value).strip().lower().replace(" ", "_").replace("-", "_")


def _optional_float(value: object) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number):
        return None
    return number


def _payload_text(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, ensure_ascii=True, default=str).lower()


def _contains_any(text: str, patterns: tuple[str, ...]) -> bool:
    return any(pattern.lower() in text for pattern in patterns)


def _numeric_equal(left: object, right: object) -> bool:
    try:
        left_number = float(left)
        right_number = float(right)
    except (TypeError, ValueError):
        return False
    return math.isfinite(left_number) and math.isfinite(right_number) and abs(left_number - right_number) < 1e-12


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


__all__ = [
    "BOUNDARY",
    "REFUSAL_CATEGORIES",
    "SCHEMA_VERSION",
    "DecisionStatus",
    "LexPacketNeutrino",
    "NeutrinoObservationInput",
    "RefusalPacket",
    "classify_neutrino_observation",
]
