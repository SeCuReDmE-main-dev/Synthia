"""Additive Chapter-14 threshold gate built on the stable neutrino lexical gate."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any, Mapping

from .neutrino_lexical_gate import classify_neutrino_observation

SCHEMA_VERSION = "chapter14.threshold_public_safe.v1"
CARRIER_NAMES = (
    "local_matching", "aperiodicity", "inflation_deflation", "fivefold_orientation",
    "tile_frequency", "adjacency", "substitution_depth", "phason_susceptibility",
    "defect_density", "scale_transfer",
)
FORBIDDEN_FIELDS = {"D_f", "D_f_hat", "dF", "i_fractal", "i_fractal_candidate"}


def classify_chapter14_threshold(payload: Mapping[str, Any]) -> dict[str, object]:
    base = classify_neutrino_observation(payload)
    contract = payload.get("chapter14_threshold_contract")
    reasons: list[str] = []
    rejected = False
    if not isinstance(contract, Mapping):
        reasons.append("chapter14_missing_threshold_contract")
        contract = {}

    sources = contract.get("sources")
    if not isinstance(sources, list) or len(sources) < 2 or any(not str(x).strip() for x in sources):
        reasons.append("chapter14_missing_primary_sources")
    packet = contract.get("penrose_rule_packet")
    if not isinstance(packet, Mapping) or not packet.get("rules") or not packet.get("provenance"):
        reasons.append("chapter14_incomplete_penrose_rule_packet")
    carriers = contract.get("i_quasicrystal_vec")
    carrier_rows = carriers.get("carriers") if isinstance(carriers, Mapping) else None
    names = [str(x.get("name")) for x in carrier_rows if isinstance(x, Mapping)] if isinstance(carrier_rows, list) else []
    if len(names) != 10 or set(names) != set(CARRIER_NAMES) or len(set(names)) != 10:
        reasons.append("chapter14_invalid_ten_carrier_vector")
    if isinstance(carrier_rows, list):
        for row in carrier_rows:
            if not isinstance(row, Mapping) or not _bounded(row.get("tension")) or not _positive(row.get("weight")):
                reasons.append("chapter14_invalid_carrier_value")
                break
    phason = contract.get("phason_transition")
    if not isinstance(phason, Mapping) or not all(k in phason for k in ("state_before", "state_after", "scale", "uncertainty")):
        reasons.append("chapter14_unbounded_phason_transition")
    elif not _bounded(phason.get("uncertainty")):
        reasons.append("chapter14_unbounded_phason_transition")
    limits = contract.get("limits")
    if not isinstance(limits, list) or not limits:
        reasons.append("chapter14_missing_claim_limits")

    claim_flags = contract.get("claim_flags") if isinstance(contract.get("claim_flags"), Mapping) else {}
    for flag, code in (
        ("substrate_as_established_fact", "chapter14_substrate_as_fact"),
        ("real_detection_claim", "chapter14_real_detection_claim"),
        ("penrose_as_physical_proof", "chapter14_penrose_as_physical_proof"),
        ("quasicrystal_proves_neutrino", "chapter14_quasicrystal_proves_neutrino"),
        ("biological_validation_claim", "chapter14_biological_claim_in_core"),
    ):
        if claim_flags.get(flag) is True:
            reasons.append(code)
            rejected = True

    if _contains_forbidden(contract):
        reasons.append("chapter14_fnp_output_in_synthia")
        rejected = True
    if base.get("Adm_lex") is not True:
        reasons.append("chapter14_base_lexical_gate_not_admitted")

    reasons = list(dict.fromkeys(reasons))
    if rejected:
        status = "rejected"
    elif reasons:
        status = "suspended"
    else:
        status = "ready_for_fnp_threshold_calculation"
    admitted = status == "ready_for_fnp_threshold_calculation"
    profile = {
        "profile_version": SCHEMA_VERSION,
        "chapter14_status": status,
        "source_count": len(sources) if isinstance(sources, list) else 0,
        "carrier_policy": {"exact_ten_carrier_set": set(names) == set(CARRIER_NAMES) and len(names) == 10, "provided_count": len(names)},
        "SynthiaReading_14": {"approved_for_fnp_threshold_calculation": admitted, "ready_for_FNP": "true_after_Synthia" if admitted else "false", "reason_codes": reasons},
        "capability_boundary": {"maximum_proof_state": "P2_internal_repeatability", "physical_model_validated": False, "substrate_validated": False, "simulation_is_detection": False},
        "boundary": {"synthia_role": "chapter14 source object and lexical gate only", "no_fractal_computation": True},
    }
    result = deepcopy(base)
    result["LexPacket_neutrino"]["chapter14_threshold_profile"] = profile
    result["chapter14_threshold_profile"] = profile
    result["Adm_lex"] = admitted
    result["decision"] = {"status": "accepted" if admitted else status, "reason_codes": reasons, "next_action": "admit_to_fnp" if admitted else "hold_for_review" if status == "suspended" else "block_fnp"}
    result["claim_boundary"] = "threshold simulation only; Penrose rules are not a physical substrate; simulation is not detection"
    return result


def classify_chapter14_threshold_from_file(path: str | Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError("chapter14 input must contain a JSON object")
    return classify_chapter14_threshold(payload)


def _bounded(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and 0.0 <= float(value) <= 1.0


def _positive(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and float(value) > 0.0


def _contains_forbidden(value: object) -> bool:
    if isinstance(value, Mapping):
        return bool(FORBIDDEN_FIELDS & set(map(str, value))) or any(_contains_forbidden(x) for x in value.values())
    if isinstance(value, list):
        return any(_contains_forbidden(x) for x in value)
    return False
