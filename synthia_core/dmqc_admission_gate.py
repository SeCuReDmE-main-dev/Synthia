"""Deterministic DMQC provenance and claim admission gate.

Synthia validates whether a scientific-result packet may proceed to FNP-QNN.
It does not calculate physical, crystal, or fractal descriptors.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from typing import Any, Mapping


INPUT_SCHEMA_VERSION = "synthia.dmqc_admission_input.v1"
OUTPUT_SCHEMA_VERSION = "synthia.dmqc_admission.v1"
POLICY_VERSION = "synthia.dmqc_policy.v1"
SOURCE_LAYER = "provenance_and_claim_gate"
LEXICAL_HIERARCHY = "I -> I_system^S -> H_lex -> G_lex -> I_lexicon"

FORBIDDEN_FNP_FIELDS = frozenset(
    {
        "D_crystal",
        "dC",
        "i_crystal",
        "D_f",
        "D_f_hat",
        "dF",
        "i_fractal",
        "i_fractal_candidate",
    }
)

BASE_FORBIDDEN_CLAIMS = (
    "validated_material_discovery",
    "validated_dft",
    "experimental_crystal_growth",
    "quantum_hardware_result",
)

PROHIBITED_CLAIM_CODES = {
    "validated_material_discovery": "dmqc_validated_material_claim_without_evidence",
    "validated_dft": "dmqc_validated_material_claim_without_evidence",
    "experimental_crystal_growth": "dmqc_simulation_claimed_as_experiment",
    "validated_crystal_growth": "dmqc_simulation_claimed_as_experiment",
    "quantum_hardware_result": "dmqc_quantum_hardware_claim_without_backend_evidence",
    "quantum_advantage": "dmqc_quantum_hardware_claim_without_backend_evidence",
}

HARD_REJECTION_CODES = frozenset(
    {
        "dmqc_invalid_input_schema",
        "dmqc_impossible_unit",
        "dmqc_simulation_claimed_as_experiment",
        "dmqc_validated_material_claim_without_evidence",
        "dmqc_quantum_hardware_claim_without_backend_evidence",
        "dmqc_fnp_output_in_synthia",
        "dmqc_raw_reference_hash_mismatch",
    }
)

SUSPENSION_CODES = frozenset(
    {
        "dmqc_missing_case_identity",
        "dmqc_missing_source_type",
        "dmqc_missing_method",
        "dmqc_missing_provenance",
        "dmqc_missing_software_version",
        "dmqc_missing_uncertainty_model",
        "dmqc_incomplete_quality_flags",
        "dmqc_missing_licence_or_access",
        "dmqc_recoverable_source_contradiction",
        "dmqc_missing_fractal_measurement_metadata",
    }
)

SAFE_CLAIM_MAP = {
    "synthetic_case_is_eligible_for_crystal_route": "synthetic_case_may_be_processed_by_fnp",
}

ALLOWED_UNITS = {
    "formation_energy": {"eV/atom"},
    "growth_rate": {"normalized_benchmark_unit"},
    "branch_drift": {"dimensionless"},
    "surface_roughness": {"dimensionless"},
    "defect_density": {"dimensionless"},
}

_SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")


def evaluate_dmqc_admission(payload: Mapping[str, Any]) -> dict[str, object]:
    """Evaluate a DMQC input without calculating downstream FNP descriptors."""

    if not isinstance(payload, Mapping):
        raise ValueError("DMQC admission input must be a JSON object")

    reasons = _reason_codes(payload)
    hard_reasons = [code for code in reasons if code in HARD_REJECTION_CODES]
    suspended_reasons = [code for code in reasons if code in SUSPENSION_CODES]

    if hard_reasons:
        status = "rejected"
        normalized_state = "rejected"
        next_action = "block_fnp"
    elif suspended_reasons:
        status = "suspended"
        normalized_state = "suspended"
        next_action = "hold_for_review"
    else:
        status = "accepted"
        normalized_state = "admitted"
        next_action = "route_to_fnp"

    components = _evidence_profile(payload, reasons)
    tif = _experimental_tif(components)
    ready_for_fnp = status == "accepted"
    requested_claims = _string_list(payload.get("requested_claims"))
    permitted_claims = (
        sorted({SAFE_CLAIM_MAP[claim] for claim in requested_claims if claim in SAFE_CLAIM_MAP})
        if ready_for_fnp
        else []
    )
    forbidden_claims = sorted(set(BASE_FORBIDDEN_CLAIMS) | set(requested_claims) - set(SAFE_CLAIM_MAP))
    raw_reference = payload.get("raw_result_reference")
    evidence_refs = []
    if isinstance(raw_reference, Mapping) and str(raw_reference.get("uri", "")).strip():
        evidence_refs.append(str(raw_reference["uri"]).strip())

    result: dict[str, object] = {
        "schema_version": OUTPUT_SCHEMA_VERSION,
        "case_id": str(payload.get("case_id", "")).strip(),
        "source_layer": SOURCE_LAYER,
        "decision": {
            "status": status,
            "normalized_state": normalized_state,
            "next_action": next_action,
            "reason_codes": reasons,
        },
        "ready_for_fnp": ready_for_fnp,
        "evidence_profile": components,
        "T": tif["T"],
        "I": tif["I"],
        "F": tif["F"],
        "permitted_claims": permitted_claims,
        "forbidden_claims": forbidden_claims,
        "evidence_refs": evidence_refs,
        "reproducibility_status": _reproducibility_status(status, components),
        "policy_version": POLICY_VERSION,
        "boundary": {
            "no_physical_descriptor_computation": True,
            "forbidden_output_fields": sorted(FORBIDDEN_FNP_FIELDS),
            "authority": "traceability_support_under_human_review",
        },
        "lexical_hierarchy": LEXICAL_HIERARCHY,
        "mathematical_status": "experimental_policy_scores_not_canonical_neutrosophic_mathematics",
        "human_review_required": status != "accepted",
    }
    if _contains_forbidden_key(result):
        raise RuntimeError("Synthia DMQC output leaked a forbidden FNP field")
    return result


def canonical_json_bytes(value: object) -> bytes:
    """Return the canonical JSON encoding used for deterministic replay."""

    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def canonical_sha256(value: object) -> str:
    """Hash a JSON-safe value using the benchmark canonical encoding."""

    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _reason_codes(payload: Mapping[str, Any]) -> list[str]:
    reasons: list[str] = []
    if payload.get("schema_version") != INPUT_SCHEMA_VERSION:
        reasons.append("dmqc_invalid_input_schema")
    if _contains_forbidden_key(payload):
        reasons.append("dmqc_fnp_output_in_synthia")
    if not str(payload.get("case_id", "")).strip():
        reasons.append("dmqc_missing_case_identity")
    if not str(payload.get("source_type", "")).strip() or not str(payload.get("domain", "")).strip():
        reasons.append("dmqc_missing_source_type")

    method = payload.get("method")
    if not isinstance(method, Mapping) or not str(method.get("name", "")).strip() or not str(
        method.get("category", "")
    ).strip():
        reasons.append("dmqc_missing_method")

    software = payload.get("software")
    if not isinstance(software, Mapping) or not str(software.get("name", "")).strip() or not str(
        software.get("version", "")
    ).strip():
        reasons.append("dmqc_missing_software_version")

    raw_reference = payload.get("raw_result_reference")
    if (
        not isinstance(raw_reference, Mapping)
        or not str(raw_reference.get("uri", "")).strip()
        or not _SHA256_RE.fullmatch(str(raw_reference.get("sha256", "")).strip())
    ):
        reasons.append("dmqc_raw_reference_hash_mismatch")

    provenance = payload.get("provenance_reference")
    if not isinstance(provenance, Mapping) or any(
        not str(provenance.get(key, "")).strip() for key in ("entity_id", "activity_id", "agent_id")
    ):
        reasons.append("dmqc_missing_provenance")

    units = payload.get("units")
    if not isinstance(units, Mapping):
        reasons.append("dmqc_impossible_unit")
    else:
        for field, allowed in ALLOWED_UNITS.items():
            if str(units.get(field, "")).strip() not in allowed:
                reasons.append("dmqc_impossible_unit")
                break

    uncertainty = payload.get("uncertainty_model")
    if not isinstance(uncertainty, Mapping) or uncertainty.get("declared") is not True or not str(
        uncertainty.get("type", "")
    ).strip():
        reasons.append("dmqc_missing_uncertainty_model")

    quality = payload.get("convergence_or_quality_flags")
    if not isinstance(quality, Mapping) or any(
        quality.get(key) is not True for key in ("schema_valid", "finite_values", "controlled_fixture")
    ):
        reasons.append("dmqc_incomplete_quality_flags")

    licence = payload.get("licence_and_access")
    if not isinstance(licence, Mapping) or not str(licence.get("licence", "")).strip() or not str(
        licence.get("access", "")
    ).strip():
        reasons.append("dmqc_missing_licence_or_access")

    contradictions = payload.get("declared_contradictions")
    if isinstance(contradictions, list) and contradictions:
        reasons.append("dmqc_recoverable_source_contradiction")
    elif contradictions is not None and not isinstance(contradictions, list):
        reasons.append("dmqc_recoverable_source_contradiction")

    requested_claims = _string_list(payload.get("requested_claims"))
    for claim in requested_claims:
        code = PROHIBITED_CLAIM_CODES.get(claim)
        if code:
            reasons.append(code)

    return list(dict.fromkeys(reasons))


def _evidence_profile(payload: Mapping[str, Any], reasons: list[str]) -> dict[str, float]:
    provenance = payload.get("provenance_reference")
    provenance_score = _mapping_completeness(provenance, ("entity_id", "activity_id", "agent_id"))

    quality = payload.get("convergence_or_quality_flags")
    quality_score = _boolean_completeness(quality, ("schema_valid", "finite_values", "controlled_fixture"))

    method = payload.get("method")
    software = payload.get("software")
    raw_reference = payload.get("raw_result_reference")
    reproducibility_checks = (
        _mapping_completeness(method, ("name", "category")),
        _mapping_completeness(software, ("name", "version")),
        float(
            isinstance(raw_reference, Mapping)
            and bool(str(raw_reference.get("uri", "")).strip())
            and bool(_SHA256_RE.fullmatch(str(raw_reference.get("sha256", "")).strip()))
        ),
    )
    reproducibility_score = sum(reproducibility_checks) / len(reproducibility_checks)

    uncertainty = payload.get("uncertainty_model")
    uncertainty_load = 0.2
    if not isinstance(uncertainty, Mapping) or uncertainty.get("declared") is not True:
        uncertainty_load = 0.8

    contradictions = payload.get("declared_contradictions")
    contradiction_count = len(contradictions) if isinstance(contradictions, list) else int(contradictions is not None)
    contradiction_load = min(1.0, 0.35 * contradiction_count)

    suspension_count = sum(code in SUSPENSION_CODES for code in reasons)
    metadata_gap_load = min(1.0, suspension_count / max(1, len(SUSPENSION_CODES)))
    hard_failure_load = float(any(code in HARD_REJECTION_CODES for code in reasons))
    policy_violation_load = float(
        any(
            code
            in {
                "dmqc_simulation_claimed_as_experiment",
                "dmqc_validated_material_claim_without_evidence",
                "dmqc_quantum_hardware_claim_without_backend_evidence",
                "dmqc_fnp_output_in_synthia",
            }
            for code in reasons
        )
    )
    requested_claims = _string_list(payload.get("requested_claims"))
    claim_excess_load = min(
        1.0,
        sum(claim in PROHIBITED_CLAIM_CODES for claim in requested_claims) / max(1, len(requested_claims)),
    )

    return {
        "P": _round01(provenance_score),
        "Q": _round01(quality_score),
        "R": _round01(reproducibility_score),
        "U": _round01(uncertainty_load),
        "C": _round01(contradiction_load),
        "M": _round01(metadata_gap_load),
        "H": _round01(hard_failure_load),
        "V": _round01(policy_violation_load),
        "X": _round01(claim_excess_load),
    }


def _experimental_tif(components: Mapping[str, float]) -> dict[str, float]:
    truth = (
        0.40 * components["P"]
        + 0.30 * components["Q"]
        + 0.30 * components["R"]
    )
    indeterminacy = max(components["U"], components["C"], components["M"])
    falsity_evidence = max(components["H"], components["V"], components["X"])
    return {
        "T": _round01(truth),
        "I": _round01(indeterminacy),
        "F": _round01(falsity_evidence),
    }


def _reproducibility_status(status: str, components: Mapping[str, float]) -> str:
    if status == "rejected":
        return "blocked"
    if status == "suspended" or components["R"] < 1.0:
        return "incomplete_metadata"
    return "deterministic_fixture"


def _mapping_completeness(value: object, keys: tuple[str, ...]) -> float:
    if not isinstance(value, Mapping):
        return 0.0
    return sum(bool(str(value.get(key, "")).strip()) for key in keys) / len(keys)


def _boolean_completeness(value: object, keys: tuple[str, ...]) -> float:
    if not isinstance(value, Mapping):
        return 0.0
    return sum(value.get(key) is True for key in keys) / len(keys)


def _contains_forbidden_key(value: object) -> bool:
    if isinstance(value, Mapping):
        if FORBIDDEN_FNP_FIELDS & {str(key) for key in value}:
            return True
        return any(_contains_forbidden_key(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return any(_contains_forbidden_key(item) for item in value)
    return False


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return sorted({str(item).strip() for item in value if str(item).strip()})


def _round01(value: float) -> float:
    number = float(value)
    if not math.isfinite(number):
        return 1.0
    return round(max(0.0, min(1.0, number)), 8)


__all__ = [
    "BASE_FORBIDDEN_CLAIMS",
    "FORBIDDEN_FNP_FIELDS",
    "INPUT_SCHEMA_VERSION",
    "LEXICAL_HIERARCHY",
    "OUTPUT_SCHEMA_VERSION",
    "POLICY_VERSION",
    "canonical_json_bytes",
    "canonical_sha256",
    "evaluate_dmqc_admission",
]
