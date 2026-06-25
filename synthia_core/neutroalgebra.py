"""NeutroAlgebra kernel for Synthia phase 20."""

from __future__ import annotations

from dataclasses import dataclass

from .plithogenic import TIF, clamp01
from .safety import HIERARCHY


NEUTROALGEBRA_SOURCE_ID = "nss.neutroalgebra_generalizes_partial_algebra"
NEUTROALGEBRA_SOURCE_URL = "https://fs.unm.edu/NeutroAlgebra.pdf"


@dataclass(frozen=True)
class NeutroOperationProfile:
    carrier: tuple[str, ...]
    table: dict[tuple[str, str], object]

    @classmethod
    def from_raw(cls, raw: object) -> "NeutroOperationProfile":
        if not isinstance(raw, dict):
            raise ValueError("operation must be a JSON object")
        carrier = tuple(str(value) for value in raw.get("carrier", []))
        raw_table = raw.get("table", {})
        table: dict[tuple[str, str], object] = {}
        if isinstance(raw_table, dict):
            for key, value in raw_table.items():
                parts = str(key).split(",")
                if len(parts) != 2:
                    raise ValueError("operation table keys must be formatted as 'a,b'")
                table[(parts[0].strip(), parts[1].strip())] = value
        elif isinstance(raw_table, list):
            for row_index, row in enumerate(raw_table):
                if not isinstance(row, list):
                    raise ValueError("operation table rows must be arrays")
                for col_index, value in enumerate(row):
                    if row_index < len(carrier) and col_index < len(carrier):
                        table[(carrier[row_index], carrier[col_index])] = value
        else:
            raise ValueError("operation table must be a JSON object or matrix")
        return cls(carrier=carrier, table=table)

    def classify(self) -> dict[str, object]:
        carrier_set = set(self.carrier)
        total_slots = len(self.carrier) * len(self.carrier)
        partial_slots = 0
        outer_slots = 0
        indeterminate_slots = 0
        closed_slots = 0
        for left in self.carrier:
            for right in self.carrier:
                value = self.table.get((left, right))
                if value is None:
                    partial_slots += 1
                elif str(value).lower() in {"i", "indeterminate", "unknown"}:
                    indeterminate_slots += 1
                elif str(value) not in carrier_set:
                    outer_slots += 1
                else:
                    closed_slots += 1
        load = clamp01((partial_slots + outer_slots + indeterminate_slots) / max(1, total_slots))
        classification = "classical_algebra"
        if indeterminate_slots:
            classification = "neutroalgebra_indeterminate_operation"
        elif outer_slots:
            classification = "neutroalgebra_outer_defined_operation"
        elif partial_slots:
            classification = "partial_algebra"
        tif = TIF(T=clamp01(closed_slots / max(1, total_slots)), I=load, F=0.0, I_system=load, H_lex=load, G_lex=load, I_lexicon=load)
        return {
            "classification": classification,
            "carrier": list(self.carrier),
            "slot_count": total_slots,
            "closed_slots": closed_slots,
            "partial_slots": partial_slots,
            "outer_defined_slots": outer_slots,
            "indeterminate_slots": indeterminate_slots,
            "operational_tif": tif.as_dict(),
            "source": source_payload(),
            "hierarchy": HIERARCHY,
        }

    def lookup(self, left: str, right: str) -> object:
        return self.table.get((left, right))

    def commutativity(self) -> dict[str, object]:
        failures = []
        unknown = []
        for left in self.carrier:
            for right in self.carrier:
                a = self.lookup(left, right)
                b = self.lookup(right, left)
                if a is None or b is None or str(a).lower() in {"i", "indeterminate", "unknown"} or str(b).lower() in {"i", "indeterminate", "unknown"}:
                    unknown.append([left, right])
                elif a != b:
                    failures.append([left, right])
        return _axiom_payload("commutativity", failures, unknown)

    def associativity(self) -> dict[str, object]:
        failures = []
        unknown = []
        for a in self.carrier:
            for b in self.carrier:
                for c in self.carrier:
                    ab = self.lookup(a, b)
                    bc = self.lookup(b, c)
                    if ab is None or bc is None or str(ab) not in self.carrier or str(bc) not in self.carrier:
                        unknown.append([a, b, c])
                        continue
                    left = self.lookup(str(ab), c)
                    right = self.lookup(a, str(bc))
                    if left is None or right is None:
                        unknown.append([a, b, c])
                    elif left != right:
                        failures.append([a, b, c])
        return _axiom_payload("associativity", failures, unknown)


def _axiom_payload(name: str, failures: list[list[str]], unknown: list[list[str]]) -> dict[str, object]:
    status = "valid"
    if failures:
        status = "invalid"
    elif unknown:
        status = "neutro_unknown"
    return {
        "axiom": name,
        "status": status,
        "failure_count": len(failures),
        "unknown_count": len(unknown),
        "failures": failures[:25],
        "unknown": unknown[:25],
        "source": source_payload(),
        "hierarchy": HIERARCHY,
    }


def classify_neutroalgebra_operation(operation: object) -> dict[str, object]:
    return NeutroOperationProfile.from_raw(operation).classify()


def evaluate_neutroalgebra_axiom(axiom: str, table: object) -> dict[str, object]:
    profile = NeutroOperationProfile.from_raw(table)
    name = axiom.strip().lower()
    if name == "commutativity":
        return profile.commutativity()
    if name == "associativity":
        return profile.associativity()
    raise ValueError(f"unsupported neutroalgebra axiom: {axiom}")


def neutroalgebra_explain() -> dict[str, object]:
    return {
        "source": source_payload(),
        "roles": [
            "partial operation diagnostics",
            "outer-defined operation diagnostics",
            "indeterminate operation diagnostics",
            "NeutroAxiom review packets",
        ],
        "hierarchy": HIERARCHY,
    }


def neutroalgebra_profile_for_text(text: str) -> dict[str, object] | None:
    lowered = text.lower()
    if not any(term in lowered for term in ("neutroalgebra", "partial algebra", "neutrooperation", "neutroaxiom")):
        return None
    return classify_neutroalgebra_operation({"carrier": ["a", "b"], "table": {"a,a": "a", "a,b": "I", "b,a": "b"}})


def source_payload() -> dict[str, object]:
    return {
        "source_id": NEUTROALGEBRA_SOURCE_ID,
        "title": "NeutroAlgebra is a Generalization of Partial Algebra",
        "url": NEUTROALGEBRA_SOURCE_URL,
        "evidence_kind": "public_nss",
        "public_safe": True,
    }
