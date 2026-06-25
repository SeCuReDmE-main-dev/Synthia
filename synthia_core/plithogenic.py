"""Bounded plithogenic and system-indeterminacy helpers for Synthia."""

from __future__ import annotations

from dataclasses import dataclass
from math import fabs
from typing import Iterable, Mapping

from .safety import HIERARCHY


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


@dataclass(frozen=True)
class MathSource:
    """Public source pointer for Synthia math doctrine."""

    source_id: str
    title: str
    url: str | None
    evidence_kind: str
    scope: str
    public_safe: bool = True

    def as_dict(self) -> dict[str, object]:
        return {
            "source_id": self.source_id,
            "title": self.title,
            "url": self.url,
            "evidence_kind": self.evidence_kind,
            "scope": self.scope,
            "public_safe": self.public_safe,
        }


@dataclass(frozen=True)
class SymbolicNotation:
    """Stable symbolic forms for code, docs, and algorithm surfaces."""

    canonical_id: str
    ascii: str
    latex: str
    unicode: str
    algorithm: str
    aliases: tuple[str, ...] = ()

    def render(self, format_name: str = "ascii") -> str:
        if format_name == "ascii":
            return self.ascii
        if format_name == "latex":
            return self.latex
        if format_name == "unicode":
            return self.unicode
        if format_name == "algorithm":
            return self.algorithm
        raise ValueError(f"unsupported notation format: {format_name}")

    def as_dict(self) -> dict[str, object]:
        return {
            "canonical_id": self.canonical_id,
            "ascii": self.ascii,
            "latex": self.latex,
            "unicode": self.unicode,
            "algorithm": self.algorithm,
            "aliases": list(self.aliases),
        }


@dataclass(frozen=True)
class IndeterminacyLayer:
    canonical_id: str
    order: int
    role: str
    notation: SymbolicNotation
    source_ids: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "canonical_id": self.canonical_id,
            "order": self.order,
            "role": self.role,
            "notation": self.notation.as_dict(),
            "source_ids": list(self.source_ids),
        }


MATH_SOURCES: dict[str, MathSource] = {
    "nss.hub": MathSource(
        "nss.hub",
        "Neutrosophic Sets and Systems journal hub",
        "https://fs.unm.edu/NSS/",
        "public_nss",
        "public mathematical source-family map",
    ),
    "nss.articles": MathSource(
        "nss.articles",
        "Neutrosophic Sets and Systems articles index",
        "https://fs.unm.edu/NSS/Articles.htm",
        "public_nss",
        "source discovery and verification index",
    ),
    "nss.unifying_field_logics": MathSource(
        "nss.unifying_field_logics",
        "A Unifying Field in Logics: Neutrosophic Logic, Neutrosophy, Neutrosophic Set, Probability and Statistics",
        "https://fs.unm.edu/eBook-Neutrosophics6.pdf",
        "public_nss",
        "primary public foundation for T/I/F, logic, set, probability, and statistics",
    ),
    "nss.indeterminacy": MathSource(
        "nss.indeterminacy",
        "Indeterminacy in Neutrosophic Theories and their Applications",
        "https://fs.unm.edu/Indeterminacy.pdf",
        "public_nss",
        "base and refined indeterminacy",
    ),
    "nss.plithogenic_set": MathSource(
        "nss.plithogenic_set",
        "Plithogenic Set, an Extension of Crisp, Fuzzy, Intuitionistic Fuzzy, and Neutrosophic Sets",
        "https://fs.unm.edu/NSS/PlithogenicSetAnExtensionOfCrisp.pdf",
        "public_nss",
        "plithogenic attributes, values, and contradiction",
    ),
    "nss.plithogenic_logic": MathSource(
        "nss.plithogenic_logic",
        "Introduction to Plithogenic Logic",
        "https://fs.unm.edu/NSS/IntroductionPlithogenicLogic1.pdf",
        "public_nss",
        "plithogenic multivariate logic",
    ),
    "nss.plithogenic_probability_statistics": MathSource(
        "nss.plithogenic_probability_statistics",
        "Plithogenic Probability and Statistics",
        "https://fs.unm.edu/NSS/PlithogenicProbabilityStatistics20.pdf",
        "public_nss",
        "multi-variable probability, statistics, and refined T/I/F",
    ),
    "nss.symbolic_plithogenic_algebra": MathSource(
        "nss.symbolic_plithogenic_algebra",
        "Symbolic Plithogenic Algebraic Structures",
        "https://fs.unm.edu/NSS/SymbolicPlithogenicAlgebraic39.pdf",
        "public_nss",
        "symbolic plithogenic numbers and algebraic notation",
    ),
}


SYMBOLIC_NOTATIONS: dict[str, SymbolicNotation] = {
    "I": SymbolicNotation(
        canonical_id="I",
        ascii="I",
        latex="I",
        unicode="I",
        algorithm="I := base_indeterminacy(TIF)",
    ),
    "I_system^S": SymbolicNotation(
        canonical_id="I_system^S",
        ascii="I_system^S",
        latex=r"I_{\mathrm{system}}^{S}",
        unicode="I_system^S",
        algorithm="I_system^S := system_scope(I, active_system, source_context)",
        aliases=("I_s", "I_s_system", "I_system"),
    ),
    "H_lex": SymbolicNotation(
        canonical_id="H_lex",
        ascii="H_lex",
        latex=r"H_{\mathrm{lex}}",
        unicode="H_lex",
        algorithm="H_lex := -sum(P(L_i) log(P(L_i))) / log(|L|)",
    ),
    "G_lex": SymbolicNotation(
        canonical_id="G_lex",
        ascii="G_lex",
        latex=r"G_{\mathrm{lex}}",
        unicode="G_lex",
        algorithm="G_lex := 1 - (P_top - P_second)",
    ),
    "I_lexicon": SymbolicNotation(
        canonical_id="I_lexicon",
        ascii="I_lexicon",
        latex=r"I_{\mathrm{lexicon}}",
        unicode="I_lexicon",
        algorithm="I_lexicon := bounded(alpha*H_lex + beta*G_lex + gamma*contradiction_load)",
    ),
    "D_f": SymbolicNotation(
        canonical_id="D_f",
        ascii="D_f",
        latex=r"D_f",
        unicode="D_f",
        algorithm="D_f := explicit_fractal_geometry_carrier_only",
    ),
    "dF": SymbolicNotation(
        canonical_id="dF",
        ascii="dF",
        latex=r"dF",
        unicode="dF",
        algorithm="dF := explicit_fractal_geometry_delta_only",
    ),
    "i_fractal": SymbolicNotation(
        canonical_id="i_fractal",
        ascii="i_fractal",
        latex=r"i_{\mathrm{fractal}}",
        unicode="i_fractal",
        algorithm="i_fractal := explicit_fractal_geometry_indeterminacy_only",
        aliases=("I_fractal",),
    ),
    "plithogenic_matrix": SymbolicNotation(
        canonical_id="plithogenic_matrix",
        ascii="P(attributes, contradiction_degree, TIF)",
        latex=r"P(A, c(v_i,v_j), (T,I,F))",
        unicode="P(attributes, contradiction_degree, TIF)",
        algorithm="P := aggregate(attribute_values, contradiction_degree, TIF, weights)",
    ),
}


INDETERMINACY_LAYERS: dict[str, IndeterminacyLayer] = {
    "I": IndeterminacyLayer(
        "I",
        0,
        "base indeterminacy signal",
        SYMBOLIC_NOTATIONS["I"],
        ("nss.unifying_field_logics", "nss.indeterminacy"),
    ),
    "I_system^S": IndeterminacyLayer(
        "I_system^S",
        1,
        "system-scoped indeterminacy inside the active lexicon, task, corpus, and source context",
        SYMBOLIC_NOTATIONS["I_system^S"],
        ("nss.hub", "nss.unifying_field_logics", "nss.indeterminacy", "nss.plithogenic_logic"),
    ),
    "H_lex": IndeterminacyLayer(
        "H_lex",
        2,
        "normalized lexicon entropy over candidate lexicons",
        SYMBOLIC_NOTATIONS["H_lex"],
        ("nss.hub", "nss.plithogenic_probability_statistics"),
    ),
    "G_lex": IndeterminacyLayer(
        "G_lex",
        3,
        "lexicon decision-gap uncertainty between the strongest and second-strongest lexicon",
        SYMBOLIC_NOTATIONS["G_lex"],
        ("nss.hub", "nss.plithogenic_probability_statistics"),
    ),
    "I_lexicon": IndeterminacyLayer(
        "I_lexicon",
        4,
        "final context-preserving lexicon indeterminacy state",
        SYMBOLIC_NOTATIONS["I_lexicon"],
        ("nss.hub", "nss.plithogenic_logic", "nss.plithogenic_probability_statistics"),
    ),
}

DEFAULT_LAYER_ORDER = ("I", "I_system^S", "H_lex", "G_lex", "I_lexicon")

SYMBOL_ALIASES: dict[str, str] = {}
for _canonical, _notation in SYMBOLIC_NOTATIONS.items():
    SYMBOL_ALIASES[_canonical.lower()] = _canonical
    SYMBOL_ALIASES[_notation.ascii.lower()] = _canonical
    for _alias in _notation.aliases:
        SYMBOL_ALIASES[_alias.lower()] = _canonical


def resolve_indeterminacy_symbol(symbol: str) -> str:
    key = symbol.strip().lower()
    if key not in SYMBOL_ALIASES:
        raise KeyError(f"unknown indeterminacy symbol: {symbol}")
    return SYMBOL_ALIASES[key]


def render_symbolic_notation(symbol: str, format_name: str = "ascii") -> dict[str, object]:
    canonical = resolve_indeterminacy_symbol(symbol)
    notation = SYMBOLIC_NOTATIONS[canonical]
    return {"symbol": canonical, "format": format_name, "rendered": notation.render(format_name), "notation": notation.as_dict()}


@dataclass(frozen=True)
class FractalCarrierProfile:
    """Explicit opt-in carrier for geometric or multiscale indeterminacy."""

    D_f: float | None = None
    dF: float | None = None
    i_fractal: float | None = None
    source_id: str = "fractal_neutrogeometry_internal"

    def as_dict(self) -> dict[str, object]:
        return {
            "carrier_type": "fractal_geometry",
            "system_principle": "I must first become I_system^S before a geometric or multiscale carrier is selected.",
            "public_default": False,
            "variables": {
                "D_f": None if self.D_f is None else float(self.D_f),
                "dF": None if self.dF is None else float(self.dF),
                "i_fractal": None if self.i_fractal is None else clamp01(self.i_fractal),
            },
            "source_id": self.source_id,
            "boundary": "This carrier is specialized; it is not Synthia's public default I_lexicon chain.",
        }


@dataclass(frozen=True)
class SystemIndeterminacyChain:
    """Generic Synthia chain after I has been located inside a system."""

    I: float
    I_system: float
    H_lex: float
    G_lex: float
    I_lexicon: float
    carrier_type: str = "lexicon_distribution"
    source: str = "derived"
    specialized_carrier: FractalCarrierProfile | None = None

    @classmethod
    def from_tif(cls, tif: "TIF", carrier_type: str = "lexicon_distribution") -> "SystemIndeterminacyChain":
        bounded = tif.bounded()
        base_i = bounded.I
        system_i = base_i if bounded.I_system is None else bounded.I_system
        h_lex = system_i if bounded.H_lex is None else bounded.H_lex
        g_lex = base_i if bounded.G_lex is None else bounded.G_lex
        i_lexicon = clamp01((system_i + h_lex + g_lex) / 3.0) if bounded.I_lexicon is None else bounded.I_lexicon
        specialized = None
        if carrier_type == "fractal_geometry":
            specialized = FractalCarrierProfile(bounded.D_f, bounded.dF, bounded.i_fractal)
        return cls(
            I=base_i,
            I_system=system_i,
            H_lex=h_lex,
            G_lex=g_lex,
            I_lexicon=i_lexicon,
            carrier_type=carrier_type,
            source="explicit_or_derived",
            specialized_carrier=specialized,
        )

    def as_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "I": clamp01(self.I),
            "I_system^S": clamp01(self.I_system),
            "H_lex": clamp01(self.H_lex),
            "G_lex": clamp01(self.G_lex),
            "I_lexicon": clamp01(self.I_lexicon),
            "carrier_type": self.carrier_type,
            "hierarchy": HIERARCHY,
            "classification_family": "I",
            "source": self.source,
            "layers": [INDETERMINACY_LAYERS[symbol].as_dict() for symbol in DEFAULT_LAYER_ORDER],
        }
        if self.specialized_carrier is not None:
            payload["specialized_carrier"] = self.specialized_carrier.as_dict()
        return payload


IndeterminacyChain = SystemIndeterminacyChain


@dataclass(frozen=True)
class PlithogenicIProfile:
    """Synthia doctrine: plithogenic work belongs to I_system^S."""

    canonical_indeterminacy_class: str = "I_system^S"
    role: str = "multi-attribute / multi-variable system indeterminacy organizer"
    evidence_status: str = "public_nss_supported + system_indeterminacy_inferred"
    source_ids: tuple[str, ...] = (
        "nss.hub",
        "nss.plithogenic_set",
        "nss.plithogenic_logic",
        "nss.plithogenic_probability_statistics",
        "nss.symbolic_plithogenic_algebra",
    )

    def as_dict(self) -> dict[str, object]:
        canonical = resolve_indeterminacy_symbol(self.canonical_indeterminacy_class)
        return {
            "classification_family": "I",
            "canonical_indeterminacy_class": canonical,
            "aliases": list(SYMBOLIC_NOTATIONS[canonical].aliases),
            "role": self.role,
            "evidence_status": self.evidence_status,
            "notation": SYMBOLIC_NOTATIONS[canonical].as_dict(),
            "algorithm_notation": SYMBOLIC_NOTATIONS["plithogenic_matrix"].as_dict(),
            "source_ids": list(self.source_ids),
            "human_authority_boundary": "Public NSS sources support the math layer; Synthia remains an educational classifier.",
        }


@dataclass(frozen=True)
class TIF:
    """Truth, indeterminacy, falsity triplet with optional carriers."""

    T: float = 1.0
    I: float = 0.0
    F: float = 0.0
    I_system: float | None = None
    H_lex: float | None = None
    G_lex: float | None = None
    I_lexicon: float | None = None
    D_f: float | None = None
    dF: float | None = None
    i_fractal: float | None = None

    def bounded(self) -> "TIF":
        return TIF(
            T=clamp01(self.T),
            I=clamp01(self.I),
            F=clamp01(self.F),
            I_system=None if self.I_system is None else clamp01(self.I_system),
            H_lex=None if self.H_lex is None else clamp01(self.H_lex),
            G_lex=None if self.G_lex is None else clamp01(self.G_lex),
            I_lexicon=None if self.I_lexicon is None else clamp01(self.I_lexicon),
            D_f=None if self.D_f is None else float(self.D_f),
            dF=None if self.dF is None else float(self.dF),
            i_fractal=None if self.i_fractal is None else clamp01(self.i_fractal),
        )

    def system_chain(self, carrier_type: str = "lexicon_distribution") -> SystemIndeterminacyChain:
        return SystemIndeterminacyChain.from_tif(self, carrier_type=carrier_type)

    def as_dict(self, carrier_type: str = "lexicon_distribution") -> dict[str, object]:
        bounded = self.bounded()
        chain = bounded.system_chain(carrier_type=carrier_type)
        return {
            "T": bounded.T,
            "I": bounded.I,
            "F": bounded.F,
            "I_system^S": bounded.I_system,
            "H_lex": bounded.H_lex,
            "G_lex": bounded.G_lex,
            "I_lexicon": bounded.I_lexicon,
            "system_indeterminacy_chain": chain.as_dict(),
            "i_lexicon_layer": "I_lexicon",
            "classification_family": "I",
            "hierarchy": HIERARCHY,
        }


@dataclass(frozen=True)
class PlithogenicAttribute:
    name: str
    value: str
    tif: TIF
    weight: float = 1.0
    source_id: str | None = None

    def as_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "value": self.value,
            "tif": self.tif.as_dict(),
            "weight": clamp01(self.weight),
            "source_id": self.source_id,
        }


class PlithogenicMatrix:
    """Small deterministic matrix for contradiction and cumulative truth."""

    def __init__(self, attributes: Iterable[PlithogenicAttribute] | None = None):
        self.attributes = list(attributes or [])

    @classmethod
    def from_mappings(cls, mappings: Iterable[Mapping[str, object]]) -> "PlithogenicMatrix":
        attributes: list[PlithogenicAttribute] = []
        for item in mappings:
            tif_payload = item.get("tif") if isinstance(item.get("tif"), Mapping) else {}
            attributes.append(
                PlithogenicAttribute(
                    name=str(item.get("name", "unknown")),
                    value=str(item.get("value", "")),
                    tif=TIF(
                        T=float(tif_payload.get("T", item.get("T", 1.0))),
                        I=float(tif_payload.get("I", item.get("I", 0.0))),
                        F=float(tif_payload.get("F", item.get("F", 0.0))),
                        I_system=tif_payload.get("I_system^S", payload_or_none(item, "I_system")),
                        H_lex=tif_payload.get("H_lex", payload_or_none(item, "H_lex")),
                        G_lex=tif_payload.get("G_lex", payload_or_none(item, "G_lex")),
                        I_lexicon=tif_payload.get("I_lexicon", payload_or_none(item, "I_lexicon")),
                        D_f=tif_payload.get("D_f", payload_or_none(item, "D_f")),
                        dF=tif_payload.get("dF", payload_or_none(item, "dF")),
                        i_fractal=tif_payload.get("i_fractal", payload_or_none(item, "i_fractal")),
                    ),
                    weight=float(item.get("weight", 1.0)),
                    source_id=None if item.get("source_id") is None else str(item.get("source_id")),
                )
            )
        return cls(attributes)

    def contradiction_degree(self, left: PlithogenicAttribute, right: PlithogenicAttribute) -> float:
        left_tif = left.tif.bounded()
        right_tif = right.tif.bounded()
        truth_gap = fabs(left_tif.T - right_tif.T)
        falsity_gap = fabs(left_tif.F - right_tif.F)
        indeterminacy_load = max(left_tif.I, right_tif.I)
        same_name_penalty = 0.15 if left.name == right.name and left.value != right.value else 0.0
        return clamp01((truth_gap + falsity_gap + indeterminacy_load) / 3.0 + same_name_penalty)

    def contradiction_summary(self) -> dict[str, object]:
        pairs: list[dict[str, object]] = []
        max_degree = 0.0
        for index, left in enumerate(self.attributes):
            for right in self.attributes[index + 1 :]:
                degree = self.contradiction_degree(left, right)
                max_degree = max(max_degree, degree)
                pairs.append({"left": left.name, "right": right.name, "degree": degree})
        return {"max_degree": max_degree, "pair_count": len(pairs), "pairs": pairs}

    def weighted_cumulative_truth(self) -> dict[str, float]:
        if not self.attributes:
            return {"T": 0.0, "I": 0.0, "F": 0.0}
        weight_sum = sum(max(0.0, item.weight) for item in self.attributes) or 1.0
        return {
            "T": clamp01(sum(item.tif.bounded().T * max(0.0, item.weight) for item in self.attributes) / weight_sum),
            "I": clamp01(sum(item.tif.bounded().I * max(0.0, item.weight) for item in self.attributes) / weight_sum),
            "F": clamp01(sum(item.tif.bounded().F * max(0.0, item.weight) for item in self.attributes) / weight_sum),
        }

    def system_indeterminacy_chain(self) -> SystemIndeterminacyChain:
        if not self.attributes:
            return TIF(T=0.0, I=1.0, F=0.0, I_system=1.0, H_lex=1.0, G_lex=1.0, I_lexicon=1.0).system_chain()
        truth = self.weighted_cumulative_truth()
        contradiction = float(self.contradiction_summary()["max_degree"])
        h_lex = clamp01(max(truth["I"], contradiction))
        g_lex = clamp01(1.0 - max(0.0, truth["T"] - truth["F"]))
        i_lexicon = clamp01((h_lex + g_lex + contradiction) / 3.0)
        return TIF(T=truth["T"], I=truth["I"], F=truth["F"], I_system=h_lex, H_lex=h_lex, G_lex=g_lex, I_lexicon=i_lexicon).system_chain()

    def feature_vector(self) -> list[float]:
        truth = self.weighted_cumulative_truth()
        contradictions = self.contradiction_summary()
        chain = self.system_indeterminacy_chain()
        return [truth["T"], truth["I"], truth["F"], float(contradictions["max_degree"]), chain.H_lex, chain.G_lex, chain.I_lexicon]

    def indeterminacy_profile(self) -> dict[str, object]:
        chain = self.system_indeterminacy_chain()
        return {
            "classification_family": "I",
            "plithogenic_classified_as": "I_system^S",
            "plithogenic_i_profile": PlithogenicIProfile().as_dict(),
            "weighted_I": self.weighted_cumulative_truth()["I"] if self.attributes else 1.0,
            "system_indeterminacy_chain": chain.as_dict(),
            "chain_count": len(self.attributes),
            "rule": "Plithogenic classification is treated as a system-level aggregation and contradiction layer before final lexicon selection.",
            "hierarchy": HIERARCHY,
        }

    def profile(self) -> dict[str, object]:
        return {
            "model": "synthia_plithogenic_matrix_v2",
            "classification_family": "I",
            "plithogenic_classified_as": "I_system^S",
            "attributes": [item.as_dict() for item in self.attributes],
            "weighted_cumulative_truth": self.weighted_cumulative_truth(),
            "contradiction_summary": self.contradiction_summary(),
            "indeterminacy_profile": self.indeterminacy_profile(),
            "feature_vector": self.feature_vector(),
            "hierarchy": HIERARCHY,
        }


def payload_or_none(payload: Mapping[str, object], key: str) -> object | None:
    return payload.get(key) if key in payload else None


def math_sources_payload(public_only: bool = True) -> list[dict[str, object]]:
    return [
        source.as_dict()
        for source in MATH_SOURCES.values()
        if source.public_safe or not public_only
    ]


def explain_i_chain(term: str = "", domain: str = "general") -> dict[str, object]:
    lowered = f"{term} {domain}".lower()
    carrier_type = "fractal_geometry" if domain == "fractal_geometry" else "lexicon_distribution"
    chain = TIF(T=0.0, I=1.0, F=0.0, I_system=1.0, H_lex=1.0, G_lex=1.0, I_lexicon=1.0).system_chain(carrier_type=carrier_type)
    payload = {
        "term": term,
        "domain": domain,
        "selected_layer": "I_lexicon",
        "carrier_type": carrier_type,
        "selected_layer_detail": INDETERMINACY_LAYERS["I_lexicon"].as_dict(),
        "hierarchy": HIERARCHY,
        "layers": [INDETERMINACY_LAYERS[symbol].as_dict() for symbol in DEFAULT_LAYER_ORDER],
        "system_indeterminacy_chain": chain.as_dict(),
        "public_sources": math_sources_payload(public_only=True),
    }
    if "plitho" in lowered or "contradiction" in lowered:
        payload["plithogenic_i_profile"] = PlithogenicIProfile().as_dict()
    if carrier_type == "fractal_geometry":
        payload["specialized_carrier"] = FractalCarrierProfile().as_dict()
    return payload


def classify_i_chain_text(text: str, domain: str) -> dict[str, object]:
    from .neutrosophic_foundation import foundation_profile_for_text

    lowered = text.lower()
    carrier_type = "fractal_geometry" if domain == "fractal_geometry" else "lexicon_distribution"
    chain = TIF(
        T=0.7,
        I=0.3,
        F=0.0,
        I_system=0.3,
        H_lex=0.3,
        G_lex=0.3,
        I_lexicon=0.3,
    ).system_chain(carrier_type=carrier_type)
    payload = {
        "domain": domain,
        "text": text,
        "selected_layer": "I_lexicon" if carrier_type == "lexicon_distribution" else "I_system^S",
        "carrier_type": carrier_type,
        "selected_layer_detail": INDETERMINACY_LAYERS["I_lexicon"].as_dict(),
        "chain": explain_i_chain(text, domain=domain),
        "plithogenic_profile": PlithogenicIProfile().as_dict() if "plitho" in lowered or "contradiction" in lowered else None,
        "system_indeterminacy_chain": chain.as_dict(),
        "hierarchy": HIERARCHY,
    }
    foundation_profile = foundation_profile_for_text(text)
    if foundation_profile is not None:
        payload["foundation_profile"] = foundation_profile
    return payload


def plithogenic_profile_for_source(source_id: str) -> dict[str, object]:
    profile = PlithogenicIProfile().as_dict()
    profile["requested_source_id"] = source_id
    profile["requested_source"] = MATH_SOURCES.get(source_id, MathSource(source_id, "Unregistered source", None, "unknown", "unregistered")).as_dict()
    profile["public_sources"] = math_sources_payload(public_only=True)
    profile["hierarchy"] = HIERARCHY
    return profile
