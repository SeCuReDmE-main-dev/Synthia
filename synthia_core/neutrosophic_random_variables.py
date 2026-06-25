"""Neutrosophic random variable helpers for Synthia phase 11."""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from statistics import mean
from typing import Iterable

from .plithogenic import TIF, clamp01
from .safety import HIERARCHY


RANDOM_VARIABLE_SOURCE_ID = "nss.neutrosophic_random_variables"
RANDOM_VARIABLE_SOURCE_URL = "https://fs.unm.edu/NSS/NeutrosophicRandomVariables4.pdf"


@dataclass(frozen=True)
class NeutrosophicRandomVariable:
    name: str
    base_value: float
    indeterminacy: float

    def expected_value(self) -> dict[str, object]:
        return {
            "symbolic": f"E({self.name}_N) = E({self.name}) + I",
            "base_expected_value": self.base_value,
            "indeterminate_component": self.indeterminacy,
            "operational_expected_value": self.base_value + clamp01(self.indeterminacy),
        }

    def distribution_metadata(self) -> dict[str, object]:
        return {
            "PDF": f"f_{self.name}N(x) = f_{self.name}(x - I)",
            "PMF": f"p_{self.name}N(x) = p_{self.name}(x - I)",
            "CDF": f"F_{self.name}N(x) = F_{self.name}(x - I)",
            "boundary": "Symbolic metadata for routing; Synthia does not perform full symbolic calculus here.",
        }

    def to_i_lexicon(self) -> dict[str, object]:
        load = clamp01(abs(self.indeterminacy))
        return TIF(T=clamp01(1.0 - load), I=load, F=0.0, I_system=load, H_lex=load, G_lex=load, I_lexicon=load).as_dict()

    def as_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "formal_value": {"base": self.base_value, "I": self.indeterminacy, "form": f"{self.base_value} + {self.indeterminacy}I"},
            "distribution_metadata": self.distribution_metadata(),
            "expected_value": self.expected_value(),
            "i_lexicon_projection": self.to_i_lexicon(),
            "source": source_payload(),
            "hierarchy": HIERARCHY,
        }


@dataclass(frozen=True)
class RandomVariableDatum:
    base_value: float
    indeterminacy: float
    weight: float = 1.0

    @classmethod
    def from_raw(cls, raw: object) -> "RandomVariableDatum":
        if isinstance(raw, (int, float)):
            return cls(float(raw), 0.0, 1.0)
        if isinstance(raw, dict):
            return cls(
                float(raw.get("base", raw.get("value", 0.0))),
                float(raw.get("I", raw.get("indeterminacy", 0.0))),
                float(raw.get("weight", 1.0)),
            )
        if isinstance(raw, (list, tuple)) and len(raw) >= 2:
            return cls(float(raw[0]), float(raw[1]), float(raw[2]) if len(raw) >= 3 else 1.0)
        raise ValueError(f"unsupported random variable datum: {raw!r}")

    def as_dict(self) -> dict[str, object]:
        return {"base": self.base_value, "I": self.indeterminacy, "weight": self.weight}


@dataclass(frozen=True)
class NeutrosophicRandomVariableSummary:
    values: tuple[RandomVariableDatum, ...]

    def as_dict(self) -> dict[str, object]:
        if not self.values:
            return {
                "count": 0,
                "expected_value": None,
                "variance": None,
                "standard_deviation": None,
                "indeterminacy_load": 1.0,
                "operational_tif": TIF(T=0.0, I=1.0, F=0.0, I_system=1.0, H_lex=1.0, G_lex=1.0, I_lexicon=1.0).as_dict(),
                "source": source_payload(),
                "hierarchy": HIERARCHY,
            }
        weights = [max(0.0, value.weight) for value in self.values]
        weight_sum = sum(weights) or 1.0
        expected = sum(value.base_value * max(0.0, value.weight) for value in self.values) / weight_sum
        variance = sum(((value.base_value - expected) ** 2) * max(0.0, value.weight) for value in self.values) / weight_sum
        indeterminacy_load = clamp01(mean(abs(value.indeterminacy) for value in self.values))
        tif = TIF(
            T=clamp01(1.0 - indeterminacy_load),
            I=indeterminacy_load,
            F=0.0,
            I_system=indeterminacy_load,
            H_lex=indeterminacy_load,
            G_lex=indeterminacy_load,
            I_lexicon=indeterminacy_load,
        )
        return {
            "count": len(self.values),
            "values": [value.as_dict() for value in self.values],
            "expected_value": expected,
            "variance": variance,
            "standard_deviation": sqrt(variance),
            "moment_summary": {"first": expected, "second_central": variance},
            "indeterminacy_load": indeterminacy_load,
            "operational_tif": tif.as_dict(),
            "source": source_payload(),
            "hierarchy": HIERARCHY,
        }


def summarize_random_variables(values: Iterable[object]) -> dict[str, object]:
    return NeutrosophicRandomVariableSummary(tuple(RandomVariableDatum.from_raw(value) for value in values)).as_dict()


def random_variable_explain() -> dict[str, object]:
    return {
        "source": source_payload(),
        "roles": [
            "neutrosophic random variable X_N = X + I",
            "PDF/PMF/CDF symbolic metadata",
            "expected value, variance, standard deviation, and moment summaries",
            "bounded projection into I_lexicon",
        ],
        "hierarchy": HIERARCHY,
    }


def random_variable_profile_for_text(text: str) -> dict[str, object] | None:
    lowered = text.lower()
    if not any(term in lowered for term in ("random variable", "cdf", "pdf", "pmf", "expected value", "variance")):
        return None
    return NeutrosophicRandomVariable("text_random_variable", 0.5, 0.3).as_dict()


def source_payload() -> dict[str, object]:
    return {
        "source_id": RANDOM_VARIABLE_SOURCE_ID,
        "title": "Neutrosophic Random Variables",
        "url": RANDOM_VARIABLE_SOURCE_URL,
        "evidence_kind": "public_nss",
        "public_safe": True,
    }
