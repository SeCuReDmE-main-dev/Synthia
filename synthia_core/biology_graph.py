"""Public-safe biology graph review layer with plithogenic uncertainty."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Mapping

from .plithogenic import TIF, clamp01
from .safety import HIERARCHY


TREE_TOBACCO_SOURCE_ID = "nss.tree_tobacco_extract_plithogenic_superhypergraph"
CONCENTRIC_HYPERGRAPH_SOURCE_ID = "nss.concentric_plithogenic_hypergraph"
HYPERSOFT_GRAPH_SOURCE_ID = "nss.neutrosophic_hypersoft_graphs"
RESTRICTED_SUPERHYPERGRAPH_SOURCE_ID = "nss.restricted_superhypergraphs_supertrees"


class BiologyNodeType(str, Enum):
    TAXON = "taxon"
    TREATMENT = "treatment"
    CRITERION = "criterion"
    SOURCE = "source"
    EXPERT = "expert"
    RISK_CASE = "risk_case"
    HABITAT = "habitat"
    OUTCOME = "outcome"


class BiologyEdgeType(str, Enum):
    EVIDENCE = "evidence"
    CONTRADICTION = "contradiction"
    COMPOSITION = "composition"
    REVIEW_DEPENDENCY = "review_dependency"
    RISK_SIGNAL = "risk_signal"
    CONTEXT_LINK = "context_link"


class GraphReviewPriority(str, Enum):
    ROUTINE = "routine"
    WATCH = "watch"
    ELEVATED = "elevated"
    CRITICAL_REVIEW = "critical_review"


@dataclass(frozen=True)
class BiologyGraphNode:
    id: str
    label: str
    node_type: str
    T: float
    I: float
    F: float
    weight: float = 1.0
    source_ids: tuple[str, ...] = ()
    notes: str = ""

    @classmethod
    def from_raw(cls, raw: object, index: int) -> "BiologyGraphNode":
        if not isinstance(raw, Mapping):
            raise ValueError("each biology graph node must be a JSON object")
        return cls(
            id=str(raw.get("id", f"node_{index + 1}")),
            label=str(raw.get("label", raw.get("id", f"Node {index + 1}"))),
            node_type=str(raw.get("node_type", BiologyNodeType.CRITERION.value)),
            T=float(raw.get("T", 0.0)),
            I=float(raw.get("I", 0.0)),
            F=float(raw.get("F", 0.0)),
            weight=max(0.0, float(raw.get("weight", 1.0))),
            source_ids=_source_ids(raw.get("source_ids", ())),
            notes=str(raw.get("notes", "")),
        )

    def operational_tif(self) -> TIF:
        return TIF(T=clamp01(self.T), I=clamp01(self.I), F=clamp01(self.F))

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "label": self.label,
            "node_type": self.node_type,
            "formal_value": {"T": self.T, "I": self.I, "F": self.F},
            "operational_tif": self.operational_tif().as_dict(),
            "weight": self.weight,
            "source_ids": list(self.source_ids),
            "notes": self.notes,
        }


@dataclass(frozen=True)
class BiologyGraphEdge:
    id: str
    source: str
    target: str
    edge_type: str
    T: float
    I: float
    F: float
    weight: float = 1.0
    source_ids: tuple[str, ...] = ()
    notes: str = ""

    @classmethod
    def from_raw(cls, raw: object, index: int) -> "BiologyGraphEdge":
        if not isinstance(raw, Mapping):
            raise ValueError("each biology graph edge must be a JSON object")
        return cls(
            id=str(raw.get("id", f"edge_{index + 1}")),
            source=str(raw.get("source", "")),
            target=str(raw.get("target", "")),
            edge_type=str(raw.get("edge_type", BiologyEdgeType.EVIDENCE.value)),
            T=float(raw.get("T", 0.0)),
            I=float(raw.get("I", 0.0)),
            F=float(raw.get("F", 0.0)),
            weight=max(0.0, float(raw.get("weight", 1.0))),
            source_ids=_source_ids(raw.get("source_ids", ())),
            notes=str(raw.get("notes", "")),
        )

    def operational_tif(self) -> TIF:
        return TIF(T=clamp01(self.T), I=clamp01(self.I), F=clamp01(self.F))

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "source": self.source,
            "target": self.target,
            "edge_type": self.edge_type,
            "formal_value": {"T": self.T, "I": self.I, "F": self.F},
            "operational_tif": self.operational_tif().as_dict(),
            "weight": self.weight,
            "source_ids": list(self.source_ids),
            "notes": self.notes,
        }


@dataclass(frozen=True)
class BiologyHyperEdge:
    id: str
    member_node_ids: tuple[str, ...]
    label: str
    T: float
    I: float
    F: float
    weight: float = 1.0
    source_ids: tuple[str, ...] = ()
    notes: str = ""

    @classmethod
    def from_raw(cls, raw: object, index: int) -> "BiologyHyperEdge":
        if not isinstance(raw, Mapping):
            raise ValueError("each biology hyperedge must be a JSON object")
        return cls(
            id=str(raw.get("id", f"hyperedge_{index + 1}")),
            member_node_ids=tuple(str(item) for item in raw.get("member_node_ids", ())),
            label=str(raw.get("label", f"Hyperedge {index + 1}")),
            T=float(raw.get("T", 0.0)),
            I=float(raw.get("I", 0.0)),
            F=float(raw.get("F", 0.0)),
            weight=max(0.0, float(raw.get("weight", 1.0))),
            source_ids=_source_ids(raw.get("source_ids", ())),
            notes=str(raw.get("notes", "")),
        )

    def operational_tif(self) -> TIF:
        return TIF(T=clamp01(self.T), I=clamp01(self.I), F=clamp01(self.F))

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "member_node_ids": list(self.member_node_ids),
            "label": self.label,
            "formal_value": {"T": self.T, "I": self.I, "F": self.F},
            "operational_tif": self.operational_tif().as_dict(),
            "weight": self.weight,
            "source_ids": list(self.source_ids),
            "notes": self.notes,
        }


@dataclass(frozen=True)
class BiologySuperVertex:
    id: str
    member_node_ids: tuple[str, ...]
    label: str
    T: float
    I: float
    F: float
    source_ids: tuple[str, ...] = ()
    notes: str = ""

    @classmethod
    def from_raw(cls, raw: object, index: int) -> "BiologySuperVertex":
        if not isinstance(raw, Mapping):
            raise ValueError("each biology supervertex must be a JSON object")
        return cls(
            id=str(raw.get("id", f"supervertex_{index + 1}")),
            member_node_ids=tuple(str(item) for item in raw.get("member_node_ids", ())),
            label=str(raw.get("label", f"Supervertex {index + 1}")),
            T=float(raw.get("T", 0.0)),
            I=float(raw.get("I", 0.0)),
            F=float(raw.get("F", 0.0)),
            source_ids=_source_ids(raw.get("source_ids", ())),
            notes=str(raw.get("notes", "")),
        )

    def operational_tif(self) -> TIF:
        return TIF(T=clamp01(self.T), I=clamp01(self.I), F=clamp01(self.F))

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "member_node_ids": list(self.member_node_ids),
            "label": self.label,
            "formal_value": {"T": self.T, "I": self.I, "F": self.F},
            "operational_tif": self.operational_tif().as_dict(),
            "source_ids": list(self.source_ids),
            "notes": self.notes,
        }


@dataclass(frozen=True)
class BiologyGraphReviewLayer:
    graph_label: str
    nodes: tuple[BiologyGraphNode, ...]
    edges: tuple[BiologyGraphEdge, ...] = ()
    hyperedges: tuple[BiologyHyperEdge, ...] = ()
    supervertices: tuple[BiologySuperVertex, ...] = ()
    source_ids: tuple[str, ...] = ()
    reviewer_notes: str = ""
    related_taxon_packet: Mapping[str, object] | None = None
    related_risk_case: Mapping[str, object] | None = None

    @classmethod
    def from_raw_graph(cls, raw: object) -> "BiologyGraphReviewLayer":
        if not isinstance(raw, Mapping):
            raise ValueError("biology graph review layer must be a JSON object")
        raw_nodes = _raw_list(raw, "nodes")
        raw_edges = _raw_list(raw, "edges")
        raw_hyperedges = _raw_list(raw, "hyperedges")
        raw_supervertices = _raw_list(raw, "supervertices")

        nodes = tuple(BiologyGraphNode.from_raw(item, index) for index, item in enumerate(raw_nodes))
        node_ids = {node.id for node in nodes}
        if len(node_ids) != len(nodes):
            raise ValueError("biology graph node ids must be unique")

        edges = tuple(BiologyGraphEdge.from_raw(item, index) for index, item in enumerate(raw_edges))
        for edge in edges:
            _require_node_id(edge.source, node_ids, f"edge {edge.id} source")
            _require_node_id(edge.target, node_ids, f"edge {edge.id} target")

        hyperedges = tuple(BiologyHyperEdge.from_raw(item, index) for index, item in enumerate(raw_hyperedges))
        for hyperedge in hyperedges:
            for member_node_id in hyperedge.member_node_ids:
                _require_node_id(member_node_id, node_ids, f"hyperedge {hyperedge.id} member")

        supervertices = tuple(BiologySuperVertex.from_raw(item, index) for index, item in enumerate(raw_supervertices))
        for supervertex in supervertices:
            for member_node_id in supervertex.member_node_ids:
                _require_node_id(member_node_id, node_ids, f"supervertex {supervertex.id} member")

        related_taxon_packet = raw.get("related_taxon_packet")
        if related_taxon_packet is not None and not isinstance(related_taxon_packet, Mapping):
            raise ValueError("related_taxon_packet must be a JSON object when provided")
        related_risk_case = raw.get("related_risk_case")
        if related_risk_case is not None and not isinstance(related_risk_case, Mapping):
            raise ValueError("related_risk_case must be a JSON object when provided")

        return cls(
            graph_label=str(raw.get("graph_label", "unnamed biology graph review layer")),
            nodes=nodes,
            edges=edges,
            hyperedges=hyperedges,
            supervertices=supervertices,
            source_ids=_source_ids(raw.get("source_ids", ())),
            reviewer_notes=str(raw.get("reviewer_notes", "")),
            related_taxon_packet=related_taxon_packet,
            related_risk_case=related_risk_case,
        )

    def dominant_system_node(self) -> BiologyGraphNode | None:
        if not self.nodes:
            return None
        return sorted(self.nodes, key=lambda node: (-node.weight, -node.operational_tif().I, node.id))[0]

    def score(self) -> dict[str, object]:
        if not self.nodes:
            tif = TIF(T=0.0, I=1.0, F=0.0, I_system=1.0, H_lex=1.0, G_lex=1.0, I_lexicon=1.0)
            return self._base_payload(
                operational_tif=tif,
                node_weighted_tif=tif,
                edge_weighted_tif=tif,
                hyperedge_uncertainty_load=1.0,
                supervertex_uncertainty_load=1.0,
                contradiction_load=1.0,
                uncertainty_load=1.0,
                review_priority=GraphReviewPriority.CRITICAL_REVIEW.value,
            )

        node_weighted_tif = _weighted_tif(self.nodes)
        edge_weighted_tif = _weighted_tif(self.edges)
        combined_tif = _weighted_tif((*self.nodes, *self.edges, *self.hyperedges, *self.supervertices))
        hyperedge_uncertainty_load = _weighted_indeterminacy(self.hyperedges)
        supervertex_uncertainty_load = _weighted_indeterminacy(self.supervertices)
        contradiction_load = _contradiction_load(self.edges, self.hyperedges)
        uncertainty_load = clamp01(max(combined_tif.I, contradiction_load, hyperedge_uncertainty_load, supervertex_uncertainty_load))
        operational_tif = TIF(
            T=combined_tif.T,
            I=combined_tif.I,
            F=combined_tif.F,
            I_system=uncertainty_load,
            H_lex=uncertainty_load,
            G_lex=contradiction_load,
            I_lexicon=uncertainty_load,
        )
        return self._base_payload(
            operational_tif=operational_tif,
            node_weighted_tif=node_weighted_tif,
            edge_weighted_tif=edge_weighted_tif,
            hyperedge_uncertainty_load=hyperedge_uncertainty_load,
            supervertex_uncertainty_load=supervertex_uncertainty_load,
            contradiction_load=contradiction_load,
            uncertainty_load=uncertainty_load,
            review_priority=_review_priority(uncertainty_load, contradiction_load),
        )

    def _base_payload(
        self,
        operational_tif: TIF,
        node_weighted_tif: TIF,
        edge_weighted_tif: TIF,
        hyperedge_uncertainty_load: float,
        supervertex_uncertainty_load: float,
        contradiction_load: float,
        uncertainty_load: float,
        review_priority: str,
    ) -> dict[str, object]:
        dominant = self.dominant_system_node()
        return {
            "graph_label": self.graph_label,
            "nodes": [node.as_dict() for node in self.nodes],
            "edges": [edge.as_dict() for edge in self.edges],
            "hyperedges": [hyperedge.as_dict() for hyperedge in self.hyperedges],
            "supervertices": [supervertex.as_dict() for supervertex in self.supervertices],
            "source_ids": list(_all_source_ids(self)),
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
            "hyperedge_count": len(self.hyperedges),
            "supervertex_count": len(self.supervertices),
            "dominant_system_node": None if dominant is None else dominant.as_dict(),
            "node_weighted_tif": node_weighted_tif.as_dict(),
            "edge_weighted_tif": edge_weighted_tif.as_dict(),
            "hyperedge_uncertainty_load": hyperedge_uncertainty_load,
            "supervertex_uncertainty_load": supervertex_uncertainty_load,
            "contradiction_load": contradiction_load,
            "uncertainty_load": uncertainty_load,
            "operational_tif": operational_tif.as_dict(),
            "review_priority": review_priority,
            "related_taxon_packet": self.related_taxon_packet,
            "related_risk_case": self.related_risk_case,
            "reviewer_notes": self.reviewer_notes,
            "human_review_required": True,
            "authority_boundary": (
                "Review support only; no formal taxonomic act, safety declaration, "
                "public-health decision, conservation order, or autonomous scientific conclusion."
            ),
            "societal_use": [
                "education",
                "graph review preparation",
                "source-linked uncertainty communication",
                "expert-traceable biology triage",
            ],
            "source_anchors": [
                {
                    "source_id": TREE_TOBACCO_SOURCE_ID,
                    "url": "https://fs.unm.edu/NSS/6TreeTobaccoExtract.pdf",
                    "role": "applied biology and plithogenic n-superhypergraph anchor",
                    "public_safe": True,
                },
                {
                    "source_id": CONCENTRIC_HYPERGRAPH_SOURCE_ID,
                    "url": "https://fs.unm.edu/NSS/ConcentricPlithogenicHypergraph.pdf",
                    "role": "plithogenic hypergraph envelope anchor",
                    "public_safe": True,
                },
                {
                    "source_id": HYPERSOFT_GRAPH_SOURCE_ID,
                    "url": "https://fs.unm.edu/NSS/NeutrosophicHypersoftGraphs24.pdf",
                    "role": "neutrosophic hypersoft graph anchor",
                    "public_safe": True,
                },
                {
                    "source_id": RESTRICTED_SUPERHYPERGRAPH_SOURCE_ID,
                    "url": "https://fs.unm.edu/NSS/NutrosophicSuperHyperGraphs28.pdf",
                    "role": "restricted superhypergraph and supertree anchor",
                    "public_safe": True,
                },
            ],
            "hierarchy": HIERARCHY,
        }


def score_biology_graph_review(raw: object) -> dict[str, object]:
    graph = raw if isinstance(raw, BiologyGraphReviewLayer) else BiologyGraphReviewLayer.from_raw_graph(raw)
    return graph.score()


def build_tree_tobacco_demo_graph() -> BiologyGraphReviewLayer:
    source_ids = (
        TREE_TOBACCO_SOURCE_ID,
        CONCENTRIC_HYPERGRAPH_SOURCE_ID,
        HYPERSOFT_GRAPH_SOURCE_ID,
        RESTRICTED_SUPERHYPERGRAPH_SOURCE_ID,
    )
    return BiologyGraphReviewLayer(
        graph_label="Synthetic tree tobacco extract review graph",
        nodes=(
            BiologyGraphNode(
                id="treatment.extract",
                label="Synthetic plant-extract treatment",
                node_type=BiologyNodeType.TREATMENT.value,
                T=0.72,
                I=0.24,
                F=0.08,
                weight=1.3,
                source_ids=(TREE_TOBACCO_SOURCE_ID,),
                notes="Synthetic treatment node for public-safe graph review.",
            ),
            BiologyGraphNode(
                id="criterion.solvent",
                label="Solvent preparation criterion",
                node_type=BiologyNodeType.CRITERION.value,
                T=0.66,
                I=0.28,
                F=0.12,
                weight=0.9,
                source_ids=(TREE_TOBACCO_SOURCE_ID, CONCENTRIC_HYPERGRAPH_SOURCE_ID),
                notes="Synthetic preparation-context signal.",
            ),
            BiologyGraphNode(
                id="habitat.crop_context",
                label="Crop habitat context",
                node_type=BiologyNodeType.HABITAT.value,
                T=0.58,
                I=0.36,
                F=0.16,
                weight=0.8,
                source_ids=(HYPERSOFT_GRAPH_SOURCE_ID,),
                notes="Synthetic field-context signal.",
            ),
            BiologyGraphNode(
                id="outcome.review_signal",
                label="Observed efficacy review signal",
                node_type=BiologyNodeType.OUTCOME.value,
                T=0.62,
                I=0.34,
                F=0.18,
                weight=1.1,
                source_ids=(TREE_TOBACCO_SOURCE_ID,),
                notes="Synthetic outcome node; not a biological finding.",
            ),
            BiologyGraphNode(
                id="expert.disagreement",
                label="Expert disagreement review node",
                node_type=BiologyNodeType.EXPERT.value,
                T=0.42,
                I=0.62,
                F=0.24,
                weight=0.7,
                source_ids=(RESTRICTED_SUPERHYPERGRAPH_SOURCE_ID,),
                notes="Synthetic review-disagreement node forcing human review.",
            ),
        ),
        edges=(
            BiologyGraphEdge(
                id="edge.composition",
                source="treatment.extract",
                target="criterion.solvent",
                edge_type=BiologyEdgeType.COMPOSITION.value,
                T=0.68,
                I=0.24,
                F=0.10,
                weight=1.0,
                source_ids=(CONCENTRIC_HYPERGRAPH_SOURCE_ID,),
            ),
            BiologyGraphEdge(
                id="edge.context",
                source="criterion.solvent",
                target="habitat.crop_context",
                edge_type=BiologyEdgeType.CONTEXT_LINK.value,
                T=0.56,
                I=0.38,
                F=0.14,
                weight=0.8,
                source_ids=(HYPERSOFT_GRAPH_SOURCE_ID,),
            ),
            BiologyGraphEdge(
                id="edge.risk_signal",
                source="treatment.extract",
                target="outcome.review_signal",
                edge_type=BiologyEdgeType.RISK_SIGNAL.value,
                T=0.64,
                I=0.30,
                F=0.12,
                weight=1.0,
                source_ids=(TREE_TOBACCO_SOURCE_ID,),
            ),
            BiologyGraphEdge(
                id="edge.contradiction",
                source="outcome.review_signal",
                target="expert.disagreement",
                edge_type=BiologyEdgeType.CONTRADICTION.value,
                T=0.34,
                I=0.70,
                F=0.42,
                weight=1.2,
                source_ids=(RESTRICTED_SUPERHYPERGRAPH_SOURCE_ID,),
                notes="Synthetic contradiction edge; it creates review priority, not authority.",
            ),
        ),
        hyperedges=(
            BiologyHyperEdge(
                id="hyperedge.treatment_context",
                member_node_ids=("treatment.extract", "criterion.solvent", "habitat.crop_context", "outcome.review_signal"),
                label="Treatment-context hyperedge",
                T=0.64,
                I=0.40,
                F=0.16,
                weight=1.1,
                source_ids=(CONCENTRIC_HYPERGRAPH_SOURCE_ID, HYPERSOFT_GRAPH_SOURCE_ID),
                notes="Synthetic multi-node context inspired by hypergraph review.",
            ),
        ),
        supervertices=(
            BiologySuperVertex(
                id="supervertex.review_bundle",
                member_node_ids=("treatment.extract", "outcome.review_signal", "expert.disagreement"),
                label="Human review bundle",
                T=0.56,
                I=0.52,
                F=0.22,
                source_ids=(RESTRICTED_SUPERHYPERGRAPH_SOURCE_ID,),
                notes="Synthetic grouped review object inspired by restricted superhypergraph structure.",
            ),
        ),
        source_ids=source_ids,
        reviewer_notes="Public-safe synthetic biology graph demo; not a pesticide, safety, or taxonomic decision.",
    )


def _source_ids(value: object) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    if isinstance(value, Iterable):
        return tuple(str(item) for item in value)
    return (str(value),)


def _raw_list(raw: Mapping[str, object], key: str) -> list[object]:
    value = raw.get(key, [])
    if not isinstance(value, list):
        raise ValueError(f"biology graph {key} must be a JSON array")
    return value


def _require_node_id(node_id: str, known_node_ids: set[str], label: str) -> None:
    if node_id not in known_node_ids:
        raise ValueError(f"{label} must reference an existing biology graph node id")


def _weighted_tif(items: Iterable[object]) -> TIF:
    items = tuple(items)
    if not items:
        return TIF(T=0.0, I=1.0, F=0.0)
    weight_sum = sum(float(getattr(item, "weight", 1.0)) for item in items) or 1.0
    return TIF(
        T=clamp01(sum(item.operational_tif().T * float(getattr(item, "weight", 1.0)) for item in items) / weight_sum),
        I=clamp01(sum(item.operational_tif().I * float(getattr(item, "weight", 1.0)) for item in items) / weight_sum),
        F=clamp01(sum(item.operational_tif().F * float(getattr(item, "weight", 1.0)) for item in items) / weight_sum),
    )


def _weighted_indeterminacy(items: Iterable[object]) -> float:
    items = tuple(items)
    if not items:
        return 0.0
    weight_sum = sum(float(getattr(item, "weight", 1.0)) for item in items) or 1.0
    return clamp01(sum(item.operational_tif().I * float(getattr(item, "weight", 1.0)) for item in items) / weight_sum)


def _contradiction_load(edges: Iterable[BiologyGraphEdge], hyperedges: Iterable[BiologyHyperEdge]) -> float:
    contradiction_edges = tuple(edge for edge in edges if edge.edge_type == BiologyEdgeType.CONTRADICTION.value)
    edge_load = _weighted_indeterminacy(contradiction_edges)
    hyperedge_load = _weighted_indeterminacy(hyperedge for hyperedge in hyperedges if hyperedge.operational_tif().I >= 0.35)
    return clamp01(max(edge_load, hyperedge_load))


def _review_priority(uncertainty_load: float, contradiction_load: float) -> str:
    signal = max(uncertainty_load, contradiction_load)
    if signal >= 0.75:
        return GraphReviewPriority.CRITICAL_REVIEW.value
    if signal >= 0.50:
        return GraphReviewPriority.ELEVATED.value
    if signal >= 0.25:
        return GraphReviewPriority.WATCH.value
    return GraphReviewPriority.ROUTINE.value


def _all_source_ids(layer: BiologyGraphReviewLayer) -> tuple[str, ...]:
    seen: set[str] = set()
    ordered: list[str] = []
    containers = (layer.nodes, layer.edges, layer.hyperedges, layer.supervertices)
    for source_id in layer.source_ids:
        if source_id not in seen:
            seen.add(source_id)
            ordered.append(source_id)
    for container in containers:
        for item in container:
            for source_id in item.source_ids:
                if source_id not in seen:
                    seen.add(source_id)
                    ordered.append(source_id)
    return tuple(ordered)
