"""Neutrosophic set membership interpretation for Synthia."""

from __future__ import annotations

from dataclasses import dataclass

from .neutrosophic_foundation import NeutrosophicTruthValue, get_neutrosophic_profile
from .plithogenic import TIF, clamp01
from .safety import HIERARCHY


SET_SOURCE_ID = "nss.neutrosophic_set_generalizes_ifs"
SET_SOURCE_URL = "https://fs.unm.edu/IFS-generalized.pdf"
EPSILON = 1e-9


@dataclass(frozen=True)
class NeutrosophicSetSource:
    source_id: str = SET_SOURCE_ID
    title: str = "Neutrosophic Set as a Generalization of the Intuitionistic Fuzzy Set"
    url: str = SET_SOURCE_URL
    evidence_kind: str = "public_nss"
    role: str = "Public source for T/I/F set membership and IFS comparison boundaries."

    def as_dict(self) -> dict[str, object]:
        return {
            "source_id": self.source_id,
            "title": self.title,
            "url": self.url,
            "evidence_kind": self.evidence_kind,
            "role": self.role,
            "public_safe": True,
        }


@dataclass(frozen=True)
class TIFDependencyProfile:
    T: float
    I: float
    F: float

    def as_dict(self) -> dict[str, object]:
        formal_sum = self.T + self.I + self.F
        bounded_components = all(0.0 <= value <= 1.0 for value in (self.T, self.I, self.F))
        return {
            "formal_sum_TIF": formal_sum,
            "bounded_components": bounded_components,
            "components_independent": True,
            "dependency_boundary": "IFS constrains T and F through T+F <= 1; neutrosophic sets keep T, I, and F separately interpretable.",
        }


@dataclass(frozen=True)
class IFSCompatibilityResult:
    T: float
    I: float
    F: float

    def as_dict(self) -> dict[str, object]:
        bounded_TF = 0.0 <= self.T <= 1.0 and 0.0 <= self.F <= 1.0
        compatible = bounded_TF and self.T + self.F <= 1.0 + EPSILON
        return {
            "is_ifs_compatible": compatible,
            "T_plus_F": self.T + self.F,
            "bounded_TF": bounded_TF,
            "reason": "T and F are bounded and T+F <= 1." if compatible else "IFS compatibility rejected because T/F are unbounded or T+F > 1.",
            "source": NeutrosophicSetSource().as_dict(),
        }


@dataclass(frozen=True)
class NeutrosophicSetMembership:
    T: float
    I: float
    F: float
    profile: str = "standard"

    def formal_truth_value(self) -> NeutrosophicTruthValue:
        return NeutrosophicTruthValue(T=self.T, I=self.I, F=self.F, profile=get_neutrosophic_profile(self.profile))

    def operational_tif(self) -> TIF:
        return self.formal_truth_value().to_operational_tif()

    def as_dict(self) -> dict[str, object]:
        truth_value = self.formal_truth_value()
        return {
            "formal_value": truth_value.formal_value(),
            "operational_tif": self.operational_tif().as_dict(),
            "dependency_profile": TIFDependencyProfile(self.T, self.I, self.F).as_dict(),
            "ifs_compatibility": IFSCompatibilityResult(self.T, self.I, self.F).as_dict(),
            "source": NeutrosophicSetSource().as_dict(),
            "hierarchy": HIERARCHY,
        }


class NeutrosophicSetClassifier:
    """Classify formal T/I/F tuples under neutrosophic set-membership boundaries."""

    def classify(self, T: float, I: float, F: float, profile: str = "standard") -> dict[str, object]:
        membership = NeutrosophicSetMembership(T=float(T), I=float(I), F=float(F), profile=profile)
        classifications = self._classifications(float(T), float(I), float(F))
        payload = membership.as_dict()
        payload["set_membership_classification"] = classifications
        payload["primary_classification"] = classifications[0]
        payload["boundary"] = "IFS compatibility is diagnostic; general neutrosophic membership preserves formal T/I/F."
        return payload

    def compare_ifs(self, T: float, I: float, F: float) -> dict[str, object]:
        result = IFSCompatibilityResult(float(T), float(I), float(F)).as_dict()
        result["set_classification"] = self.classify(T, I, F)["set_membership_classification"]
        result["hierarchy"] = HIERARCHY
        return result

    @staticmethod
    def _classifications(T: float, I: float, F: float) -> list[str]:
        classifications: list[str] = []
        for label, value in (("membership", T), ("indeterminacy", I), ("nonmembership", F)):
            if value > 1.0:
                classifications.append(f"over_{label}")
            if value < 0.0:
                classifications.append(f"under_{label}")

        bounded = all(0.0 <= value <= 1.0 for value in (T, I, F))
        total = T + I + F
        if bounded:
            if abs(total - 1.0) <= EPSILON:
                classifications.append("consistent_complete")
            elif total < 1.0:
                classifications.append("incomplete")
            else:
                classifications.append("paraconsistent")
            if T + F <= 1.0 + EPSILON:
                classifications.append("intuitionistic_fuzzy_compatible")
        classifications.append("general_neutrosophic")
        return classifications

    def explain(self) -> dict[str, object]:
        return {
            "source": NeutrosophicSetSource().as_dict(),
            "roles": [
                "membership T",
                "indeterminacy I",
                "non-membership F",
                "T+I+F interpretation",
                "intuitionistic fuzzy set compatibility",
                "paraconsistent and incomplete set diagnostics",
            ],
            "classification_labels": [
                "consistent_complete",
                "incomplete",
                "paraconsistent",
                "intuitionistic_fuzzy_compatible",
                "over_membership",
                "under_membership",
                "over_indeterminacy",
                "under_indeterminacy",
                "over_nonmembership",
                "under_nonmembership",
                "general_neutrosophic",
            ],
            "hierarchy": HIERARCHY,
        }


def set_membership_profile_for_text(text: str) -> dict[str, object] | None:
    lowered = text.lower()
    triggers = (
        "set",
        "membership",
        "non-membership",
        "nonmembership",
        "ifs",
        "intuitionistic fuzzy",
        "paraconsistent",
        "incomplete",
    )
    if not any(trigger in lowered for trigger in triggers):
        return None
    if "paraconsistent" in lowered:
        return NeutrosophicSetClassifier().classify(0.3, 0.51, 0.28)
    if "incomplete" in lowered:
        return NeutrosophicSetClassifier().classify(0.1, 0.3, 0.4)
    return NeutrosophicSetClassifier().classify(0.5, 0.2, 0.3)
