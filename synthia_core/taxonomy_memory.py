"""White-paper-derived taxonomic memory system."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable

from .plithogenic import TIF
from .safety import HIERARCHY


class RepairType(str, Enum):
    MORPHOLOGY = "morphology"
    SEXUAL_DIMORPHISM = "sexual_dimorphism"
    GEOGRAPHY = "geography"
    SYNONYMY = "synonymy"
    ECOLOGY = "ecology"
    NESTING = "nesting"
    TYPE_INTERPRETATION = "type_interpretation"
    DIAGNOSTIC_CONTEXT = "diagnostic_context"
    UNRESOLVED_LAYER = "unresolved_layer"


class IndeterminacyStatus(str, Enum):
    RESOLVED = "resolved"
    PARTIALLY_RESOLVED = "partially_resolved"
    CONTESTED = "contested"
    PENDING_SPECIALIST_REVIEW = "pending_specialist_review"


@dataclass(frozen=True)
class RedescriptionTrace:
    formal_name: str
    formal_authority: str
    critical_redescription: str
    repair_types: tuple[str, ...]
    indeterminacy_status: str
    conservation_link: str = ""
    source_ids: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, object]:
        return {
            "formal_name": self.formal_name,
            "formal_authority": self.formal_authority,
            "critical_redescription": self.critical_redescription,
            "repair_types": list(self.repair_types),
            "indeterminacy_status": self.indeterminacy_status,
            "conservation_link": self.conservation_link,
            "source_ids": list(self.source_ids),
            "code_aware_boundary": "Formal nomenclatural authority remains governed by the relevant Code and human review.",
            "hierarchy": HIERARCHY,
        }


@dataclass(frozen=True)
class TaxonomicMemoryRecord:
    name: str
    formal_authority: str
    original_description: str = ""
    type_concept: str = ""
    redescriptions: tuple[RedescriptionTrace, ...] = ()
    synonymy: tuple[str, ...] = ()
    ecology: tuple[str, ...] = ()
    geography: tuple[str, ...] = ()
    conservation: tuple[str, ...] = ()
    education: tuple[str, ...] = ()
    source_ids: tuple[str, ...] = ()
    tif: TIF = field(default_factory=lambda: TIF(T=0.8, I=0.2, F=0.0, I_system=0.2))

    def as_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "formal_authority": self.formal_authority,
            "original_description": self.original_description,
            "type_concept": self.type_concept,
            "redescriptions": [item.as_dict() for item in self.redescriptions],
            "synonymy": list(self.synonymy),
            "ecology": list(self.ecology),
            "geography": list(self.geography),
            "conservation": list(self.conservation),
            "education": list(self.education),
            "source_ids": list(self.source_ids),
            "tif": self.tif.as_dict(),
            "memory_object": True,
        }


class MemoryRepairClassifier:
    """Classify the repair function described by a redescription note."""

    KEYWORDS = {
        RepairType.MORPHOLOGY: ("morpholog", "diagnos", "character", "plumage", "measurement"),
        RepairType.SEXUAL_DIMORPHISM: ("sex", "male", "female", "dimorphism", "age"),
        RepairType.GEOGRAPHY: ("geograph", "distribution", "locality", "range", "venezuela"),
        RepairType.SYNONYMY: ("synonym", "homonym", "comb. nov", "combination", "subspecies"),
        RepairType.ECOLOGY: ("ecolog", "habitat", "feeding", "behavior", "field"),
        RepairType.NESTING: ("nest", "egg", "breeding"),
        RepairType.TYPE_INTERPRETATION: ("type", "specimen", "museum"),
        RepairType.DIAGNOSTIC_CONTEXT: ("diagnostic", "identification", "recognize", "clarify"),
        RepairType.UNRESOLVED_LAYER: ("unresolved", "contested", "pending", "uncertain", "insufficient"),
    }

    def classify(self, text: str) -> tuple[str, ...]:
        lowered = text.lower()
        hits = [
            repair_type.value
            for repair_type, markers in self.KEYWORDS.items()
            if any(marker in lowered for marker in markers)
        ]
        return tuple(dict.fromkeys(hits or [RepairType.DIAGNOSTIC_CONTEXT.value]))


class PriorityVsMemoryBoundary:
    """Separate Code-governed priority from epistemic recognition."""

    def annotate(self, trace: RedescriptionTrace) -> dict[str, object]:
        return {
            "formal_name": trace.formal_name,
            "formal_authority_preserved": trace.formal_authority,
            "redescriptive_authority_visible": trace.critical_redescription,
            "can_transfer_formal_authorship": False,
            "recognition_layer": "metadata_and_citation_trace",
            "human_review_required": True,
        }


class IndeterminacyLocator:
    """Map uncertainty to concrete taxonomic source structures."""

    SOURCES = {
        "incomplete_diagnosis": ("incomplete", "insufficient", "missing diagnostic"),
        "immature_specimens": ("immature", "juvenile"),
        "sexual_dimorphism": ("sexual", "male", "female", "dimorphism"),
        "geographic_variation": ("geographic", "range", "locality", "distribution"),
        "synonymy": ("synonym", "combination", "comb. nov"),
        "homonymy": ("homonym",),
        "type_access": ("type", "specimen", "museum"),
        "contradictory_literature": ("contradict", "conflict"),
        "species_subspecies_boundary": ("subspecies", "rank", "species boundary"),
    }

    def locate(self, text: str) -> dict[str, object]:
        lowered = text.lower()
        sources = [
            name for name, markers in self.SOURCES.items() if any(marker in lowered for marker in markers)
        ]
        i_value = min(1.0, 0.1 + 0.1 * len(sources))
        return {
            "sources": sources or ["unspecified_taxonomic_context"],
            "tif": TIF(T=max(0.0, 1.0 - i_value), I=i_value, F=0.0, I_system=i_value).as_dict(),
            "hierarchy": HIERARCHY,
            "rule": "Do not collapse located taxonomic indeterminacy into generic uncertainty.",
        }


class RedescriptionTraceProtocol:
    """Create redescription-trace metadata beside formal name metadata."""

    def __init__(self, classifier: MemoryRepairClassifier | None = None) -> None:
        self.classifier = classifier or MemoryRepairClassifier()

    def build_trace(
        self,
        formal_name: str,
        formal_authority: str,
        critical_redescription: str,
        repair_note: str,
        indeterminacy_status: str = IndeterminacyStatus.PENDING_SPECIALIST_REVIEW,
        conservation_link: str = "",
        source_ids: Iterable[str] = (),
    ) -> RedescriptionTrace:
        return RedescriptionTrace(
            formal_name=formal_name,
            formal_authority=formal_authority,
            critical_redescription=critical_redescription,
            repair_types=self.classifier.classify(repair_note),
            indeterminacy_status=(
                indeterminacy_status.value
                if isinstance(indeterminacy_status, IndeterminacyStatus)
                else str(indeterminacy_status)
            ),
            conservation_link=conservation_link,
            source_ids=tuple(source_ids),
        )


class TaxonomicMemorySystem:
    """Registry for species names as memory objects."""

    def __init__(self) -> None:
        self.records: dict[str, TaxonomicMemoryRecord] = {}

    def add_record(self, record: TaxonomicMemoryRecord) -> TaxonomicMemoryRecord:
        self.records[record.name] = record
        return record

    def get_record(self, name: str) -> TaxonomicMemoryRecord | None:
        return self.records.get(name)

    def build_aburria_anchor(self) -> TaxonomicMemoryRecord:
        trace = RedescriptionTraceProtocol().build_trace(
            formal_name="Aburria aburri",
            formal_authority="Lesson, 1828",
            critical_redescription="Aguilar H. F. & R. F. Aguilar 2012",
            repair_note="Morphological redescription with notes on nest, egg, field context, and diagnostic clarification.",
            indeterminacy_status=IndeterminacyStatus.PARTIALLY_RESOLVED,
            conservation_link="Checklist, local education, habitat monitoring, conservation report.",
            source_ids=("gdoc.aguilar_beaulieu_white_paper",),
        )
        return self.add_record(
            TaxonomicMemoryRecord(
                name="Aburria aburri",
                formal_authority="Lesson, 1828",
                original_description="Formal original authority preserved.",
                redescriptions=(trace,),
                ecology=("nest and egg notes", "field-context clarification"),
                conservation=("Integral Conservation memory continuity",),
                education=("local biodiversity education",),
                source_ids=("gdoc.aguilar_beaulieu_white_paper",),
                tif=TIF(T=0.86, I=0.14, F=0.0, I_system=0.14),
            )
        )


class TaxonomicReviewPacketBuilder:
    def build(self, record: TaxonomicMemoryRecord) -> dict[str, object]:
        traces = [trace.as_dict() for trace in record.redescriptions]
        unresolved = [
            trace for trace in traces if trace["indeterminacy_status"] != IndeterminacyStatus.RESOLVED.value
        ]
        return {
            "formal_name": record.name,
            "formal_authority": record.formal_authority,
            "critical_redescriptions": traces,
            "unresolved_layers": unresolved,
            "conservation_links": list(record.conservation),
            "source_ids": list(record.source_ids),
            "human_review_required": True,
            "ai_role": "traceability_support_only",
        }


class CitationTraceAuditor:
    BINOMIAL_PATTERN = re.compile(r"\b[A-Z][a-z]+ [a-z][a-z-]+\b")
    AUTHOR_DATE_PATTERN = re.compile(r"\([A-Z][A-Za-z .&-]+,\s*\d{4}\)|[A-Z][A-Za-z .&-]+,\s*\d{4}")

    def audit(self, text: str, known_records: Iterable[TaxonomicMemoryRecord] = ()) -> dict[str, object]:
        names = self.BINOMIAL_PATTERN.findall(text)
        has_author_date = bool(self.AUTHOR_DATE_PATTERN.search(text))
        record_names = {record.name: record for record in known_records}
        hidden_redescriptions = [
            name for name in names if name in record_names and record_names[name].redescriptions and "redescription" not in text.lower()
        ]
        return {
            "species_names": names,
            "missing_author_date": bool(names and not has_author_date),
            "hidden_redescriptions": hidden_redescriptions,
            "possible_homonym_signal": "homonym" in text.lower(),
            "synonymy_conflict_signal": "synonym" in text.lower() or "comb. nov" in text.lower(),
            "human_review_required": bool(hidden_redescriptions or names and not has_author_date),
        }


class IntegralConservationLinker:
    def link(self, trace: RedescriptionTrace) -> dict[str, object]:
        return {
            "formal_name": trace.formal_name,
            "conservation_memory": trace.conservation_link,
            "actions": ["checklist", "local education", "habitat monitoring", "conservation report"],
            "rationale": "Taxonomic traceability is conservation infrastructure.",
        }


class MultilingualTaxonomyBridge:
    TERM_MAP = {
        "redescription": {"es": "redescripcion", "fr": "redescription", "la": "redescriptio"},
        "taxonomic memory repair": {
            "es": "reparacion de memoria taxonomica",
            "fr": "reparation de memoire taxonomique",
            "la": "reparatio memoriae taxonomicae",
        },
        "formal authority": {"es": "autoridad formal", "fr": "autorite formelle", "la": "auctoritas formalis"},
    }

    def bridge(self, term: str) -> dict[str, object]:
        key = term.lower().strip()
        return {
            "term": term,
            "translations": self.TERM_MAP.get(key, {}),
            "preserve_taxonomic_logic": True,
        }


@dataclass(frozen=True)
class AIAssistanceDisclosure:
    system: str
    model: str
    date: str
    role: str
    human_verified: bool = False

    def as_dict(self) -> dict[str, object]:
        return {
            "system": self.system,
            "model": self.model,
            "date": self.date,
            "role": self.role,
            "human_verified": self.human_verified,
            "authority_boundary": "AI assistance only; no autonomous scientific authority.",
        }


class AIAssistanceDisclosureTracker:
    def __init__(self) -> None:
        self.disclosures: list[AIAssistanceDisclosure] = []

    def record(self, disclosure: AIAssistanceDisclosure) -> AIAssistanceDisclosure:
        self.disclosures.append(disclosure)
        return disclosure

    def as_list(self) -> list[dict[str, object]]:
        return [item.as_dict() for item in self.disclosures]
