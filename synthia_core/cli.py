"""Synthia command line interface."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from .codex_connector import build_wake_prompt, codex_status
from .hipporag_bridge import (
    HippoRAGEdgeTrace,
    RethinkDBHippoRAGTraceStore,
    build_memory_bit_from_cli,
)
from .lexicon import seed_base_lexicon
from .nss import NSSMathRouter
from .plithogenic import (
    TIF,
    classify_i_chain_text,
    explain_i_chain,
    plithogenic_profile_for_source,
    render_symbolic_notation,
)
from .sources import scan_root
from .swarm import (
    DigitalPheromoneMap,
    DroneNodeApp,
    EvidenceVault,
    MissionSafetyGate,
    QueenCoordinator,
    RethinkDBBackendConfig,
    RethinkDBSwarmBackend,
    SwarmReviewPacketBuilder,
    load_json_mapping,
    parse_detection_arg,
)
from .taxonomy_memory import TaxonomicMemorySystem


def _print_json(payload: object) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def _default_private_org() -> Path:
    return Path.cwd().parent / "Synthia_organisation"


def _rethinkdb_config_from_args(args: argparse.Namespace) -> RethinkDBBackendConfig:
    return RethinkDBBackendConfig(
        host=getattr(args, "rethinkdb_host", None) or os.environ.get("SYNTHIA_RETHINKDB_HOST", "127.0.0.1"),
        port=int(getattr(args, "rethinkdb_port", None) or os.environ.get("SYNTHIA_RETHINKDB_PORT", "28015")),
        database=getattr(args, "rethinkdb_db", None) or os.environ.get("SYNTHIA_RETHINKDB_DB", "synthia_swarm"),
        executable=os.environ.get("SYNTHIA_RETHINKDB_EXE"),
        data_dir=os.environ.get("SYNTHIA_RETHINKDB_DATA"),
    )


def _configure_rethinkdb_flags(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--rethinkdb-host", default=None)
    parser.add_argument("--rethinkdb-port", type=int, default=None)
    parser.add_argument("--rethinkdb-db", default=None)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="synthia")
    subparsers = parser.add_subparsers(dest="area", required=True)

    sources = subparsers.add_parser("sources")
    sources_sub = sources.add_subparsers(dest="command", required=True)
    scan = sources_sub.add_parser("scan-root")
    scan.add_argument("--root", default=str(Path.cwd().parent))

    soul = subparsers.add_parser("soul")
    soul_sub = soul.add_subparsers(dest="command", required=True)
    soul_build = soul_sub.add_parser("build")
    soul_build.add_argument("--private-org", default=str(_default_private_org()))

    lexicon = subparsers.add_parser("lexicon")
    lexicon_sub = lexicon.add_subparsers(dest="command", required=True)
    ingest = lexicon_sub.add_parser("ingest")
    ingest.add_argument("--domain", required=True)
    ingest.add_argument("--source", required=True)
    ingest.add_argument("--term", action="append", default=[])
    classify = lexicon_sub.add_parser("classify")
    classify.add_argument("--text", required=True)
    classify.add_argument("--domain", required=True)
    switch = lexicon_sub.add_parser("switch")
    switch.add_argument("--from", dest="from_domain", required=True)
    switch.add_argument("--to", dest="to_domain", required=True)
    switch.add_argument("--context", required=True)
    i_chain = lexicon_sub.add_parser("i-chain")
    i_chain_sub = i_chain.add_subparsers(dest="i_chain_command", required=True)
    i_chain_explain = i_chain_sub.add_parser("explain")
    i_chain_explain.add_argument("--term", required=True)
    i_chain_explain.add_argument("--domain", default="general")
    i_chain_classify = i_chain_sub.add_parser("classify")
    i_chain_classify.add_argument("--text", required=True)
    i_chain_classify.add_argument("--domain", required=True)
    notation = lexicon_sub.add_parser("notation")
    notation_sub = notation.add_subparsers(dest="notation_command", required=True)
    notation_render = notation_sub.add_parser("render")
    notation_render.add_argument("--symbol", required=True)
    notation_render.add_argument("--format", default="ascii", choices=["ascii", "latex", "unicode", "algorithm"])

    plithogenic = subparsers.add_parser("plithogenic")
    plithogenic_sub = plithogenic.add_subparsers(dest="command", required=True)
    plithogenic_profile = plithogenic_sub.add_parser("profile")
    plithogenic_profile.add_argument("--source", required=True)

    nss = subparsers.add_parser("nss")
    nss_sub = nss.add_subparsers(dest="command", required=True)
    nss_sources = nss_sub.add_parser("sources")
    nss_sources.add_argument("action", choices=["list"])
    nss_route = nss_sub.add_parser("route")
    nss_route.add_argument("--text", required=True)

    codex = subparsers.add_parser("codex")
    codex_sub = codex.add_subparsers(dest="command", required=True)
    codex_sub.add_parser("status")
    wake = codex_sub.add_parser("wake-prompt")
    wake.add_argument("--private-org", default=str(_default_private_org()))

    taxonomy = subparsers.add_parser("taxonomy")
    taxonomy_sub = taxonomy.add_subparsers(dest="command", required=True)
    taxonomy_sub.add_parser("aburria-packet")

    hipporag = subparsers.add_parser("hipporag")
    hipporag_sub = hipporag.add_subparsers(dest="command", required=True)
    hippo_backend = hipporag_sub.add_parser("backend")
    hippo_backend.add_argument("action", choices=["status", "ensure-schema"])
    _configure_rethinkdb_flags(hippo_backend)
    hippo_trace = hipporag_sub.add_parser("trace")
    hippo_trace_sub = hippo_trace.add_subparsers(dest="trace_command", required=True)
    trace_add = hippo_trace_sub.add_parser("add")
    trace_add.add_argument("--lexicon-type", required=True)
    trace_add.add_argument("--content", required=True)
    trace_add.add_argument("--namespace", default="synthia")
    trace_add.add_argument("--node-type", default="memory_bit")
    trace_add.add_argument("--node-id", required=True)
    trace_add.add_argument("--selection-mechanism", default="plithogenic_trace")
    trace_add.add_argument("--relevance", type=float, default=0.5)
    trace_add.add_argument("--source-id", action="append", default=[])
    trace_add.add_argument("--T", type=float, default=0.7)
    trace_add.add_argument("--I", type=float, default=0.25)
    trace_add.add_argument("--F", type=float, default=0.05)
    trace_add.add_argument("--H-lex", dest="H_lex", type=float, default=None)
    trace_add.add_argument("--G-lex", dest="G_lex", type=float, default=None)
    trace_add.add_argument("--I-lexicon", dest="I_lexicon", type=float, default=None)
    trace_add.add_argument("--D-f", dest="D_f", type=float, default=None)
    trace_add.add_argument("--dF", type=float, default=None)
    trace_add.add_argument("--i-fractal", dest="i_fractal", type=float, default=None)
    _configure_rethinkdb_flags(trace_add)
    trace_select = hippo_trace_sub.add_parser("select")
    trace_select.add_argument("--lexicon-type", default=None)
    trace_select.add_argument("--selection-mechanism", default=None)
    trace_select.add_argument("--limit", type=int, default=10)
    _configure_rethinkdb_flags(trace_select)
    hippo_edge = hipporag_sub.add_parser("edge")
    hippo_edge_sub = hippo_edge.add_subparsers(dest="edge_command", required=True)
    edge_add = hippo_edge_sub.add_parser("add")
    edge_add.add_argument("--left", required=True)
    edge_add.add_argument("--right", required=True)
    edge_add.add_argument("--relation", required=True)
    edge_add.add_argument("--lexicon-type", default="general")
    edge_add.add_argument("--weight", type=float, default=1.0)
    _configure_rethinkdb_flags(edge_add)

    swarm = subparsers.add_parser("swarm")
    swarm_sub = swarm.add_subparsers(dest="command", required=True)
    node = swarm_sub.add_parser("node")
    node_sub = node.add_subparsers(dest="node_command", required=True)
    node_run = node_sub.add_parser("run")
    node_run.add_argument("--config", required=True)
    node_run.add_argument("--private-org", default=str(_default_private_org()))
    node_run.add_argument("--use-rethinkdb", action="store_true")
    _configure_rethinkdb_flags(node_run)
    simulate = swarm_sub.add_parser("simulate")
    simulate.add_argument("--dataset", required=True)
    simulate.add_argument("--node-id", default="drone.sim.1")
    simulate.add_argument("--private-org", default=str(_default_private_org()))
    simulate.add_argument("--store", action="store_true")
    ingest_frame = swarm_sub.add_parser("ingest-frame")
    ingest_frame.add_argument("--image", required=True)
    ingest_frame.add_argument("--telemetry", required=True, help="JSON object or path to JSON telemetry")
    ingest_frame.add_argument("--node-id", default="drone.sim.1")
    ingest_frame.add_argument("--detection", action="append", default=[], help="label or label:confidence")
    ingest_frame.add_argument("--private-org", default=str(_default_private_org()))
    ingest_frame.add_argument("--store", action="store_true")
    ingest_frame.add_argument("--use-rethinkdb", action="store_true")
    _configure_rethinkdb_flags(ingest_frame)
    pheromone = swarm_sub.add_parser("pheromone")
    pheromone.add_argument("action", choices=["export"])
    pheromone.add_argument("--format", default="geojson", choices=["geojson", "json"])
    queen = swarm_sub.add_parser("queen")
    queen.add_argument("action", choices=["status"])
    review = swarm_sub.add_parser("review-packet")
    review.add_argument("action", choices=["build"])
    review.add_argument("--image", required=False)
    review.add_argument("--telemetry", default='{"source":"simulated"}')
    review.add_argument("--node-id", default="drone.sim.1")
    review.add_argument("--detection", action="append", default=[])
    review.add_argument("--observation", default=None)
    review.add_argument("--private-org", default=str(_default_private_org()))
    review.add_argument("--use-rethinkdb", action="store_true")
    _configure_rethinkdb_flags(review)
    safety_check = swarm_sub.add_parser("safety-check")
    safety_check.add_argument("--mission", required=True, help="JSON object or path to JSON mission")
    backend = swarm_sub.add_parser("backend")
    backend.add_argument("action", choices=["status", "ensure-schema"])
    _configure_rethinkdb_flags(backend)

    args = parser.parse_args(argv)

    if args.area == "sources" and args.command == "scan-root":
        _print_json(scan_root(args.root))
        return 0

    if args.area == "soul" and args.command == "build":
        path = Path(args.private_org) / "01_soul_and_storyline" / "synthia_soul.md"
        _print_json({"path": str(path), "exists": path.exists(), "private_org": args.private_org})
        return 0

    if args.area == "lexicon":
        registry = seed_base_lexicon()
        if args.command == "ingest":
            nodes = registry.ingest_terms(args.domain, args.term, args.source)
            _print_json({"created": [node.as_dict() for node in nodes]})
            return 0
        if args.command == "classify":
            _print_json(registry.classify_text(args.text, args.domain))
            return 0
        if args.command == "switch":
            _print_json(registry.switch_context(args.from_domain, args.to_domain, args.context).as_dict())
            return 0
        if args.command == "i-chain" and args.i_chain_command == "explain":
            _print_json(explain_i_chain(args.term, domain=args.domain))
            return 0
        if args.command == "i-chain" and args.i_chain_command == "classify":
            _print_json(classify_i_chain_text(args.text, args.domain))
            return 0
        if args.command == "notation" and args.notation_command == "render":
            _print_json(render_symbolic_notation(args.symbol, args.format))
            return 0

    if args.area == "plithogenic" and args.command == "profile":
        _print_json(plithogenic_profile_for_source(args.source))
        return 0

    if args.area == "nss":
        router = NSSMathRouter()
        if args.command == "sources" and args.action == "list":
            _print_json(router.list_sources())
            return 0
        if args.command == "route":
            _print_json(router.route(args.text))
            return 0

    if args.area == "codex" and args.command == "status":
        _print_json(codex_status().as_dict())
        return 0
    if args.area == "codex" and args.command == "wake-prompt":
        print(build_wake_prompt(args.private_org))
        return 0

    if args.area == "taxonomy" and args.command == "aburria-packet":
        system = TaxonomicMemorySystem()
        record = system.build_aburria_anchor()
        from .taxonomy_memory import TaxonomicReviewPacketBuilder

        _print_json(TaxonomicReviewPacketBuilder().build(record))
        return 0

    if args.area == "hipporag":
        store = RethinkDBHippoRAGTraceStore(_rethinkdb_config_from_args(args))
        if args.command == "backend" and args.action == "status":
            _print_json(store.status())
            return 0
        if args.command == "backend" and args.action == "ensure-schema":
            _print_json(store.ensure_schema())
            return 0
        if args.command == "trace" and args.trace_command == "add":
            memory_bit = build_memory_bit_from_cli(
                lexicon_type=args.lexicon_type,
                content=args.content,
                namespace=args.namespace,
                node_type=args.node_type,
                node_id=args.node_id,
                selection_mechanism=args.selection_mechanism,
                relevance=args.relevance,
                source_ids=args.source_id,
                tif=TIF(
                    T=args.T,
                    I=args.I,
                    F=args.F,
                    I_system=args.I,
                    D_f=args.D_f,
                    dF=args.dF,
                    i_fractal=args.i_fractal,
                ),
            )
            _print_json(store.store_memory_bit(memory_bit))
            return 0
        if args.command == "trace" and args.trace_command == "select":
            _print_json(store.select_memory_bits(args.lexicon_type, args.selection_mechanism, args.limit))
            return 0
        if args.command == "edge" and args.edge_command == "add":
            _print_json(
                store.store_edge(
                    HippoRAGEdgeTrace(
                        left_memory_bit_id=args.left,
                        right_memory_bit_id=args.right,
                        relation=args.relation,
                        lexicon_type=args.lexicon_type,
                        weight=args.weight,
                    )
                )
            )
            return 0

    if args.area == "swarm":
        if args.command == "node" and args.node_command == "run":
            config = load_json_mapping(args.config)
            node_id = str(config.get("node_id", "drone.sim.1"))
            app = DroneNodeApp(node_id)
            vault = EvidenceVault.from_private_org(args.private_org)
            backend = RethinkDBSwarmBackend(_rethinkdb_config_from_args(args)) if args.use_rethinkdb else None
            queen = QueenCoordinator(evidence_vault=vault, rethinkdb_backend=backend)
            heartbeat = queen.heartbeat(node_id, config.get("status") if isinstance(config.get("status"), dict) else {})
            ingested = []
            for frame in config.get("frames", []):
                if not isinstance(frame, dict):
                    continue
                observation = app.ingest_frame(
                    frame["image"],
                    frame.get("telemetry", {}),
                    frame.get("detections"),
                )
                ingested.append(queen.ingest_observation(observation))
            _print_json({"node_id": node_id, "heartbeat": heartbeat, "ingested": ingested, "queen": queen.status()})
            return 0
        if args.command == "simulate":
            dataset = Path(args.dataset)
            app = DroneNodeApp(args.node_id)
            queen = QueenCoordinator(evidence_vault=EvidenceVault.from_private_org(args.private_org) if args.store else None)
            suffixes = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"}
            observations = []
            for image in sorted(path for path in dataset.glob("*") if path.suffix.lower() in suffixes):
                observation = app.ingest_frame(
                    image,
                    {"source": "simulated_dataset", "latitude": 0.0, "longitude": 0.0},
                )
                observations.append(queen.ingest_observation(observation))
            _print_json(
                {
                    "dataset": str(dataset),
                    "observation_count": len(observations),
                    "observations": observations,
                    "queen": queen.status(),
                }
            )
            return 0
        if args.command == "ingest-frame":
            app = DroneNodeApp(args.node_id)
            observation = app.ingest_frame(
                args.image,
                load_json_mapping(args.telemetry),
                parse_detection_arg(args.detection) if args.detection else None,
            )
            vault = EvidenceVault.from_private_org(args.private_org) if args.store else None
            backend = RethinkDBSwarmBackend(_rethinkdb_config_from_args(args)) if args.use_rethinkdb else None
            queen = QueenCoordinator(evidence_vault=vault, rethinkdb_backend=backend)
            _print_json(queen.ingest_observation(observation))
            return 0
        if args.command == "pheromone" and args.action == "export":
            pheromone_map = DigitalPheromoneMap()
            payload = pheromone_map.as_geojson() if args.format == "geojson" else {"cells": []}
            _print_json(payload)
            return 0
        if args.command == "queen" and args.action == "status":
            _print_json(QueenCoordinator().status())
            return 0
        if args.command == "review-packet" and args.action == "build":
            if args.observation:
                vault = EvidenceVault.from_private_org(args.private_org)
                backend = RethinkDBSwarmBackend(_rethinkdb_config_from_args(args)) if args.use_rethinkdb else None
                observation = vault.load_observation(args.observation)
                if backend is not None:
                    observation = backend.load_observation(args.observation) or observation
                _print_json(SwarmReviewPacketBuilder().build(observation))
                return 0
            image = args.image or "simulated_field_frame.jpg"
            app = DroneNodeApp(args.node_id)
            observation = app.ingest_frame(
                image,
                load_json_mapping(args.telemetry),
                parse_detection_arg(args.detection) if args.detection else None,
            )
            _print_json(SwarmReviewPacketBuilder().build(observation))
            return 0
        if args.command == "safety-check":
            _print_json(MissionSafetyGate().evaluate(load_json_mapping(args.mission)))
            return 0
        if args.command == "backend" and args.action == "status":
            _print_json(RethinkDBSwarmBackend(_rethinkdb_config_from_args(args)).status())
            return 0
        if args.command == "backend" and args.action == "ensure-schema":
            _print_json(RethinkDBSwarmBackend(_rethinkdb_config_from_args(args)).ensure_schema())
            return 0

    parser.error("unhandled command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
