"""Plithogenic probability and statistics kernel for Synthia phase 16."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .plithogenic import PlithogenicIProfile, TIF, clamp01
from .safety import HIERARCHY


PLITHOGENIC_PROBABILITY_SOURCE_ID = "nss.plithogenic_probability_statistics"
PLITHOGENIC_PROBABILITY_SOURCE_URL = "https://fs.unm.edu/NSS/PlithogenicProbabilityStatistics20.pdf"


@dataclass(frozen=True)
class PlithogenicProbabilityVariable:
    name: str
    T: float
    I: float
    F: float
    weight: float = 1.0
    distribution: str = "candidate"

    @classmethod
    def from_raw(cls, raw: object, index: int) -> "PlithogenicProbabilityVariable":
        if not isinstance(raw, dict):
            raise ValueError("each plithogenic probability variable must be a JSON object")
        return cls(
            name=str(raw.get("name", f"X_{index + 1}")),
            T=float(raw.get("T", raw.get("truth", 0.0))),
            I=float(raw.get("I", raw.get("indeterminacy", 0.0))),
            F=float(raw.get("F", raw.get("falsity", 0.0))),
            weight=float(raw.get("weight", 1.0)),
            distribution=str(raw.get("distribution", "candidate")),
        )

    def bounded_tif(self) -> TIF:
        return TIF(T=clamp01(self.T), I=clamp01(self.I), F=clamp01(self.F))

    def contradiction_degree(self) -> float:
        return clamp01(abs(clamp01(self.T) - (1.0 - clamp01(self.F))) + 0.5 * clamp01(self.I))

    def as_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "formal_value": {"T": self.T, "I": self.I, "F": self.F},
            "operational_tif": self.bounded_tif().as_dict(),
            "weight": self.weight,
            "distribution": self.distribution,
            "contradiction_degree": self.contradiction_degree(),
        }


@dataclass(frozen=True)
class PlithogenicProbabilityEvent:
    name: str
    variables: tuple[PlithogenicProbabilityVariable, ...]

    def summarize(self) -> dict[str, object]:
        if not self.variables:
            tif = TIF(T=0.0, I=1.0, F=0.0, I_system=1.0, H_lex=1.0, G_lex=1.0, I_lexicon=1.0)
            return {
                "name": self.name,
                "variable_count": 0,
                "variables": [],
                "weighted_probability": {"T": 0.0, "I": 1.0, "F": 0.0},
                "contradiction_load": 1.0,
                "operational_tif": tif.as_dict(),
                "plithogenic_i_profile": PlithogenicIProfile().as_dict(),
                "source": source_payload(),
                "hierarchy": HIERARCHY,
            }
        weights = [max(0.0, variable.weight) for variable in self.variables]
        weight_sum = sum(weights) or 1.0
        truth = sum(clamp01(variable.T) * max(0.0, variable.weight) for variable in self.variables) / weight_sum
        indeterminacy = sum(clamp01(variable.I) * max(0.0, variable.weight) for variable in self.variables) / weight_sum
        falsity = sum(clamp01(variable.F) * max(0.0, variable.weight) for variable in self.variables) / weight_sum
        contradiction_load = max(variable.contradiction_degree() for variable in self.variables)
        load = clamp01(max(indeterminacy, contradiction_load))
        tif = TIF(T=truth, I=indeterminacy, F=falsity, I_system=load, H_lex=load, G_lex=load, I_lexicon=load)
        return {
            "name": self.name,
            "variable_count": len(self.variables),
            "variables": [variable.as_dict() for variable in self.variables],
            "weighted_probability": {"T": truth, "I": indeterminacy, "F": falsity},
            "refined_components": refined_components(self.variables),
            "contradiction_load": contradiction_load,
            "operational_tif": tif.as_dict(),
            "plithogenic_i_profile": PlithogenicIProfile().as_dict(),
            "source": source_payload(),
            "hierarchy": HIERARCHY,
        }


def refined_components(variables: Iterable[PlithogenicProbabilityVariable]) -> list[dict[str, object]]:
    return [
        {
            "variable": variable.name,
            "T_component": clamp01(variable.T),
            "I_component": clamp01(variable.I),
            "F_component": clamp01(variable.F),
            "weight": max(0.0, variable.weight),
        }
        for variable in variables
    ]


def summarize_plithogenic_probability_event(variables: Iterable[object], name: str = "plithogenic_event") -> dict[str, object]:
    event = PlithogenicProbabilityEvent(
        name=name,
        variables=tuple(PlithogenicProbabilityVariable.from_raw(variable, index) for index, variable in enumerate(variables)),
    )
    return event.summarize()


def refine_plithogenic_probability(components: Iterable[object]) -> dict[str, object]:
    variables = tuple(PlithogenicProbabilityVariable.from_raw(component, index) for index, component in enumerate(components))
    payload = PlithogenicProbabilityEvent("refined_plithogenic_probability", variables).summarize()
    payload["refinement_rule"] = "Refined T/I/F components are preserved per variable before bounded operational fusion."
    return payload


def plithogenic_probability_explain() -> dict[str, object]:
    return {
        "source": source_payload(),
        "roles": [
            "multi-variable plithogenic probability events",
            "refined T/I/F component preservation",
            "contradiction load for system-level indeterminacy",
            "bounded projection into H_lex, G_lex, and I_lexicon",
        ],
        "hierarchy": HIERARCHY,
    }


def plithogenic_probability_profile_for_text(text: str) -> dict[str, object] | None:
    lowered = text.lower()
    if not ("plithogenic" in lowered and any(term in lowered for term in ("probability", "statistics", "refined"))):
        return None
    return summarize_plithogenic_probability_event(
        [
            {"name": "source_probability", "T": 0.72, "I": 0.22, "F": 0.08, "weight": 0.7},
            {"name": "contradiction_probability", "T": 0.44, "I": 0.42, "F": 0.18, "weight": 0.3},
        ]
    )


def source_payload() -> dict[str, object]:
    return {
        "source_id": PLITHOGENIC_PROBABILITY_SOURCE_ID,
        "title": "Plithogenic Probability and Statistics",
        "url": PLITHOGENIC_PROBABILITY_SOURCE_URL,
        "evidence_kind": "public_nss",
        "public_safe": True,
    }
