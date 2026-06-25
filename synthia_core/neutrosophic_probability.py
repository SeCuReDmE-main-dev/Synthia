"""Neutrosophic event and sample-space helpers for Synthia phase 8."""

from __future__ import annotations

from dataclasses import dataclass

from .neutrosophic_foundation import NeutrosophicTruthValue, get_neutrosophic_profile
from .plithogenic import TIF, clamp01
from .safety import HIERARCHY


PROBABILITY_SOURCE_ID = "nss.measure_integral_probability"
PROBABILITY_SOURCE_URL = "https://fs.unm.edu/NeutrosophicMeasureIntegralProbability.pdf"
EPSILON = 1e-9


@dataclass(frozen=True)
class NeutrosophicProbability:
    T: float
    I: float
    F: float

    def truth_value(self) -> NeutrosophicTruthValue:
        profile = "uncertain" if self.I >= max(self.T, self.F) else "standard"
        return NeutrosophicTruthValue(T=self.T, I=self.I, F=self.F, profile=get_neutrosophic_profile(profile))

    def operational_tif(self) -> TIF:
        return self.truth_value().to_operational_tif()

    def as_dict(self) -> dict[str, object]:
        return {
            "formal_probability": {"T": float(self.T), "I": float(self.I), "F": float(self.F)},
            "formal_value": self.truth_value().formal_value(),
            "operational_tif": self.operational_tif().as_dict(),
            "source_id": PROBABILITY_SOURCE_ID,
            "hierarchy": HIERARCHY,
        }


@dataclass(frozen=True)
class NeutrosophicEvent:
    name: str
    probability: NeutrosophicProbability

    @classmethod
    def empty(cls) -> "NeutrosophicEvent":
        return cls("empty_event", NeutrosophicProbability(0.0, 0.0, 0.0))

    def complement(self) -> "NeutrosophicEvent":
        return NeutrosophicEvent(
            f"not_{self.name}",
            NeutrosophicProbability(self.probability.F, self.probability.I, self.probability.T),
        )

    def to_i_lexicon(self) -> dict[str, object]:
        tif = self.probability.operational_tif().bounded()
        i_load = clamp01(max(tif.I, 1.0 - tif.T))
        return TIF(T=tif.T, I=tif.I, F=tif.F, I_system=i_load, H_lex=i_load, G_lex=i_load, I_lexicon=i_load).as_dict()

    def as_dict(self) -> dict[str, object]:
        return {
            "event": self.name,
            "probability": self.probability.as_dict(),
            "complement": {
                "event": f"not_{self.name}",
                "T": clamp01(self.probability.F),
                "I": clamp01(self.probability.I),
                "F": clamp01(self.probability.T),
            },
            "i_lexicon_projection": self.to_i_lexicon(),
            "source": {
                "source_id": PROBABILITY_SOURCE_ID,
                "title": "Introduction to Neutrosophic Measure, Integral, and Probability",
                "url": PROBABILITY_SOURCE_URL,
                "evidence_kind": "public_nss",
                "public_safe": True,
            },
            "hierarchy": HIERARCHY,
        }


@dataclass(frozen=True)
class NeutrosophicSampleSpace:
    events: tuple[NeutrosophicEvent, ...]

    def as_dict(self) -> dict[str, object]:
        total_T = sum(event.probability.T for event in self.events)
        total_I = sum(event.probability.I for event in self.events)
        total_F = sum(event.probability.F for event in self.events)
        event_count = len(self.events)
        classifications = self._classifications(total_T, total_I, total_F)
        summary_tif = TIF(
            T=clamp01(total_T),
            I=clamp01(total_I / event_count if event_count else 1.0),
            F=clamp01(total_F),
            I_system=clamp01(total_I / event_count if event_count else 1.0),
            H_lex=clamp01(total_I / event_count if event_count else 1.0),
            G_lex=clamp01(abs(total_T - 1.0)),
            I_lexicon=clamp01((total_I / event_count if event_count else 1.0) + abs(total_T - 1.0)),
        )
        return {
            "event_count": event_count,
            "events": [event.as_dict() for event in self.events],
            "sample_space_totals": {"T": total_T, "I": total_I, "F": total_F},
            "sample_space_classification": classifications,
            "primary_classification": classifications[0],
            "operational_tif": summary_tif.as_dict(),
            "source_id": PROBABILITY_SOURCE_ID,
            "hierarchy": HIERARCHY,
        }

    @staticmethod
    def _classifications(T: float, I: float, F: float) -> list[str]:
        labels: list[str] = []
        if abs(T - 1.0) <= EPSILON and I <= EPSILON:
            labels.append("complete_sample_space")
        elif T < 1.0 - EPSILON:
            labels.append("incomplete_sample_space")
        elif T > 1.0 + EPSILON:
            labels.append("overfull_sample_space")
        if I > EPSILON:
            labels.append("indeterminate_sample_space")
        if F > EPSILON:
            labels.append("counter_event_load")
        labels.append("general_neutrosophic_probability")
        return labels


def probability_explain() -> dict[str, object]:
    return {
        "source": {
            "source_id": PROBABILITY_SOURCE_ID,
            "title": "Introduction to Neutrosophic Measure, Integral, and Probability",
            "url": PROBABILITY_SOURCE_URL,
            "evidence_kind": "public_nss",
            "public_safe": True,
        },
        "roles": [
            "event triples",
            "empty event",
            "sample-space diagnostics",
            "complement behavior",
            "probability-to-I_lexicon projection",
        ],
        "hierarchy": HIERARCHY,
    }


def probability_profile_for_text(text: str) -> dict[str, object] | None:
    lowered = text.lower()
    if not any(term in lowered for term in ("probability", "event", "measure", "sample space")):
        return None
    return NeutrosophicEvent("text_probability_event", NeutrosophicProbability(0.6, 0.3, 0.1)).as_dict()
