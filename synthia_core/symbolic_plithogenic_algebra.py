"""Symbolic plithogenic algebra kernel for Synthia phase 17."""

from __future__ import annotations

import json
from dataclasses import dataclass

from .plithogenic import TIF, clamp01
from .safety import HIERARCHY


SYMBOLIC_PLITHOGENIC_SOURCE_ID = "nss.symbolic_plithogenic_algebra"
SYMBOLIC_PLITHOGENIC_SOURCE_URL = "https://fs.unm.edu/NSS/SymbolicPlithogenicAlgebraic39.pdf"


@dataclass(frozen=True)
class SymbolicPlithogenicNumber:
    base: float = 0.0
    coefficients: tuple[tuple[str, float], ...] = ()

    @classmethod
    def from_raw(cls, raw: object) -> "SymbolicPlithogenicNumber":
        if isinstance(raw, str):
            try:
                raw = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise ValueError("symbolic plithogenic number strings must be JSON for v1") from exc
        if isinstance(raw, (int, float)):
            return cls(base=float(raw), coefficients=())
        if not isinstance(raw, dict):
            raise ValueError("symbolic plithogenic number must be a JSON object")
        components = raw.get("components", raw.get("coefficients", {}))
        if isinstance(components, dict):
            pairs = tuple(sorted((str(symbol), float(value)) for symbol, value in components.items() if float(value) != 0.0))
        elif isinstance(components, list):
            pairs = tuple(
                sorted(
                    (str(item.get("symbol", f"P{index + 1}")), float(item.get("coefficient", 0.0)))
                    for index, item in enumerate(components)
                    if isinstance(item, dict) and float(item.get("coefficient", 0.0)) != 0.0
                )
            )
        else:
            raise ValueError("components must be a JSON object or array")
        return cls(base=float(raw.get("base", 0.0)), coefficients=pairs)

    def coefficient_map(self) -> dict[str, float]:
        merged: dict[str, float] = {}
        for symbol, value in self.coefficients:
            merged[symbol] = merged.get(symbol, 0.0) + value
        return {symbol: value for symbol, value in sorted(merged.items()) if value != 0.0}

    def normalize(self) -> "SymbolicPlithogenicNumber":
        return SymbolicPlithogenicNumber(self.base, tuple(self.coefficient_map().items()))

    def add(self, other: "SymbolicPlithogenicNumber", sign: float = 1.0) -> "SymbolicPlithogenicNumber":
        values = self.coefficient_map()
        for symbol, coefficient in other.coefficient_map().items():
            values[symbol] = values.get(symbol, 0.0) + sign * coefficient
        return SymbolicPlithogenicNumber(self.base + sign * other.base, tuple(sorted(values.items()))).normalize()

    def as_expression(self) -> str:
        parts = [str(self.base)] if self.base != 0.0 or not self.coefficients else []
        for symbol, coefficient in self.coefficient_map().items():
            parts.append(f"{coefficient}{symbol}")
        return " + ".join(parts) if parts else "0"

    def as_dict(self) -> dict[str, object]:
        indeterminacy_load = clamp01(sum(abs(value) for value in self.coefficient_map().values()) / max(1.0, abs(self.base) + 1.0))
        tif = TIF(T=clamp01(1.0 - indeterminacy_load), I=indeterminacy_load, F=0.0, I_system=indeterminacy_load, H_lex=indeterminacy_load, G_lex=indeterminacy_load, I_lexicon=indeterminacy_load)
        return {
            "base": self.base,
            "coefficients": self.coefficient_map(),
            "expression": self.as_expression(),
            "operational_tif": tif.as_dict(),
            "source": source_payload(),
            "hierarchy": HIERARCHY,
        }


def parse_symbolic_plithogenic_number(value: object) -> dict[str, object]:
    return SymbolicPlithogenicNumber.from_raw(value).as_dict()


def operate_symbolic_plithogenic_numbers(op: str, left: object, right: object) -> dict[str, object]:
    operation = op.strip().lower()
    left_number = SymbolicPlithogenicNumber.from_raw(left)
    right_number = SymbolicPlithogenicNumber.from_raw(right)
    if operation == "add":
        result = left_number.add(right_number)
    elif operation == "subtract":
        result = left_number.add(right_number, sign=-1.0)
    else:
        raise ValueError(f"unsupported symbolic plithogenic operation: {op}")
    return {
        "operation": operation,
        "left": left_number.as_dict(),
        "right": right_number.as_dict(),
        "result": result.as_dict(),
        "source": source_payload(),
        "hierarchy": HIERARCHY,
    }


def symbolic_plithogenic_explain() -> dict[str, object]:
    return {
        "source": source_payload(),
        "roles": [
            "symbolic plithogenic component storage",
            "coefficient-vector representation",
            "deterministic parsing and rendering",
            "safe input to later plithogenic arithmetic",
        ],
        "canonical_form": "a0 + a1P1 + ... + anPn",
        "hierarchy": HIERARCHY,
    }


def symbolic_plithogenic_profile_for_text(text: str) -> dict[str, object] | None:
    lowered = text.lower()
    if not ("symbolic" in lowered and ("plithogenic" in lowered or "algebra" in lowered)):
        return None
    return SymbolicPlithogenicNumber(base=1.0, coefficients=(("P1", 0.4), ("P2", 0.2))).as_dict()


def source_payload() -> dict[str, object]:
    return {
        "source_id": SYMBOLIC_PLITHOGENIC_SOURCE_ID,
        "title": "Symbolic Plithogenic Algebraic Structures",
        "url": SYMBOLIC_PLITHOGENIC_SOURCE_URL,
        "evidence_kind": "public_nss",
        "public_safe": True,
    }
