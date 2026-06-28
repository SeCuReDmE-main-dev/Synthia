"""Phylogenetic taxon review packets scored through plithogenic contradiction."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Mapping

from .plithogenic import TIF, clamp01
from .plithogenic_set import score_plithogenic_set
from .safety import HIERARCHY


class ReviewStatus(str, Enum):
    DRAFT = "draft"
    PENDING_SPECIALIST_REVIEW = "pending_specialist_review"
    APPROVED_FOR_SUMMARY = "approved_for_summary"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"


class TaxonObjectType(str, Enum):
    SPECIES = "species"
    SUBSPECIES = "subspecies"
    POPULATION = "population"
    HYBRID = "hybrid"
    CLADE = "clade"
    CANDIDATE_TAXON = "candidate_taxon"


@dataclass(frozen=True)
class PhyloEvidenceDimension:
    name: str
    value: str
    T: float
    I: float
    F: float
    weight: float = 1.0
    dominant: bool = False
    source_ids: tuple[str, ...] = ()
    notes: str = ""

    @classmethod
    def from_raw(cls, raw: object, index: int) -> "PhyloEvidenceDimension":
        if not isinstance(raw, Mapping):
            raise ValueError("each phylo-plithogenic dimension must be a JSON object")
        return cls(
            name=str(raw.get("name", f"dimension_{index + 1}")),
            value=str(raw.get("value", "")),
            T=float(raw.get("T", 0.0)),
            I=float(raw.get("I", 0.0)),
            F=float(raw.get("F", 0.0)),
            weight=max(0.0, float(raw.get("weight", 1.0))),
            dominant=bool(raw.get("dominant", False)),
            source_ids=tuple(str(item) for item in raw.get("source_ids", ())),
            notes=str(raw.get("notes", "")),
        )

    def operational_tif(self) -> TIF:
        return TIF(T=clamp01(self.T), I=clamp01(self.I), F=clamp01(self.F))

    def as_plithogenic_attribute(self) -> dict[str, object]:
        tif = self.operational_tif()
        return {
            "name": self.name,
            "value": self.value,
            "T": tif.T,
            "I": tif.I,
            "F": tif.F,
            "weight": self.weight,
            "dominant": self.dominant,
        }

    def as_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "value": self.value,
            "formal_value": {"T": self.T, "I": self.I, "F": self.F},
            "operational_tif": self.operational_tif().as_dict(),
            "weight": self.weight,
            "dominant": self.dominant,
            "source_ids": list(self.source_ids),
            "notes": self.notes,
        }


@dataclass(frozen=True)
class PhyloPlithogenicReviewPacket:
    taxon_label: str
    taxon_type: str
    phylo_context: str
    dimensions: tuple[PhyloEvidenceDimension, ...]
    review_status: str = ReviewStatus.PENDING_SPECIALIST_REVIEW.value
    source_ids: tuple[str, ...] = ()
    reviewer_notes: str = ""

    @classmethod
    def from_raw_packet(cls, raw: object) -> "PhyloPlithogenicReviewPacket":
        if not isinstance(raw, Mapping):
            raise ValueError("phylo-plithogenic packet must be a JSON object")
        dimensions = raw.get("dimensions", [])
        if not isinstance(dimensions, list):
            raise ValueError("phylo-plithogenic packet dimensions must be a JSON array")
        return cls(
            taxon_label=str(raw.get("taxon_label", "unnamed taxon review candidate")),
            taxon_type=str(raw.get("taxon_type", TaxonObjectType.CANDIDATE_TAXON.value)),
            phylo_context=str(raw.get("phylo_context", "")),
            dimensions=tuple(PhyloEvidenceDimension.from_raw(item, index) for index, item in enumerate(dimensions)),
            review_status=str(raw.get("review_status", ReviewStatus.PENDING_SPECIALIST_REVIEW.value)),
            source_ids=tuple(str(item) for item in raw.get("source_ids", ())),
            reviewer_notes=str(raw.get("reviewer_notes", "")),
        )

    def dominant_dimension(self) -> PhyloEvidenceDimension | None:
        for dimension in self.dimensions:
            if dimension.dominant:
                return dimension
        return self.dimensions[0] if self.dimensions else None

    def score(self) -> dict[str, object]:
        if not self.dimensions:
            empty_tif = TIF(T=0.0, I=1.0, F=0.0, I_system=1.0, H_lex=1.0, G_lex=1.0, I_lexicon=1.0)
            return self._base_payload(
                plithogenic_score={
                    "attribute_count": 0,
                    "weighted_cumulative_truth": {"T": 0.0, "I": 1.0, "F": 0.0},
                    "contradiction_load": 1.0,
                    "contradictions": [],
                },
                operational_tif=empty_tif,
                contradiction_load=1.0,
            )

        plithogenic_score = score_plithogenic_set([dimension.as_plithogenic_attribute() for dimension in self.dimensions])
        weighted = plithogenic_score["weighted_cumulative_truth"]
        contradiction_load = clamp01(max(float(plithogenic_score["contradiction_load"]), float(weighted["I"])))
        operational_tif = TIF(
            T=clamp01(float(weighted["T"])),
            I=clamp01(float(weighted["I"])),
            F=clamp01(float(weighted["F"])),
            I_system=contradiction_load,
            H_lex=contradiction_load,
            G_lex=contradiction_load,
            I_lexicon=contradiction_load,
        )
        return self._base_payload(plithogenic_score, operational_tif, contradiction_load)

    def _base_payload(
        self,
        plithogenic_score: dict[str, object],
        operational_tif: TIF,
        contradiction_load: float,
    ) -> dict[str, object]:
        dominant = self.dominant_dimension()
        return {
            "taxon_label": self.taxon_label,
            "taxon_type": self.taxon_type,
            "phylo_context": self.phylo_context,
            "dimensions": [dimension.as_dict() for dimension in self.dimensions],
            "dominant_dimension": None if dominant is None else dominant.as_dict(),
            "review_status": self.review_status,
            "review_priority": _review_priority(contradiction_load),
            "source_ids": list(self.source_ids),
            "reviewer_notes": self.reviewer_notes,
            "human_review_required": True,
            "authority_boundary": "Review support only; no formal nomenclatural act or autonomous species decision.",
            "scientific_boundary": "Phylogeny defines biological object identity; the plithogenic layer models review uncertainty and contradiction.",
            "societal_use": [
                "education",
                "conservation triage",
                "source-linked review",
                "non-authoritative decision support",
            ],
            "source_pair_hint": {
                "phylogenetic_anchor": "drive.aguilar.wiley_mayden_species_speciation_1985",
                "plithogenic_anchor": "nss.tilapia_tilv_plithogenic_fuzzy_soft_set_2025",
                "publication_boundary": "public-safe metadata only; no private correspondence or unpublished body text",
            },
            "weighted_cumulative_truth": plithogenic_score["weighted_cumulative_truth"],
            "contradiction_load": contradiction_load,
            "contradictions": plithogenic_score["contradictions"],
            "operational_tif": operational_tif.as_dict(),
            "plithogenic_score": plithogenic_score,
            "hierarchy": HIERARCHY,
        }


class PhyloPlithogenicReviewer:
    def score(self, packet: PhyloPlithogenicReviewPacket | object) -> dict[str, object]:
        if isinstance(packet, PhyloPlithogenicReviewPacket):
            return packet.score()
        return PhyloPlithogenicReviewPacket.from_raw_packet(packet).score()


def score_phylo_plithogenic_packet(raw: object) -> dict[str, object]:
    return PhyloPlithogenicReviewer().score(raw)


def build_tilapia_style_demo_packet() -> PhyloPlithogenicReviewPacket:
    source_ids = (
        "drive.aguilar.wiley_mayden_species_speciation_1985",
        "nss.tilapia_tilv_plithogenic_fuzzy_soft_set_2025",
    )
    return PhyloPlithogenicReviewPacket(
        taxon_label="Oreochromis niloticus review candidate",
        taxon_type=TaxonObjectType.SPECIES.value,
        phylo_context="Synthetic public-safe review packet linking phylogenetic identity to plithogenic uncertainty scoring.",
        dimensions=(
            PhyloEvidenceDimension(
                name="phylogenetic_placement",
                value="dominant_review_anchor",
                T=0.88,
                I=0.10,
                F=0.02,
                weight=1.4,
                dominant=True,
                source_ids=(source_ids[0],),
                notes="Synthetic anchor dimension for species identity context.",
            ),
            PhyloEvidenceDimension(
                name="morphology",
                value="mostly_consistent",
                T=0.76,
                I=0.18,
                F=0.06,
                weight=1.0,
                source_ids=(source_ids[0],),
                notes="Synthetic morphology signal for review support.",
            ),
            PhyloEvidenceDimension(
                name="geography_ecology",
                value="context_dependent",
                T=0.62,
                I=0.30,
                F=0.10,
                weight=0.9,
                source_ids=(source_ids[0], source_ids[1]),
                notes="Synthetic habitat and management-context signal.",
            ),
            PhyloEvidenceDimension(
                name="viral_susceptibility",
                value="elevated_review_signal",
                T=0.82,
                I=0.24,
                F=0.08,
                weight=1.1,
                source_ids=(source_ids[1],),
                notes="Synthetic disease-susceptibility review signal.",
            ),
            PhyloEvidenceDimension(
                name="expert_disagreement",
                value="multi_expert_variation",
                T=0.42,
                I=0.58,
                F=0.20,
                weight=0.8,
                source_ids=(source_ids[1],),
                notes="Synthetic disagreement dimension forcing human review.",
            ),
        ),
        review_status=ReviewStatus.PENDING_SPECIALIST_REVIEW.value,
        source_ids=source_ids,
        reviewer_notes="Public-safe synthetic demo; not a scientific finding.",
    )


def _review_priority(contradiction_load: float) -> str:
    if contradiction_load >= 0.6:
        return "high"
    if contradiction_load >= 0.3:
        return "medium"
    return "routine"

