"""I_lexicon context-preserving classification core."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable
from uuid import uuid4

from .plithogenic import PlithogenicAttribute, PlithogenicMatrix, TIF, resolve_indeterminacy_symbol, SYMBOLIC_NOTATIONS
from .safety import HIERARCHY


class LexiconDomain(str, Enum):
    BIOLOGY = "biology"
    TAXONOMY = "taxonomy"
    PHYLOCODE_NOMENCLATURE = "phylocode_nomenclature"
    AI_GOVERNANCE = "ai_governance"
    FFED_MATH = "ffed_math"
    PHYSICS = "physics"
    ARCHAEOLOGY = "archaeology"
    CONSERVATION = "conservation"
    GENERAL = "general"


class BridgeRelation(str, Enum):
    SYNONYMY = "synonymy"
    REDESCRIPTION = "redescription"
    RANK_SHIFT = "rank_shift"
    ANALOGY = "analogy"
    CONTRADICTION = "contradiction"
    UNCERTAINTY = "uncertainty"
    MEMORY_REPAIR = "memory_repair"


@dataclass(frozen=True)
class LexiconNode:
    term: str
    domain: str
    node_type: str = "concept"
    definition: str = ""
    source_ids: tuple[str, ...] = ()
    tif: TIF = field(default_factory=TIF)
    indeterminacy_layer: str = "I_system^S"
    plithogenic_role: str = "lexicon classification under system-level indeterminacy"
    private_evidence_ids: tuple[str, ...] = ()
    node_id: str = field(default_factory=lambda: f"node.{uuid4().hex}")

    def as_dict(self) -> dict[str, object]:
        canonical_layer = resolve_indeterminacy_symbol(self.indeterminacy_layer)
        return {
            "node_id": self.node_id,
            "term": self.term,
            "domain": self.domain,
            "node_type": self.node_type,
            "definition": self.definition,
            "source_ids": list(self.source_ids),
            "tif": self.tif.as_dict(),
            "i_lexicon": {
                "indeterminacy_layer": canonical_layer,
                "symbolic_notation": SYMBOLIC_NOTATIONS[canonical_layer].as_dict(),
                "plithogenic_role": self.plithogenic_role,
                "source_ids": list(self.source_ids),
                "private_evidence_ids": list(self.private_evidence_ids),
            },
            "hierarchy": HIERARCHY,
        }


@dataclass(frozen=True)
class LexiconBridge:
    left_node_id: str
    right_node_id: str
    relation: str
    source_ids: tuple[str, ...] = ()
    tif: TIF = field(default_factory=lambda: TIF(T=0.8, I=0.2, F=0.0))

    def as_dict(self) -> dict[str, object]:
        return {
            "left_node_id": self.left_node_id,
            "right_node_id": self.right_node_id,
            "relation": self.relation,
            "source_ids": list(self.source_ids),
            "tif": self.tif.as_dict(),
        }


@dataclass(frozen=True)
class LexiconSwitchTrace:
    from_domain: str
    to_domain: str
    context_id: str
    preserved_node_ids: tuple[str, ...]
    bridge_ids: tuple[int, ...]
    plithogenic_profile: dict[str, object]

    def as_dict(self) -> dict[str, object]:
        return {
            "from_domain": self.from_domain,
            "to_domain": self.to_domain,
            "context_id": self.context_id,
            "preserved_node_ids": list(self.preserved_node_ids),
            "bridge_ids": list(self.bridge_ids),
            "plithogenic_profile": self.plithogenic_profile,
            "i_lexicon_switch_state": self.plithogenic_profile.get("indeterminacy_profile", {}),
            "hierarchy": HIERARCHY,
        }


class ILexicon:
    """In-memory I_lexicon registry with deterministic classification helpers."""

    def __init__(self) -> None:
        self.nodes: dict[str, LexiconNode] = {}
        self.bridges: list[LexiconBridge] = []

    def add_node(self, node: LexiconNode) -> LexiconNode:
        self.nodes[node.node_id] = node
        return node

    def add_bridge(self, bridge: LexiconBridge) -> LexiconBridge:
        if bridge.left_node_id not in self.nodes or bridge.right_node_id not in self.nodes:
            raise KeyError("bridge endpoints must exist in the lexicon")
        self.bridges.append(bridge)
        return bridge

    def ingest_terms(self, domain: str, terms: Iterable[str], source_id: str) -> list[LexiconNode]:
        created: list[LexiconNode] = []
        for term in terms:
            cleaned = term.strip()
            if not cleaned:
                continue
            created.append(
                self.add_node(
                    LexiconNode(
                        term=cleaned,
                        domain=domain,
                        definition=f"Imported {domain} term: {cleaned}",
                        source_ids=(source_id,),
                        tif=TIF(T=0.72, I=0.2, F=0.08, I_system=0.2),
                    )
                )
            )
        return created

    def classify_text(self, text: str, domain: str) -> dict[str, object]:
        lowered = text.lower()
        matching = [
            node for node in self.nodes.values() if node.domain == domain and node.term.lower() in lowered
        ]
        attributes = [
            PlithogenicAttribute(
                name=node.term,
                value=node.domain,
                tif=node.tif,
                weight=1.0,
                source_id=node.source_ids[0] if node.source_ids else None,
            )
            for node in matching
        ]
        matrix = PlithogenicMatrix(attributes)
        return {
            "domain": domain,
            "matched_terms": [node.as_dict() for node in matching],
            "plithogenic_profile": matrix.profile(),
            "i_lexicon_classification": matrix.indeterminacy_profile(),
            "hierarchy": HIERARCHY,
        }

    def switch_context(self, from_domain: str, to_domain: str, context_id: str) -> LexiconSwitchTrace:
        preserved = [
            node.node_id
            for node in self.nodes.values()
            if node.domain in {from_domain, to_domain}
        ]
        bridge_ids = [
            index
            for index, bridge in enumerate(self.bridges)
            if self.nodes[bridge.left_node_id].domain in {from_domain, to_domain}
            and self.nodes[bridge.right_node_id].domain in {from_domain, to_domain}
        ]
        attributes = [
            PlithogenicAttribute(
                name=f"bridge_{index}",
                value=self.bridges[index].relation,
                tif=self.bridges[index].tif,
                weight=1.0,
                source_id=self.bridges[index].source_ids[0] if self.bridges[index].source_ids else None,
            )
            for index in bridge_ids
        ]
        return LexiconSwitchTrace(
            from_domain=from_domain,
            to_domain=to_domain,
            context_id=context_id,
            preserved_node_ids=tuple(preserved),
            bridge_ids=tuple(bridge_ids),
            plithogenic_profile=PlithogenicMatrix(attributes).profile(),
        )


def seed_base_lexicon() -> ILexicon:
    lexicon = ILexicon()
    species = lexicon.add_node(
        LexiconNode(
            term="species as systems",
            domain=LexiconDomain.TAXONOMY,
            node_type="framework",
            definition="Species names as living knowledge-system nodes, not dead labels.",
            source_ids=("gdoc.aguilar_beaulieu_white_paper",),
            tif=TIF(T=0.9, I=0.1, F=0.0, I_system=0.1),
        )
    )
    repair = lexicon.add_node(
        LexiconNode(
            term="taxonomic memory repair",
            domain=LexiconDomain.PHYLOCODE_NOMENCLATURE,
            node_type="function",
            definition="Redescription materially improves the usable memory of a taxon.",
            source_ids=("gdoc.aguilar_beaulieu_white_paper",),
            tif=TIF(T=0.92, I=0.08, F=0.0, I_system=0.08),
        )
    )
    governance = lexicon.add_node(
        LexiconNode(
            term="AI-assisted traceability",
            domain=LexiconDomain.AI_GOVERNANCE,
            node_type="boundary",
            definition="AI organizes source-linked evidence under human review.",
            source_ids=("gdoc.aguilar_beaulieu_white_paper",),
            tif=TIF(T=0.86, I=0.12, F=0.02, I_system=0.12),
        )
    )
    lexicon.add_bridge(
        LexiconBridge(
            species.node_id,
            repair.node_id,
            BridgeRelation.MEMORY_REPAIR,
            source_ids=("gdoc.aguilar_beaulieu_white_paper",),
            tif=TIF(T=0.91, I=0.08, F=0.01, I_system=0.08),
        )
    )
    lexicon.add_bridge(
        LexiconBridge(
            repair.node_id,
            governance.node_id,
            BridgeRelation.ANALOGY,
            source_ids=("gdoc.aguilar_beaulieu_white_paper",),
            tif=TIF(T=0.78, I=0.18, F=0.04, I_system=0.18),
        )
    )
    return lexicon
