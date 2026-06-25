"""Synthia command line interface."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .codex_connector import build_wake_prompt, codex_status
from .lexicon import seed_base_lexicon
from .sources import scan_root
from .swarm import (
    DigitalPheromoneMap,
    DroneNodeApp,
    MissionSafetyGate,
    QueenCoordinator,
    SwarmReviewPacketBuilder,
    load_json_mapping,
    parse_detection_arg,
)
from .taxonomy_memory import TaxonomicMemorySystem


def _print_json(payload: object) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def _default_private_org() -> Path:
    return Path.cwd().parent / "Synthia_organisation"


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

    codex = subparsers.add_parser("codex")
    codex_sub = codex.add_subparsers(dest="command", required=True)
    codex_sub.add_parser("status")
    wake = codex_sub.add_parser("wake-prompt")
    wake.add_argument("--private-org", default=str(_default_private_org()))

    taxonomy = subparsers.add_parser("taxonomy")
    taxonomy_sub = taxonomy.add_subparsers(dest="command", required=True)
    taxonomy_sub.add_parser("aburria-packet")

    swarm = subparsers.add_parser("swarm")
    swarm_sub = swarm.add_subparsers(dest="command", required=True)
    simulate = swarm_sub.add_parser("simulate")
    simulate.add_argument("--dataset", required=True)
    simulate.add_argument("--node-id", default="drone.sim.1")
    ingest_frame = swarm_sub.add_parser("ingest-frame")
    ingest_frame.add_argument("--image", required=True)
    ingest_frame.add_argument("--telemetry", required=True, help="JSON object or path to JSON telemetry")
    ingest_frame.add_argument("--node-id", default="drone.sim.1")
    ingest_frame.add_argument("--detection", action="append", default=[], help="label or label:confidence")
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
    safety_check = swarm_sub.add_parser("safety-check")
    safety_check.add_argument("--mission", required=True, help="JSON object or path to JSON mission")

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

    if args.area == "swarm":
        if args.command == "simulate":
            dataset = Path(args.dataset)
            app = DroneNodeApp(args.node_id)
            queen = QueenCoordinator()
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
            queen = QueenCoordinator()
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

    parser.error("unhandled command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
