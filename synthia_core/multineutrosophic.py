"""Multi-source neutrosophic fusion for Synthia phase 13."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Iterable

from .plithogenic import TIF, clamp01
from .safety import HIERARCHY


MULTI_SOURCE_ID = "nss.multineutrosophic_set"
MULTI_SOURCE_URL = "https://fs.unm.edu/NSS/MultiNeutrosophicSet.pdf"


@dataclass(frozen=True)
class MultiNeutrosophicSource:
    source_id: str
    weight: float = 1.0

    def as_dict(self) -> dict[str, object]:
        return {"source_id": self.source_id, "weight": max(0.0, self.weight)}


@dataclass(frozen=True)
class MultiTIFAssessment:
    source: MultiNeutrosophicSource
    T: float
    I: float
    F: float

    @classmethod
    def from_raw(cls, raw: object, index: int) -> "MultiTIFAssessment":
        if not isinstance(raw, dict):
            raise ValueError("each multi-neutrosophic assessment must be a JSON object")
        return cls(
            MultiNeutrosophicSource(str(raw.get("source", raw.get("source_id", f"source_{index + 1}"))), float(raw.get("weight", 1.0))),
            float(raw.get("T", 0.0)),
            float(raw.get("I", 0.0)),
            float(raw.get("F", 0.0)),
        )

    def bounded_tuple(self) -> tuple[float, float, float]:
        return clamp01(self.T), clamp01(self.I), clamp01(self.F)

    def as_dict(self) -> dict[str, object]:
        return {"source": self.source.as_dict(), "T": self.T, "I": self.I, "F": self.F}


@dataclass(frozen=True)
class MultiNeutrosophicFusion:
    assessments: tuple[MultiTIFAssessment, ...]

    def as_dict(self) -> dict[str, object]:
        if not self.assessments:
            return {
                "assessment_count": 0,
                "fused_tif": TIF(T=0.0, I=1.0, F=0.0, I_system=1.0, H_lex=1.0, G_lex=1.0, I_lexicon=1.0).as_dict(),
                "agreement_score": 0.0,
                "conflict_score": 1.0,
                "review_risk": "high",
                "source": source_payload(),
                "hierarchy": HIERARCHY,
            }
        weight_sum = sum(max(0.0, item.source.weight) for item in self.assessments) or 1.0
        fused_T = sum(item.bounded_tuple()[0] * max(0.0, item.source.weight) for item in self.assessments) / weight_sum
        fused_I = sum(item.bounded_tuple()[1] * max(0.0, item.source.weight) for item in self.assessments) / weight_sum
        fused_F = sum(item.bounded_tuple()[2] * max(0.0, item.source.weight) for item in self.assessments) / weight_sum
        conflict = self.conflict_score()
        load = clamp01(max(fused_I, conflict))
        return {
            "assessment_count": len(self.assessments),
            "assessments": [item.as_dict() for item in self.assessments],
            "fused_components": {"T": fused_T, "I": fused_I, "F": fused_F},
            "agreement_score": clamp01(1.0 - conflict),
            "conflict_score": conflict,
            "review_risk": "high" if load >= 0.66 else "medium" if load >= 0.33 else "low",
            "fused_tif": TIF(T=fused_T, I=fused_I, F=fused_F, I_system=load, H_lex=load, G_lex=load, I_lexicon=load).as_dict(),
            "source": source_payload(),
            "hierarchy": HIERARCHY,
        }

    def conflict_score(self) -> float:
        if len(self.assessments) < 2:
            return 0.0
        distances: list[float] = []
        for left, right in combinations(self.assessments, 2):
            left_tuple = left.bounded_tuple()
            right_tuple = right.bounded_tuple()
            distances.append(sum(abs(left_tuple[index] - right_tuple[index]) for index in range(3)) / 3.0)
        return clamp01(max(distances) if distances else 0.0)


def fuse_multineutrosophic_assessments(values: Iterable[object]) -> dict[str, object]:
    return MultiNeutrosophicFusion(tuple(MultiTIFAssessment.from_raw(value, index) for index, value in enumerate(values))).as_dict()


def multineutrosophic_explain() -> dict[str, object]:
    return {
        "source": source_payload(),
        "roles": [
            "many-source T/I/F assessment",
            "weighted expert/source fusion",
            "agreement, conflict, and review-risk scoring",
            "bounded projection into I_lexicon",
        ],
        "hierarchy": HIERARCHY,
    }


def multineutrosophic_profile_for_text(text: str) -> dict[str, object] | None:
    lowered = text.lower()
    if not any(term in lowered for term in ("multineutrosophic", "multi-source", "many sources", "expert fusion")):
        return None
    return fuse_multineutrosophic_assessments(
        [
            {"source": "expert_a", "T": 0.7, "I": 0.2, "F": 0.1},
            {"source": "expert_b", "T": 0.5, "I": 0.4, "F": 0.2},
        ]
    )


def source_payload() -> dict[str, object]:
    return {
        "source_id": MULTI_SOURCE_ID,
        "title": "Introduction to the MultiNeutrosophic Set",
        "url": MULTI_SOURCE_URL,
        "evidence_kind": "public_nss",
        "public_safe": True,
    }
