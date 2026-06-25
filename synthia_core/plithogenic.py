"""Bounded plithogenic helpers for Synthia's I_lexicon."""

from __future__ import annotations

from dataclasses import dataclass
from math import fabs
from typing import Iterable, Mapping

from .safety import HIERARCHY


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


@dataclass(frozen=True)
class MathSource:
    """Public or private-safe source pointer for Synthia math doctrine."""

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
    "nss.neutrogeometry_fractal": MathSource(
        "nss.neutrogeometry_fractal",
        "NeutroGeometry and Fractal Geometry",
        "https://fs.unm.edu/NSS/01NeutroGeometryFractal.pdf",
        "public_nss",
        "fractal geometry, fractal dimension, and indeterminacy",
    ),
    "nss.neutrosophy_hub": MathSource(
        "nss.neutrosophy_hub",
        "NSS / Neutrosophy source hub",
        "https://fs.unm.edu/neutrosophy.htm",
        "public_nss",
        "source index for neutrosophic and plithogenic theories",
    ),
    "private.gmail.prof_fs.plitho_i_system": MathSource(
        "private.gmail.prof_fs.plitho_i_system",
        "Private Gmail evidence ledger: Prof. FS plithogenic system-indeterminacy thread",
        None,
        "private_gmail_metadata",
        "working doctrine that plithogenic belongs under I_system^S",
        public_safe=False,
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
        algorithm="I_system^S := system_scope(I, lexicon_domain, agent_state)",
        aliases=("I_s", "I_s_system", "I_system"),
    ),
    "D_f": SymbolicNotation(
        canonical_id="D_f",
        ascii="D_f",
        latex=r"D_f",
        unicode="D_f",
        algorithm="D_f := fractal_depth_or_dimension(I_system^S)",
    ),
    "dF": SymbolicNotation(
        canonical_id="dF",
        ascii="dF",
        latex=r"dF",
        unicode="dF",
        algorithm="dF := abs(D_f - I_system^S)",
    ),
    "i_fractal": SymbolicNotation(
        canonical_id="i_fractal",
        ascii="i_fractal",
        latex=r"i_{\mathrm{fractal}}",
        unicode="i_fractal",
        algorithm="i_fractal := recursive_fractalized_indeterminacy(I, I_system^S, D_f, dF)",
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
        ("nss.indeterminacy",),
    ),
    "I_system^S": IndeterminacyLayer(
        "I_system^S",
        1,
        "system-scoped indeterminacy inside the active lexicon or agent system",
        SYMBOLIC_NOTATIONS["I_system^S"],
        ("nss.indeterminacy", "nss.plithogenic_logic", "private.gmail.prof_fs.plitho_i_system"),
    ),
    "D_f": IndeterminacyLayer(
        "D_f",
        2,
        "fractal depth or dimension marker of the indeterminate structure",
        SYMBOLIC_NOTATIONS["D_f"],
        ("nss.neutrogeometry_fractal",),
    ),
    "dF": IndeterminacyLayer(
        "dF",
        3,
        "delta-fractal drift between system indeterminacy and fractal depth",
        SYMBOLIC_NOTATIONS["dF"],
        ("nss.neutrogeometry_fractal",),
    ),
    "i_fractal": IndeterminacyLayer(
        "i_fractal",
        4,
        "fractalized indeterminacy retained for recursive classification",
        SYMBOLIC_NOTATIONS["i_fractal"],
        ("nss.indeterminacy", "nss.neutrogeometry_fractal"),
    ),
}

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
class PlithogenicIProfile:
    """Synthia doctrine: plithogenic work belongs to I_system^S."""

    canonical_indeterminacy_class: str = "I_system^S"
    role: str = "multi-attribute / multi-variable system indeterminacy organizer"
    evidence_status: str = "public_nss_supported + gmail_prof_fs_confirmed_inferred"
    source_ids: tuple[str, ...] = (
        "nss.indeterminacy",
        "nss.plithogenic_set",
        "nss.plithogenic_logic",
        "nss.plithogenic_probability_statistics",
        "nss.symbolic_plithogenic_algebra",
        "private.gmail.prof_fs.plitho_i_system",
    )
    private_evidence_ids: tuple[str, ...] = ("gmail.thread.19edbb1c9fd0030e",)

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
            "private_evidence_ids": list(self.private_evidence_ids),
            "human_authority_boundary": "Gmail evidence guides Synthia doctrine; public NSS sources remain the formal math sources.",
        }


@dataclass(frozen=True)
class IndeterminacyChain:
    """Explicit Synthia hierarchy for non-collapsed indeterminacy."""

    I: float
    I_system: float
    D_f: float
    dF: float
    i_fractal: float
    source: str = "derived"

    @classmethod
    def from_tif(cls, tif: "TIF") -> "IndeterminacyChain":
        bounded = tif.bounded()
        base_i = bounded.I
        system_i = base_i if bounded.I_system is None else bounded.I_system
        fractal_dimension = system_i if bounded.D_f is None else float(bounded.D_f)
        delta_fractal = abs(fractal_dimension - system_i) if bounded.dF is None else float(bounded.dF)
        fractalized_i = (
            clamp01(max(base_i, system_i, min(1.0, abs(delta_fractal))))
            if bounded.i_fractal is None
            else bounded.i_fractal
        )
        return cls(
            I=base_i,
            I_system=system_i,
            D_f=fractal_dimension,
            dF=delta_fractal,
            i_fractal=fractalized_i,
            source="explicit_or_derived",
        )

    def as_dict(self) -> dict[str, object]:
        return {
            "I": clamp01(self.I),
            "I_system^S": clamp01(self.I_system),
            "D_f": float(self.D_f),
            "dF": float(self.dF),
            "i_fractal": clamp01(self.i_fractal),
            "hierarchy": HIERARCHY,
            "classification_family": "I",
            "source": self.source,
            "layers": [INDETERMINACY_LAYERS[symbol].as_dict() for symbol in ("I", "I_system^S", "D_f", "dF", "i_fractal")],
        }


@dataclass(frozen=True)
class TIF:
    """Truth, indeterminacy, falsity triplet."""

    T: float = 1.0
    I: float = 0.0
    F: float = 0.0
    I_system: float | None = None
    D_f: float | None = None
    dF: float | None = None
    i_fractal: float | None = None

    def bounded(self) -> "TIF":
        return TIF(
            T=clamp01(self.T),
            I=clamp01(self.I),
            F=clamp01(self.F),
            I_system=None if self.I_system is None else clamp01(self.I_system),
            D_f=None if self.D_f is None else float(self.D_f),
            dF=None if self.dF is None else float(self.dF),
            i_fractal=None if self.i_fractal is None else clamp01(self.i_fractal),
        )

    def as_dict(self) -> dict[str, object]:
        bounded = self.bounded()
        chain = IndeterminacyChain.from_tif(bounded)
        explicit_layer = "I"
        if bounded.I_system is not None:
            explicit_layer = "I_system^S"
        if bounded.D_f is not None:
            explicit_layer = "D_f"
        if bounded.dF is not None:
            explicit_layer = "dF"
        if bounded.i_fractal is not None:
            explicit_layer = "i_fractal"
        return {
            "T": bounded.T,
            "I": bounded.I,
            "F": bounded.F,
            "I_system^S": bounded.I_system,
            "D_f": bounded.D_f,
            "dF": bounded.dF,
            "i_fractal": bounded.i_fractal,
            "indeterminacy_chain": chain.as_dict(),
            "i_lexicon_layer": explicit_layer,
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
                        I_system=tif_payload.get("I_system^S") if "I_system^S" in tif_payload else item.get("I_system"),
                        D_f=tif_payload.get("D_f") if "D_f" in tif_payload else item.get("D_f"),
                        dF=tif_payload.get("dF") if "dF" in tif_payload else item.get("dF"),
                        i_fractal=tif_payload.get("i_fractal") if "i_fractal" in tif_payload else item.get("i_fractal"),
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

    def feature_vector(self) -> list[float]:
        truth = self.weighted_cumulative_truth()
        contradictions = self.contradiction_summary()
        return [truth["T"], truth["I"], truth["F"], float(contradictions["max_degree"])]

    def indeterminacy_profile(self) -> dict[str, object]:
        plithogenic_i = PlithogenicIProfile().as_dict()
        if not self.attributes:
            chain = IndeterminacyChain.from_tif(TIF(T=0.0, I=1.0, F=0.0, I_system=1.0, D_f=1.0, dF=0.0, i_fractal=1.0))
            return {
                "classification_family": "I",
                "plithogenic_classified_as": "I_system^S",
                "plithogenic_i_profile": plithogenic_i,
                "dominant_chain": chain.as_dict(),
                "chain_count": 0,
                "hierarchy": HIERARCHY,
            }
        weighted_i = self.weighted_cumulative_truth()["I"]
        dominant = max(
            (IndeterminacyChain.from_tif(item.tif) for item in self.attributes),
            key=lambda chain: chain.i_fractal,
        )
        return {
            "classification_family": "I",
            "plithogenic_classified_as": "I_system^S",
            "plithogenic_i_profile": plithogenic_i,
            "weighted_I": weighted_i,
            "dominant_chain": dominant.as_dict(),
            "chain_count": len(self.attributes),
            "rule": "Plithogenic classification is treated as an I-family operation because contradiction and attribute multiplicity are organized indeterminacy.",
            "hierarchy": HIERARCHY,
        }

    def profile(self) -> dict[str, object]:
        return {
            "model": "synthia_plithogenic_matrix_v1",
            "classification_family": "I",
            "plithogenic_classified_as": "I_system^S",
            "attributes": [item.as_dict() for item in self.attributes],
            "weighted_cumulative_truth": self.weighted_cumulative_truth(),
            "contradiction_summary": self.contradiction_summary(),
            "indeterminacy_profile": self.indeterminacy_profile(),
            "feature_vector": self.feature_vector(),
            "hierarchy": HIERARCHY,
        }


def math_sources_payload(public_only: bool = True) -> list[dict[str, object]]:
    return [
        source.as_dict()
        for source in MATH_SOURCES.values()
        if source.public_safe or not public_only
    ]


def explain_i_chain(term: str = "") -> dict[str, object]:
    lowered = term.lower()
    selected = "I_system^S" if "plitho" in lowered else "I"
    if "d_f" in lowered or "dimension" in lowered:
        selected = "D_f"
    elif "df" in lowered or "delta" in lowered or "drift" in lowered:
        selected = "dF"
    elif "fractal" in lowered:
        selected = "i_fractal"
    return {
        "term": term,
        "selected_layer": selected,
        "selected_layer_detail": INDETERMINACY_LAYERS[selected].as_dict(),
        "hierarchy": HIERARCHY,
        "layers": [INDETERMINACY_LAYERS[symbol].as_dict() for symbol in ("I", "I_system^S", "D_f", "dF", "i_fractal")],
        "plithogenic_i_profile": PlithogenicIProfile().as_dict() if "plitho" in lowered else None,
        "public_sources": math_sources_payload(public_only=True),
    }


def classify_i_chain_text(text: str, domain: str) -> dict[str, object]:
    lowered = text.lower()
    if "plitho" in lowered or "contradiction" in lowered or "attribute" in lowered:
        selected = "I_system^S"
    elif "dimension" in lowered or "d_f" in lowered:
        selected = "D_f"
    elif "delta" in lowered or "drift" in lowered or "df" in lowered:
        selected = "dF"
    elif "fractal" in lowered:
        selected = "i_fractal"
    else:
        selected = "I"
    return {
        "domain": domain,
        "text": text,
        "selected_layer": selected,
        "selected_layer_detail": INDETERMINACY_LAYERS[selected].as_dict(),
        "chain": explain_i_chain(text),
        "plithogenic_profile": PlithogenicIProfile().as_dict() if selected == "I_system^S" else None,
        "hierarchy": HIERARCHY,
    }


def plithogenic_profile_for_source(source_id: str) -> dict[str, object]:
    profile = PlithogenicIProfile().as_dict()
    profile["requested_source_id"] = source_id
    profile["requested_source"] = MATH_SOURCES.get(source_id, MathSource(source_id, "Unregistered source", None, "unknown", "unregistered")).as_dict()
    profile["public_sources"] = math_sources_payload(public_only=True)
    profile["hierarchy"] = HIERARCHY
    return profile
