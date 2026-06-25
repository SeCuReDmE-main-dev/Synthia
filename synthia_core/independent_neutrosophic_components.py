"""Independent and offset neutrosophic component profiles for Synthia phase 12."""

from __future__ import annotations

from dataclasses import dataclass

from .plithogenic import TIF, clamp01
from .safety import HIERARCHY


COMPONENTS_SOURCE_ID = "nss.independent_neutrosophic_components"
COMPONENTS_SOURCE_URL = "https://fs.unm.edu/NSS/PracticalIndependentNeutrosophic36.pdf"
VALID_MODES = ("independent", "partial", "dependent", "offset")


@dataclass(frozen=True)
class IndependentTIFComponentProfile:
    T: float
    I: float
    F: float
    mode: str = "independent"

    def classifications(self) -> list[str]:
        mode = self.mode if self.mode in VALID_MODES else "independent"
        labels = [f"{mode}_components"]
        if any(value > 1.0 for value in (self.T, self.I, self.F)):
            labels.append("over_component")
        if any(value < 0.0 for value in (self.T, self.I, self.F)):
            labels.append("under_component")
        if mode == "offset" or any(value < 0.0 or value > 1.0 for value in (self.T, self.I, self.F)):
            labels.append("offset_components")
        labels.append("general_neutrosophic_components")
        return labels

    def dependency_score(self) -> float:
        scores = {"independent": 0.0, "partial": 0.5, "dependent": 1.0, "offset": 0.35}
        return scores.get(self.mode, 0.0)

    def operational_tif(self) -> TIF:
        load = clamp01(max(abs(self.I), self.dependency_score()))
        if "offset_components" in self.classifications():
            load = clamp01(max(load, 0.4))
        return TIF(T=clamp01(self.T), I=clamp01(self.I), F=clamp01(self.F), I_system=load, H_lex=load, G_lex=load, I_lexicon=load)

    def as_dict(self) -> dict[str, object]:
        classifications = self.classifications()
        return {
            "formal_components": {"T": self.T, "I": self.I, "F": self.F},
            "mode": self.mode,
            "component_classification": classifications,
            "primary_classification": classifications[0],
            "dependency_score": self.dependency_score(),
            "operational_tif": self.operational_tif().as_dict(),
            "source": source_payload(),
            "hierarchy": HIERARCHY,
        }


def classify_components(T: float, I: float, F: float, mode: str = "independent") -> dict[str, object]:
    return IndependentTIFComponentProfile(float(T), float(I), float(F), mode).as_dict()


def components_explain() -> dict[str, object]:
    return {
        "source": source_payload(),
        "modes": list(VALID_MODES),
        "roles": [
            "preserve T, I, and F as independent or partially dependent components",
            "preserve offset values outside 0..1 as formal metadata",
            "derive bounded operational TIF for Synthia scoring",
        ],
        "hierarchy": HIERARCHY,
    }


def independent_components_profile_for_text(text: str) -> dict[str, object] | None:
    lowered = text.lower()
    if not any(term in lowered for term in ("independent component", "offset component", "trivariate", "multivariate truth")):
        return None
    mode = "offset" if "offset" in lowered else "independent"
    return classify_components(1.2 if mode == "offset" else 0.7, 0.3, -0.1 if mode == "offset" else 0.1, mode)


def source_payload() -> dict[str, object]:
    return {
        "source_id": COMPONENTS_SOURCE_ID,
        "title": "Practical Applications of the Independent Neutrosophic Components and of the Neutrosophic Offset Components",
        "url": COMPONENTS_SOURCE_URL,
        "evidence_kind": "public_nss",
        "public_safe": True,
    }
