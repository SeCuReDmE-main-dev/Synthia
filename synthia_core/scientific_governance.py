"""Scientific governance reporting for bounded Synthia review outputs."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Mapping

from .plithogenic import TIF, clamp01
from .safety import HIERARCHY


NIST_AI_RMF_SOURCE_ID = "standard.nist_ai_risk_management_framework"
TRIPOD_AI_SOURCE_ID = "standard.tripod_ai_reporting"
MODEL_CARDS_SOURCE_ID = "standard.model_cards"
DATASHEETS_SOURCE_ID = "standard.datasheets_for_datasets"
FAIR_PRINCIPLES_SOURCE_ID = "standard.fair_principles"


class GovernanceStandard(str, Enum):
    AI_RISK_MANAGEMENT = "ai_risk_management"
    PREDICTIVE_REPORTING = "predictive_reporting"
    MODEL_CARD = "model_card"
    DATASET_SHEET = "dataset_sheet"
    FAIR_DATA = "fair_data"


class GovernancePriority(str, Enum):
    ROUTINE = "routine"
    WATCH = "watch"
    ELEVATED = "elevated"
    CRITICAL_REVIEW = "critical_review"


class ValidationStatus(str, Enum):
    DRAFT = "draft"
    SOURCE_LINKED = "source_linked"
    INTERNALLY_REVIEWED = "internally_reviewed"
    SPECIALIST_REVIEW_REQUIRED = "specialist_review_required"
    NOT_VALIDATED = "not_validated"


@dataclass(frozen=True)
class GovernanceEvidenceSource:
    source_id: str
    standard: str
    title: str
    url: str
    coverage_T: float
    coverage_I: float
    coverage_F: float
    weight: float = 1.0
    notes: str = ""

    @classmethod
    def from_raw(cls, raw: object, index: int) -> "GovernanceEvidenceSource":
        if not isinstance(raw, Mapping):
            raise ValueError("each governance evidence source must be a JSON object")
        return cls(
            source_id=str(raw.get("source_id", f"governance_source_{index + 1}")),
            standard=str(raw.get("standard", GovernanceStandard.AI_RISK_MANAGEMENT.value)),
            title=str(raw.get("title", f"Governance evidence source {index + 1}")),
            url=str(raw.get("url", "")),
            coverage_T=float(raw.get("coverage_T", raw.get("T", 0.0))),
            coverage_I=float(raw.get("coverage_I", raw.get("I", 0.0))),
            coverage_F=float(raw.get("coverage_F", raw.get("F", 0.0))),
            weight=max(0.0, float(raw.get("weight", 1.0))),
            notes=str(raw.get("notes", "")),
        )

    def operational_tif(self) -> TIF:
        return TIF(T=clamp01(self.coverage_T), I=clamp01(self.coverage_I), F=clamp01(self.coverage_F))

    def as_dict(self) -> dict[str, object]:
        return {
            "source_id": self.source_id,
            "standard": self.standard,
            "title": self.title,
            "url": self.url,
            "formal_value": {"T": self.coverage_T, "I": self.coverage_I, "F": self.coverage_F},
            "operational_tif": self.operational_tif().as_dict(),
            "weight": self.weight,
            "notes": self.notes,
        }


@dataclass(frozen=True)
class ScientificGovernanceCase:
    case_label: str
    review_subject: str
    intended_use: str
    out_of_scope_use: str
    evidence_sources: tuple[GovernanceEvidenceSource, ...]
    validation_status: str = ValidationStatus.SPECIALIST_REVIEW_REQUIRED.value
    source_ids: tuple[str, ...] = ()
    reviewer_notes: str = ""
    related_taxon_packet: Mapping[str, object] | None = None
    related_risk_case: Mapping[str, object] | None = None
    related_biology_graph: Mapping[str, object] | None = None
    related_molecular_review: Mapping[str, object] | None = None
    related_algorithm_behavior: Mapping[str, object] | None = None

    @classmethod
    def from_raw_case(cls, raw: object) -> "ScientificGovernanceCase":
        if not isinstance(raw, Mapping):
            raise ValueError("scientific governance case must be a JSON object")
        evidence_sources = raw.get("evidence_sources", [])
        if not isinstance(evidence_sources, list):
            raise ValueError("scientific governance case evidence_sources must be a JSON array")
        return cls(
            case_label=str(raw.get("case_label", "unnamed scientific governance case")),
            review_subject=str(raw.get("review_subject", "")),
            intended_use=str(raw.get("intended_use", "educational review support")),
            out_of_scope_use=str(raw.get("out_of_scope_use", "scientific certification or autonomous decision-making")),
            evidence_sources=tuple(GovernanceEvidenceSource.from_raw(item, index) for index, item in enumerate(evidence_sources)),
            validation_status=str(raw.get("validation_status", ValidationStatus.SPECIALIST_REVIEW_REQUIRED.value)),
            source_ids=_source_ids(raw.get("source_ids", ())),
            reviewer_notes=str(raw.get("reviewer_notes", "")),
            related_taxon_packet=_optional_mapping(raw.get("related_taxon_packet"), "related_taxon_packet"),
            related_risk_case=_optional_mapping(raw.get("related_risk_case"), "related_risk_case"),
            related_biology_graph=_optional_mapping(raw.get("related_biology_graph"), "related_biology_graph"),
            related_molecular_review=_optional_mapping(raw.get("related_molecular_review"), "related_molecular_review"),
            related_algorithm_behavior=_optional_mapping(raw.get("related_algorithm_behavior"), "related_algorithm_behavior"),
        )


class ScientificGovernanceReviewer:
    def score(self, case: ScientificGovernanceCase | object) -> dict[str, object]:
        review_case = case if isinstance(case, ScientificGovernanceCase) else ScientificGovernanceCase.from_raw_case(case)
        if not review_case.evidence_sources:
            operational_tif = TIF(T=0.0, I=1.0, F=0.0, I_system=1.0, H_lex=1.0, G_lex=1.0, I_lexicon=1.0)
            return _base_payload(
                review_case,
                operational_tif=operational_tif,
                reporting_standard_coverage=_empty_standard_coverage(),
                evidence_gap_load=1.0,
                contradiction_load=1.0,
                uncertainty_load=1.0,
                governance_priority=GovernancePriority.CRITICAL_REVIEW.value,
            )

        weighted_tif = _weighted_tif(review_case.evidence_sources)
        reporting_standard_coverage = _reporting_standard_coverage(review_case.evidence_sources)
        evidence_gap_load = _evidence_gap_load(review_case.evidence_sources, weighted_tif)
        contradiction_load = _contradiction_load(review_case.evidence_sources)
        uncertainty_load = clamp01(max(weighted_tif.I, evidence_gap_load, contradiction_load))
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
            reporting_standard_coverage=reporting_standard_coverage,
            evidence_gap_load=evidence_gap_load,
            contradiction_load=contradiction_load,
            uncertainty_load=uncertainty_load,
            governance_priority=_governance_priority(max(uncertainty_load, evidence_gap_load)),
        )


def score_scientific_governance_case(raw: object) -> dict[str, object]:
    return ScientificGovernanceReviewer().score(raw)


def build_synthia_governance_demo_case() -> ScientificGovernanceCase:
    evidence_sources = (
        GovernanceEvidenceSource(
            source_id=NIST_AI_RMF_SOURCE_ID,
            standard=GovernanceStandard.AI_RISK_MANAGEMENT.value,
            title="NIST AI Risk Management Framework",
            url="https://www.nist.gov/itl/ai-risk-management-framework",
            coverage_T=0.78,
            coverage_I=0.18,
            coverage_F=0.06,
            weight=1.2,
            notes="Risk-management framing for transparent, bounded AI review.",
        ),
        GovernanceEvidenceSource(
            source_id=TRIPOD_AI_SOURCE_ID,
            standard=GovernanceStandard.PREDICTIVE_REPORTING.value,
            title="TRIPOD+AI reporting guidance",
            url="https://www.tripod-statement.org/",
            coverage_T=0.70,
            coverage_I=0.24,
            coverage_F=0.08,
            weight=1.0,
            notes="Predictive reporting anchor; not a validation claim.",
        ),
        GovernanceEvidenceSource(
            source_id=MODEL_CARDS_SOURCE_ID,
            standard=GovernanceStandard.MODEL_CARD.value,
            title="Model Cards for Model Reporting",
            url="https://arxiv.org/abs/1810.03993",
            coverage_T=0.82,
            coverage_I=0.14,
            coverage_F=0.05,
            weight=1.1,
            notes="Model-facing intended use and limitation reporting.",
        ),
        GovernanceEvidenceSource(
            source_id=DATASHEETS_SOURCE_ID,
            standard=GovernanceStandard.DATASET_SHEET.value,
            title="Datasheets for Datasets",
            url="https://arxiv.org/abs/1803.09010",
            coverage_T=0.76,
            coverage_I=0.20,
            coverage_F=0.06,
            weight=1.1,
            notes="Dataset provenance and reuse-boundary reporting.",
        ),
        GovernanceEvidenceSource(
            source_id=FAIR_PRINCIPLES_SOURCE_ID,
            standard=GovernanceStandard.FAIR_DATA.value,
            title="FAIR Principles",
            url="https://www.go-fair.org/fair-principles/",
            coverage_T=0.74,
            coverage_I=0.22,
            coverage_F=0.06,
            weight=1.0,
            notes="Metadata visibility and reuse-readiness anchor.",
        ),
    )
    source_ids = tuple(source.source_id for source in evidence_sources)
    return ScientificGovernanceCase(
        case_label="Synthetic Synthia governance reporting case",
        review_subject="Synthia Phase 1-5 review-output reporting packet",
        intended_use="Education, evidence reporting, source traceability, and specialist-review preparation.",
        out_of_scope_use="Scientific certification, regulatory approval, diagnosis, formal taxonomy, or autonomous conclusion.",
        evidence_sources=evidence_sources,
        validation_status=ValidationStatus.SOURCE_LINKED.value,
        source_ids=source_ids,
        reviewer_notes="Public-safe synthetic governance demo; standards are anchors, not runtime dependencies.",
        related_algorithm_behavior={"case_label": "Synthetic algorithm behavior review", "human_review_required": True},
        related_molecular_review={"case_label": "Synthetic molecular evidence review", "human_review_required": True},
    )


def _base_payload(
    case: ScientificGovernanceCase,
    operational_tif: TIF,
    reporting_standard_coverage: Mapping[str, float],
    evidence_gap_load: float,
    contradiction_load: float,
    uncertainty_load: float,
    governance_priority: str,
) -> dict[str, object]:
    return {
        "case_label": case.case_label,
        "review_subject": case.review_subject,
        "intended_use": case.intended_use,
        "out_of_scope_use": case.out_of_scope_use,
        "evidence_sources": [source.as_dict() for source in case.evidence_sources],
        "source_ids": list(_all_source_ids(case)),
        "reporting_standard_coverage": dict(reporting_standard_coverage),
        "model_card": _model_card(case),
        "dataset_sheet": _dataset_sheet(case),
        "validation_status": case.validation_status,
        "governance_priority": governance_priority,
        "evidence_gap_load": evidence_gap_load,
        "contradiction_load": contradiction_load,
        "uncertainty_load": uncertainty_load,
        "operational_tif": operational_tif.as_dict(),
        "related_taxon_packet": case.related_taxon_packet,
        "related_risk_case": case.related_risk_case,
        "related_biology_graph": case.related_biology_graph,
        "related_molecular_review": case.related_molecular_review,
        "related_algorithm_behavior": case.related_algorithm_behavior,
        "reviewer_notes": case.reviewer_notes,
        "human_review_required": True,
        "authority_boundary": (
            "Review support only; no scientific certification, no regulatory approval, no diagnostic result, "
            "no formal taxonomic act, and no autonomous scientific conclusion."
        ),
        "scientific_boundary": "Reporting improves transparency and traceability, but it does not replace expert review.",
        "hierarchy": HIERARCHY,
    }


def _model_card(case: ScientificGovernanceCase) -> dict[str, object]:
    return {
        "review_subject": case.review_subject,
        "intended_use": case.intended_use,
        "limitations": case.out_of_scope_use,
        "human_review_required": True,
        "validation_status": case.validation_status,
        "linked_phase_payloads": _linked_phase_payload_names(case),
    }


def _dataset_sheet(case: ScientificGovernanceCase) -> dict[str, object]:
    coverage = _reporting_standard_coverage(case.evidence_sources)
    return {
        "source_provenance": list(_all_source_ids(case)),
        "sensitivity": "public_safe_or_user_supplied_metadata",
        "approval_state": "pending_specialist_review",
        "reuse_boundary": "education, traceability, and review preparation only",
        "fair_metadata_status": "source_linked" if coverage.get(GovernanceStandard.FAIR_DATA.value, 0.0) > 0 else "missing",
    }


def _linked_phase_payload_names(case: ScientificGovernanceCase) -> list[str]:
    payloads = (
        ("phase_1_taxon_packet", case.related_taxon_packet),
        ("phase_2_risk_case", case.related_risk_case),
        ("phase_3_biology_graph", case.related_biology_graph),
        ("phase_4_molecular_review", case.related_molecular_review),
        ("phase_5_algorithm_behavior", case.related_algorithm_behavior),
    )
    return [label for label, payload in payloads if payload is not None]


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


def _weighted_tif(sources: Iterable[GovernanceEvidenceSource]) -> TIF:
    sources = tuple(sources)
    if not sources:
        return TIF(T=0.0, I=1.0, F=0.0)
    weight_sum = sum(source.weight for source in sources) or 1.0
    return TIF(
        T=clamp01(sum(source.operational_tif().T * source.weight for source in sources) / weight_sum),
        I=clamp01(sum(source.operational_tif().I * source.weight for source in sources) / weight_sum),
        F=clamp01(sum(source.operational_tif().F * source.weight for source in sources) / weight_sum),
    )


def _reporting_standard_coverage(sources: Iterable[GovernanceEvidenceSource]) -> dict[str, float]:
    loads = _empty_standard_coverage()
    for source in sources:
        loads[source.standard] = loads.get(source.standard, 0.0) + source.weight
    total = sum(loads.values()) or 1.0
    return {standard: clamp01(load / total) for standard, load in sorted(loads.items())}


def _empty_standard_coverage() -> dict[str, float]:
    return {standard.value: 0.0 for standard in GovernanceStandard}


def _evidence_gap_load(sources: Iterable[GovernanceEvidenceSource], weighted_tif: TIF) -> float:
    sources = tuple(sources)
    present = {source.standard for source in sources}
    missing = [standard.value for standard in GovernanceStandard if standard.value not in present]
    missing_fraction = len(missing) / len(GovernanceStandard)
    return clamp01((0.65 * missing_fraction) + (0.35 * weighted_tif.I))


def _contradiction_load(sources: Iterable[GovernanceEvidenceSource]) -> float:
    sources = tuple(sources)
    if not sources:
        return 1.0
    weight_sum = sum(source.weight for source in sources) or 1.0
    load = 0.0
    for source in sources:
        tif = source.operational_tif()
        load += tif.T * max(tif.I, tif.F) * source.weight
    return clamp01(load / weight_sum)


def _governance_priority(signal: float) -> str:
    if signal >= 0.75:
        return GovernancePriority.CRITICAL_REVIEW.value
    if signal >= 0.50:
        return GovernancePriority.ELEVATED.value
    if signal >= 0.25:
        return GovernancePriority.WATCH.value
    return GovernancePriority.ROUTINE.value


def _all_source_ids(case: ScientificGovernanceCase) -> tuple[str, ...]:
    seen: set[str] = set()
    ordered: list[str] = []
    for source_id in case.source_ids:
        if source_id not in seen:
            seen.add(source_id)
            ordered.append(source_id)
    for source in case.evidence_sources:
        if source.source_id not in seen:
            seen.add(source.source_id)
            ordered.append(source.source_id)
    return tuple(ordered)
