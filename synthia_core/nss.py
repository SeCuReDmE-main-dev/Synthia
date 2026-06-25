"""NSS source-family registry and routing for Synthia math."""

from __future__ import annotations

from dataclasses import dataclass

from .plithogenic import FractalCarrierProfile, PlithogenicIProfile, TIF, math_sources_payload
from .safety import HIERARCHY


@dataclass(frozen=True)
class NSSSourceFamily:
    family_id: str
    label: str
    url: str
    allowed_variables: tuple[str, ...]
    synthia_modules: tuple[str, ...]
    role: str
    keywords: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "family_id": self.family_id,
            "label": self.label,
            "url": self.url,
            "allowed_variables": list(self.allowed_variables),
            "synthia_modules": list(self.synthia_modules),
            "role": self.role,
            "keywords": list(self.keywords),
        }


NSS_SOURCE_FAMILIES: tuple[NSSSourceFamily, ...] = (
    NSSSourceFamily(
        "neutrosophy",
        "Neutrosophy and base indeterminacy",
        "https://fs.unm.edu/NSS/",
        ("T", "I", "F", "I_system^S"),
        ("TIF", "SystemIndeterminacyChain", "I_lexicon"),
        "Base grammar for truth, indeterminacy, falsity, and system-located indeterminacy.",
        ("neutrosophy", "indeterminacy", "truth", "falsity", "tif"),
    ),
    NSSSourceFamily(
        "probability_statistics",
        "Neutrosophic probability and statistics",
        "https://fs.unm.edu/NSS/",
        ("P(L_i | d, S)", "H_lex", "G_lex", "I_lexicon"),
        ("I_lexicon", "HippoRAGMemoryBit", "TaxonomicReviewPacket", "NeutrosophicRandomVariable"),
        "Probability, statistics, distribution, and random-variable support for document filtration and lexicon uncertainty.",
        ("probability", "statistics", "distribution", "random variable", "expected value", "variance", "entropy"),
    ),
    NSSSourceFamily(
        "independent_components",
        "Independent and offset neutrosophic components",
        "https://fs.unm.edu/NSS/PracticalIndependentNeutrosophic36.pdf",
        ("T", "I", "F", "component_dependency", "offset_component"),
        ("IndependentTIFComponentProfile", "TIFNormalizationPolicy", "I_lexicon"),
        "Independent, partially dependent, dependent, and offset component interpretation.",
        ("independent component", "offset component", "trivariate", "multivariate truth"),
    ),
    NSSSourceFamily(
        "multineutrosophic",
        "MultiNeutrosophic source fusion",
        "https://fs.unm.edu/NSS/MultiNeutrosophicSet.pdf",
        ("T_1..T_n", "I_1..I_n", "F_1..F_n", "source_weight"),
        ("MultiTIFAssessment", "MultiNeutrosophicFusion", "I_lexicon"),
        "Multi-source truth, indeterminacy, and falsity fusion for expert/source review.",
        ("multineutrosophic", "multi-source", "many sources", "expert fusion"),
    ),
    NSSSourceFamily(
        "plithogenic",
        "Plithogenic set, logic, probability, and statistics",
        "https://fs.unm.edu/NSS/PlithogenicProbabilityStatistics20.pdf",
        ("I_system^S", "contradiction_degree", "T", "I", "F"),
        ("PlithogenicMatrix", "PlithogenicSetProfile", "PlithogenicLogicalProposition", "PlithogenicProbabilityEvent", "I_lexicon", "NSSMathRouter"),
        "System-level multi-attribute contradiction, set, logic, probability, and statistics layer.",
        ("plithogenic", "contradiction", "attribute", "dominant value", "multivariate", "cumulative truth", "refined probability"),
    ),
    NSSSourceFamily(
        "symbolic_algebra",
        "Symbolic plithogenic algebraic structures",
        "https://fs.unm.edu/NSS/SymbolicPlithogenicAlgebraic39.pdf",
        ("symbolic_notation", "algorithm_notation"),
        ("SymbolicNotation", "SymbolicPlithogenicNumber", "PlithogenicArithmetic"),
        "Notation, symbolic plithogenic numbers, and arithmetic traces for future math-language rendering.",
        ("symbolic", "algebra", "notation", "structure", "plithogenic number", "absorbance"),
    ),
    NSSSourceFamily(
        "hypersoft",
        "Hypersoft and plithogenic hypersoft structures",
        "https://fs.unm.edu/NSS/ExtensionOfSoftSetToHypersoftSet.pdf",
        ("attribute_parameter", "taxonomy_filter"),
        ("HypersoftAttributeProduct", "I_lexicon", "LexiconNode", "TaxonomicReviewPacket"),
        "Attribute-parameter structures for multi-criteria taxonomy filtering.",
        ("hypersoft", "plithogenic hypersoft", "soft set", "attribute product", "parameter", "multi-criteria"),
    ),
    NSSSourceFamily(
        "neutroalgebra",
        "NeutroAlgebra and partially defined operations",
        "https://fs.unm.edu/NeutroAlgebra.pdf",
        ("partial_operation", "outer_defined_operation", "indeterminate_operation"),
        ("NeutroOperationProfile", "HippoRAGMemoryBit", "LexiconBridge"),
        "Future math lexicon for partially defined or indeterminate graph operations.",
        ("neutroalgebra", "partial algebra", "neutrooperation", "neutroaxiom", "outer-defined", "operation", "axiom"),
    ),
    NSSSourceFamily(
        "neutrogeometry",
        "NeutroGeometry and specialized geometric carriers",
        "https://fs.unm.edu/NSS/",
        ("I_system^S", "specialized_carrier"),
        ("FractalCarrierProfile", "NSSMathRouter"),
        "Specialized geometric or multiscale carrier branch after system-location.",
        ("neutrogeometry", "geometry", "fractal", "multiscale", "dimension"),
    ),
    NSSSourceFamily(
        "future_math_lexicon",
        "Future NSS math lexicon expansion",
        "https://fs.unm.edu/NSS/Articles.htm",
        ("source_family", "allowed_variables"),
        ("NSSMathRouter", "MathSource"),
        "Controlled extension point for new NSS domains without changing the default I_lexicon chain.",
        ("topology", "superhyperset", "extension", "future"),
    ),
)


class NSSMathRouter:
    """Route text to an NSS source family and Synthia carrier."""

    def __init__(self, families: tuple[NSSSourceFamily, ...] = NSS_SOURCE_FAMILIES) -> None:
        self.families = families

    def list_sources(self) -> dict[str, object]:
        return {
            "entrydoor": "https://fs.unm.edu/NSS/",
            "hierarchy": HIERARCHY,
            "source_families": [family.as_dict() for family in self.families],
            "public_sources": math_sources_payload(public_only=True),
        }

    def route(self, text: str) -> dict[str, object]:
        lowered = text.lower()
        matches = [
            family
            for family in self.families
            if any(keyword in lowered for keyword in family.keywords)
        ]
        family = matches[0] if matches else self.families[0]
        carrier_type = "fractal_geometry" if family.family_id == "neutrogeometry" else "lexicon_distribution"
        chain = TIF(T=0.7, I=0.3, F=0.0, I_system=0.3, H_lex=0.3, G_lex=0.3, I_lexicon=0.3).system_chain(
            carrier_type=carrier_type
        )
        payload: dict[str, object] = {
            "text": text,
            "selected_family": family.as_dict(),
            "carrier_type": carrier_type,
            "system_location_rule": "I must first become I_system^S before Synthia selects a domain-specific carrier.",
            "system_indeterminacy_chain": chain.as_dict(),
            "hierarchy": HIERARCHY,
        }
        if family.family_id == "plithogenic":
            payload["plithogenic_profile"] = PlithogenicIProfile().as_dict()
        if family.family_id == "neutrogeometry":
            payload["specialized_carrier"] = FractalCarrierProfile().as_dict()
        return payload
