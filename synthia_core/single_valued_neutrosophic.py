"""Single-valued neutrosophic set operations for Synthia phase 7."""

from __future__ import annotations

from dataclasses import dataclass

from .plithogenic import TIF, clamp01
from .safety import HIERARCHY


SVNS_SOURCE_ID = "nss.single_valued_neutrosophic_sets"
SVNS_SOURCE_URL = "https://fs.unm.edu/SingleValuedNeutrosophicSets.pdf"


@dataclass(frozen=True)
class SingleValuedNeutrosophicSet:
    T: float
    I: float
    F: float
    label: str = "svns"

    def tif(self) -> TIF:
        return TIF(T=clamp01(self.T), I=clamp01(self.I), F=clamp01(self.F))

    def as_dict(self) -> dict[str, object]:
        return {
            "label": self.label,
            "T": clamp01(self.T),
            "I": clamp01(self.I),
            "F": clamp01(self.F),
            "operational_tif": self.tif().as_dict(),
            "source_id": SVNS_SOURCE_ID,
            "hierarchy": HIERARCHY,
        }


@dataclass(frozen=True)
class SVNSOperation:
    op: str
    left: SingleValuedNeutrosophicSet
    right: SingleValuedNeutrosophicSet | None
    result: SingleValuedNeutrosophicSet
    rule: str

    def as_dict(self) -> dict[str, object]:
        return {
            "operation": self.op,
            "left": self.left.as_dict(),
            "right": None if self.right is None else self.right.as_dict(),
            "result": self.result.as_dict(),
            "rule": self.rule,
            "source": {
                "source_id": SVNS_SOURCE_ID,
                "title": "Single Valued Neutrosophic Sets",
                "url": SVNS_SOURCE_URL,
                "evidence_kind": "public_nss",
                "public_safe": True,
            },
            "hierarchy": HIERARCHY,
        }


class SVNSOperator:
    """Bounded SVNS operators using the current Synthia runtime TIF."""

    def operate(
        self,
        op: str,
        left: SingleValuedNeutrosophicSet,
        right: SingleValuedNeutrosophicSet,
    ) -> dict[str, object]:
        operation = op.strip().lower()
        if operation == "union":
            result = SingleValuedNeutrosophicSet(
                T=max(clamp01(left.T), clamp01(right.T)),
                I=max(clamp01(left.I), clamp01(right.I)),
                F=min(clamp01(left.F), clamp01(right.F)),
                label="union",
            )
            rule = "T=max(TA,TB), I=max(IA,IB), F=min(FA,FB)"
        elif operation == "intersection":
            result = SingleValuedNeutrosophicSet(
                T=min(clamp01(left.T), clamp01(right.T)),
                I=min(clamp01(left.I), clamp01(right.I)),
                F=max(clamp01(left.F), clamp01(right.F)),
                label="intersection",
            )
            rule = "T=min(TA,TB), I=min(IA,IB), F=max(FA,FB)"
        elif operation == "difference":
            result = SingleValuedNeutrosophicSet(
                T=min(clamp01(left.T), clamp01(right.F)),
                I=min(clamp01(left.I), 1.0 - clamp01(right.I)),
                F=max(clamp01(left.F), clamp01(right.T)),
                label="difference",
            )
            rule = "T=min(TA,FB), I=min(IA,1-IB), F=max(FA,TB)"
        else:
            raise ValueError(f"unsupported SVNS operation: {op}")
        return SVNSOperation(operation, left, right, result, rule).as_dict()

    def favorite(self, mode: str, value: SingleValuedNeutrosophicSet) -> dict[str, object]:
        selected = mode.strip().lower()
        if selected == "truth":
            result = SingleValuedNeutrosophicSet(
                T=min(clamp01(value.T) + clamp01(value.I), 1.0),
                I=0.0,
                F=clamp01(value.F),
                label="truth_favorite",
            )
            rule = "T=min(T+I,1), I=0, F=F"
        elif selected == "falsity":
            result = SingleValuedNeutrosophicSet(
                T=clamp01(value.T),
                I=0.0,
                F=min(clamp01(value.F) + clamp01(value.I), 1.0),
                label="falsity_favorite",
            )
            rule = "T=T, I=0, F=min(F+I,1)"
        else:
            raise ValueError(f"unsupported favorite mode: {mode}")
        return SVNSOperation(f"{selected}_favorite", value, None, result, rule).as_dict()

    def explain(self) -> dict[str, object]:
        return {
            "source": {
                "source_id": SVNS_SOURCE_ID,
                "title": "Single Valued Neutrosophic Sets",
                "url": SVNS_SOURCE_URL,
                "evidence_kind": "public_nss",
                "public_safe": True,
            },
            "operations": ["union", "intersection", "difference", "truth_favorite", "falsity_favorite"],
            "boundary": "Synthia applies the bounded single-valued form for runtime scoring.",
            "hierarchy": HIERARCHY,
        }
