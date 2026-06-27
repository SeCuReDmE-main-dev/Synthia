"""Uncertainty-aware societal risk triage for public-safe review support."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Mapping

from .plithogenic import TIF, clamp01
from .plithogenic_probability_statistics import summarize_plithogenic_probability_event
from .safety import HIERARCHY


P2NRS_SOURCE_URL = "https://fs.unm.edu/NSS/59ProbabilisticPlithogenic.pdf"
P2NRS_SOURCE_ID = "nss.p2nrs_food_safety_2025"


class RiskDomain(str, Enum):
    FOOD_SAFETY = "food_safety"
    CONSERVATION = "conservation"
    PUBLIC_HEALTH = "public_health"
    ENVIRONMENT = "environment"
    TAXONOMY_REVIEW = "taxonomy_review"


class RoughRegion(str, Enum):
    LOWER_APPROXIMATION = "lower_approximation"
    BOUNDARY_REGION = "boundary_region"
    UPPER_APPROXIMATION = "upper_approximation"


class RiskPriority(str, Enum):
    ROUTINE = "routine"
    WATCH = "watch"
    ELEVATED = "elevated"
    CRITICAL_REVIEW = "critical_review"


@dataclass(frozen=True)
class RiskCriterion:
    name: str
    value: str
    T: float
    I: float
    F: float
    probability: float
    weight: float = 1.0
    source_ids: tuple[str, ...] = ()
    notes: str = ""

    @classmethod
    def from_raw(cls, raw: object, index: int) -> "RiskCriterion":
        if not isinstance(raw, Mapping):
            raise ValueError("each risk criterion must be a JSON object")
        return cls(
            name=str(raw.get("name", f"criterion_{index + 1}")),
            value=str(raw.get("value", "")),
            T=float(raw.get("T", 0.0)),
            I=float(raw.get("I", 0.0)),
            F=float(raw.get("F", 0.0)),
            probability=float(raw.get("probability", raw.get("P", 0.0))),
            weight=max(0.0, float(raw.get("weight", 1.0))),
            source_ids=tuple(str(item) for item in raw.get("source_ids", ())),
            notes=str(raw.get("notes", "")),
        )

    def operational_tif(self) -> TIF:
        return TIF(T=clamp01(self.T), I=clamp01(self.I), F=clamp01(self.F))

    def operational_probability(self) -> float:
        return clamp01(self.probability)

    def as_probability_variable(self) -> dict[str, object]:
        tif = self.operational_tif()
        return {
            "name": self.name,
            "T": tif.T,
            "I": tif.I,
            "F": tif.F,
            "weight": self.weight,
            "distribution": self.value,
        }

    def as_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "value": self.value,
            "formal_value": {"T": self.T, "I": self.I, "F": self.F, "probability": self.probability},
            "operational_tif": self.operational_tif().as_dict(),
            "operational_probability": self.operational_probability(),
            "weight": self.weight,
            "source_ids": list(self.source_ids),
            "notes": self.notes,
        }


@dataclass(frozen=True)
class RiskTriageCase:
    case_label: str
    domain: str
    criteria: tuple[RiskCriterion, ...]
    source_ids: tuple[str, ...] = ()
    reviewer_notes: str = ""
    related_taxon_packet: Mapping[str, object] | None = None

    @classmethod
    def from_raw_case(cls, raw: object) -> "RiskTriageCase":
        if not isinstance(raw, Mapping):
            raise ValueError("risk triage case must be a JSON object")
        criteria = raw.get("criteria", [])
        if not isinstance(criteria, list):
            raise ValueError("risk triage case criteria must be a JSON array")
        related_taxon_packet = raw.get("related_taxon_packet")
        if related_taxon_packet is not None and not isinstance(related_taxon_packet, Mapping):
            raise ValueError("related_taxon_packet must be a JSON object when provided")
        return cls(
            case_label=str(raw.get("case_label", "unnamed risk triage case")),
            domain=str(raw.get("domain", RiskDomain.FOOD_SAFETY.value)),
            criteria=tuple(RiskCriterion.from_raw(item, index) for index, item in enumerate(criteria)),
            source_ids=tuple(str(item) for item in raw.get("source_ids", ())),
            reviewer_notes=str(raw.get("reviewer_notes", "")),
            related_taxon_packet=related_taxon_packet,
        )


class RiskTriageReviewer:
    def score(self, case: RiskTriageCase | object) -> dict[str, object]:
        triage_case = case if isinstance(case, RiskTriageCase) else RiskTriageCase.from_raw_case(case)
        if not triage_case.criteria:
            operational_tif = TIF(T=0.0, I=1.0, F=0.0, I_system=1.0, H_lex=1.0, G_lex=1.0, I_lexicon=1.0)
            return _base_payload(
                triage_case,
                probability_payload={
                    "variable_count": 0,
                    "weighted_probability": {"T": 0.0, "I": 1.0, "F": 0.0},
                    "contradiction_load": 1.0,
                    "variables": [],
                },
                operational_tif=operational_tif,
                probability_load=1.0,
                contradiction_load=1.0,
                uncertainty_load=1.0,
                risk_signal=1.0,
                rough_region=RoughRegion.BOUNDARY_REGION.value,
                risk_priority=RiskPriority.CRITICAL_REVIEW.value,
            )

        probability_payload = summarize_plithogenic_probability_event(
            [criterion.as_probability_variable() for criterion in triage_case.criteria],
            name=triage_case.case_label,
        )
        weighted = probability_payload["weighted_probability"]
        probability_load = _weighted_probability_load(triage_case.criteria)
        contradiction_load = clamp01(float(probability_payload["contradiction_load"]))
        weighted_i = clamp01(float(weighted["I"]))
        uncertainty_load = clamp01(max(weighted_i, contradiction_load))
        risk_signal = clamp01(0.5 * float(weighted["T"]) + 0.3 * probability_load + 0.2 * contradiction_load)
        rough_region = _rough_region(risk_signal, uncertainty_load)
        risk_priority = _risk_priority(risk_signal, rough_region)
        operational_tif = TIF(
            T=clamp01(float(weighted["T"])),
            I=weighted_i,
            F=clamp01(float(weighted["F"])),
            I_system=uncertainty_load,
            H_lex=uncertainty_load,
            G_lex=contradiction_load,
            I_lexicon=uncertainty_load,
        )
        return _base_payload(
            triage_case,
            probability_payload=probability_payload,
            operational_tif=operational_tif,
            probability_load=probability_load,
            contradiction_load=contradiction_load,
            uncertainty_load=uncertainty_load,
            risk_signal=risk_signal,
            rough_region=rough_region,
            risk_priority=risk_priority,
        )


def score_risk_triage_case(raw: object) -> dict[str, object]:
    return RiskTriageReviewer().score(raw)


def build_food_safety_demo_case() -> RiskTriageCase:
    source_ids = (P2NRS_SOURCE_ID,)
    return RiskTriageCase(
        case_label="Synthetic milk batch review case",
        domain=RiskDomain.FOOD_SAFETY.value,
        criteria=(
            RiskCriterion(
                name="microbial_signal",
                value="elevated_possible_contamination",
                T=0.78,
                I=0.16,
                F=0.08,
                probability=0.72,
                weight=1.4,
                source_ids=source_ids,
                notes="Synthetic microbial indicator for public-safe review.",
            ),
            RiskCriterion(
                name="storage_temperature",
                value="temperature_excursion",
                T=0.68,
                I=0.24,
                F=0.10,
                probability=0.64,
                weight=1.1,
                source_ids=source_ids,
                notes="Synthetic storage condition signal.",
            ),
            RiskCriterion(
                name="supply_chain_disruption",
                value="traceability_gap",
                T=0.52,
                I=0.42,
                F=0.16,
                probability=0.58,
                weight=0.9,
                source_ids=source_ids,
                notes="Synthetic chain-of-custody uncertainty signal.",
            ),
            RiskCriterion(
                name="sensor_uncertainty",
                value="imprecise_sensor_record",
                T=0.46,
                I=0.50,
                F=0.20,
                probability=0.48,
                weight=0.8,
                source_ids=source_ids,
                notes="Synthetic missing-data and instrument uncertainty signal.",
            ),
            RiskCriterion(
                name="expert_disagreement",
                value="conflicting_review",
                T=0.44,
                I=0.56,
                F=0.22,
                probability=0.54,
                weight=0.8,
                source_ids=source_ids,
                notes="Synthetic expert disagreement signal.",
            ),
        ),
        source_ids=source_ids,
        reviewer_notes="Public-safe synthetic food-safety demo; not a safety declaration.",
    )


def _base_payload(
    case: RiskTriageCase,
    probability_payload: dict[str, object],
    operational_tif: TIF,
    probability_load: float,
    contradiction_load: float,
    uncertainty_load: float,
    risk_signal: float,
    rough_region: str,
    risk_priority: str,
) -> dict[str, object]:
    return {
        "case_label": case.case_label,
        "domain": case.domain,
        "criteria": [criterion.as_dict() for criterion in case.criteria],
        "source_ids": list(case.source_ids),
        "reviewer_notes": case.reviewer_notes,
        "related_taxon_packet": case.related_taxon_packet,
        "rough_region": rough_region,
        "risk_priority": risk_priority,
        "risk_signal": risk_signal,
        "probability_load": probability_load,
        "contradiction_load": contradiction_load,
        "uncertainty_load": uncertainty_load,
        "operational_tif": operational_tif.as_dict(),
        "plithogenic_probability": probability_payload,
        "human_review_required": True,
        "decision_boundary": (
            "Review support only; no public-health, food-safety, conservation, "
            "environmental, or taxonomic authority."
        ),
        "societal_use": [
            "education",
            "early triage",
            "expert review preparation",
            "source-linked uncertainty communication",
        ],
        "source_anchor": {
            "source_id": P2NRS_SOURCE_ID,
            "title": "A Probabilistic Plithogenic Neutrosophic Rough Set for Uncertainty-Aware Food Safety Analysis",
            "url": P2NRS_SOURCE_URL,
            "evidence_kind": "public_nss",
            "public_safe": True,
        },
        "hierarchy": HIERARCHY,
    }


def _weighted_probability_load(criteria: Iterable[RiskCriterion]) -> float:
    criteria = tuple(criteria)
    weights = [criterion.weight for criterion in criteria]
    weight_sum = sum(weights) or 1.0
    return clamp01(sum(criterion.operational_probability() * criterion.weight for criterion in criteria) / weight_sum)


def _rough_region(risk_signal: float, uncertainty_load: float) -> str:
    if risk_signal >= 0.70 and uncertainty_load <= 0.35:
        return RoughRegion.LOWER_APPROXIMATION.value
    if uncertainty_load > 0.35:
        return RoughRegion.BOUNDARY_REGION.value
    return RoughRegion.UPPER_APPROXIMATION.value


def _risk_priority(risk_signal: float, rough_region: str) -> str:
    if rough_region == RoughRegion.LOWER_APPROXIMATION.value or risk_signal >= 0.80:
        return RiskPriority.CRITICAL_REVIEW.value
    if rough_region == RoughRegion.BOUNDARY_REGION.value or risk_signal >= 0.55:
        return RiskPriority.ELEVATED.value
    if risk_signal >= 0.30:
        return RiskPriority.WATCH.value
    return RiskPriority.ROUTINE.value

