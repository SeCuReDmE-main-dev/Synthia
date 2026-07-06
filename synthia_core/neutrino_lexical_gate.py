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
    "decay_as_internal_flavor_mechanism",
    "fusion_as_internal_flavor_mechanism",
    "choice_or_intention_language",
    "dL_lex_equals_dF",
    "I_lexicon_equals_i_fractal",
    "missing_source_truth",
    "missing_interaction_channel",
    "detector_trace_confused_with_particle",
    "candidate_confused_with_proof",
)

CRITICAL_REJECTION_CODES = {
    "real_detection_claim",
    "strong_primary_interaction_claim",
    "dL_lex_equals_dF",
    "I_lexicon_equals_i_fractal",
    "detector_trace_confused_with_particle",
    "candidate_confused_with_proof",
}
CORRECTION_CODES = {
    "literal_mass_gain_loss_claim",
    "decay_as_internal_flavor_mechanism",
    "fusion_as_internal_flavor_mechanism",
    "choice_or_intention_language",
}
SUSPENSION_CODES = {"missing_source_truth", "missing_interaction_channel"}
VALID_INTERACTION_CHANNELS = {"weak_CC", "weak_NC"}


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
            "guardrail_categories": list(REFUSAL_CATEGORIES),
            "metric_definition": "dL_lex is lexical admission load only; downstream FNP friction is separate.",
        }


def classify_neutrino_observation(payload: Mapping[str, Any]) -> dict[str, object]:
    """Return the public-safe Synthia lexical admission contract."""

    observation = NeutrinoObservationInput.from_mapping(payload)
    reason_codes = tuple(_reason_codes(observation))
    status = _decision_status(reason_codes)
    adm_lex = status in {DecisionStatus.ACCEPTED, DecisionStatus.ACCEPTED_WITH_PARTITION}
    refusal_packet = RefusalPacket(
        blocked=not adm_lex,
        reason_codes=reason_codes,
        next_action=_next_action(status),
        human_message=_human_message(status),
    )
    packet = LexPacketNeutrino(
        event_id=observation.event_id,
        Adm_lex=adm_lex,
        dL_lex=_d_l_lex(reason_codes),
        decision_status=status,
        refusal_packet=refusal_packet,
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
        ("detector trace is the neutrino", "trace equals neutrino", "secondary particle is the neutrino"),
    ):
        reasons.append("detector_trace_confused_with_particle")

    if _contains_any(
        text,
        ("candidate is proof", "candidate proves", "proof of mapped neutrino", "i_fractal_candidate proves"),
    ):
        reasons.append("candidate_confused_with_proof")

    return [code for code in REFUSAL_CATEGORIES if code in set(reasons)]


def _decision_status(reason_codes: tuple[str, ...]) -> DecisionStatus:
    reason_set = set(reason_codes)
    if reason_set & CRITICAL_REJECTION_CODES:
        return DecisionStatus.REJECTED
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


def _normalize_interaction_channel(value: object) -> str:
    raw = str(value or "").strip()
    lowered = raw.lower().replace("-", "_").replace(" ", "_")
    if lowered in {"weak_cc", "charged_current", "weak_charged_current"}:
        return "weak_CC"
    if lowered in {"weak_nc", "neutral_current", "weak_neutral_current"}:
        return "weak_NC"
    return raw


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
