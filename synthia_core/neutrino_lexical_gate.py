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
    if _contains_any(text, ("choice", "choose", "chooses", "intention", "decides", "decide")):
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
