"""Plithogenic set operators for Synthia phase 14."""

from __future__ import annotations

from dataclasses import dataclass
from math import fabs
from typing import Iterable

from .plithogenic import PlithogenicIProfile, TIF, clamp01
from .safety import HIERARCHY


PLITHOGENIC_SET_SOURCE_ID = "nss.plithogenic_set_extension"
PLITHOGENIC_SET_SOURCE_URL = "https://fs.unm.edu/NSS/PlithogenicSetAnExtensionOfCrisp.pdf"


@dataclass(frozen=True)
class PlithogenicAttributeValue:
    name: str
    value: str
    T: float
    I: float
    F: float
    weight: float = 1.0
    dominant: bool = False

    @classmethod
    def from_raw(cls, raw: object, index: int) -> "PlithogenicAttributeValue":
        if not isinstance(raw, dict):
            raise ValueError("each plithogenic attribute must be a JSON object")
        return cls(
            name=str(raw.get("name", f"attribute_{index + 1}")),
            value=str(raw.get("value", "")),
            T=float(raw.get("T", 0.0)),
            I=float(raw.get("I", 0.0)),
            F=float(raw.get("F", 0.0)),
            weight=float(raw.get("weight", 1.0)),
            dominant=bool(raw.get("dominant", False)),
        )

    def tif(self) -> TIF:
        return TIF(T=clamp01(self.T), I=clamp01(self.I), F=clamp01(self.F))

    def as_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "value": self.value,
            "T": self.T,
            "I": self.I,
            "F": self.F,
            "weight": self.weight,
            "dominant": self.dominant,
        }


@dataclass(frozen=True)
class PlithogenicSetProfile:
    attributes: tuple[PlithogenicAttributeValue, ...]

    def dominant_attribute(self) -> PlithogenicAttributeValue | None:
        for attribute in self.attributes:
            if attribute.dominant:
                return attribute
        return self.attributes[0] if self.attributes else None

    def contradiction_degree(self, attribute: PlithogenicAttributeValue) -> float:
        dominant = self.dominant_attribute()
        if dominant is None:
            return 0.0
        truth_gap = fabs(clamp01(attribute.T) - clamp01(dominant.T))
        indeterminacy_gap = fabs(clamp01(attribute.I) - clamp01(dominant.I))
        falsity_gap = fabs(clamp01(attribute.F) - clamp01(dominant.F))
        value_gap = 0.15 if attribute.value != dominant.value else 0.0
        return clamp01((truth_gap + indeterminacy_gap + falsity_gap) / 3.0 + value_gap)

    def score(self) -> dict[str, object]:
        if not self.attributes:
            return {
                "attribute_count": 0,
                "contradiction_load": 1.0,
                "weighted_cumulative_truth": {"T": 0.0, "I": 1.0, "F": 0.0},
                "operational_tif": TIF(T=0.0, I=1.0, F=0.0, I_system=1.0, H_lex=1.0, G_lex=1.0, I_lexicon=1.0).as_dict(),
                "source": source_payload(),
                "hierarchy": HIERARCHY,
            }
        weights = [max(0.0, attribute.weight) for attribute in self.attributes]
        weight_sum = sum(weights) or 1.0
        truth = sum(clamp01(attribute.T) * max(0.0, attribute.weight) for attribute in self.attributes) / weight_sum
        indeterminacy = sum(clamp01(attribute.I) * max(0.0, attribute.weight) for attribute in self.attributes) / weight_sum
        falsity = sum(clamp01(attribute.F) * max(0.0, attribute.weight) for attribute in self.attributes) / weight_sum
        contradictions = [
            {"name": attribute.name, "value": attribute.value, "degree": self.contradiction_degree(attribute)}
            for attribute in self.attributes
        ]
        contradiction_load = clamp01(max(item["degree"] for item in contradictions))
        load = clamp01(max(indeterminacy, contradiction_load))
        return {
            "attribute_count": len(self.attributes),
            "attributes": [attribute.as_dict() for attribute in self.attributes],
            "dominant_attribute": None if self.dominant_attribute() is None else self.dominant_attribute().as_dict(),
            "contradictions": contradictions,
            "contradiction_load": contradiction_load,
            "weighted_cumulative_truth": {"T": truth, "I": indeterminacy, "F": falsity},
            "plithogenic_i_profile": PlithogenicIProfile().as_dict(),
            "operational_tif": TIF(T=truth, I=indeterminacy, F=falsity, I_system=load, H_lex=load, G_lex=load, I_lexicon=load).as_dict(),
            "source": source_payload(),
            "hierarchy": HIERARCHY,
        }


def score_plithogenic_set(values: Iterable[object]) -> dict[str, object]:
    return PlithogenicSetProfile(tuple(PlithogenicAttributeValue.from_raw(value, index) for index, value in enumerate(values))).score()


def operate_plithogenic_sets(op: str, left: dict[str, object], right: dict[str, object] | None = None) -> dict[str, object]:
    operation = op.strip().lower()
    left_tif = _payload_tif(left)
    right_tif = _payload_tif(right or left)
    if operation == "union":
        result = TIF(T=max(left_tif.T, right_tif.T), I=max(left_tif.I, right_tif.I), F=min(left_tif.F, right_tif.F))
        rule = "bounded plithogenic union approximation: T=max, I=max, F=min"
    elif operation == "intersection":
        result = TIF(T=min(left_tif.T, right_tif.T), I=min(left_tif.I, right_tif.I), F=max(left_tif.F, right_tif.F))
        rule = "bounded plithogenic intersection approximation: T=min, I=min, F=max"
    elif operation == "complement":
        result = TIF(T=left_tif.F, I=left_tif.I, F=left_tif.T)
        rule = "bounded plithogenic complement approximation: T=F, I=I, F=T"
    else:
        raise ValueError(f"unsupported plithogenic set operation: {op}")
    load = clamp01(result.I)
    result = TIF(T=result.T, I=result.I, F=result.F, I_system=load, H_lex=load, G_lex=load, I_lexicon=load)
    return {
        "operation": operation,
        "left": left,
        "right": right,
        "rule": rule,
        "result": result.as_dict(),
        "source": source_payload(),
        "hierarchy": HIERARCHY,
    }


def _payload_tif(payload: dict[str, object]) -> TIF:
    return TIF(T=float(payload.get("T", 0.0)), I=float(payload.get("I", 0.0)), F=float(payload.get("F", 0.0))).bounded()


def plithogenic_set_explain() -> dict[str, object]:
    return {
        "source": source_payload(),
        "roles": [
            "attribute spectrum",
            "dominant attribute value",
            "contradiction degree",
            "bounded plithogenic union/intersection/complement diagnostics",
        ],
        "hierarchy": HIERARCHY,
    }


def plithogenic_set_profile_for_text(text: str) -> dict[str, object] | None:
    lowered = text.lower()
    if not any(term in lowered for term in ("plithogenic set", "dominant value", "attribute spectrum")):
        return None
    return score_plithogenic_set(
        [
            {"name": "attribute", "value": "dominant", "T": 0.8, "I": 0.1, "F": 0.1, "dominant": True},
            {"name": "attribute", "value": "variant", "T": 0.5, "I": 0.4, "F": 0.2},
        ]
    )


def source_payload() -> dict[str, object]:
    return {
        "source_id": PLITHOGENIC_SET_SOURCE_ID,
        "title": "Plithogenic Set, an Extension of Crisp, Fuzzy, Intuitionistic Fuzzy, and Neutrosophic Sets",
        "url": PLITHOGENIC_SET_SOURCE_URL,
        "evidence_kind": "public_nss",
        "public_safe": True,
    }
