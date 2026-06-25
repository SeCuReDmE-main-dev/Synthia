"""Hypersoft and plithogenic hypersoft kernel for Synthia phase 19."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product

from .plithogenic import PlithogenicIProfile, TIF, clamp01
from .safety import HIERARCHY


PLITHOGENIC_HYPERSOFT_SOURCE_ID = "nss.plithogenic_hypersoft_set"
PLITHOGENIC_HYPERSOFT_SOURCE_URL = "https://fs.unm.edu/NSS/ExtensionOfSoftSetToHypersoftSet.pdf"


@dataclass(frozen=True)
class HypersoftAttributeProduct:
    attributes: dict[str, tuple[str, ...]]

    @classmethod
    def from_raw(cls, raw: object) -> "HypersoftAttributeProduct":
        if not isinstance(raw, dict):
            raise ValueError("attributes must be a JSON object")
        attributes: dict[str, tuple[str, ...]] = {}
        for key, values in raw.items():
            if not isinstance(values, list):
                raise ValueError("each hypersoft attribute must map to a JSON array")
            attributes[str(key)] = tuple(str(value) for value in values)
        return cls(attributes)

    def combinations(self) -> tuple[dict[str, str], ...]:
        keys = tuple(self.attributes.keys())
        if not keys:
            return ()
        return tuple(dict(zip(keys, values)) for values in product(*(self.attributes[key] for key in keys)))

    def as_dict(self) -> dict[str, object]:
        combos = self.combinations()
        return {
            "attributes": {key: list(values) for key, values in self.attributes.items()},
            "combination_count": len(combos),
            "combinations": list(combos[:25]),
            "truncated": len(combos) > 25,
            "source": source_payload(),
            "hierarchy": HIERARCHY,
        }


def classify_hypersoft_mapping(mapping: object) -> dict[str, object]:
    if not isinstance(mapping, dict):
        raise ValueError("hypersoft mapping must be a JSON object")
    attributes = HypersoftAttributeProduct.from_raw(mapping.get("attributes", {}))
    memberships = mapping.get("memberships", [])
    if memberships is None:
        memberships = []
    if not isinstance(memberships, list):
        raise ValueError("memberships must be a JSON array")
    product_count = len(attributes.combinations())
    unresolved = max(0, product_count - len(memberships))
    indeterminacy_load = clamp01(unresolved / max(1, product_count))
    contradiction_load = 0.0
    normalized_memberships: list[dict[str, object]] = []
    for item in memberships:
        if not isinstance(item, dict):
            continue
        T = clamp01(float(item.get("T", 0.0)))
        I = clamp01(float(item.get("I", 0.0)))
        F = clamp01(float(item.get("F", 0.0)))
        contradiction = clamp01(abs(T - (1.0 - F)) + 0.5 * I)
        contradiction_load = max(contradiction_load, contradiction)
        normalized_memberships.append({"point": item.get("point", {}), "T": T, "I": I, "F": F, "contradiction_degree": contradiction})
    load = clamp01(max(indeterminacy_load, contradiction_load))
    tif = TIF(T=clamp01(1.0 - load), I=load, F=0.0, I_system=load, H_lex=load, G_lex=load, I_lexicon=load)
    return {
        "classification": "plithogenic_hypersoft" if normalized_memberships else "hypersoft",
        "attribute_product": attributes.as_dict(),
        "membership_count": len(normalized_memberships),
        "memberships": normalized_memberships,
        "unresolved_points": unresolved,
        "contradiction_load": contradiction_load,
        "operational_tif": tif.as_dict(),
        "plithogenic_i_profile": PlithogenicIProfile().as_dict(),
        "source": source_payload(),
        "hierarchy": HIERARCHY,
    }


def hypersoft_product(attributes: object) -> dict[str, object]:
    return HypersoftAttributeProduct.from_raw(attributes).as_dict()


def plithogenic_hypersoft_explain() -> dict[str, object]:
    return {
        "source": source_payload(),
        "roles": [
            "attribute-value Cartesian products",
            "hypersoft mapping F: A1 x A2 x ... -> P(U)",
            "neutrosophic hypersoft T/I/F membership",
            "plithogenic hypersoft contradiction for taxonomy filtering",
        ],
        "hierarchy": HIERARCHY,
    }


def plithogenic_hypersoft_profile_for_text(text: str) -> dict[str, object] | None:
    lowered = text.lower()
    if not any(term in lowered for term in ("hypersoft", "plithogenic hypersoft", "soft set")):
        return None
    return classify_hypersoft_mapping(
        {
            "attributes": {"habitat": ["forest", "river"], "trait": ["leaf", "flower"]},
            "memberships": [{"point": {"habitat": "forest", "trait": "leaf"}, "T": 0.7, "I": 0.2, "F": 0.1}],
        }
    )


def source_payload() -> dict[str, object]:
    return {
        "source_id": PLITHOGENIC_HYPERSOFT_SOURCE_ID,
        "title": "Extension of Soft Set to Hypersoft Set, and then to Plithogenic Hypersoft Set",
        "url": PLITHOGENIC_HYPERSOFT_SOURCE_URL,
        "evidence_kind": "public_nss",
        "public_safe": True,
    }
