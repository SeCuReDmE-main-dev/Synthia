"""Synthia command line interface."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

from .codex_connector import build_wake_prompt, codex_status
from .document_pipeline import run_document_pipeline
from .hipporag_bridge import (
    HippoRAGEdgeTrace,
    RethinkDBHippoRAGTraceStore,
    build_memory_bit_from_cli,
)
from .lexicon import seed_base_lexicon
from .nss import NSSMathRouter
from .nss_articles import NSSArticleIndex
from .independent_neutrosophic_components import classify_components, components_explain
from .multineutrosophic import fuse_multineutrosophic_assessments, multineutrosophic_explain
from .neutrosophic_foundation import foundation_explain, foundation_normalize, foundation_profile
from .neutrosophic_logic import LogicCompatibilityClassifier
from .neutrosophic_probability import (
    NeutrosophicEvent,
    NeutrosophicProbability,
    NeutrosophicSampleSpace,
    probability_explain,
)
from .neutrosophic_random_variables import (
    NeutrosophicRandomVariable,
    random_variable_explain,
    summarize_random_variables,
)
from .neutrosophic_sets import NeutrosophicSetClassifier
from .neutrosophic_statistics import (
    classify_neutrosophic_distribution,
    statistics_explain,
    summarize_neutrosophic_dataset,
)
from .neutroalgebra import classify_neutroalgebra_operation, evaluate_neutroalgebra_axiom, neutroalgebra_explain
from .plithogenic import (
    TIF,
    classify_i_chain_text,
    explain_i_chain,
    plithogenic_profile_for_source,
    render_symbolic_notation,
)
from .plithogenic_arithmetic import multiply_symbolic_plithogenic_numbers, plithogenic_arithmetic_explain
from .plithogenic_hypersoft import classify_hypersoft_mapping, hypersoft_product, plithogenic_hypersoft_explain
from .plithogenic_logic import classify_plithogenic_logic, plithogenic_logic_explain
from .plithogenic_probability_statistics import (
    plithogenic_probability_explain,
    refine_plithogenic_probability,
    summarize_plithogenic_probability_event,
)
from .plithogenic_set import operate_plithogenic_sets, plithogenic_set_explain, score_plithogenic_set
from .algorithm_behavior import build_algorithmic_bioinformatics_demo_case, score_algorithm_behavior_case
from .biology_graph import build_tree_tobacco_demo_graph, score_biology_graph_review
from .molecular_evidence import build_dna_similarity_demo_case, score_molecular_review_case
from .neutrino_lexical_gate import classify_neutrino_observation
from .chapter14_threshold_gate import classify_chapter14_threshold
from .phylo_plithogenic import build_tilapia_style_demo_packet, score_phylo_plithogenic_packet
from .research_object_provenance import build_academic_platform_demo_case, score_research_object_provenance_case
from .risk_triage import build_food_safety_demo_case, score_risk_triage_case
from .novak_anderson_phi_pi import build_novak_anderson_governance_case
from .scientific_governance import build_synthia_governance_demo_case, score_scientific_governance_case
from .single_valued_neutrosophic import SingleValuedNeutrosophicSet, SVNSOperator
from .safety import HIERARCHY
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
from .symbolic_plithogenic_algebra import (
    operate_symbolic_plithogenic_numbers,
    parse_symbolic_plithogenic_number,
    symbolic_plithogenic_explain,
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


def _read_text_arg(value: str | None) -> str | None:
    if value is None:
        return None
    path = Path(value)
    if path.exists():
        return path.read_text(encoding="utf-8", errors="replace")
    return value


def _write_private_nss_article_ledger(private_org: str, payload: dict[str, object]) -> Path:
    target_dir = Path(private_org) / "02_taxonomy_lexicon_model"
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / "nss_article_index.json"
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return target


def _parse_tif_triplet(value: str, label: str = "value") -> tuple[float, float, float]:
    parts = [part.strip() for part in value.split(",")]
    if len(parts) != 3:
        raise ValueError(f"{label} must be formatted as T,I,F")
    return float(parts[0]), float(parts[1]), float(parts[2])


def _load_json_value(value: str) -> object:
    path = Path(value)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return json.loads(value)


def main(argv: list[str] | None = None) -> int:
    effective_argv = argv if argv is not None else sys.argv[1:]
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

    document = subparsers.add_parser("document")
    document_sub = document.add_subparsers(dest="command", required=True)
    document_pipeline = document_sub.add_parser("pipeline")
    document_pipeline.add_argument("--input", required=True)
    document_pipeline.add_argument("--profile", default="taxonomy-review")
    document_pipeline.add_argument("--private-org", default=str(_default_private_org()))
    document_pipeline.add_argument("--emit-lexicon", action="store_true")
    document_pipeline.add_argument("--emit-annex", action="store_true")

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
    plithogenic_probability = plithogenic_sub.add_parser("probability")
    plithogenic_probability_sub = plithogenic_probability.add_subparsers(dest="probability_command", required=True)
    plithogenic_probability_sub.add_parser("explain")
    plithogenic_probability_event = plithogenic_probability_sub.add_parser("event")
    plithogenic_probability_event.add_argument("--variables", required=True, help="JSON array or path")
    plithogenic_probability_refine = plithogenic_probability_sub.add_parser("refine")
    plithogenic_probability_refine.add_argument("--components", required=True, help="JSON array or path")
    plithogenic_set = plithogenic_sub.add_parser("set")
    plithogenic_set_sub = plithogenic_set.add_subparsers(dest="set_command", required=True)
    plithogenic_set_sub.add_parser("explain")
    plithogenic_set_score = plithogenic_set_sub.add_parser("score")
    plithogenic_set_score.add_argument("--attributes", required=True, help="JSON array or path")
    plithogenic_set_operate = plithogenic_set_sub.add_parser("operate")
    plithogenic_set_operate.add_argument("--op", choices=["union", "intersection", "complement"], required=True)
    plithogenic_set_operate.add_argument("--left", required=True, help="JSON object or path")
    plithogenic_set_operate.add_argument("--right", default=None, help="JSON object or path")
    plithogenic_logic = plithogenic_sub.add_parser("logic")
    plithogenic_logic_sub = plithogenic_logic.add_subparsers(dest="logic_command", required=True)
    plithogenic_logic_sub.add_parser("explain")
    plithogenic_logic_classify = plithogenic_logic_sub.add_parser("classify")
    plithogenic_logic_classify.add_argument("--variables", required=True, help="JSON array or path")

    symbolic_plithogenic = subparsers.add_parser("symbolic-plithogenic")
    symbolic_plithogenic_sub = symbolic_plithogenic.add_subparsers(dest="command", required=True)
    symbolic_plithogenic_sub.add_parser("explain")
    symbolic_number = symbolic_plithogenic_sub.add_parser("number")
    symbolic_number_sub = symbolic_number.add_subparsers(dest="number_command", required=True)
    symbolic_number_parse = symbolic_number_sub.add_parser("parse")
    symbolic_number_parse.add_argument("--value", required=True, help="JSON object or path")
    symbolic_operate = symbolic_plithogenic_sub.add_parser("operate")
    symbolic_operate.add_argument("--op", choices=["add", "subtract"], required=True)
    symbolic_operate.add_argument("--left", required=True, help="JSON object or path")
    symbolic_operate.add_argument("--right", required=True, help="JSON object or path")
    symbolic_multiply = symbolic_plithogenic_sub.add_parser("multiply")
    symbolic_multiply.add_argument("--left", required=True, help="JSON object or path")
    symbolic_multiply.add_argument("--right", required=True, help="JSON object or path")
    symbolic_multiply.add_argument("--law", default="absorbance")

    hypersoft = subparsers.add_parser("hypersoft")
    hypersoft_sub = hypersoft.add_subparsers(dest="command", required=True)
    hypersoft_sub.add_parser("explain")
    hypersoft_classify = hypersoft_sub.add_parser("classify")
    hypersoft_classify.add_argument("--mapping", required=True, help="JSON object or path")
    hypersoft_product_parser = hypersoft_sub.add_parser("product")
    hypersoft_product_parser.add_argument("--attributes", required=True, help="JSON object or path")

    neutroalgebra = subparsers.add_parser("neutroalgebra")
    neutroalgebra_sub = neutroalgebra.add_subparsers(dest="command", required=True)
    neutroalgebra_sub.add_parser("explain")
    neutroalgebra_classify = neutroalgebra_sub.add_parser("classify")
    neutroalgebra_classify.add_argument("--operation", required=True, help="JSON object or path")
    neutroalgebra_axiom = neutroalgebra_sub.add_parser("axiom")
    neutroalgebra_axiom.add_argument("--axiom", choices=["associativity", "commutativity"], required=True)
    neutroalgebra_axiom.add_argument("--table", required=True, help="JSON object or path")

    nss = subparsers.add_parser("nss")
    nss_sub = nss.add_subparsers(dest="command", required=True)
    nss_sources = nss_sub.add_parser("sources")
    nss_sources.add_argument("action", choices=["list"])
    nss_route = nss_sub.add_parser("route")
    nss_route.add_argument("--text", required=True)
    nss_foundation = nss_sub.add_parser("foundation")
    nss_foundation_sub = nss_foundation.add_subparsers(dest="foundation_command", required=True)
    nss_foundation_sub.add_parser("explain")
    nss_foundation_normalize = nss_foundation_sub.add_parser("normalize")
    nss_foundation_normalize.add_argument("--T", type=float, required=True)
    nss_foundation_normalize.add_argument("--I", type=float, required=True)
    nss_foundation_normalize.add_argument("--F", type=float, required=True)
    nss_foundation_normalize.add_argument("--profile", default="standard")
    nss_foundation_profile = nss_foundation_sub.add_parser("profile")
    nss_foundation_profile.add_argument("--name", required=True)
    nss_set = nss_sub.add_parser("set")
    nss_set_sub = nss_set.add_subparsers(dest="set_command", required=True)
    nss_set_sub.add_parser("explain")
    nss_set_classify = nss_set_sub.add_parser("classify")
    nss_set_classify.add_argument("--T", type=float, required=True)
    nss_set_classify.add_argument("--I", type=float, required=True)
    nss_set_classify.add_argument("--F", type=float, required=True)
    nss_set_compare = nss_set_sub.add_parser("compare-ifs")
    nss_set_compare.add_argument("--T", type=float, required=True)
    nss_set_compare.add_argument("--I", type=float, required=True)
    nss_set_compare.add_argument("--F", type=float, required=True)
    nss_logic = nss_sub.add_parser("logic")
    nss_logic_sub = nss_logic.add_subparsers(dest="logic_command", required=True)
    nss_logic_sub.add_parser("explain")
    nss_logic_classify = nss_logic_sub.add_parser("classify")
    nss_logic_classify.add_argument("--T", type=float, required=True)
    nss_logic_classify.add_argument("--I", type=float, required=True)
    nss_logic_classify.add_argument("--F", type=float, required=True)
    nss_logic_classify.add_argument("--text", default="")
    nss_logic_compare = nss_logic_sub.add_parser("compare-ifl")
    nss_logic_compare.add_argument("--T", type=float, required=True)
    nss_logic_compare.add_argument("--I", type=float, required=True)
    nss_logic_compare.add_argument("--F", type=float, required=True)
    nss_svns = nss_sub.add_parser("svns")
    nss_svns_sub = nss_svns.add_subparsers(dest="svns_command", required=True)
    nss_svns_sub.add_parser("explain")
    nss_svns_operate = nss_svns_sub.add_parser("operate")
    nss_svns_operate.add_argument("--op", choices=["union", "intersection", "difference"], required=True)
    nss_svns_operate.add_argument("--left", required=True, help="T,I,F")
    nss_svns_operate.add_argument("--right", required=True, help="T,I,F")
    nss_svns_favorite = nss_svns_sub.add_parser("favorite")
    nss_svns_favorite.add_argument("--mode", choices=["truth", "falsity"], required=True)
    nss_svns_favorite.add_argument("--T", type=float, required=True)
    nss_svns_favorite.add_argument("--I", type=float, required=True)
    nss_svns_favorite.add_argument("--F", type=float, required=True)
    nss_probability = nss_sub.add_parser("probability")
    nss_probability_sub = nss_probability.add_subparsers(dest="probability_command", required=True)
    nss_probability_sub.add_parser("explain")
    nss_probability_event = nss_probability_sub.add_parser("event")
    nss_probability_event.add_argument("--name", required=True)
    nss_probability_event.add_argument("--T", type=float, required=True)
    nss_probability_event.add_argument("--I", type=float, required=True)
    nss_probability_event.add_argument("--F", type=float, required=True)
    nss_probability_sample = nss_probability_sub.add_parser("sample-space")
    nss_probability_sample.add_argument("--events", required=True, help="JSON array or path")
    nss_statistics = nss_sub.add_parser("statistics")
    nss_statistics_sub = nss_statistics.add_subparsers(dest="statistics_command", required=True)
    nss_statistics_sub.add_parser("explain")
    nss_statistics_summarize = nss_statistics_sub.add_parser("summarize")
    nss_statistics_summarize.add_argument("--values", required=True, help="JSON array or path")
    nss_distribution = nss_sub.add_parser("distribution")
    nss_distribution_sub = nss_distribution.add_subparsers(dest="distribution_command", required=True)
    nss_distribution_classify = nss_distribution_sub.add_parser("classify")
    nss_distribution_classify.add_argument("--text", required=True)
    nss_random_variable = nss_sub.add_parser("random-variable")
    nss_random_variable_sub = nss_random_variable.add_subparsers(dest="random_variable_command", required=True)
    nss_random_variable_sub.add_parser("explain")
    nss_random_variable_define = nss_random_variable_sub.add_parser("define")
    nss_random_variable_define.add_argument("--name", required=True)
    nss_random_variable_define.add_argument("--base", type=float, required=True)
    nss_random_variable_define.add_argument("--I", type=float, required=True)
    nss_random_variable_summarize = nss_random_variable_sub.add_parser("summarize")
    nss_random_variable_summarize.add_argument("--values", required=True, help="JSON array or path")
    nss_components = nss_sub.add_parser("components")
    nss_components_sub = nss_components.add_subparsers(dest="components_command", required=True)
    nss_components_sub.add_parser("explain")
    nss_components_classify = nss_components_sub.add_parser("classify")
    nss_components_classify.add_argument("--T", type=float, required=True)
    nss_components_classify.add_argument("--I", type=float, required=True)
    nss_components_classify.add_argument("--F", type=float, required=True)
    nss_components_classify.add_argument("--mode", choices=["independent", "partial", "dependent", "offset"], required=True)
    nss_multi_set = nss_sub.add_parser("multi-set")
    nss_multi_set_sub = nss_multi_set.add_subparsers(dest="multi_set_command", required=True)
    nss_multi_set_sub.add_parser("explain")
    nss_multi_set_fuse = nss_multi_set_sub.add_parser("fuse")
    nss_multi_set_fuse.add_argument("--assessments", required=True, help="JSON array or path")
    nss_articles = nss_sub.add_parser("articles")
    nss_articles_sub = nss_articles.add_subparsers(dest="articles_command", required=True)
    nss_articles_scan = nss_articles_sub.add_parser("scan")
    nss_articles_scan.add_argument("--limit", type=int, default=None)
    nss_articles_scan.add_argument("--private-org", default=str(_default_private_org()))
    nss_articles_scan.add_argument("--html", default=None, help="Optional path to a local Articles.htm fixture")
    nss_articles_classify = nss_articles_sub.add_parser("classify")
    nss_articles_classify.add_argument("--text", required=True)
    nss_articles_source = nss_articles_sub.add_parser("source")
    nss_articles_source.add_argument("--url", required=True)
    nss_articles_source.add_argument("--title", default=None)
    nss_index = nss_sub.add_parser("index")
    nss_index_sub = nss_index.add_subparsers(dest="index_command", required=True)
    nss_index_explain = nss_index_sub.add_parser("explain")
    nss_index_explain.add_argument("--text", required=True)

    risk_triage = subparsers.add_parser("risk-triage")
    risk_triage_sub = risk_triage.add_subparsers(dest="command", required=True)
    risk_triage_score = risk_triage_sub.add_parser("score")
    risk_triage_score.add_argument("--case", required=True, help="JSON object or path")
    risk_triage_sub.add_parser("demo")

    biology_graph = subparsers.add_parser("biology-graph")
    biology_graph_sub = biology_graph.add_subparsers(dest="command", required=True)
    biology_graph_score = biology_graph_sub.add_parser("score")
    biology_graph_score.add_argument("--graph", required=True, help="JSON object or path")
    biology_graph_sub.add_parser("demo")

    molecular_evidence = subparsers.add_parser("molecular-evidence")
    molecular_evidence_sub = molecular_evidence.add_subparsers(dest="command", required=True)
    molecular_evidence_score = molecular_evidence_sub.add_parser("score")
    molecular_evidence_score.add_argument("--case", required=True, help="JSON object or path")
    molecular_evidence_sub.add_parser("demo")

    algorithm_behavior = subparsers.add_parser("algorithm-behavior")
    algorithm_behavior_sub = algorithm_behavior.add_subparsers(dest="command", required=True)
    algorithm_behavior_score = algorithm_behavior_sub.add_parser("score")
    algorithm_behavior_score.add_argument("--case", required=True, help="JSON object or path")
    algorithm_behavior_sub.add_parser("demo")

    scientific_governance = subparsers.add_parser("scientific-governance")
    scientific_governance_sub = scientific_governance.add_subparsers(dest="command", required=True)
    scientific_governance_score = scientific_governance_sub.add_parser("score")
    scientific_governance_score.add_argument("--case", required=True, help="JSON object or path")
    scientific_governance_sub.add_parser("demo")
    scientific_governance_sub.add_parser("novak-anderson")

    research_object_provenance = subparsers.add_parser("research-object-provenance")
    research_object_provenance_sub = research_object_provenance.add_subparsers(dest="command", required=True)
    research_object_provenance_score = research_object_provenance_sub.add_parser("score")
    research_object_provenance_score.add_argument("--case", required=True, help="JSON object or path")
    research_object_provenance_sub.add_parser("demo")

    neutrino = subparsers.add_parser("neutrino")
    neutrino_sub = neutrino.add_subparsers(dest="command", required=True)
    neutrino_guardrail = neutrino_sub.add_parser("guardrail-check")
    neutrino_guardrail.add_argument("--input", required=True, help="JSON object or path")
    neutrino_guardrail.add_argument("--json", action="store_true")
    neutrino_chapter14 = neutrino_sub.add_parser("chapter14-threshold-check")
    neutrino_chapter14.add_argument("--input", required=True, help="JSON object or path")
    neutrino_chapter14.add_argument("--json", action="store_true")

    codex = subparsers.add_parser("codex")
    codex_sub = codex.add_subparsers(dest="command", required=True)
    codex_sub.add_parser("status")
    wake = codex_sub.add_parser("wake-prompt")
    wake.add_argument("--private-org", default=str(_default_private_org()))

    taxonomy = subparsers.add_parser("taxonomy")
    taxonomy_sub = taxonomy.add_subparsers(dest="command", required=True)
    taxonomy_sub.add_parser("aburria-packet")
    phylo_plithogenic = taxonomy_sub.add_parser("phylo-plithogenic")
    phylo_plithogenic_sub = phylo_plithogenic.add_subparsers(dest="phylo_plithogenic_command", required=True)
    phylo_plithogenic_score = phylo_plithogenic_sub.add_parser("score")
    phylo_plithogenic_score.add_argument("--packet", required=True, help="JSON object or path")
    phylo_plithogenic_sub.add_parser("demo")

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

    args = parser.parse_args(effective_argv)

    if args.area == "sources" and args.command == "scan-root":
        _print_json(scan_root(args.root))
        return 0

    if args.area == "soul" and args.command == "build":
        path = Path(args.private_org) / "01_soul_and_storyline" / "synthia_soul.md"
        _print_json({"path": str(path), "exists": path.exists(), "private_org": args.private_org})
        return 0

    if args.area == "document" and args.command == "pipeline":
        payload, exit_code = run_document_pipeline(
            input_path=args.input,
            profile_name=args.profile,
            private_org=args.private_org,
            command=effective_argv,
            emit_lexicon=args.emit_lexicon,
            emit_annex=args.emit_annex,
        )
        _print_json(payload)
        return exit_code

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
    if args.area == "plithogenic" and args.command == "probability" and args.probability_command == "explain":
        _print_json(plithogenic_probability_explain())
        return 0
    if args.area == "plithogenic" and args.command == "probability" and args.probability_command == "event":
        variables = _load_json_value(args.variables)
        if not isinstance(variables, list):
            raise ValueError("--variables must decode to a JSON array")
        _print_json(summarize_plithogenic_probability_event(variables))
        return 0
    if args.area == "plithogenic" and args.command == "probability" and args.probability_command == "refine":
        components = _load_json_value(args.components)
        if not isinstance(components, list):
            raise ValueError("--components must decode to a JSON array")
        _print_json(refine_plithogenic_probability(components))
        return 0
    if args.area == "plithogenic" and args.command == "set" and args.set_command == "explain":
        _print_json(plithogenic_set_explain())
        return 0
    if args.area == "plithogenic" and args.command == "set" and args.set_command == "score":
        attributes = _load_json_value(args.attributes)
        if not isinstance(attributes, list):
            raise ValueError("--attributes must decode to a JSON array")
        _print_json(score_plithogenic_set(attributes))
        return 0
    if args.area == "plithogenic" and args.command == "set" and args.set_command == "operate":
        left = _load_json_value(args.left)
        right = _load_json_value(args.right) if args.right is not None else None
        if not isinstance(left, dict) or (right is not None and not isinstance(right, dict)):
            raise ValueError("--left and --right must decode to JSON objects")
        _print_json(operate_plithogenic_sets(args.op, left, right))
        return 0
    if args.area == "plithogenic" and args.command == "logic" and args.logic_command == "explain":
        _print_json(plithogenic_logic_explain())
        return 0
    if args.area == "plithogenic" and args.command == "logic" and args.logic_command == "classify":
        variables = _load_json_value(args.variables)
        if not isinstance(variables, list):
            raise ValueError("--variables must decode to a JSON array")
        _print_json(classify_plithogenic_logic(variables))
        return 0

    if args.area == "symbolic-plithogenic":
        if args.command == "explain":
            _print_json(symbolic_plithogenic_explain())
            return 0
        if args.command == "number" and args.number_command == "parse":
            _print_json(parse_symbolic_plithogenic_number(_load_json_value(args.value)))
            return 0
        if args.command == "operate":
            _print_json(operate_symbolic_plithogenic_numbers(args.op, _load_json_value(args.left), _load_json_value(args.right)))
            return 0
        if args.command == "multiply":
            _print_json(multiply_symbolic_plithogenic_numbers(_load_json_value(args.left), _load_json_value(args.right), law=args.law))
            return 0

    if args.area == "hypersoft":
        if args.command == "explain":
            _print_json(plithogenic_hypersoft_explain())
            return 0
        if args.command == "classify":
            _print_json(classify_hypersoft_mapping(_load_json_value(args.mapping)))
            return 0
        if args.command == "product":
            _print_json(hypersoft_product(_load_json_value(args.attributes)))
            return 0

    if args.area == "neutroalgebra":
        if args.command == "explain":
            _print_json(neutroalgebra_explain())
            return 0
        if args.command == "classify":
            _print_json(classify_neutroalgebra_operation(_load_json_value(args.operation)))
            return 0
        if args.command == "axiom":
            _print_json(evaluate_neutroalgebra_axiom(args.axiom, _load_json_value(args.table)))
            return 0

    if args.area == "nss":
        router = NSSMathRouter()
        article_index = NSSArticleIndex()
        set_classifier = NeutrosophicSetClassifier()
        logic_classifier = LogicCompatibilityClassifier()
        svns_operator = SVNSOperator()
        if args.command == "sources" and args.action == "list":
            _print_json(router.list_sources())
            return 0
        if args.command == "route":
            _print_json(router.route(args.text))
            return 0
        if args.command == "foundation" and args.foundation_command == "explain":
            _print_json(foundation_explain())
            return 0
        if args.command == "foundation" and args.foundation_command == "normalize":
            _print_json(foundation_normalize(T=args.T, I=args.I, F=args.F, profile=args.profile))
            return 0
        if args.command == "foundation" and args.foundation_command == "profile":
            _print_json(foundation_profile(args.name))
            return 0
        if args.command == "set" and args.set_command == "explain":
            _print_json(set_classifier.explain())
            return 0
        if args.command == "set" and args.set_command == "classify":
            _print_json(set_classifier.classify(args.T, args.I, args.F))
            return 0
        if args.command == "set" and args.set_command == "compare-ifs":
            _print_json(set_classifier.compare_ifs(args.T, args.I, args.F))
            return 0
        if args.command == "logic" and args.logic_command == "explain":
            _print_json(logic_classifier.explain())
            return 0
        if args.command == "logic" and args.logic_command == "classify":
            _print_json(logic_classifier.classify(args.T, args.I, args.F, text=args.text))
            return 0
        if args.command == "logic" and args.logic_command == "compare-ifl":
            _print_json(logic_classifier.compare_ifl(args.T, args.I, args.F))
            return 0
        if args.command == "svns" and args.svns_command == "explain":
            _print_json(svns_operator.explain())
            return 0
        if args.command == "svns" and args.svns_command == "operate":
            left = SingleValuedNeutrosophicSet(*_parse_tif_triplet(args.left, "left"), label="left")
            right = SingleValuedNeutrosophicSet(*_parse_tif_triplet(args.right, "right"), label="right")
            _print_json(svns_operator.operate(args.op, left, right))
            return 0
        if args.command == "svns" and args.svns_command == "favorite":
            value = SingleValuedNeutrosophicSet(args.T, args.I, args.F, label="value")
            _print_json(svns_operator.favorite(args.mode, value))
            return 0
        if args.command == "probability" and args.probability_command == "explain":
            _print_json(probability_explain())
            return 0
        if args.command == "probability" and args.probability_command == "event":
            event = NeutrosophicEvent(args.name, NeutrosophicProbability(args.T, args.I, args.F))
            _print_json(event.as_dict())
            return 0
        if args.command == "probability" and args.probability_command == "sample-space":
            raw_events = _load_json_value(args.events)
            if not isinstance(raw_events, list):
                raise ValueError("--events must decode to a JSON array")
            events = []
            for index, item in enumerate(raw_events):
                if not isinstance(item, dict):
                    raise ValueError("each event must be a JSON object")
                events.append(
                    NeutrosophicEvent(
                        str(item.get("name", f"event_{index + 1}")),
                        NeutrosophicProbability(float(item.get("T", 0.0)), float(item.get("I", 0.0)), float(item.get("F", 0.0))),
                    )
                )
            _print_json(NeutrosophicSampleSpace(tuple(events)).as_dict())
            return 0
        if args.command == "statistics" and args.statistics_command == "explain":
            _print_json(statistics_explain())
            return 0
        if args.command == "statistics" and args.statistics_command == "summarize":
            values = _load_json_value(args.values)
            if not isinstance(values, list):
                raise ValueError("--values must decode to a JSON array")
            _print_json(summarize_neutrosophic_dataset(values))
            return 0
        if args.command == "distribution" and args.distribution_command == "classify":
            _print_json(classify_neutrosophic_distribution(args.text))
            return 0
        if args.command == "random-variable" and args.random_variable_command == "explain":
            _print_json(random_variable_explain())
            return 0
        if args.command == "random-variable" and args.random_variable_command == "define":
            _print_json(NeutrosophicRandomVariable(args.name, args.base, args.I).as_dict())
            return 0
        if args.command == "random-variable" and args.random_variable_command == "summarize":
            values = _load_json_value(args.values)
            if not isinstance(values, list):
                raise ValueError("--values must decode to a JSON array")
            _print_json(summarize_random_variables(values))
            return 0
        if args.command == "components" and args.components_command == "explain":
            _print_json(components_explain())
            return 0
        if args.command == "components" and args.components_command == "classify":
            _print_json(classify_components(args.T, args.I, args.F, args.mode))
            return 0
        if args.command == "multi-set" and args.multi_set_command == "explain":
            _print_json(multineutrosophic_explain())
            return 0
        if args.command == "multi-set" and args.multi_set_command == "fuse":
            assessments = _load_json_value(args.assessments)
            if not isinstance(assessments, list):
                raise ValueError("--assessments must decode to a JSON array")
            _print_json(fuse_multineutrosophic_assessments(assessments))
            return 0
        if args.command == "articles" and args.articles_command == "scan":
            scan_result = article_index.scan(limit=args.limit, html=_read_text_arg(args.html))
            ledger_path = _write_private_nss_article_ledger(args.private_org, scan_result.as_dict())
            _print_json(
                {
                    "source_url": scan_result.source_url,
                    "scanned_at": scan_result.scanned_at,
                    "total_records": scan_result.total_records,
                    "ledger_path": str(ledger_path),
                    "public_output": "sanitized_scan_summary_only",
                    "hierarchy": HIERARCHY,
                }
            )
            return 0
        if args.command == "articles" and args.articles_command == "classify":
            _print_json(article_index.classify_text(args.text))
            return 0
        if args.command == "articles" and args.articles_command == "source":
            _print_json(article_index.classify_source(args.url, title=args.title))
            return 0
        if args.command == "index" and args.index_command == "explain":
            _print_json(article_index.classify_text(args.text))
            return 0

    if args.area == "risk-triage":
        if args.command == "demo":
            _print_json(score_risk_triage_case(build_food_safety_demo_case()))
            return 0
        if args.command == "score":
            risk_case = _load_json_value(args.case)
            if not isinstance(risk_case, dict):
                raise ValueError("--case must decode to a JSON object")
            _print_json(score_risk_triage_case(risk_case))
            return 0

    if args.area == "biology-graph":
        if args.command == "demo":
            _print_json(score_biology_graph_review(build_tree_tobacco_demo_graph()))
            return 0
        if args.command == "score":
            graph = _load_json_value(args.graph)
            if not isinstance(graph, dict):
                raise ValueError("--graph must decode to a JSON object")
            _print_json(score_biology_graph_review(graph))
            return 0

    if args.area == "molecular-evidence":
        if args.command == "demo":
            _print_json(score_molecular_review_case(build_dna_similarity_demo_case()))
            return 0
        if args.command == "score":
            molecular_case = _load_json_value(args.case)
            if not isinstance(molecular_case, dict):
                raise ValueError("--case must decode to a JSON object")
            _print_json(score_molecular_review_case(molecular_case))
            return 0

    if args.area == "algorithm-behavior":
        if args.command == "demo":
            _print_json(score_algorithm_behavior_case(build_algorithmic_bioinformatics_demo_case()))
            return 0
        if args.command == "score":
            algorithm_case = _load_json_value(args.case)
            if not isinstance(algorithm_case, dict):
                raise ValueError("--case must decode to a JSON object")
            _print_json(score_algorithm_behavior_case(algorithm_case))
            return 0

    if args.area == "scientific-governance":
        if args.command == "demo":
            _print_json(score_scientific_governance_case(build_synthia_governance_demo_case()))
            return 0
        if args.command == "novak-anderson":
            _print_json(score_scientific_governance_case(build_novak_anderson_governance_case()))
            return 0
        if args.command == "score":
            governance_case = _load_json_value(args.case)
            if not isinstance(governance_case, dict):
                raise ValueError("--case must decode to a JSON object")
            _print_json(score_scientific_governance_case(governance_case))
            return 0

    if args.area == "research-object-provenance":
        if args.command == "demo":
            _print_json(score_research_object_provenance_case(build_academic_platform_demo_case()))
            return 0
        if args.command == "score":
            provenance_case = _load_json_value(args.case)
            if not isinstance(provenance_case, dict):
                raise ValueError("--case must decode to a JSON object")
            _print_json(score_research_object_provenance_case(provenance_case))
            return 0

    if args.area == "neutrino":
        if args.command == "guardrail-check":
            payload = _load_json_value(args.input)
            if not isinstance(payload, dict):
                raise ValueError("--input must decode to a JSON object")
            result = classify_neutrino_observation(payload)
            _print_json(result)
            return 0 if result["Adm_lex"] else 1
        if args.command == "chapter14-threshold-check":
            payload = _load_json_value(args.input)
            if not isinstance(payload, dict):
                raise ValueError("--input must decode to a JSON object")
            result = classify_chapter14_threshold(payload)
            _print_json(result)
            return 0 if result["Adm_lex"] else 1

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
    if args.area == "taxonomy" and args.command == "phylo-plithogenic":
        if args.phylo_plithogenic_command == "demo":
            _print_json(build_tilapia_style_demo_packet().score())
            return 0
        if args.phylo_plithogenic_command == "score":
            packet = _load_json_value(args.packet)
            if not isinstance(packet, dict):
                raise ValueError("--packet must decode to a JSON object")
            _print_json(score_phylo_plithogenic_packet(packet))
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
                    H_lex=args.H_lex,
                    G_lex=args.G_lex,
                    I_lexicon=args.I_lexicon,
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
