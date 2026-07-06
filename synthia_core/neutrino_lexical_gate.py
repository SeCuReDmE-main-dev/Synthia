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
            "guardrail_categories": list(REFUSAL_CATEGORIES),
            "metric_definition": "dL_lex is lexical admission load only; downstream FNP friction is separate.",
        }


def classify_neutrino_observation(payload: Mapping[str, Any]) -> dict[str, object]:
    """Return the public-safe Synthia lexical admission contract."""

    observation = NeutrinoObservationInput.from_mapping(payload)
    reason_codes = tuple(_reason_codes(observation))
    status = _decision_status(reason_codes)
    adm_lex = status in {DecisionStatus.ACCEPTED, DecisionStatus.ACCEPTED_WITH_PARTITION}
    d_l_lex = _d_l_lex(reason_codes)
    chapter3_profile = _chapter3_profile(observation, reason_codes)
    chapter4_profile = _chapter4_profile(observation, reason_codes, status, d_l_lex, chapter3_profile)
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


def _d_l_lex(reason_codes: tuple[str, ...]) -> float:
    if not reason_codes:
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
