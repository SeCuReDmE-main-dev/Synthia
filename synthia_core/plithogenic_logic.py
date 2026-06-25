"""Plithogenic logic helpers for Synthia phase 15."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .plithogenic import PlithogenicIProfile, TIF, clamp01
from .safety import HIERARCHY


PLITHOGENIC_LOGIC_SOURCE_ID = "nss.plithogenic_logic_intro"
PLITHOGENIC_LOGIC_SOURCE_URL = "https://fs.unm.edu/NSS/IntroductionPlithogenicLogic1.pdf"


@dataclass(frozen=True)
class PlithogenicLogicVariable:
    name: str
    T: float
    I: float = 0.0
    F: float = 0.0
    weight: float = 1.0
    dependence: float = 0.0

    @classmethod
    def from_raw(cls, raw: object, index: int) -> "PlithogenicLogicVariable":
        if not isinstance(raw, dict):
            raise ValueError("each plithogenic logic variable must be a JSON object")
        return cls(
            name=str(raw.get("name", f"V{index + 1}")),
            T=float(raw.get("T", raw.get("truth", 0.0))),
            I=float(raw.get("I", raw.get("indeterminacy", 0.0))),
            F=float(raw.get("F", raw.get("falsity", 0.0))),
            weight=float(raw.get("weight", 1.0)),
            dependence=float(raw.get("dependence", 0.0)),
        )

    def as_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "T": self.T,
            "I": self.I,
            "F": self.F,
            "weight": self.weight,
            "dependence": self.dependence,
        }


@dataclass(frozen=True)
class PlithogenicLogicalProposition:
    variables: tuple[PlithogenicLogicVariable, ...]

    def cumulative_truth(self) -> dict[str, float]:
        if not self.variables:
            return {"T": 0.0, "I": 1.0, "F": 0.0}
        weight_sum = sum(max(0.0, variable.weight) for variable in self.variables) or 1.0
        return {
            "T": clamp01(sum(clamp01(variable.T) * max(0.0, variable.weight) for variable in self.variables) / weight_sum),
            "I": clamp01(sum(clamp01(variable.I) * max(0.0, variable.weight) for variable in self.variables) / weight_sum),
            "F": clamp01(sum(clamp01(variable.F) * max(0.0, variable.weight) for variable in self.variables) / weight_sum),
        }

    def dependence_load(self) -> float:
        if not self.variables:
            return 1.0
        return clamp01(sum(clamp01(variable.dependence) for variable in self.variables) / len(self.variables))

    def categories(self) -> list[str]:
        labels: list[str] = []
        if self.variables and all(variable.T in (0.0, 1.0) and variable.I == 0.0 and variable.F in (0.0, 1.0) for variable in self.variables):
            labels.append("plithogenic_boolean_logic")
        if any(0.0 < clamp01(variable.T) < 1.0 for variable in self.variables):
            labels.append("plithogenic_fuzzy_logic")
        if any(variable.I > 0.0 for variable in self.variables):
            labels.append("plithogenic_neutrosophic_logic")
        if any(variable.I >= max(variable.T, variable.F) for variable in self.variables):
            labels.append("plithogenic_indeterminate_logic")
        labels.append("general_plithogenic_logic")
        return labels

    def as_dict(self) -> dict[str, object]:
        cumulative = self.cumulative_truth()
        dependence = self.dependence_load()
        load = clamp01(max(cumulative["I"], dependence))
        return {
            "variable_count": len(self.variables),
            "variables": [variable.as_dict() for variable in self.variables],
            "cumulative_truth": cumulative,
            "dependence_load": dependence,
            "logic_categories": self.categories(),
            "primary_category": self.categories()[0],
            "plithogenic_i_profile": PlithogenicIProfile().as_dict(),
            "operational_tif": TIF(
                T=cumulative["T"],
                I=cumulative["I"],
                F=cumulative["F"],
                I_system=load,
                H_lex=load,
                G_lex=load,
                I_lexicon=load,
            ).as_dict(),
            "source": source_payload(),
            "hierarchy": HIERARCHY,
        }


def classify_plithogenic_logic(values: Iterable[object]) -> dict[str, object]:
    return PlithogenicLogicalProposition(tuple(PlithogenicLogicVariable.from_raw(value, index) for index, value in enumerate(values))).as_dict()


def plithogenic_logic_explain() -> dict[str, object]:
    return {
        "source": source_payload(),
        "roles": [
            "many-variable proposition truth",
            "variable dependence and independence metadata",
            "cumulative truth calculation",
            "plithogenic logic category routing",
        ],
        "hierarchy": HIERARCHY,
    }


def plithogenic_logic_profile_for_text(text: str) -> dict[str, object] | None:
    lowered = text.lower()
    if not any(term in lowered for term in ("plithogenic logic", "cumulative truth", "plithogenic proposition")):
        return None
    return classify_plithogenic_logic(
        [
            {"name": "V1", "T": 0.8, "I": 0.1, "F": 0.1, "dependence": 0.2},
            {"name": "V2", "T": 0.6, "I": 0.3, "F": 0.2, "dependence": 0.4},
        ]
    )


def source_payload() -> dict[str, object]:
    return {
        "source_id": PLITHOGENIC_LOGIC_SOURCE_ID,
        "title": "Introduction to Plithogenic Logic",
        "url": PLITHOGENIC_LOGIC_SOURCE_URL,
        "evidence_kind": "public_nss",
        "public_safe": True,
    }
