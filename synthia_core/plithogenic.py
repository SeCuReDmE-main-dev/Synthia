"""Bounded plithogenic helpers for Synthia's I_lexicon."""

from __future__ import annotations

from dataclasses import dataclass
from math import fabs
from typing import Iterable, Mapping

from .safety import HIERARCHY


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


@dataclass(frozen=True)
class TIF:
    """Truth, indeterminacy, falsity triplet."""

    T: float = 1.0
    I: float = 0.0
    F: float = 0.0
    I_system: float | None = None
    D_f: float | None = None
    dF: float | None = None
    i_fractal: float | None = None

    def bounded(self) -> "TIF":
        return TIF(
            T=clamp01(self.T),
            I=clamp01(self.I),
            F=clamp01(self.F),
            I_system=None if self.I_system is None else clamp01(self.I_system),
            D_f=None if self.D_f is None else float(self.D_f),
            dF=None if self.dF is None else float(self.dF),
            i_fractal=None if self.i_fractal is None else clamp01(self.i_fractal),
        )

    def as_dict(self) -> dict[str, float | str | None]:
        bounded = self.bounded()
        return {
            "T": bounded.T,
            "I": bounded.I,
            "F": bounded.F,
            "I_system^S": bounded.I_system,
            "D_f": bounded.D_f,
            "dF": bounded.dF,
            "i_fractal": bounded.i_fractal,
            "hierarchy": HIERARCHY,
        }


@dataclass(frozen=True)
class PlithogenicAttribute:
    name: str
    value: str
    tif: TIF
    weight: float = 1.0
    source_id: str | None = None

    def as_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "value": self.value,
            "tif": self.tif.as_dict(),
            "weight": clamp01(self.weight),
            "source_id": self.source_id,
        }


class PlithogenicMatrix:
    """Small deterministic matrix for contradiction and cumulative truth."""

    def __init__(self, attributes: Iterable[PlithogenicAttribute] | None = None):
        self.attributes = list(attributes or [])

    @classmethod
    def from_mappings(cls, mappings: Iterable[Mapping[str, object]]) -> "PlithogenicMatrix":
        attributes: list[PlithogenicAttribute] = []
        for item in mappings:
            tif_payload = item.get("tif") if isinstance(item.get("tif"), Mapping) else {}
            attributes.append(
                PlithogenicAttribute(
                    name=str(item.get("name", "unknown")),
                    value=str(item.get("value", "")),
                    tif=TIF(
                        T=float(tif_payload.get("T", item.get("T", 1.0))),
                        I=float(tif_payload.get("I", item.get("I", 0.0))),
                        F=float(tif_payload.get("F", item.get("F", 0.0))),
                        I_system=tif_payload.get("I_system^S") if "I_system^S" in tif_payload else item.get("I_system"),
                        D_f=tif_payload.get("D_f") if "D_f" in tif_payload else item.get("D_f"),
                        dF=tif_payload.get("dF") if "dF" in tif_payload else item.get("dF"),
                        i_fractal=tif_payload.get("i_fractal") if "i_fractal" in tif_payload else item.get("i_fractal"),
                    ),
                    weight=float(item.get("weight", 1.0)),
                    source_id=None if item.get("source_id") is None else str(item.get("source_id")),
                )
            )
        return cls(attributes)

    def contradiction_degree(self, left: PlithogenicAttribute, right: PlithogenicAttribute) -> float:
        left_tif = left.tif.bounded()
        right_tif = right.tif.bounded()
        truth_gap = fabs(left_tif.T - right_tif.T)
        falsity_gap = fabs(left_tif.F - right_tif.F)
        indeterminacy_load = max(left_tif.I, right_tif.I)
        same_name_penalty = 0.15 if left.name == right.name and left.value != right.value else 0.0
        return clamp01((truth_gap + falsity_gap + indeterminacy_load) / 3.0 + same_name_penalty)

    def contradiction_summary(self) -> dict[str, object]:
        pairs: list[dict[str, object]] = []
        max_degree = 0.0
        for index, left in enumerate(self.attributes):
            for right in self.attributes[index + 1 :]:
                degree = self.contradiction_degree(left, right)
                max_degree = max(max_degree, degree)
                pairs.append({"left": left.name, "right": right.name, "degree": degree})
        return {"max_degree": max_degree, "pair_count": len(pairs), "pairs": pairs}

    def weighted_cumulative_truth(self) -> dict[str, float]:
        if not self.attributes:
            return {"T": 0.0, "I": 0.0, "F": 0.0}
        weight_sum = sum(max(0.0, item.weight) for item in self.attributes) or 1.0
        return {
            "T": clamp01(sum(item.tif.bounded().T * max(0.0, item.weight) for item in self.attributes) / weight_sum),
            "I": clamp01(sum(item.tif.bounded().I * max(0.0, item.weight) for item in self.attributes) / weight_sum),
            "F": clamp01(sum(item.tif.bounded().F * max(0.0, item.weight) for item in self.attributes) / weight_sum),
        }

    def feature_vector(self) -> list[float]:
        truth = self.weighted_cumulative_truth()
        contradictions = self.contradiction_summary()
        return [truth["T"], truth["I"], truth["F"], float(contradictions["max_degree"])]

    def profile(self) -> dict[str, object]:
        return {
            "model": "synthia_plithogenic_matrix_v1",
            "attributes": [item.as_dict() for item in self.attributes],
            "weighted_cumulative_truth": self.weighted_cumulative_truth(),
            "contradiction_summary": self.contradiction_summary(),
            "feature_vector": self.feature_vector(),
            "hierarchy": HIERARCHY,
        }
