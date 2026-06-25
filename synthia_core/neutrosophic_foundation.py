"""Neutrosophic foundation profiles and bounded Synthia normalization."""

from __future__ import annotations

from dataclasses import dataclass

from .plithogenic import TIF, clamp01
from .safety import HIERARCHY


FOUNDATION_SOURCE_ID = "nss.unifying_field_logics"
FOUNDATION_URL = "https://fs.unm.edu/eBook-Neutrosophics6.pdf"


@dataclass(frozen=True)
class NeutrosophicFoundationSource:
    source_id: str = FOUNDATION_SOURCE_ID
    title: str = "A Unifying Field in Logics: Neutrosophic Logic, Neutrosophy, Neutrosophic Set, Probability and Statistics"
    url: str = FOUNDATION_URL
    evidence_kind: str = "public_nss"
    role: str = "Primary public foundation for T/I/F, neutrosophic logic, set, probability, and statistics."

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
class NeutrosophicComponent:
    name: str
    value: float
    interpretation: str
    operational_value: float
    was_clamped: bool

    @classmethod
    def from_value(cls, name: str, value: float, interpretation: str) -> "NeutrosophicComponent":
        operational_value = clamp01(value)
        return cls(
            name=name,
            value=float(value),
            interpretation=interpretation,
            operational_value=operational_value,
            was_clamped=float(value) != operational_value,
        )

    def as_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "formal_value": self.value,
            "interpretation": self.interpretation,
            "operational_value": self.operational_value,
            "was_clamped": self.was_clamped,
        }


@dataclass(frozen=True)
class NeutrosophicProfile:
    name: str
    role: str
    allows_high_truth_and_falsity: bool
    indeterminacy_bias: float
    default_T: float
    default_I: float
    default_F: float
    source_id: str = FOUNDATION_SOURCE_ID

    def as_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "role": self.role,
            "allows_high_truth_and_falsity": self.allows_high_truth_and_falsity,
            "indeterminacy_bias": self.indeterminacy_bias,
            "defaults": {"T": self.default_T, "I": self.default_I, "F": self.default_F},
            "source_id": self.source_id,
        }


PROFILES: dict[str, NeutrosophicProfile] = {
    "standard": NeutrosophicProfile(
        "standard",
        "Ordinary bounded operational profile for current Synthia scoring.",
        False,
        0.0,
        1.0,
        0.0,
        0.0,
    ),
    "paradoxist": NeutrosophicProfile(
        "paradoxist",
        "Contradiction-aware profile where high truth and high falsity can coexist.",
        True,
        0.15,
        1.0,
        0.2,
        1.0,
    ),
    "dialetheist": NeutrosophicProfile(
        "dialetheist",
        "Set/proposition profile for contradiction-bearing membership.",
        True,
        0.2,
        1.0,
        0.25,
        1.0,
    ),
    "tautological": NeutrosophicProfile(
        "tautological",
        "Absolute or near-absolute truth profile.",
        False,
        0.0,
        1.0,
        0.0,
        0.0,
    ),
    "nihilist": NeutrosophicProfile(
        "nihilist",
        "Near-empty or denial-heavy profile.",
        False,
        0.05,
        0.0,
        0.05,
        1.0,
    ),
    "uncertain": NeutrosophicProfile(
        "uncertain",
        "Indeterminacy-dominant profile for unresolved evidence.",
        False,
        0.35,
        0.2,
        1.0,
        0.2,
    ),
}


def get_neutrosophic_profile(name: str) -> NeutrosophicProfile:
    key = name.strip().lower()
    if key not in PROFILES:
        raise KeyError(f"unknown neutrosophic profile: {name}")
    return PROFILES[key]


@dataclass(frozen=True)
class NeutrosophicTruthValue:
    T: float
    I: float
    F: float
    profile: NeutrosophicProfile
    source: NeutrosophicFoundationSource = NeutrosophicFoundationSource()

    def formal_value(self) -> dict[str, object]:
        return {
            "profile": self.profile.as_dict(),
            "components": {
                "T": NeutrosophicComponent.from_value("T", self.T, "truth").as_dict(),
                "I": NeutrosophicComponent.from_value("I", self.I, "indeterminacy").as_dict(),
                "F": NeutrosophicComponent.from_value("F", self.F, "falsity").as_dict(),
            },
            "allows_high_truth_and_falsity": self.profile.allows_high_truth_and_falsity,
            "source": self.source.as_dict(),
        }

    def to_operational_tif(self) -> TIF:
        operational_i = clamp01(max(self.I, self.profile.indeterminacy_bias))
        if self.profile.allows_high_truth_and_falsity and self.T > 0.75 and self.F > 0.75:
            operational_i = clamp01(max(operational_i, 0.5))
        return TIF(
            T=clamp01(self.T),
            I=clamp01(self.I),
            F=clamp01(self.F),
            I_system=operational_i,
            H_lex=operational_i,
            G_lex=operational_i,
            I_lexicon=operational_i,
        )

    def as_dict(self) -> dict[str, object]:
        operational_tif = self.to_operational_tif()
        return {
            "formal_value": self.formal_value(),
            "operational_tif": operational_tif.as_dict(),
            "normalization_policy": TIFNormalizationPolicy().as_dict(),
            "hierarchy": HIERARCHY,
        }


@dataclass(frozen=True)
class TIFNormalizationPolicy:
    name: str = "synthia_bounded_operational_tif_v1"
    role: str = "Preserve formal neutrosophic values while clamping operational TIF values for Synthia scoring."
    source_id: str = FOUNDATION_SOURCE_ID

    def normalize(self, T: float, I: float, F: float, profile: str = "standard") -> dict[str, object]:
        truth_value = NeutrosophicTruthValue(T=T, I=I, F=F, profile=get_neutrosophic_profile(profile))
        return truth_value.as_dict()

    def as_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "role": self.role,
            "source_id": self.source_id,
            "formal_boundary": "Formal neutrosophic values are preserved as provided.",
            "operational_boundary": "Synthia runtime values are bounded to 0..1 for deterministic scoring.",
        }


def foundation_explain() -> dict[str, object]:
    source = NeutrosophicFoundationSource()
    return {
        "source": source.as_dict(),
        "foundation_roles": [
            "base T/I/F doctrine",
            "neutrosophic logic propositions",
            "neutrosophic set membership",
            "neutrosophic probability events",
            "neutrosophic statistics context",
            "future-safe contradiction and special-profile categories",
        ],
        "profiles": [profile.as_dict() for profile in PROFILES.values()],
        "normalization_policy": TIFNormalizationPolicy().as_dict(),
        "hierarchy": HIERARCHY,
        "boundary": "This layer separates formal neutrosophic richness from Synthia's bounded operational scoring.",
    }


def foundation_profile(name: str) -> dict[str, object]:
    profile = get_neutrosophic_profile(name)
    truth_value = NeutrosophicTruthValue(
        T=profile.default_T,
        I=profile.default_I,
        F=profile.default_F,
        profile=profile,
    )
    payload = truth_value.as_dict()
    payload["profile"] = profile.as_dict()
    return payload


def foundation_normalize(T: float, I: float, F: float, profile: str = "standard") -> dict[str, object]:
    return TIFNormalizationPolicy().normalize(T=T, I=I, F=F, profile=profile)


def foundation_profile_for_text(text: str) -> dict[str, object] | None:
    lowered = text.lower()
    if any(term in lowered for term in ("paradox", "contradiction", "true and false")):
        return foundation_profile("paradoxist")
    if any(term in lowered for term in ("dialetheist", "both true", "set complement")):
        return foundation_profile("dialetheist")
    if any(term in lowered for term in ("tautology", "tautological", "absolute truth")):
        return foundation_profile("tautological")
    if any(term in lowered for term in ("nihilist", "empty set", "denial")):
        return foundation_profile("nihilist")
    if any(term in lowered for term in ("uncertain", "unknown", "unresolved", "indeterminate")):
        return foundation_profile("uncertain")
    if any(term in lowered for term in ("truth", "falsity", "probability", "statistics", "neutrosophic")):
        return foundation_profile("standard")
    return None
