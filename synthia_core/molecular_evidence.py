"""Molecular sequence evidence guardrails for bounded review support."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Mapping

from .plithogenic import TIF, clamp01
from .safety import HIERARCHY


NSS_DNA_SEQUENCE_SOURCE_ID = "nss.dna_sequence_neutrosophic_similarity"
NCBI_BLAST_GUARDRAIL_SOURCE_ID = "guardrail.ncbi_blast"
NCBI_DATASETS_GUARDRAIL_SOURCE_ID = "guardrail.ncbi_datasets"
ENSEMBL_GUARDRAIL_SOURCE_ID = "guardrail.ensembl"


class MoleculeType(str, Enum):
    DNA = "dna"
    RNA = "rna"
    PROTEIN = "protein"
    MARKER_GENE = "marker_gene"
    GENOME_REGION = "genome_region"


class EvidenceProvider(str, Enum):
    NCBI_BLAST = "ncbi_blast"
    NCBI_DATASETS = "ncbi_datasets"
    ENSEMBL = "ensembl"
    CURATED_PUBLIC_FIXTURE = "curated_public_fixture"


class MolecularReviewPriority(str, Enum):
    ROUTINE = "routine"
    WATCH = "watch"
    ELEVATED = "elevated"
    CRITICAL_REVIEW = "critical_review"


@dataclass(frozen=True)
class MolecularEvidenceRecord:
    id: str
    provider: str
    molecule_type: str
    label: str
    accession: str
    taxon_label: str
    taxon_id: str
    T: float
    I: float
    F: float
    weight: float = 1.0
    source_ids: tuple[str, ...] = ()
    notes: str = ""
    percent_identity: float | None = None
    query_coverage: float | None = None
    evalue: float | None = None
    bit_score: float | None = None
    annotation_match: bool | None = None
    taxon_match: bool | None = None

    @classmethod
    def from_raw(cls, raw: object, index: int) -> "MolecularEvidenceRecord":
        if not isinstance(raw, Mapping):
            raise ValueError("each molecular evidence record must be a JSON object")
        return cls(
            id=str(raw.get("id", f"molecular_evidence_{index + 1}")),
            provider=str(raw.get("provider", EvidenceProvider.CURATED_PUBLIC_FIXTURE.value)),
            molecule_type=str(raw.get("molecule_type", MoleculeType.DNA.value)),
            label=str(raw.get("label", raw.get("accession", f"Molecular evidence {index + 1}"))),
            accession=str(raw.get("accession", "")),
            taxon_label=str(raw.get("taxon_label", "")),
            taxon_id=str(raw.get("taxon_id", "")),
            T=float(raw.get("T", 0.0)),
            I=float(raw.get("I", 0.0)),
            F=float(raw.get("F", 0.0)),
            weight=max(0.0, float(raw.get("weight", 1.0))),
            source_ids=_source_ids(raw.get("source_ids", ())),
            notes=str(raw.get("notes", "")),
            percent_identity=_optional_float(raw.get("percent_identity")),
            query_coverage=_optional_float(raw.get("query_coverage")),
            evalue=_optional_float(raw.get("evalue")),
            bit_score=_optional_float(raw.get("bit_score")),
            annotation_match=_optional_bool(raw.get("annotation_match")),
            taxon_match=_optional_bool(raw.get("taxon_match")),
        )

    def operational_tif(self) -> TIF:
        return TIF(T=clamp01(self.T), I=clamp01(self.I), F=clamp01(self.F))

    def formal_metrics(self) -> dict[str, object]:
        return {
            "percent_identity": self.percent_identity,
            "query_coverage": self.query_coverage,
            "evalue": self.evalue,
            "bit_score": self.bit_score,
            "annotation_match": self.annotation_match,
            "taxon_match": self.taxon_match,
        }

    def operational_metrics(self) -> dict[str, object]:
        return {
            "percent_identity": None if self.percent_identity is None else clamp01(self.percent_identity / 100.0),
            "query_coverage": None if self.query_coverage is None else clamp01(self.query_coverage / 100.0),
            "evalue": self.evalue,
            "bit_score": None if self.bit_score is None else clamp01(self.bit_score / 1000.0),
            "annotation_match": None if self.annotation_match is None else (1.0 if self.annotation_match else 0.0),
            "taxon_match": None if self.taxon_match is None else (1.0 if self.taxon_match else 0.0),
            "evalue_boundary": "evalue is retained as source metadata, not converted into truth probability",
        }

    def molecular_signal(self) -> float:
        metrics = self.operational_metrics()
        values = [self.operational_tif().T]
        for key in ("percent_identity", "query_coverage", "bit_score", "annotation_match", "taxon_match"):
            value = metrics[key]
            if value is not None:
                values.append(float(value))
        return clamp01(sum(values) / (len(values) or 1))

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "provider": self.provider,
            "molecule_type": self.molecule_type,
            "label": self.label,
            "accession": self.accession,
            "taxon_label": self.taxon_label,
            "taxon_id": self.taxon_id,
            "formal_value": {"T": self.T, "I": self.I, "F": self.F},
            "operational_tif": self.operational_tif().as_dict(),
            "formal_metrics": self.formal_metrics(),
            "operational_metrics": self.operational_metrics(),
            "molecular_signal": self.molecular_signal(),
            "weight": self.weight,
            "source_ids": list(self.source_ids),
            "notes": self.notes,
        }


@dataclass(frozen=True)
class MolecularReviewCase:
    case_label: str
    query_label: str
    molecule_type: str
    evidence_records: tuple[MolecularEvidenceRecord, ...]
    source_ids: tuple[str, ...] = ()
    reviewer_notes: str = ""
    related_taxon_packet: Mapping[str, object] | None = None
    related_risk_case: Mapping[str, object] | None = None
    related_biology_graph: Mapping[str, object] | None = None

    @classmethod
    def from_raw_case(cls, raw: object) -> "MolecularReviewCase":
        if not isinstance(raw, Mapping):
            raise ValueError("molecular review case must be a JSON object")
        evidence_records = raw.get("evidence_records", [])
        if not isinstance(evidence_records, list):
            raise ValueError("molecular review case evidence_records must be a JSON array")
        related_taxon_packet = _optional_mapping(raw.get("related_taxon_packet"), "related_taxon_packet")
        related_risk_case = _optional_mapping(raw.get("related_risk_case"), "related_risk_case")
        related_biology_graph = _optional_mapping(raw.get("related_biology_graph"), "related_biology_graph")
        return cls(
            case_label=str(raw.get("case_label", "unnamed molecular review case")),
            query_label=str(raw.get("query_label", "")),
            molecule_type=str(raw.get("molecule_type", MoleculeType.DNA.value)),
            evidence_records=tuple(MolecularEvidenceRecord.from_raw(item, index) for index, item in enumerate(evidence_records)),
            source_ids=_source_ids(raw.get("source_ids", ())),
            reviewer_notes=str(raw.get("reviewer_notes", "")),
            related_taxon_packet=related_taxon_packet,
            related_risk_case=related_risk_case,
            related_biology_graph=related_biology_graph,
        )

    def dominant_evidence_record(self) -> MolecularEvidenceRecord | None:
        if not self.evidence_records:
            return None
        return sorted(self.evidence_records, key=lambda record: (-record.weight, -record.molecular_signal(), record.id))[0]


class MolecularEvidenceReviewer:
    def score(self, case: MolecularReviewCase | object) -> dict[str, object]:
        review_case = case if isinstance(case, MolecularReviewCase) else MolecularReviewCase.from_raw_case(case)
        if not review_case.evidence_records:
            operational_tif = TIF(T=0.0, I=1.0, F=0.0, I_system=1.0, H_lex=1.0, G_lex=1.0, I_lexicon=1.0)
            return _base_payload(
                review_case,
                operational_tif=operational_tif,
                molecular_support_signal=0.0,
                contradiction_load=1.0,
                uncertainty_load=1.0,
                review_priority=MolecularReviewPriority.CRITICAL_REVIEW.value,
            )

        weighted_tif = _weighted_tif(review_case.evidence_records)
        molecular_support_signal = _weighted_molecular_signal(review_case.evidence_records)
        contradiction_load = _contradiction_load(review_case.evidence_records)
        uncertainty_load = clamp01(max(weighted_tif.I, contradiction_load))
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
            molecular_support_signal=molecular_support_signal,
            contradiction_load=contradiction_load,
            uncertainty_load=uncertainty_load,
            review_priority=_review_priority(uncertainty_load, contradiction_load),
        )


def score_molecular_review_case(raw: object) -> dict[str, object]:
    return MolecularEvidenceReviewer().score(raw)


def build_dna_similarity_demo_case() -> MolecularReviewCase:
    source_ids = (
        NSS_DNA_SEQUENCE_SOURCE_ID,
        NCBI_BLAST_GUARDRAIL_SOURCE_ID,
        NCBI_DATASETS_GUARDRAIL_SOURCE_ID,
        ENSEMBL_GUARDRAIL_SOURCE_ID,
    )
    return MolecularReviewCase(
        case_label="Synthetic DNA similarity review case",
        query_label="Synthetic marker-region query",
        molecule_type=MoleculeType.MARKER_GENE.value,
        evidence_records=(
            MolecularEvidenceRecord(
                id="blast.top_hit",
                provider=EvidenceProvider.NCBI_BLAST.value,
                molecule_type=MoleculeType.MARKER_GENE.value,
                label="Compact BLAST-like top hit summary",
                accession="SYNTH_BLAST_HIT_001",
                taxon_label="Synthetic reference taxon",
                taxon_id="taxon.synthetic.001",
                T=0.82,
                I=0.16,
                F=0.06,
                weight=1.3,
                source_ids=(NSS_DNA_SEQUENCE_SOURCE_ID, NCBI_BLAST_GUARDRAIL_SOURCE_ID),
                notes="Synthetic compact similarity evidence; no raw alignment or species decision.",
                percent_identity=96.4,
                query_coverage=91.0,
                evalue=1e-42,
                bit_score=242.0,
                taxon_match=True,
            ),
            MolecularEvidenceRecord(
                id="datasets.taxon_anchor",
                provider=EvidenceProvider.NCBI_DATASETS.value,
                molecule_type=MoleculeType.DNA.value,
                label="Compact NCBI Datasets-like taxon anchor",
                accession="SYNTH_ASSEMBLY_001",
                taxon_label="Synthetic reference taxon",
                taxon_id="taxon.synthetic.001",
                T=0.74,
                I=0.22,
                F=0.08,
                weight=1.1,
                source_ids=(NCBI_DATASETS_GUARDRAIL_SOURCE_ID,),
                notes="Synthetic genome/taxon metadata anchor; not a classification decision.",
                taxon_match=True,
            ),
            MolecularEvidenceRecord(
                id="ensembl.annotation_anchor",
                provider=EvidenceProvider.ENSEMBL.value,
                molecule_type=MoleculeType.GENOME_REGION.value,
                label="Compact Ensembl-like annotation xref",
                accession="SYNTH_REGION_001",
                taxon_label="Synthetic reference taxon",
                taxon_id="taxon.synthetic.001",
                T=0.68,
                I=0.28,
                F=0.10,
                weight=0.9,
                source_ids=(ENSEMBL_GUARDRAIL_SOURCE_ID,),
                notes="Synthetic annotation support; specialist interpretation remains required.",
                annotation_match=True,
                taxon_match=True,
            ),
        ),
        source_ids=source_ids,
        reviewer_notes="Public-safe synthetic molecular evidence demo; not a taxonomic, diagnostic, or safety conclusion.",
    )


def _base_payload(
    case: MolecularReviewCase,
    operational_tif: TIF,
    molecular_support_signal: float,
    contradiction_load: float,
    uncertainty_load: float,
    review_priority: str,
) -> dict[str, object]:
    dominant = case.dominant_evidence_record()
    return {
        "case_label": case.case_label,
        "query_label": case.query_label,
        "molecule_type": case.molecule_type,
        "evidence_records": [record.as_dict() for record in case.evidence_records],
        "source_ids": list(_all_source_ids(case)),
        "sequence_evidence_count": len(case.evidence_records),
        "dominant_evidence_record": None if dominant is None else dominant.as_dict(),
        "molecular_support_signal": molecular_support_signal,
        "contradiction_load": contradiction_load,
        "uncertainty_load": uncertainty_load,
        "operational_tif": operational_tif.as_dict(),
        "review_priority": review_priority,
        "related_taxon_packet": case.related_taxon_packet,
        "related_risk_case": case.related_risk_case,
        "related_biology_graph": case.related_biology_graph,
        "reviewer_notes": case.reviewer_notes,
        "human_review_required": True,
        "authority_boundary": (
            "Review support only; no formal taxonomic act, diagnostic result, safety decision, "
            "regulatory action, or autonomous molecular conclusion."
        ),
        "scientific_boundary": (
            "Sequence evidence supports review only when tied to external source identifiers, "
            "compact provenance, and specialist interpretation."
        ),
        "guardrail_sources": [
            {
                "source_id": NCBI_BLAST_GUARDRAIL_SOURCE_ID,
                "role": "sequence similarity guardrail; compact top-hit summaries only",
                "runtime_dependency": False,
            },
            {
                "source_id": NCBI_DATASETS_GUARDRAIL_SOURCE_ID,
                "role": "taxon, genome, and assembly metadata guardrail",
                "runtime_dependency": False,
            },
            {
                "source_id": ENSEMBL_GUARDRAIL_SOURCE_ID,
                "role": "annotation, cross-reference, and genomic-region guardrail",
                "runtime_dependency": False,
            },
        ],
        "source_anchor": {
            "source_id": NSS_DNA_SEQUENCE_SOURCE_ID,
            "title": "Enhanced Multi-Criteria DNA Sequence Analysis Using Neutrosophic Similarity Measures",
            "url": "https://fs.unm.edu/NSS/27DNASequence.pdf",
            "evidence_kind": "public_nss",
            "public_safe": True,
        },
        "hierarchy": HIERARCHY,
    }


def _optional_float(value: object) -> float | None:
    if value is None or value == "":
        return None
    return float(value)


def _optional_bool(value: object) -> bool | None:
    if value is None or value == "":
        return None
    return bool(value)


def _optional_mapping(value: object, label: str) -> Mapping[str, object] | None:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must be a JSON object when provided")
    return value


def _source_ids(value: object) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    if isinstance(value, Iterable):
        return tuple(str(item) for item in value)
    return (str(value),)


def _weighted_tif(records: Iterable[MolecularEvidenceRecord]) -> TIF:
    records = tuple(records)
    if not records:
        return TIF(T=0.0, I=1.0, F=0.0)
    weight_sum = sum(record.weight for record in records) or 1.0
    return TIF(
        T=clamp01(sum(record.operational_tif().T * record.weight for record in records) / weight_sum),
        I=clamp01(sum(record.operational_tif().I * record.weight for record in records) / weight_sum),
        F=clamp01(sum(record.operational_tif().F * record.weight for record in records) / weight_sum),
    )


def _weighted_molecular_signal(records: Iterable[MolecularEvidenceRecord]) -> float:
    records = tuple(records)
    if not records:
        return 0.0
    weight_sum = sum(record.weight for record in records) or 1.0
    return clamp01(sum(record.molecular_signal() * record.weight for record in records) / weight_sum)


def _contradiction_load(records: Iterable[MolecularEvidenceRecord]) -> float:
    records = tuple(records)
    if not records:
        return 1.0
    weight_sum = sum(record.weight for record in records) or 1.0
    load = 0.0
    for record in records:
        tif = record.operational_tif()
        load += record.molecular_signal() * max(tif.I, tif.F) * record.weight
    return clamp01(load / weight_sum)


def _review_priority(uncertainty_load: float, contradiction_load: float) -> str:
    signal = max(uncertainty_load, contradiction_load)
    if signal >= 0.75:
        return MolecularReviewPriority.CRITICAL_REVIEW.value
    if signal >= 0.50:
        return MolecularReviewPriority.ELEVATED.value
    if signal >= 0.25:
        return MolecularReviewPriority.WATCH.value
    return MolecularReviewPriority.ROUTINE.value


def _all_source_ids(case: MolecularReviewCase) -> tuple[str, ...]:
    seen: set[str] = set()
    ordered: list[str] = []
    for source_id in case.source_ids:
        if source_id not in seen:
            seen.add(source_id)
            ordered.append(source_id)
    for record in case.evidence_records:
        for source_id in record.source_ids:
            if source_id not in seen:
                seen.add(source_id)
                ordered.append(source_id)
    return tuple(ordered)
