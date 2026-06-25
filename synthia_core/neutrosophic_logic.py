"""Neutrosophic logic proposition profiles for Synthia phases 5-6."""

from __future__ import annotations

from dataclasses import dataclass

from .neutrosophic_foundation import NeutrosophicTruthValue, get_neutrosophic_profile
from .neutrosophic_sets import IFSCompatibilityResult
from .safety import HIERARCHY


LOGIC_GENERALIZES_IFL_SOURCE_ID = "nss.logic_generalizes_ifl"
INTRO_LOGIC_SOURCE_ID = "nss.introduction_neutrosophic_logic"
LOGIC_GENERALIZES_IFL_URL = "https://fs.unm.edu/IFL-generalized.pdf"
INTRO_LOGIC_URL = "https://fs.unm.edu/IntrodNeutLogic.pdf"
EPSILON = 1e-9


@dataclass(frozen=True)
class NeutrosophicLogicSource:
    source_id: str
    title: str
    url: str
    phase: int
    role: str
    evidence_kind: str = "public_nss"

    def as_dict(self) -> dict[str, object]:
        return {
            "source_id": self.source_id,
            "title": self.title,
            "url": self.url,
            "phase": self.phase,
            "role": self.role,
            "evidence_kind": self.evidence_kind,
            "public_safe": True,
        }


LOGIC_SOURCES: tuple[NeutrosophicLogicSource, ...] = (
    NeutrosophicLogicSource(
        LOGIC_GENERALIZES_IFL_SOURCE_ID,
        "Neutrosophic Logic as a Generalization of Intuitionistic Fuzzy Logic",
        LOGIC_GENERALIZES_IFL_URL,
        5,
        "Formal boundary between intuitionistic fuzzy logic and broader neutrosophic logic.",
    ),
    NeutrosophicLogicSource(
        INTRO_LOGIC_SOURCE_ID,
        "Introduction to Neutrosophic Logic",
        INTRO_LOGIC_URL,
        6,
        "Public educational reference for proposition-level T/I/F interpretation.",
    ),
)


@dataclass(frozen=True)
class NeutrosophicProposition:
    text: str
    T: float
    I: float
    F: float
    profile: str = "standard"

    def truth_value(self) -> NeutrosophicTruthValue:
        return NeutrosophicTruthValue(
            T=float(self.T),
            I=float(self.I),
            F=float(self.F),
            profile=get_neutrosophic_profile(self.profile),
        )

    def as_dict(self) -> dict[str, object]:
        truth_value = self.truth_value()
        return {
            "text": self.text,
            "formal_value": truth_value.formal_value(),
            "operational_tif": truth_value.to_operational_tif().as_dict(),
            "sources": [source.as_dict() for source in LOGIC_SOURCES],
            "hierarchy": HIERARCHY,
        }


@dataclass(frozen=True)
class NeutrosophicLogicProfile:
    proposition: NeutrosophicProposition
    classifications: tuple[str, ...]
    ifl_compatibility: dict[str, object]

    def as_dict(self) -> dict[str, object]:
        payload = self.proposition.as_dict()
        payload.update(
            {
                "logic_classification": list(self.classifications),
                "primary_classification": self.classifications[0],
                "ifl_compatibility": self.ifl_compatibility,
                "boundary": (
                    "IFL compatibility is diagnostic; neutrosophic logic preserves "
                    "independent truth, indeterminacy, and falsity."
                ),
            }
        )
        return payload


class LogicCompatibilityClassifier:
    """Deterministic proposition classifier for public NSS logic sources."""

    def classify(self, T: float, I: float, F: float, text: str = "", profile: str | None = None) -> dict[str, object]:
        selected_profile = profile or self._profile_for(T, I, F, text)
        proposition = NeutrosophicProposition(text=text, T=float(T), I=float(I), F=float(F), profile=selected_profile)
        classifications = tuple(self._classifications(float(T), float(I), float(F), text))
        ifl = self.compare_ifl(T, I, F)
        return NeutrosophicLogicProfile(proposition, classifications, ifl).as_dict()

    def compare_ifl(self, T: float, I: float, F: float) -> dict[str, object]:
        result = IFSCompatibilityResult(float(T), float(I), float(F)).as_dict()
        result["logic_boundary"] = (
            "Intuitionistic fuzzy logic compatibility requires bounded T/F with T+F <= 1; "
            "Synthia keeps the full neutrosophic proposition when this fails."
        )
        result["hierarchy"] = HIERARCHY
        result["sources"] = [LOGIC_SOURCES[0].as_dict()]
        return result

    def explain(self) -> dict[str, object]:
        return {
            "sources": [source.as_dict() for source in LOGIC_SOURCES],
            "roles": [
                "proposition-level T/I/F",
                "relative and absolute truth/falsity markers",
                "IFL compatibility diagnostics",
                "paraconsistent, incomplete, paradoxist, and general neutrosophic logic profiles",
            ],
            "classification_labels": [
                "absolute_truth",
                "absolute_falsity",
                "absolute_indeterminacy",
                "relative_truth",
                "incomplete",
                "paraconsistent",
                "paradoxist",
                "ifl_compatible",
                "general_neutrosophic_logic",
            ],
            "hierarchy": HIERARCHY,
        }

    @staticmethod
    def _profile_for(T: float, I: float, F: float, text: str) -> str:
        lowered = text.lower()
        if "paradox" in lowered or (T >= 0.75 and F >= 0.75):
            return "paradoxist"
        if "contradiction" in lowered or "both true" in lowered:
            return "dialetheist"
        if I >= max(T, F):
            return "uncertain"
        return "standard"

    @staticmethod
    def _classifications(T: float, I: float, F: float, text: str) -> list[str]:
        classifications: list[str] = []
        lowered = text.lower()
        if T > 1.0:
            classifications.append("absolute_truth")
        if F > 1.0:
            classifications.append("absolute_falsity")
        if I > 1.0:
            classifications.append("absolute_indeterminacy")

        bounded = all(0.0 <= value <= 1.0 for value in (T, I, F))
        if bounded and T > 0.0:
            classifications.append("relative_truth")
        total = T + I + F
        if bounded:
            if total < 1.0 - EPSILON:
                classifications.append("incomplete")
            elif total > 1.0 + EPSILON:
                classifications.append("paraconsistent")
            if T + F <= 1.0 + EPSILON:
                classifications.append("ifl_compatible")
        if "paradox" in lowered or (T >= 0.75 and F >= 0.75):
            classifications.append("paradoxist")
        classifications.append("general_neutrosophic_logic")
        return classifications


def logic_profile_for_text(text: str) -> dict[str, object] | None:
    lowered = text.lower()
    triggers = ("logic", "proposition", "ifl", "intuitionistic fuzzy logic", "paradox", "contradiction")
    if not any(trigger in lowered for trigger in triggers):
        return None
    if "paradox" in lowered:
        return LogicCompatibilityClassifier().classify(1.0, 0.2, 1.0, text=text)
    if "incomplete" in lowered:
        return LogicCompatibilityClassifier().classify(0.2, 0.2, 0.2, text=text)
    return LogicCompatibilityClassifier().classify(0.6, 0.2, 0.1, text=text)
