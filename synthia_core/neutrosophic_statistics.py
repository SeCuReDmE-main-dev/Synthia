"""Neutrosophic statistics and distribution helpers for Synthia phases 9-10."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Iterable

from .plithogenic import TIF, clamp01
from .safety import HIERARCHY


STATISTICS_SOURCE_ID = "nss.neutrosophic_statistics"
DISTRIBUTION_SOURCE_ID = "nss.neutrosophic_statistical_distribution"
STATISTICS_SOURCE_URL = "https://fs.unm.edu/NeutrosophicStatistics.pdf"
DISTRIBUTION_SOURCE_URL = "https://fs.unm.edu/NSS/TheNeutrosophicStatisticalDistribution.pdf"


@dataclass(frozen=True)
class NeutrosophicDatum:
    raw: object
    known_value: float | None = None
    interval: tuple[float, float] | None = None
    indeterminate: bool = False

    @classmethod
    def from_raw(cls, raw: object) -> "NeutrosophicDatum":
        if raw is None:
            return cls(raw=raw, indeterminate=True)
        if isinstance(raw, (int, float)):
            return cls(raw=raw, known_value=float(raw))
        if isinstance(raw, (list, tuple)) and len(raw) == 2:
            left, right = float(raw[0]), float(raw[1])
            return cls(raw=raw, interval=(min(left, right), max(left, right)))
        if isinstance(raw, dict):
            if raw.get("unknown") is True or raw.get("indeterminate") is True:
                return cls(raw=raw, indeterminate=True)
            if "value" in raw:
                return cls(raw=raw, known_value=float(raw["value"]))
            if "low" in raw and "high" in raw:
                left, right = float(raw["low"]), float(raw["high"])
                return cls(raw=raw, interval=(min(left, right), max(left, right)))
        return cls(raw=raw, indeterminate=True)

    def representative_value(self) -> float | None:
        if self.known_value is not None:
            return self.known_value
        if self.interval is not None:
            return (self.interval[0] + self.interval[1]) / 2.0
        return None

    def as_dict(self) -> dict[str, object]:
        return {
            "raw": self.raw,
            "known_value": self.known_value,
            "interval": None if self.interval is None else list(self.interval),
            "indeterminate": self.indeterminate,
        }


@dataclass(frozen=True)
class NeutrosophicDatasetProfile:
    data: tuple[NeutrosophicDatum, ...]

    def summarize(self) -> dict[str, object]:
        total = len(self.data)
        known = [datum.known_value for datum in self.data if datum.known_value is not None]
        intervals = [datum.interval for datum in self.data if datum.interval is not None]
        representatives = [datum.representative_value() for datum in self.data if datum.representative_value() is not None]
        unknown_count = sum(1 for datum in self.data if datum.indeterminate)
        interval_count = len(intervals)
        load = clamp01((unknown_count + interval_count) / total) if total else 1.0
        values = [float(value) for value in representatives if value is not None]
        summary_tif = TIF(
            T=clamp01(len(known) / total) if total else 0.0,
            I=load,
            F=clamp01(unknown_count / total) if total else 1.0,
            I_system=load,
            H_lex=load,
            G_lex=load,
            I_lexicon=load,
        )
        return {
            "dataset_size": total,
            "known_count": len(known),
            "interval_count": interval_count,
            "unknown_count": unknown_count,
            "indeterminacy_load": load,
            "range": None if not values else {"min": min(values), "max": max(values)},
            "mean_representative": None if not values else mean(values),
            "data": [datum.as_dict() for datum in self.data],
            "review_risk": self._review_risk(load),
            "operational_tif": summary_tif.as_dict(),
            "source": {
                "source_id": STATISTICS_SOURCE_ID,
                "title": "Introduction to Neutrosophic Statistics",
                "url": STATISTICS_SOURCE_URL,
                "evidence_kind": "public_nss",
                "public_safe": True,
            },
            "hierarchy": HIERARCHY,
        }

    @staticmethod
    def _review_risk(load: float) -> str:
        if load >= 0.66:
            return "high"
        if load >= 0.33:
            return "medium"
        return "low"


@dataclass(frozen=True)
class NeutrosophicStatistic:
    name: str
    value: object
    indeterminacy_load: float
    source_id: str = STATISTICS_SOURCE_ID

    def as_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "value": self.value,
            "indeterminacy_load": clamp01(self.indeterminacy_load),
            "source_id": self.source_id,
            "hierarchy": HIERARCHY,
        }


@dataclass(frozen=True)
class NeutrosophicDistributionProfile:
    text: str
    labels: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        load = 0.45 if "indeterminate_distribution" in self.labels else 0.25
        return {
            "text": self.text,
            "candidate_distribution_labels": list(self.labels),
            "primary_distribution": self.labels[0],
            "operational_tif": TIF(
                T=0.6,
                I=load,
                F=0.1,
                I_system=load,
                H_lex=load,
                G_lex=load,
                I_lexicon=load,
            ).as_dict(),
            "source": {
                "source_id": DISTRIBUTION_SOURCE_ID,
                "title": "The Neutrosophic Statistical Distribution",
                "url": DISTRIBUTION_SOURCE_URL,
                "evidence_kind": "public_nss",
                "public_safe": True,
            },
            "hierarchy": HIERARCHY,
        }


def summarize_neutrosophic_dataset(values: Iterable[object]) -> dict[str, object]:
    profile = NeutrosophicDatasetProfile(tuple(NeutrosophicDatum.from_raw(value) for value in values))
    return profile.summarize()


def classify_neutrosophic_distribution(text: str) -> dict[str, object]:
    lowered = text.lower()
    labels: list[str] = []
    if any(term in lowered for term in ("binomial", "success", "failure", "trial")):
        labels.append("neutrosophic_binomial_candidate")
    if any(term in lowered for term in ("normal", "mean", "sigma", "standard deviation")):
        labels.append("neutrosophic_normal_candidate")
    if any(term in lowered for term in ("sample", "summary", "descriptive", "statistic")):
        labels.append("neutrosophic_descriptive_distribution")
    if any(term in lowered for term in ("unknown", "indeterminate", "interval", "uncertain")):
        labels.append("indeterminate_distribution")
    labels.append("general_neutrosophic_statistical_distribution")
    return NeutrosophicDistributionProfile(text=text, labels=tuple(labels)).as_dict()


def statistics_explain() -> dict[str, object]:
    return {
        "sources": [
            {
                "source_id": STATISTICS_SOURCE_ID,
                "title": "Introduction to Neutrosophic Statistics",
                "url": STATISTICS_SOURCE_URL,
                "evidence_kind": "public_nss",
                "public_safe": True,
            },
            {
                "source_id": DISTRIBUTION_SOURCE_ID,
                "title": "The Neutrosophic Statistical Distribution",
                "url": DISTRIBUTION_SOURCE_URL,
                "evidence_kind": "public_nss",
                "public_safe": True,
            },
        ],
        "roles": [
            "known, interval, and unknown data summaries",
            "indeterminacy load",
            "candidate distribution labels",
            "review risk for uncertain datasets",
        ],
        "hierarchy": HIERARCHY,
    }


def statistics_profile_for_text(text: str) -> dict[str, object] | None:
    lowered = text.lower()
    if not any(term in lowered for term in ("statistics", "distribution", "random variable", "dataset")):
        return None
    return classify_neutrosophic_distribution(text)
