"""Plithogenic arithmetic kernel for Synthia phase 18."""

from __future__ import annotations

from dataclasses import dataclass

from .safety import HIERARCHY
from .symbolic_plithogenic_algebra import SymbolicPlithogenicNumber


PLITHOGENIC_ARITHMETIC_SOURCE_ID = "nss.nidus_idearum_v"
PLITHOGENIC_ARITHMETIC_SOURCE_URL = "https://fs.unm.edu/NidusIdearum5-v3.pdf"


@dataclass(frozen=True)
class PlithogenicMultiplicationLaw:
    name: str = "absorbance"

    def combine(self, left: str, right: str) -> str:
        if self.name == "absorbance" and left == right:
            return left
        return "*".join(sorted((left, right)))

    def as_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "rule": "P_i * P_i = P_i; P_i * P_j creates a deterministic composite component.",
        }


def multiply_symbolic_plithogenic_numbers(left: object, right: object, law: str = "absorbance") -> dict[str, object]:
    left_number = SymbolicPlithogenicNumber.from_raw(left)
    right_number = SymbolicPlithogenicNumber.from_raw(right)
    multiplication_law = PlithogenicMultiplicationLaw(law)
    coefficients: dict[str, float] = {}
    base = left_number.base * right_number.base

    for symbol, value in left_number.coefficient_map().items():
        coefficients[symbol] = coefficients.get(symbol, 0.0) + value * right_number.base
    for symbol, value in right_number.coefficient_map().items():
        coefficients[symbol] = coefficients.get(symbol, 0.0) + value * left_number.base
    for left_symbol, left_value in left_number.coefficient_map().items():
        for right_symbol, right_value in right_number.coefficient_map().items():
            symbol = multiplication_law.combine(left_symbol, right_symbol)
            coefficients[symbol] = coefficients.get(symbol, 0.0) + left_value * right_value

    result = SymbolicPlithogenicNumber(base=base, coefficients=tuple(sorted(coefficients.items()))).normalize()
    return {
        "operation": "multiply",
        "law": multiplication_law.as_dict(),
        "left": left_number.as_dict(),
        "right": right_number.as_dict(),
        "result": result.as_dict(),
        "source": source_payload(),
        "hierarchy": HIERARCHY,
    }


def plithogenic_arithmetic_explain() -> dict[str, object]:
    return {
        "source": source_payload(),
        "roles": [
            "addition and subtraction use coefficient-vector arithmetic",
            "multiplication uses explicit symbolic component laws",
            "absorbance law is deterministic and inspectable",
            "arithmetic traces remain bounded before entering I_lexicon",
        ],
        "hierarchy": HIERARCHY,
    }


def plithogenic_arithmetic_profile_for_text(text: str) -> dict[str, object] | None:
    lowered = text.lower()
    if not ("plithogenic" in lowered and any(term in lowered for term in ("arithmetic", "addition", "multiplication", "absorbance"))):
        return None
    return multiply_symbolic_plithogenic_numbers(
        {"base": 1, "components": {"P1": 0.5}},
        {"base": 2, "components": {"P1": 0.25, "P2": 0.1}},
    )


def source_payload() -> dict[str, object]:
    return {
        "source_id": PLITHOGENIC_ARITHMETIC_SOURCE_ID,
        "title": "Nidus Idearum V",
        "url": PLITHOGENIC_ARITHMETIC_SOURCE_URL,
        "evidence_kind": "public_nss",
        "public_safe": True,
    }
