"""HippoRAG-style memory graph trace storage for Synthia.

This module does not vendor HippoRAG. It stores Synthia-compatible graph memory
bits in RethinkDB so HippoRAG-style passage/entity/fact locations can be traced
by lexicon type, selection mechanism, and plithogenic state.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable, Mapping
from uuid import uuid4

from .plithogenic import PlithogenicAttribute, PlithogenicMatrix, TIF, clamp01
from .safety import HIERARCHY
from .swarm import RethinkDBBackendConfig, RethinkDBSwarmBackend


class HippoRAGSelectionMechanism(str, Enum):
    DENSE_PASSAGE = "dense_passage"
    FACT_RERANK = "fact_rerank"
    PERSONALIZED_PAGERANK = "personalized_pagerank"
    LEXICON_BRIDGE = "lexicon_bridge"
    PLITHOGENIC_TRACE = "plithogenic_trace"
    MANUAL_REVIEW = "manual_review"


@dataclass(frozen=True)
class HippoRAGGraphLocation:
    namespace: str
    node_type: str
    node_id: str
    chunk_id: str | None = None
    entity_id: str | None = None
    fact_id: str | None = None
    edge_id: str | None = None
    hop_depth: int = 0

    def as_dict(self) -> dict[str, object]:
        return {
            "namespace": self.namespace,
            "node_type": self.node_type,
            "node_id": self.node_id,
            "chunk_id": self.chunk_id,
            "entity_id": self.entity_id,
            "fact_id": self.fact_id,
            "edge_id": self.edge_id,
            "hop_depth": self.hop_depth,
        }


@dataclass(frozen=True)
class HippoRAGMemoryBit:
    lexicon_type: str
    content: str
    graph_location: HippoRAGGraphLocation
    selection_mechanism: str
    tif: TIF = field(default_factory=lambda: TIF(T=0.7, I=0.25, F=0.05, I_system=0.25))
    source_ids: tuple[str, ...] = ()
    memory_bit_id: str = field(default_factory=lambda: f"hippo.bit.{uuid4().hex}")
    relevance: float = 0.5
    created_at: float = field(default_factory=time.time)

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> "HippoRAGMemoryBit":
        location_payload = payload.get("graph_location") if isinstance(payload.get("graph_location"), Mapping) else {}
        tif_payload = payload.get("tif") if isinstance(payload.get("tif"), Mapping) else {}
        return cls(
            lexicon_type=str(payload.get("lexicon_type", "general")),
            content=str(payload.get("content", "")),
            graph_location=HippoRAGGraphLocation(
                namespace=str(location_payload.get("namespace", "synthia")),
                node_type=str(location_payload.get("node_type", "memory_bit")),
                node_id=str(location_payload.get("node_id", payload.get("memory_bit_id", "unknown"))),
                chunk_id=_optional_str(location_payload.get("chunk_id")),
                entity_id=_optional_str(location_payload.get("entity_id")),
                fact_id=_optional_str(location_payload.get("fact_id")),
                edge_id=_optional_str(location_payload.get("edge_id")),
                hop_depth=int(location_payload.get("hop_depth", 0)),
            ),
            selection_mechanism=str(payload.get("selection_mechanism", HippoRAGSelectionMechanism.PLITHOGENIC_TRACE.value)),
            tif=TIF(
                T=float(tif_payload.get("T", payload.get("T", 0.7))),
                I=float(tif_payload.get("I", payload.get("I", 0.25))),
                F=float(tif_payload.get("F", payload.get("F", 0.05))),
                I_system=tif_payload.get("I_system^S", payload.get("I_system")),
                D_f=tif_payload.get("D_f", payload.get("D_f")),
                dF=tif_payload.get("dF", payload.get("dF")),
                i_fractal=tif_payload.get("i_fractal", payload.get("i_fractal")),
            ),
            source_ids=tuple(str(item) for item in payload.get("source_ids", []) if item),
            memory_bit_id=str(payload.get("memory_bit_id", payload.get("id", f"hippo.bit.{uuid4().hex}"))),
            relevance=float(payload.get("relevance", 0.5)),
            created_at=float(payload.get("created_at", time.time())),
        )

    def selection_score(self) -> float:
        bounded = self.tif.bounded()
        graph_boost = clamp01(1.0 / (1.0 + max(0, self.graph_location.hop_depth)))
        return clamp01((bounded.T * 0.45) + (self.relevance * 0.35) + (graph_boost * 0.2) - (bounded.F * 0.2))

    def as_dict(self) -> dict[str, object]:
        attribute = PlithogenicAttribute(
            name=self.memory_bit_id,
            value=self.lexicon_type,
            tif=self.tif,
            weight=self.selection_score(),
            source_id=self.source_ids[0] if self.source_ids else None,
        )
        profile = PlithogenicMatrix([attribute]).profile()
        return {
            "id": self.memory_bit_id,
            "memory_bit_id": self.memory_bit_id,
            "lexicon_type": self.lexicon_type,
            "content": self.content,
            "content_sha256": hashlib.sha256(self.content.encode("utf-8")).hexdigest(),
            "graph_location": self.graph_location.as_dict(),
            "selection_mechanism": self.selection_mechanism,
            "selection_score": self.selection_score(),
            "relevance": clamp01(self.relevance),
            "source_ids": list(self.source_ids),
            "tif": self.tif.as_dict(),
            "plithogenic_profile": profile,
            "i_lexicon_trace": profile["indeterminacy_profile"],
            "created_at": self.created_at,
            "hierarchy": HIERARCHY,
        }


@dataclass(frozen=True)
class HippoRAGEdgeTrace:
    left_memory_bit_id: str
    right_memory_bit_id: str
    relation: str
    weight: float = 1.0
    lexicon_type: str = "general"
    edge_id: str = field(default_factory=lambda: f"hippo.edge.{uuid4().hex}")

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.edge_id,
            "edge_id": self.edge_id,
            "left_memory_bit_id": self.left_memory_bit_id,
            "right_memory_bit_id": self.right_memory_bit_id,
            "relation": self.relation,
            "weight": clamp01(self.weight),
            "lexicon_type": self.lexicon_type,
            "hierarchy": HIERARCHY,
        }


class RethinkDBHippoRAGTraceStore:
    MEMORY_BITS_TABLE = "hipporag_memory_bits"
    GRAPH_EDGES_TABLE = "hipporag_graph_edges"
    SELECTION_TRACES_TABLE = "hipporag_selection_traces"

    def __init__(self, config: RethinkDBBackendConfig | None = None) -> None:
        self.backend = RethinkDBSwarmBackend(config)
        self.config = self.backend.config

    def status(self) -> dict[str, object]:
        status = self.backend.status()
        status["hipporag_tables"] = [
            self.MEMORY_BITS_TABLE,
            self.GRAPH_EDGES_TABLE,
            self.SELECTION_TRACES_TABLE,
        ]
        return status

    def ensure_schema(self) -> dict[str, object]:
        base = self.backend.ensure_schema()
        r = self.backend._driver()
        conn = self.backend._connect(r)
        try:
            existing = r.table_list().run(conn)
            created = []
            for table in (self.MEMORY_BITS_TABLE, self.GRAPH_EDGES_TABLE, self.SELECTION_TRACES_TABLE):
                if table not in existing:
                    r.table_create(table).run(conn)
                    created.append(table)
                r.table(table).wait().run(conn)
            return {
                "database": self.config.database,
                "swarm_schema": base,
                "created_tables": created,
                "hipporag_ready": True,
            }
        finally:
            conn.close()

    def store_memory_bit(self, memory_bit: HippoRAGMemoryBit) -> dict[str, object]:
        self.ensure_schema()
        r = self.backend._driver()
        conn = self.backend._connect(r)
        try:
            document = memory_bit.as_dict()
            result = r.table(self.MEMORY_BITS_TABLE).insert(document, conflict="replace").run(conn)
            trace = {
                "id": f"selection.{memory_bit.memory_bit_id}",
                "memory_bit_id": memory_bit.memory_bit_id,
                "lexicon_type": memory_bit.lexicon_type,
                "selection_mechanism": memory_bit.selection_mechanism,
                "selection_score": memory_bit.selection_score(),
                "graph_location": memory_bit.graph_location.as_dict(),
                "created_at": time.time(),
                "hierarchy": HIERARCHY,
            }
            trace_result = r.table(self.SELECTION_TRACES_TABLE).insert(trace, conflict="replace").run(conn)
            return {
                "stored": True,
                "memory_bit_id": memory_bit.memory_bit_id,
                "result": result,
                "selection_trace_result": trace_result,
            }
        finally:
            conn.close()

    def store_edge(self, edge: HippoRAGEdgeTrace) -> dict[str, object]:
        self.ensure_schema()
        r = self.backend._driver()
        conn = self.backend._connect(r)
        try:
            result = r.table(self.GRAPH_EDGES_TABLE).insert(edge.as_dict(), conflict="replace").run(conn)
            return {"stored": True, "edge_id": edge.edge_id, "result": result}
        finally:
            conn.close()

    def select_memory_bits(
        self,
        lexicon_type: str | None = None,
        selection_mechanism: str | None = None,
        limit: int = 10,
    ) -> dict[str, object]:
        r = self.backend._driver()
        conn = self.backend._connect(r)
        try:
            query = r.table(self.MEMORY_BITS_TABLE)
            if lexicon_type:
                query = query.filter({"lexicon_type": lexicon_type})
            if selection_mechanism:
                query = query.filter({"selection_mechanism": selection_mechanism})
            rows = list(query.order_by(r.desc("selection_score")).limit(limit).run(conn))
            return {
                "lexicon_type": lexicon_type,
                "selection_mechanism": selection_mechanism,
                "count": len(rows),
                "memory_bits": rows,
                "hierarchy": HIERARCHY,
            }
        finally:
            conn.close()


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    text = str(value)
    return text or None


def build_memory_bit_from_cli(
    *,
    lexicon_type: str,
    content: str,
    namespace: str,
    node_type: str,
    node_id: str,
    selection_mechanism: str,
    relevance: float,
    source_ids: Iterable[str],
    tif: TIF,
) -> HippoRAGMemoryBit:
    return HippoRAGMemoryBit(
        lexicon_type=lexicon_type,
        content=content,
        graph_location=HippoRAGGraphLocation(namespace=namespace, node_type=node_type, node_id=node_id),
        selection_mechanism=selection_mechanism,
        tif=tif,
        source_ids=tuple(source_ids),
        relevance=relevance,
    )
