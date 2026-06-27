"""Algorithmic parameter behavior guardrails for bounded review support."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Mapping

from .plithogenic import TIF, clamp01
from .safety import HIERARCHY


ALGORITHMIC_PARAMETER_CORPUS_SOURCE_ID = "source.algorithmic_parameter_corpus"
ALGORITHMIC_BEHAVIOR_SEED_SOURCE_ID = "rag.algorithmic_behavior_seed_2026_06_27"


class BehaviorFamily(str, Enum):
    REGULARIZATION_CONSTRAINTS = "regularization_constraints"
    LOSS_DISTRIBUTION_LINK = "loss_distribution_link"
    OPTIMIZATION_CONVERGENCE = "optimization_convergence"
    TREE_STRUCTURE_SAMPLING = "tree_structure_sampling"
    VALIDATION_STOPPING_CHECKPOINTING = "validation_stopping_checkpointing"
    DATA_PREPROCESSING_ENCODING = "data_preprocessing_encoding"
    SEARCH_ENSEMBLING = "search_ensembling"
    DIMENSIONALITY_CLUSTERING = "dimensionality_clustering"
    CLASS_BALANCE_CALIBRATION = "class_balance_calibration"
    REPRODUCIBILITY_RESOURCE_CONTROL = "reproducibility_resource_control"
    GENERAL_MODEL_CONTRACT = "general_model_contract"


class AlgorithmReviewPriority(str, Enum):
    ROUTINE = "routine"
    WATCH = "watch"
    ELEVATED = "elevated"
    CRITICAL_REVIEW = "critical_review"


@dataclass(frozen=True)
class AlgorithmParameterRecord:
    name: str
    algorithm_family: str
    behavior_families: tuple[str, ...]
    hyperparameter: str
    T: float
    I: float
    F: float
    weight: float = 1.0
    source_ids: tuple[str, ...] = ()
    notes: str = ""
    configured_value: object | None = None
    expected_role: str = ""
    validation_status: str = "unknown"
    bioinformatics_relevance: float = 0.5

    @classmethod
    def from_raw(cls, raw: object, index: int) -> "AlgorithmParameterRecord":
        if not isinstance(raw, Mapping):
            raise ValueError("each algorithm parameter record must be a JSON object")
        behavior_families = raw.get("behavior_families", ())
        if isinstance(behavior_families, str):
            behavior_families = (behavior_families,)
        elif behavior_families is None:
            behavior_families = ()
        elif not isinstance(behavior_families, list):
            raise ValueError("algorithm parameter behavior_families must be a JSON array when provided")
        return cls(
            name=str(raw.get("name", f"parameter_{index + 1}")),
            algorithm_family=str(raw.get("algorithm_family", "review_context")),
            behavior_families=tuple(str(family) for family in behavior_families),
            hyperparameter=str(raw.get("hyperparameter", "unknown")),
            T=float(raw.get("T", 0.0)),
            I=float(raw.get("I", 0.0)),
            F=float(raw.get("F", 0.0)),
            weight=max(0.0, float(raw.get("weight", 1.0))),
            source_ids=_source_ids(raw.get("source_ids", ())),
            notes=str(raw.get("notes", "")),
            configured_value=raw.get("configured_value"),
            expected_role=str(raw.get("expected_role", "")),
            validation_status=str(raw.get("validation_status", "unknown")),
            bioinformatics_relevance=float(raw.get("bioinformatics_relevance", 0.5)),
        )

    def operational_tif(self) -> TIF:
        return TIF(T=clamp01(self.T), I=clamp01(self.I), F=clamp01(self.F))

    def behavior_signal(self) -> float:
        tif = self.operational_tif()
        validation = _validation_signal(self.validation_status)
        relevance = clamp01(self.bioinformatics_relevance)
        return clamp01((0.45 * tif.T) + (0.30 * validation) + (0.25 * relevance))

    def as_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "algorithm_family": self.algorithm_family,
            "behavior_families": list(self.behavior_families),
            "hyperparameter": self.hyperparameter,
            "formal_value": {"T": self.T, "I": self.I, "F": self.F},
            "operational_tif": self.operational_tif().as_dict(),
            "configured_value": self.configured_value,
            "expected_role": self.expected_role,
            "validation_status": self.validation_status,
            "bioinformatics_relevance": self.bioinformatics_relevance,
            "operational_bioinformatics_relevance": clamp01(self.bioinformatics_relevance),
            "behavior_signal": self.behavior_signal(),
            "weight": self.weight,
            "source_ids": list(self.source_ids),
            "notes": self.notes,
        }


@dataclass(frozen=True)
class AlgorithmBehaviorCase:
    case_label: str
    algorithm_context: str
    parameter_records: tuple[AlgorithmParameterRecord, ...]
    source_ids: tuple[str, ...] = ()
    reviewer_notes: str = ""
    related_molecular_review: Mapping[str, object] | None = None
    related_biology_graph: Mapping[str, object] | None = None

    @classmethod
    def from_raw_case(cls, raw: object) -> "AlgorithmBehaviorCase":
        if not isinstance(raw, Mapping):
            raise ValueError("algorithm behavior case must be a JSON object")
        parameter_records = raw.get("parameter_records", [])
        if not isinstance(parameter_records, list):
            raise ValueError("algorithm behavior case parameter_records must be a JSON array")
        return cls(
            case_label=str(raw.get("case_label", "unnamed algorithm behavior case")),
            algorithm_context=str(raw.get("algorithm_context", "")),
            parameter_records=tuple(
                AlgorithmParameterRecord.from_raw(item, index) for index, item in enumerate(parameter_records)
            ),
            source_ids=_source_ids(raw.get("source_ids", ())),
            reviewer_notes=str(raw.get("reviewer_notes", "")),
            related_molecular_review=_optional_mapping(raw.get("related_molecular_review"), "related_molecular_review"),
            related_biology_graph=_optional_mapping(raw.get("related_biology_graph"), "related_biology_graph"),
        )

    def dominant_behavior_family(self) -> str | None:
        family_loads = _behavior_family_loads(self.parameter_records)
        if not family_loads:
            return None
        return sorted(family_loads.items(), key=lambda item: (-item[1], item[0]))[0][0]


class AlgorithmBehaviorReviewer:
    def score(self, case: AlgorithmBehaviorCase | object) -> dict[str, object]:
        review_case = case if isinstance(case, AlgorithmBehaviorCase) else AlgorithmBehaviorCase.from_raw_case(case)
        if not review_case.parameter_records:
            operational_tif = TIF(T=0.0, I=1.0, F=0.0, I_system=1.0, H_lex=1.0, G_lex=1.0, I_lexicon=1.0)
            return _base_payload(
                review_case,
                operational_tif=operational_tif,
                behavior_family_loads={},
                algorithmic_risk_signal=1.0,
                contradiction_load=1.0,
                uncertainty_load=1.0,
                review_priority=AlgorithmReviewPriority.CRITICAL_REVIEW.value,
            )

        weighted_tif = _weighted_tif(review_case.parameter_records)
        behavior_family_loads = _behavior_family_loads(review_case.parameter_records)
        algorithmic_risk_signal = _algorithmic_risk_signal(review_case.parameter_records)
        contradiction_load = _contradiction_load(review_case.parameter_records)
        uncertainty_load = clamp01(max(weighted_tif.I, contradiction_load, algorithmic_risk_signal))
        operational_tif = TIF(
            T=weighted_tif.T,
            I=weighted_tif.I,
            F=weighted_tif.F,
            I_system=uncertainty_load,
            H_lex=uncertainty_load,
            G_lex=contradiction_load,
            I_lexicon=uncertainty_load,
        )
        return _base_payload(
            review_case,
            operational_tif=operational_tif,
            behavior_family_loads=behavior_family_loads,
            algorithmic_risk_signal=algorithmic_risk_signal,
            contradiction_load=contradiction_load,
            uncertainty_load=uncertainty_load,
            review_priority=_review_priority(algorithmic_risk_signal),
        )


def score_algorithm_behavior_case(raw: object) -> dict[str, object]:
    return AlgorithmBehaviorReviewer().score(raw)


def build_algorithmic_bioinformatics_demo_case() -> AlgorithmBehaviorCase:
    source_ids = (ALGORITHMIC_PARAMETER_CORPUS_SOURCE_ID, ALGORITHMIC_BEHAVIOR_SEED_SOURCE_ID)
    return AlgorithmBehaviorCase(
        case_label="Synthetic bioinformatics algorithm behavior review",
        algorithm_context="Sequence-evidence review pipeline parameter audit",
        parameter_records=(
            AlgorithmParameterRecord(
                name="distribution",
                algorithm_family="objective_family",
                behavior_families=(BehaviorFamily.LOSS_DISTRIBUTION_LINK.value,),
                hyperparameter="yes",
                T=0.72,
                I=0.24,
                F=0.08,
                weight=1.2,
                source_ids=source_ids,
                expected_role="Defines the objective surface before biological interpretation.",
                validation_status="reviewed",
                bioinformatics_relevance=0.9,
            ),
            AlgorithmParameterRecord(
                name="lambda",
                algorithm_family="regularization_family",
                behavior_families=(BehaviorFamily.REGULARIZATION_CONSTRAINTS.value,),
                hyperparameter="yes",
                T=0.68,
                I=0.28,
                F=0.10,
                weight=1.0,
                source_ids=source_ids,
                expected_role="Constrains model capacity and reduces overfit risk.",
                validation_status="partially_reviewed",
                bioinformatics_relevance=0.8,
            ),
            AlgorithmParameterRecord(
                name="nfolds",
                algorithm_family="validation_family",
                behavior_families=(BehaviorFamily.VALIDATION_STOPPING_CHECKPOINTING.value,),
                hyperparameter="no",
                T=0.74,
                I=0.18,
                F=0.06,
                weight=1.3,
                source_ids=source_ids,
                expected_role="Keeps training artifacts separate from reviewable signals.",
                validation_status="reviewed",
                bioinformatics_relevance=0.85,
            ),
            AlgorithmParameterRecord(
                name="stopping_metric",
                algorithm_family="validation_family",
                behavior_families=(
                    BehaviorFamily.LOSS_DISTRIBUTION_LINK.value,
                    BehaviorFamily.VALIDATION_STOPPING_CHECKPOINTING.value,
                ),
                hyperparameter="yes",
                T=0.66,
                I=0.30,
                F=0.12,
                weight=1.1,
                source_ids=source_ids,
                expected_role="Defines when the algorithm stops improving enough for review.",
                validation_status="partially_reviewed",
                bioinformatics_relevance=0.75,
            ),
            AlgorithmParameterRecord(
                name="categorical_encoding",
                algorithm_family="data_semantics_family",
                behavior_families=(BehaviorFamily.DATA_PREPROCESSING_ENCODING.value,),
                hyperparameter="yes",
                T=0.64,
                I=0.32,
                F=0.14,
                weight=1.0,
                source_ids=source_ids,
                expected_role="Controls how categorical biological metadata enter the model.",
                validation_status="unknown",
                bioinformatics_relevance=0.7,
            ),
            AlgorithmParameterRecord(
                name="seed",
                algorithm_family="reproducibility_family",
                behavior_families=(BehaviorFamily.REPRODUCIBILITY_RESOURCE_CONTROL.value,),
                hyperparameter="yes",
                T=0.80,
                I=0.14,
                F=0.04,
                weight=0.9,
                source_ids=source_ids,
                expected_role="Preserves deterministic replay for human audit.",
                validation_status="reviewed",
                bioinformatics_relevance=0.65,
            ),
        ),
        source_ids=source_ids,
        reviewer_notes="Public-safe synthetic demo; no model-performance guarantee or biological conclusion.",
    )


def _base_payload(
    case: AlgorithmBehaviorCase,
    operational_tif: TIF,
    behavior_family_loads: Mapping[str, float],
    algorithmic_risk_signal: float,
    contradiction_load: float,
    uncertainty_load: float,
    review_priority: str,
) -> dict[str, object]:
    dominant = case.dominant_behavior_family()
    return {
        "case_label": case.case_label,
        "algorithm_context": case.algorithm_context,
        "parameter_records": [record.as_dict() for record in case.parameter_records],
        "source_ids": list(_all_source_ids(case)),
        "behavior_family_loads": dict(behavior_family_loads),
        "algorithm_count": len({record.algorithm_family for record in case.parameter_records}),
        "parameter_count": len(case.parameter_records),
        "dominant_behavior_family": dominant,
        "algorithmic_risk_signal": algorithmic_risk_signal,
        "contradiction_load": contradiction_load,
        "uncertainty_load": uncertainty_load,
        "operational_tif": operational_tif.as_dict(),
        "review_priority": review_priority,
        "related_molecular_review": case.related_molecular_review,
        "related_biology_graph": case.related_biology_graph,
        "reviewer_notes": case.reviewer_notes,
        "human_review_required": True,
        "authority_boundary": (
            "Review support only; no model-performance guarantee, no biological conclusion, "
            "formal taxonomic act, diagnostic result, or autonomous scientific authority."
        ),
        "scientific_boundary": (
            "Algorithm parameters condition biological interpretation and must remain visible before "
            "any specialist interprets model output."
        ),
        "source_anchor": {
            "source_id": ALGORITHMIC_BEHAVIOR_SEED_SOURCE_ID,
            "title": "Synthia Phase 5 algorithmic parameter behavior seed",
            "evidence_kind": "private_sanitized_rag_seed",
            "public_safe": True,
            "vendor_terms_admitted": False,
        },
        "hierarchy": HIERARCHY,
    }


def _source_ids(value: object) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    if isinstance(value, Iterable):
        return tuple(str(item) for item in value)
    return (str(value),)


def _optional_mapping(value: object, label: str) -> Mapping[str, object] | None:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must be a JSON object when provided")
    return value


def _weighted_tif(records: Iterable[AlgorithmParameterRecord]) -> TIF:
    records = tuple(records)
    if not records:
        return TIF(T=0.0, I=1.0, F=0.0)
    weight_sum = sum(record.weight for record in records) or 1.0
    return TIF(
        T=clamp01(sum(record.operational_tif().T * record.weight for record in records) / weight_sum),
        I=clamp01(sum(record.operational_tif().I * record.weight for record in records) / weight_sum),
        F=clamp01(sum(record.operational_tif().F * record.weight for record in records) / weight_sum),
    )


def _behavior_family_loads(records: Iterable[AlgorithmParameterRecord]) -> dict[str, float]:
    loads: dict[str, float] = {}
    for record in records:
        families = record.behavior_families or (BehaviorFamily.GENERAL_MODEL_CONTRACT.value,)
        share = record.weight / len(families) if families else record.weight
        for family in families:
            loads[family] = loads.get(family, 0.0) + share
    total = sum(loads.values()) or 1.0
    return {family: clamp01(load / total) for family, load in sorted(loads.items())}


def _algorithmic_risk_signal(records: Iterable[AlgorithmParameterRecord]) -> float:
    records = tuple(records)
    if not records:
        return 1.0
    weight_sum = sum(record.weight for record in records) or 1.0
    signal = 0.0
    for record in records:
        tif = record.operational_tif()
        validation_risk = 1.0 - _validation_signal(record.validation_status)
        relevance = clamp01(record.bioinformatics_relevance)
        high_impact = _high_impact_family_signal(record.behavior_families)
        signal += max(tif.I, tif.F, validation_risk * relevance, high_impact * tif.I) * record.weight
    return clamp01(signal / weight_sum)


def _contradiction_load(records: Iterable[AlgorithmParameterRecord]) -> float:
    records = tuple(records)
    if not records:
        return 1.0
    weight_sum = sum(record.weight for record in records) or 1.0
    load = 0.0
    for record in records:
        tif = record.operational_tif()
        load += record.behavior_signal() * max(tif.I, tif.F) * record.weight
    return clamp01(load / weight_sum)


def _validation_signal(status: str) -> float:
    normalized = status.strip().lower().replace("-", "_").replace(" ", "_")
    if normalized in {"validated", "reviewed", "approved"}:
        return 1.0
    if normalized in {"partially_reviewed", "partial", "limited"}:
        return 0.55
    if normalized in {"failed", "rejected", "invalid"}:
        return 0.0
    return 0.25


def _high_impact_family_signal(families: Iterable[str]) -> float:
    high_impact = {
        BehaviorFamily.LOSS_DISTRIBUTION_LINK.value,
        BehaviorFamily.REGULARIZATION_CONSTRAINTS.value,
        BehaviorFamily.VALIDATION_STOPPING_CHECKPOINTING.value,
        BehaviorFamily.DATA_PREPROCESSING_ENCODING.value,
    }
    family_set = set(families)
    if not family_set:
        return 0.25
    return 1.0 if family_set & high_impact else 0.45


def _review_priority(signal: float) -> str:
    if signal >= 0.75:
        return AlgorithmReviewPriority.CRITICAL_REVIEW.value
    if signal >= 0.50:
        return AlgorithmReviewPriority.ELEVATED.value
    if signal >= 0.25:
        return AlgorithmReviewPriority.WATCH.value
    return AlgorithmReviewPriority.ROUTINE.value


def _all_source_ids(case: AlgorithmBehaviorCase) -> tuple[str, ...]:
    seen: set[str] = set()
    ordered: list[str] = []
    for source_id in case.source_ids:
        if source_id not in seen:
            seen.add(source_id)
            ordered.append(source_id)
    for record in case.parameter_records:
        for source_id in record.source_ids:
            if source_id not in seen:
                seen.add(source_id)
                ordered.append(source_id)
    return tuple(ordered)
