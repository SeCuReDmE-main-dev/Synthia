"""Strict Synthia-first document pipeline for taxonomy review packets."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shlex
from typing import Any, Mapping, Sequence
import xml.etree.ElementTree as ET
import zipfile

from .lexicon import ILexicon, LexiconDomain, LexiconNode, TIF, seed_base_lexicon
from .safety import HIERARCHY, looks_private_path

DONE_BY_SYNTHIA = "done_by_synthia"
DONE_BY_CODEX = "done_by_codex"
MANUAL_FALLBACK = "manual_fallback"
HANDOFF_REQUIRED = "handoff_required"
BLOCKED = "blocked"

INGEST_STAGE = "ingest"
CLASSIFY_STAGE = "classify"
LEXICON_STAGE = "lexicon"
ANNEX_STAGE = "annex"
HANDOFF_STAGE = "handoff"

STAGE_ORDER = (INGEST_STAGE, CLASSIFY_STAGE, LEXICON_STAGE, ANNEX_STAGE, HANDOFF_STAGE)
SUPPORTED_INPUT_SUFFIXES = {".docx": "docx", ".md": "md", ".txt": "txt"}
WORD_NAMESPACE = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
STOPWORDS = {
    "about",
    "after",
    "before",
    "between",
    "codex",
    "document",
    "documents",
    "final",
    "first",
    "from",
    "have",
    "human",
    "into",
    "keeps",
    "lane",
    "must",
    "only",
    "review",
    "source",
    "sources",
    "supports",
    "synthia",
    "that",
    "their",
    "there",
    "these",
    "this",
    "through",
    "traceability",
    "under",
    "with",
}
SOURCE_BOUNDARY = (
    "Formal nomenclatural authority remains governed by the relevant Code and human review."
)
AI_BOUNDARY = (
    "Synthia performs ingestion, classification, lexicon extraction, and annex generation only; "
    "it does not translate, style-polish, export DOCX, or claim autonomous authority."
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class DocumentProfile:
    name: str
    description: str
    supported_formats: tuple[str, ...]
    supported_domains: tuple[str, ...]
    domain_terms: Mapping[str, tuple[str, ...]]
    annex_title: str
    allowed_codex_actions: tuple[str, ...]


@dataclass(frozen=True)
class OwnershipRecord:
    actor: str
    status: str

    def as_dict(self) -> dict[str, str]:
        return {"actor": self.actor, "status": self.status}


@dataclass(frozen=True)
class LexiconHit:
    term: str
    domain: str
    source_ids: tuple[str, ...]
    block_ids: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, object]:
        return {
            "term": self.term,
            "domain": self.domain,
            "source_ids": list(self.source_ids),
            "block_ids": list(self.block_ids),
        }


@dataclass(frozen=True)
class AnnexSection:
    title: str
    lines: tuple[str, ...]


@dataclass
class DocumentBlock:
    block_id: str
    index: int
    raw_text: str
    cleaned_text: str
    source_path: str
    source_format: str
    char_count: int
    heading_hint: str = ""
    candidate_terms: tuple[str, ...] = ()
    matched_terms: tuple[LexiconHit, ...] = ()
    matched_domains: tuple[str, ...] = ()
    dominant_domain: str = LexiconDomain.GENERAL.value
    unresolved: bool = True
    classification_profile: Mapping[str, object] | None = None

    def as_dict(self) -> dict[str, object]:
        return {
            "block_id": self.block_id,
            "index": self.index,
            "raw_text": self.raw_text,
            "cleaned_text": self.cleaned_text,
            "source_path": self.source_path,
            "source_format": self.source_format,
            "char_count": self.char_count,
            "heading_hint": self.heading_hint,
            "candidate_terms": list(self.candidate_terms),
            "matched_terms": [hit.as_dict() for hit in self.matched_terms],
            "matched_domains": list(self.matched_domains),
            "dominant_domain": self.dominant_domain,
            "unresolved": self.unresolved,
            "classification_profile": dict(self.classification_profile or {}),
        }


@dataclass(frozen=True)
class DocumentStageRecord:
    stage: str
    status: str
    actor: str
    message: str
    details: Mapping[str, object] = field(default_factory=dict)
    timestamp: str = field(default_factory=_utc_now)

    def as_dict(self) -> dict[str, object]:
        return {
            "timestamp": self.timestamp,
            "stage": self.stage,
            "status": self.status,
            "actor": self.actor,
            "message": self.message,
            "details": dict(self.details),
        }


@dataclass(frozen=True)
class DocumentBundle:
    run_id: str
    private_root: Path
    bundle_dir: Path
    decision_path: Path
    stage_log_path: Path
    normalized_document_path: Path
    block_map_path: Path
    lexicon_summary_path: Path
    annex_path: Path
    handoff_path: Path

    @classmethod
    def from_private_org(cls, private_org: str | Path, run_id: str) -> "DocumentBundle":
        private_root = Path(private_org).expanduser().resolve()
        bundle_dir = private_root / "02_taxonomy_lexicon_model" / "document_runs" / run_id
        return cls(
            run_id=run_id,
            private_root=private_root,
            bundle_dir=bundle_dir,
            decision_path=bundle_dir / "decision.json",
            stage_log_path=bundle_dir / "stage_log.jsonl",
            normalized_document_path=bundle_dir / "normalized_document.json",
            block_map_path=bundle_dir / "block_map.json",
            lexicon_summary_path=bundle_dir / "lexicon_summary.json",
            annex_path=bundle_dir / "taxonomy_annex.md",
            handoff_path=bundle_dir / "handoff.json",
        )

    def artifact_paths(self) -> dict[str, str]:
        return {
            "bundle_dir": self.bundle_dir.relative_to(self.private_root).as_posix(),
            "decision": self.decision_path.relative_to(self.private_root).as_posix(),
            "stage_log": self.stage_log_path.relative_to(self.private_root).as_posix(),
            "normalized_document": self.normalized_document_path.relative_to(self.private_root).as_posix(),
            "block_map": self.block_map_path.relative_to(self.private_root).as_posix(),
            "lexicon_summary": self.lexicon_summary_path.relative_to(self.private_root).as_posix(),
            "taxonomy_annex": self.annex_path.relative_to(self.private_root).as_posix(),
            "handoff": self.handoff_path.relative_to(self.private_root).as_posix(),
        }


@dataclass(frozen=True)
class DocumentRunDecision:
    run_id: str
    command: str
    profile: str
    input_path: str
    input_format: str
    overall_status: str
    stop_stage: str
    next_actor: str
    artifact_paths: Mapping[str, str]
    ownership: Mapping[str, OwnershipRecord]
    public_summary: Mapping[str, object]
    message: str

    def as_dict(self) -> dict[str, object]:
        return {
            "run_id": self.run_id,
            "command": self.command,
            "profile": self.profile,
            "input_path": self.input_path,
            "input_format": self.input_format,
            "overall_status": self.overall_status,
            "stop_stage": self.stop_stage,
            "next_actor": self.next_actor,
            "artifact_paths": dict(self.artifact_paths),
            "ownership": {stage: owner.as_dict() for stage, owner in self.ownership.items()},
            "public_summary": dict(self.public_summary),
            "message": self.message,
        }


class PipelineError(RuntimeError):
    def __init__(
        self,
        status: str,
        stage: str,
        message: str,
        *,
        next_actor: str = "codex",
        details: Mapping[str, object] | None = None,
    ) -> None:
        super().__init__(message)
        self.status = status
        self.stage = stage
        self.message = message
        self.next_actor = next_actor
        self.details = dict(details or {})


def available_document_profiles() -> dict[str, DocumentProfile]:
    return {
        "taxonomy-review": DocumentProfile(
            name="taxonomy-review",
            description="Taxonomy, PhyloCode, conservation, and AI-governance review packet generation.",
            supported_formats=("docx", "md", "txt"),
            supported_domains=(
                LexiconDomain.TAXONOMY.value,
                LexiconDomain.PHYLOCODE_NOMENCLATURE.value,
                LexiconDomain.CONSERVATION.value,
                LexiconDomain.AI_GOVERNANCE.value,
                LexiconDomain.GENERAL.value,
            ),
            domain_terms={
                LexiconDomain.TAXONOMY.value: (
                    "species as systems",
                    "taxonomy",
                    "taxonomic",
                    "species concept",
                    "species concepts",
                ),
                LexiconDomain.PHYLOCODE_NOMENCLATURE.value: (
                    "taxonomic memory repair",
                    "phylocode",
                    "nomenclature",
                    "redescription",
                    "clade",
                ),
                LexiconDomain.CONSERVATION.value: (
                    "integral conservation",
                    "conservation",
                    "habitat monitoring",
                    "conservation report",
                ),
                LexiconDomain.AI_GOVERNANCE.value: (
                    "ai-assisted traceability",
                    "human review",
                    "source-linked evidence",
                    "traceability",
                    "review boundary",
                ),
            },
            annex_title="Synthia Taxonomy Review Annex",
            allowed_codex_actions=(
                "assemble final document",
                "translate final prose",
                "style-polish the handoff package",
                "export or convert downstream formats",
            ),
        )
    }


def run_document_pipeline(
    *,
    input_path: str | Path,
    profile_name: str,
    private_org: str | Path,
    command: Sequence[str] | str,
    emit_lexicon: bool = False,
    emit_annex: bool = False,
) -> tuple[dict[str, object], int]:
    profiles = available_document_profiles()
    input_file = Path(input_path).expanduser()
    resolved_input = input_file.resolve()
    profile = profiles.get(profile_name)
    input_format = _format_from_suffix(input_file.suffix)
    run_id = _build_run_id(resolved_input, profile_name)
    bundle = DocumentBundle.from_private_org(private_org, run_id)
    bundle.bundle_dir.mkdir(parents=True, exist_ok=True)
    command_text = _command_text(command)
    effective_profile = profile_name
    _initialize_bundle_placeholders(bundle, run_id, effective_profile, str(resolved_input), input_format)
    public_input_path = _public_input_path(resolved_input)

    if profile is None:
        error = PipelineError(
            HANDOFF_REQUIRED,
            INGEST_STAGE,
            f"Synthia does not support the requested document profile: {profile_name}.",
            details={"reason": "unsupported_profile", "supported_profiles": sorted(profiles)},
        )
        return _finalize_failure(
            bundle,
            command_text=_public_command(public_input_path, profile_name, emit_lexicon, emit_annex),
            profile_name=profile_name,
            input_path=public_input_path,
            input_format=input_format,
            error=error,
            records=[],
            domain_counts={},
            block_count=0,
            unresolved_block_count=0,
        )

    current_stage = INGEST_STAGE
    records: list[DocumentStageRecord] = []
    blocks: list[DocumentBlock] = []
    domain_counts: dict[str, int] = {}
    unresolved_block_count = 0
    effective_emit_lexicon = emit_lexicon or profile.name == "taxonomy-review"
    effective_emit_annex = emit_annex or profile.name == "taxonomy-review"

    try:
        source_meta = _validate_input(input_file, profile)
        raw_blocks = _extract_blocks(input_file, source_meta["input_format"])
        blocks = _normalize_blocks(raw_blocks, str(resolved_input), source_meta["input_format"])
        if not blocks:
            raise PipelineError(
                BLOCKED,
                INGEST_STAGE,
                "Synthia could not extract any document blocks from the input.",
                details={"reason": "no_extractable_text"},
            )
        normalized_payload = {
            "run_id": run_id,
            "profile": profile.name,
            "input_path": str(resolved_input),
            "input_format": source_meta["input_format"],
            "human_review_required": True,
            "block_count": len(blocks),
            "blocks": [block.as_dict() for block in blocks],
            "hierarchy": HIERARCHY,
        }
        _write_json(bundle.normalized_document_path, normalized_payload)
        _record_stage(
            bundle,
            records,
            INGEST_STAGE,
            DONE_BY_SYNTHIA,
            "Synthia ingested and normalized the document input.",
            {"block_count": len(blocks), **source_meta},
        )

        current_stage = CLASSIFY_STAGE
        classified_blocks = _classify_blocks(blocks, profile)
        domain_counts = dict(Counter(block.dominant_domain for block in classified_blocks))
        unresolved_block_count = sum(1 for block in classified_blocks if block.unresolved)
        _write_json(
            bundle.block_map_path,
            {
                "run_id": run_id,
                "profile": profile.name,
                "input_path": str(resolved_input),
                "input_format": source_meta["input_format"],
                "dominant_domain_counts": domain_counts,
                "unresolved_block_count": unresolved_block_count,
                "blocks": [_block_map_entry(block) for block in classified_blocks],
                "hierarchy": HIERARCHY,
            },
        )
        _record_stage(
            bundle,
            records,
            CLASSIFY_STAGE,
            DONE_BY_SYNTHIA,
            "Synthia classified document blocks into the configured review domains.",
            {
                "block_count": len(classified_blocks),
                "dominant_domain_counts": domain_counts,
                "unresolved_block_count": unresolved_block_count,
            },
        )

        current_stage = LEXICON_STAGE
        lexicon_summary = _build_lexicon_summary(run_id, profile, classified_blocks)
        if effective_emit_lexicon:
            _write_json(bundle.lexicon_summary_path, lexicon_summary)
        _record_stage(
            bundle,
            records,
            LEXICON_STAGE,
            DONE_BY_SYNTHIA,
            "Synthia aggregated matched terms, unresolved candidates, and source-linked lexicon coverage.",
            {
                "term_count": lexicon_summary["term_count"],
                "unresolved_candidate_term_count": len(lexicon_summary["unresolved_candidate_terms"]),
            },
        )

        current_stage = ANNEX_STAGE
        annex_text = _render_annex(
            run_id=run_id,
            profile=profile,
            input_path=str(resolved_input),
            input_format=source_meta["input_format"],
            blocks=classified_blocks,
            domain_counts=domain_counts,
            unresolved_block_count=unresolved_block_count,
        )
        if effective_emit_annex:
            bundle.annex_path.write_text(annex_text, encoding="utf-8")
        _record_stage(
            bundle,
            records,
            ANNEX_STAGE,
            DONE_BY_SYNTHIA,
            "Synthia generated the taxonomy review annex and preserved the authority boundary.",
            {"annex_path": str(bundle.annex_path)},
        )

        current_stage = HANDOFF_STAGE
        _record_stage(
            bundle,
            records,
            HANDOFF_STAGE,
            DONE_BY_SYNTHIA,
            "Synthia emitted the final handoff bundle for Codex-owned downstream work.",
            {"next_actor": "codex"},
        )

        ownership = _build_ownership(records)
        public_command = _public_command(public_input_path, profile.name, effective_emit_lexicon, effective_emit_annex)
        handoff_payload = _build_handoff(
            run_id=run_id,
            profile=profile,
            overall_status=DONE_BY_SYNTHIA,
            stop_stage=HANDOFF_STAGE,
            next_actor="codex",
            input_path=public_input_path,
            input_format=source_meta["input_format"],
            artifact_paths=bundle.artifact_paths(),
            records=records,
            message="Synthia completed its owned stages and prepared a bounded Codex handoff.",
            reason="synthia_owned_stages_complete",
            command=public_command,
            ownership=ownership,
        )
        _write_json(bundle.handoff_path, handoff_payload)

        decision = DocumentRunDecision(
            run_id=run_id,
            command=public_command,
            profile=profile.name,
            input_path=public_input_path,
            input_format=source_meta["input_format"],
            overall_status=DONE_BY_SYNTHIA,
            stop_stage=HANDOFF_STAGE,
            next_actor="codex",
            artifact_paths=bundle.artifact_paths(),
            ownership=ownership,
            public_summary=_public_summary(
                block_count=len(classified_blocks),
                domain_counts=domain_counts,
                unresolved_block_count=unresolved_block_count,
                artifact_paths=bundle.artifact_paths(),
            ),
            message="Synthia completed ingestion, classification, lexicon extraction, annex generation, and handoff emission.",
        )
        _write_json(bundle.decision_path, decision.as_dict())
        return decision.as_dict(), _exit_code_for_status(DONE_BY_SYNTHIA)
    except PipelineError as error:
        return _finalize_failure(
            bundle,
            command_text=command_text,
            profile_name=profile.name,
            input_path=str(resolved_input),
            input_format=input_format,
            error=error,
            records=records,
            domain_counts=domain_counts,
            block_count=len(blocks),
            unresolved_block_count=unresolved_block_count,
        )
    except Exception as exc:  # pragma: no cover - defensive fail-closed path
        error = PipelineError(
            BLOCKED,
            current_stage,
            f"Synthia hit an unexpected error while running the document pipeline: {exc}",
            details={"reason": "unexpected_error", "error_type": type(exc).__name__},
        )
        return _finalize_failure(
            bundle,
            command_text=command_text,
            profile_name=profile.name,
            input_path=str(resolved_input),
            input_format=input_format,
            error=error,
            records=records,
            domain_counts=domain_counts,
            block_count=len(blocks),
            unresolved_block_count=unresolved_block_count,
        )


def _finalize_failure(
    bundle: DocumentBundle,
    *,
    command_text: str,
    profile_name: str,
    input_path: str,
    input_format: str,
    error: PipelineError,
    records: list[DocumentStageRecord],
    domain_counts: Mapping[str, int],
    block_count: int,
    unresolved_block_count: int,
) -> tuple[dict[str, object], int]:
    _record_stage(bundle, records, error.stage, error.status, error.message, error.details)
    ownership = _build_ownership(records)
    handoff_payload = _build_handoff(
        run_id=bundle.run_id,
        profile=available_document_profiles().get(profile_name) or available_document_profiles()["taxonomy-review"],
        overall_status=error.status,
        stop_stage=error.stage,
        next_actor=error.next_actor,
        input_path=input_path,
        input_format=input_format,
        artifact_paths=bundle.artifact_paths(),
        records=records,
        message=error.message,
        reason=str(error.details.get("reason", "handoff_required")),
        command=command_text,
        ownership=ownership,
    )
    _write_json(bundle.handoff_path, handoff_payload)
    _record_stage(
        bundle,
        records,
        HANDOFF_STAGE,
        DONE_BY_SYNTHIA,
        "Synthia emitted a fail-closed handoff bundle after stopping the document lane.",
        {"next_actor": error.next_actor, "stop_stage": error.stage},
    )
    decision = DocumentRunDecision(
        run_id=bundle.run_id,
        command=command_text,
        profile=profile_name,
        input_path=input_path,
        input_format=input_format,
        overall_status=error.status,
        stop_stage=error.stage,
        next_actor=error.next_actor,
        artifact_paths=bundle.artifact_paths(),
        ownership=ownership,
        public_summary=_public_summary(
            block_count=block_count,
            domain_counts=dict(domain_counts),
            unresolved_block_count=unresolved_block_count,
            artifact_paths=bundle.artifact_paths(),
        ),
        message=error.message,
    )
    _write_json(bundle.decision_path, decision.as_dict())
    return decision.as_dict(), _exit_code_for_status(error.status)


def _build_run_id(input_path: Path, profile_name: str) -> str:
    try:
        stat = input_path.stat()
        fingerprint = f"{input_path}|{profile_name}|{stat.st_size}|{int(stat.st_mtime)}"
    except OSError:
        fingerprint = f"{input_path}|{profile_name}|missing"
    return hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()[:12]


def _initialize_bundle_placeholders(
    bundle: DocumentBundle,
    run_id: str,
    profile_name: str,
    input_path: str,
    input_format: str,
) -> None:
    _write_json(
        bundle.normalized_document_path,
        {
            "run_id": run_id,
            "profile": profile_name,
            "input_path": input_path,
            "input_format": input_format,
            "status": "pending",
            "blocks": [],
            "hierarchy": HIERARCHY,
        },
    )
    _write_json(
        bundle.block_map_path,
        {
            "run_id": run_id,
            "profile": profile_name,
            "input_path": input_path,
            "input_format": input_format,
            "status": "pending",
            "blocks": [],
            "hierarchy": HIERARCHY,
        },
    )
    _write_json(
        bundle.lexicon_summary_path,
        {
            "run_id": run_id,
            "profile": profile_name,
            "status": "pending",
            "terms": [],
            "unresolved_blocks": [],
            "unresolved_candidate_terms": [],
            "hierarchy": HIERARCHY,
        },
    )
    bundle.annex_path.write_text(
        "# Synthia Taxonomy Review Annex\n\nPending generation.\n",
        encoding="utf-8",
    )


def _validate_input(input_path: Path, profile: DocumentProfile) -> dict[str, object]:
    if not input_path.exists():
        raise PipelineError(
            HANDOFF_REQUIRED,
            INGEST_STAGE,
            f"Synthia could not read the requested input because it does not exist: {input_path}",
            details={"reason": "missing_input"},
        )
    if input_path.is_dir():
        raise PipelineError(
            HANDOFF_REQUIRED,
            INGEST_STAGE,
            f"Synthia expects a single document file, not a directory: {input_path}",
            details={"reason": "directory_input"},
        )
    input_format = _format_from_suffix(input_path.suffix)
    if input_format not in profile.supported_formats:
        raise PipelineError(
            HANDOFF_REQUIRED,
            INGEST_STAGE,
            f"Synthia does not support the input format `{input_path.suffix or '<none>'}` for the document lane.",
            details={
                "reason": "unsupported_format",
                "supported_formats": list(profile.supported_formats),
                "received_suffix": input_path.suffix,
            },
        )
    stat = input_path.stat()
    return {
        "input_format": input_format,
        "input_size": stat.st_size,
        "input_mtime": int(stat.st_mtime),
        "supported_formats": list(profile.supported_formats),
    }


def _extract_blocks(input_path: Path, input_format: str) -> list[dict[str, str]]:
    if input_format == "docx":
        return _extract_docx_blocks(input_path)
    text = input_path.read_text(encoding="utf-8", errors="replace")
    if input_format == "md":
        return _extract_markdown_blocks(text)
    return _extract_text_blocks(text)


def _extract_docx_blocks(input_path: Path) -> list[dict[str, str]]:
    try:
        with zipfile.ZipFile(input_path) as archive:
            raw_xml = archive.read("word/document.xml")
    except (KeyError, zipfile.BadZipFile, OSError) as exc:
        raise PipelineError(
            HANDOFF_REQUIRED,
            INGEST_STAGE,
            f"Synthia could not parse the DOCX input: {input_path}",
            details={"reason": "docx_read_error", "error_type": type(exc).__name__},
        ) from exc

    try:
        root = ET.fromstring(raw_xml)
    except ET.ParseError as exc:
        raise PipelineError(
            HANDOFF_REQUIRED,
            INGEST_STAGE,
            f"Synthia could not parse the DOCX XML payload: {input_path}",
            details={"reason": "docx_xml_parse_error"},
        ) from exc

    blocks: list[dict[str, str]] = []
    for paragraph in root.findall(".//w:body/w:p", WORD_NAMESPACE):
        text_parts: list[str] = []
        for node in paragraph.iter():
            if node.tag == f"{{{WORD_NAMESPACE['w']}}}t" and node.text:
                text_parts.append(node.text)
            elif node.tag == f"{{{WORD_NAMESPACE['w']}}}tab":
                text_parts.append("\t")
            elif node.tag == f"{{{WORD_NAMESPACE['w']}}}br":
                text_parts.append("\n")
        raw_text = "".join(text_parts)
        cleaned_text = _collapse_whitespace(raw_text)
        style = paragraph.find("./w:pPr/w:pStyle", WORD_NAMESPACE)
        style_value = ""
        if style is not None:
            style_value = style.attrib.get(f"{{{WORD_NAMESPACE['w']}}}val", "")
        heading_hint = cleaned_text if "heading" in style_value.lower() else ""
        blocks.append({"raw_text": raw_text, "cleaned_text": cleaned_text, "heading_hint": heading_hint})
    return blocks


def _extract_markdown_blocks(text: str) -> list[dict[str, str]]:
    blocks: list[dict[str, str]] = []
    paragraph: list[str] = []
    fenced = False
    for raw_line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        stripped = raw_line.strip()
        if stripped.startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        if re.match(r"^#{1,6}\s+", stripped):
            if paragraph:
                joined = "\n".join(paragraph)
                blocks.append(
                    {
                        "raw_text": joined,
                        "cleaned_text": _collapse_whitespace(joined),
                        "heading_hint": "",
                    }
                )
                paragraph = []
            heading_text = re.sub(r"^#{1,6}\s+", "", stripped)
            blocks.append(
                {
                    "raw_text": raw_line,
                    "cleaned_text": _collapse_whitespace(heading_text),
                    "heading_hint": _collapse_whitespace(heading_text),
                }
            )
            continue
        if not stripped:
            if paragraph:
                joined = "\n".join(paragraph)
                blocks.append(
                    {
                        "raw_text": joined,
                        "cleaned_text": _collapse_whitespace(joined),
                        "heading_hint": "",
                    }
                )
                paragraph = []
            continue
        paragraph.append(raw_line)
    if paragraph:
        joined = "\n".join(paragraph)
        blocks.append({"raw_text": joined, "cleaned_text": _collapse_whitespace(joined), "heading_hint": ""})
    return blocks


def _extract_text_blocks(text: str) -> list[dict[str, str]]:
    blocks: list[dict[str, str]] = []
    for chunk in re.split(r"\n\s*\n", text.replace("\r\n", "\n").replace("\r", "\n")):
        cleaned = _collapse_whitespace(chunk)
        blocks.append({"raw_text": chunk, "cleaned_text": cleaned, "heading_hint": ""})
    return blocks


def _normalize_blocks(
    raw_blocks: Sequence[Mapping[str, str]],
    source_path: str,
    source_format: str,
) -> list[DocumentBlock]:
    blocks: list[DocumentBlock] = []
    for raw_block in raw_blocks:
        cleaned = _collapse_whitespace(str(raw_block.get("cleaned_text", "")))
        if not cleaned:
            continue
        block_id = f"blk-{len(blocks) + 1:04d}"
        blocks.append(
            DocumentBlock(
                block_id=block_id,
                index=len(blocks),
                raw_text=str(raw_block.get("raw_text", cleaned)),
                cleaned_text=cleaned,
                source_path=source_path,
                source_format=source_format,
                char_count=len(cleaned),
                heading_hint=_collapse_whitespace(str(raw_block.get("heading_hint", ""))),
            )
        )
    return blocks


def _build_document_lexicon(profile: DocumentProfile) -> ILexicon:
    registry = seed_base_lexicon()
    existing = {(node.term.lower(), node.domain) for node in registry.nodes.values()}
    for domain, terms in profile.domain_terms.items():
        for term in terms:
            key = (term.lower(), domain)
            if key in existing:
                continue
            registry.add_node(
                LexiconNode(
                    term=term,
                    domain=domain,
                    definition=f"Document pipeline profile term for {domain}: {term}",
                    source_ids=(f"document.profile.{profile.name}",),
                    tif=TIF(T=0.8, I=0.15, F=0.05, I_system=0.15),
                )
            )
            existing.add(key)
    return registry


def _classify_blocks(blocks: Sequence[DocumentBlock], profile: DocumentProfile) -> list[DocumentBlock]:
    registry = _build_document_lexicon(profile)
    ordered_domains = {domain: index for index, domain in enumerate(profile.supported_domains)}
    classified: list[DocumentBlock] = []
    for block in blocks:
        lowered = block.cleaned_text.lower()
        hits: list[LexiconHit] = []
        seen_terms: set[tuple[str, str]] = set()
        for node in registry.nodes.values():
            term = node.term.strip()
            if not term:
                continue
            if term.lower() not in lowered:
                continue
            key = (node.term, node.domain)
            if key in seen_terms:
                continue
            seen_terms.add(key)
            hits.append(LexiconHit(term=node.term, domain=node.domain, source_ids=node.source_ids, block_ids=(block.block_id,)))
        hits.sort(key=lambda hit: (ordered_domains.get(hit.domain, len(ordered_domains)), hit.term.lower()))
        matched_domains = tuple(dict.fromkeys(hit.domain for hit in hits))
        candidate_terms = ()
        if not hits:
            dominant_domain = LexiconDomain.GENERAL.value
            unresolved = True
            classification_profile = None
            candidate_terms = tuple(_extract_candidate_terms(block.cleaned_text))
        else:
            dominant_domain = _dominant_domain(hits, profile.supported_domains)
            unresolved = len(matched_domains) != 1
            candidate_terms = tuple(_extract_candidate_terms(block.cleaned_text)) if unresolved else ()
            profile_payload = registry.classify_text(block.cleaned_text, dominant_domain)
            classification_profile = profile_payload.get("i_lexicon_classification")
        classified.append(
            DocumentBlock(
                block_id=block.block_id,
                index=block.index,
                raw_text=block.raw_text,
                cleaned_text=block.cleaned_text,
                source_path=block.source_path,
                source_format=block.source_format,
                char_count=block.char_count,
                heading_hint=block.heading_hint,
                candidate_terms=candidate_terms,
                matched_terms=tuple(hits),
                matched_domains=matched_domains,
                dominant_domain=dominant_domain,
                unresolved=unresolved,
                classification_profile=classification_profile,
            )
        )
    return classified


def _dominant_domain(hits: Sequence[LexiconHit], supported_domains: Sequence[str]) -> str:
    counts = Counter(hit.domain for hit in hits)
    best_domain = LexiconDomain.GENERAL.value
    best_score = -1
    for domain in supported_domains:
        score = counts.get(domain, 0)
        if score > best_score:
            best_domain = domain
            best_score = score
    return best_domain


def _build_lexicon_summary(
    run_id: str,
    profile: DocumentProfile,
    blocks: Sequence[DocumentBlock],
) -> dict[str, object]:
    terms: dict[tuple[str, str], LexiconHit] = {}
    unresolved_blocks: list[dict[str, object]] = []
    unresolved_terms: set[str] = set()
    for block in blocks:
        for hit in block.matched_terms:
            key = (hit.term, hit.domain)
            if key not in terms:
                terms[key] = LexiconHit(
                    term=hit.term,
                    domain=hit.domain,
                    source_ids=hit.source_ids,
                    block_ids=(block.block_id,),
                )
            else:
                existing = terms[key]
                merged_block_ids = tuple(dict.fromkeys(existing.block_ids + (block.block_id,)))
                terms[key] = LexiconHit(
                    term=existing.term,
                    domain=existing.domain,
                    source_ids=existing.source_ids,
                    block_ids=merged_block_ids,
                )
        if block.unresolved:
            unresolved_blocks.append(
                {
                    "block_id": block.block_id,
                    "dominant_domain": block.dominant_domain,
                    "heading_hint": block.heading_hint,
                    "candidate_terms": list(block.candidate_terms),
                }
            )
            unresolved_terms.update(block.candidate_terms)
    domain_counts = Counter(block.dominant_domain for block in blocks)
    ordered_terms = sorted(terms.values(), key=lambda hit: (profile.supported_domains.index(hit.domain), hit.term.lower()))
    return {
        "run_id": run_id,
        "profile": profile.name,
        "term_count": len(ordered_terms),
        "terms": [term.as_dict() for term in ordered_terms],
        "dominant_domain_counts": dict(domain_counts),
        "unresolved_blocks": unresolved_blocks,
        "unresolved_candidate_terms": sorted(unresolved_terms),
        "human_review_required": True,
        "authority_boundary": SOURCE_BOUNDARY,
        "hierarchy": HIERARCHY,
    }


def _render_annex(
    *,
    run_id: str,
    profile: DocumentProfile,
    input_path: str,
    input_format: str,
    blocks: Sequence[DocumentBlock],
    domain_counts: Mapping[str, int],
    unresolved_block_count: int,
) -> str:
    sections: list[AnnexSection] = [
        AnnexSection(
            title="Run Metadata",
            lines=(
                f"- Run ID: `{run_id}`",
                f"- Profile: `{profile.name}`",
                f"- Input path: `{input_path}`",
                f"- Input format: `{input_format}`",
                f"- Block count: `{len(blocks)}`",
            ),
        ),
        AnnexSection(
            title="Boundary",
            lines=(
                f"- {AI_BOUNDARY}",
                f"- {SOURCE_BOUNDARY}",
                "- Human review required: `true`",
            ),
        ),
        AnnexSection(
            title="Ownership",
            lines=(
                f"- Synthia-owned stages: `{INGEST_STAGE}`, `{CLASSIFY_STAGE}`, `{LEXICON_STAGE}`, `{ANNEX_STAGE}`, `{HANDOFF_STAGE}`",
                "- Codex-owned downstream work begins only after this handoff bundle exists.",
            ),
        ),
        AnnexSection(
            title="Source IDs",
            lines=(
                "- Public seed source IDs remain visible through lexicon summary artifacts.",
                f"- Profile source ID: `document.profile.{profile.name}`",
            ),
        ),
        AnnexSection(
            title="Coverage",
            lines=tuple(
                f"- `{domain}`: `{domain_counts.get(domain, 0)}` block(s)"
                for domain in profile.supported_domains
            )
            + (f"- Unresolved blocks: `{unresolved_block_count}`",),
        ),
    ]
    for domain in profile.supported_domains:
        domain_blocks = [block for block in blocks if block.dominant_domain == domain]
        if not domain_blocks:
            continue
        lines: list[str] = []
        for block in domain_blocks:
            matched_terms = ", ".join(hit.term for hit in block.matched_terms) or "none"
            lines.append(
                f"- `{block.block_id}` matched `{matched_terms}`; unresolved=`{str(block.unresolved).lower()}`"
            )
        sections.append(AnnexSection(title=f"Domain: {domain}", lines=tuple(lines)))
    unresolved_lines = []
    for block in blocks:
        if not block.unresolved:
            continue
        candidates = ", ".join(block.candidate_terms) or "none"
        unresolved_lines.append(
            f"- `{block.block_id}` dominant=`{block.dominant_domain}` candidate_terms=`{candidates}`"
        )
    sections.append(
        AnnexSection(
            title="Unresolved Blocks",
            lines=tuple(unresolved_lines or ("- None",)),
        )
    )
    parts = [f"# {profile.annex_title}", ""]
    for section in sections:
        parts.append(f"## {section.title}")
        parts.extend(section.lines)
        parts.append("")
    parts.append(f"Hierarchy: `{HIERARCHY}`")
    parts.append("")
    return "\n".join(parts)


def _build_handoff(
    *,
    run_id: str,
    profile: DocumentProfile,
    overall_status: str,
    stop_stage: str,
    next_actor: str,
    input_path: str,
    input_format: str,
    artifact_paths: Mapping[str, str],
    records: Sequence[DocumentStageRecord],
    message: str,
    reason: str,
    command: str,
    ownership: Mapping[str, OwnershipRecord],
) -> dict[str, object]:
    next_steps = list(profile.allowed_codex_actions) if overall_status == DONE_BY_SYNTHIA else _failure_next_steps(reason)
    return {
        "run_id": run_id,
        "command": command,
        "profile": profile.name,
        "overall_status": overall_status,
        "stop_stage": stop_stage,
        "next_actor": next_actor,
        "input_path": input_path,
        "input_format": input_format,
        "reason": reason,
        "message": message,
        "next_steps": next_steps,
        "allowed_codex_actions": list(profile.allowed_codex_actions),
        "forbidden_claims": [
            "Codex must not claim Synthia completed unsupported stages.",
            "Neither Synthia nor Codex may claim formal nomenclatural authority or autonomous scientific authority.",
        ],
        "completed_stage_records": [record.as_dict() for record in records],
        "ownership": {stage: owner.as_dict() for stage, owner in ownership.items()},
        "artifact_paths": dict(artifact_paths),
        "human_review_required": True,
        "authority_boundary": SOURCE_BOUNDARY,
    }


def _failure_next_steps(reason: str) -> list[str]:
    if reason == "unsupported_format":
        return [
            "Convert the source into `.docx`, `.txt`, or `.md`.",
            "Re-run the Synthia document pipeline with the converted file.",
            "Use Codex only after the Synthia handoff bundle exists.",
        ]
    if reason == "missing_input":
        return [
            "Restore or provide the missing source document.",
            "Re-run the Synthia document pipeline with the corrected path.",
        ]
    if reason == "no_extractable_text":
        return [
            "Inspect the source for empty or image-only content.",
            "Extract usable text before re-running Synthia.",
            "If manual extraction is required, document that Codex took over after Synthia stopped.",
        ]
    if reason.startswith("docx_"):
        return [
            "Inspect the DOCX structure or convert the document to `.md` or `.txt`.",
            "Re-run the Synthia document pipeline after conversion or repair.",
        ]
    return [
        "Inspect the handoff bundle and stop reason.",
        "Repair the blocked stage or hand the task to Codex with explicit ownership disclosure.",
    ]


def _public_summary(
    *,
    block_count: int,
    domain_counts: Mapping[str, int],
    unresolved_block_count: int,
    artifact_paths: Mapping[str, str],
) -> dict[str, object]:
    return {
        "block_count": block_count,
        "dominant_domain_counts": dict(domain_counts),
        "unresolved_block_count": unresolved_block_count,
        "generated_artifacts": list(artifact_paths),
        "human_review_required": True,
        "hierarchy": HIERARCHY,
    }


def _build_ownership(records: Sequence[DocumentStageRecord]) -> dict[str, OwnershipRecord]:
    final_status_by_stage = {record.stage: record.status for record in records}
    ownership: dict[str, OwnershipRecord] = {}
    handoff_started = False
    for stage in STAGE_ORDER:
        if stage in final_status_by_stage:
            ownership[stage] = OwnershipRecord(actor="synthia", status=final_status_by_stage[stage])
            if final_status_by_stage[stage] in {HANDOFF_REQUIRED, BLOCKED, MANUAL_FALLBACK}:
                handoff_started = True
            continue
        if handoff_started:
            ownership[stage] = OwnershipRecord(actor="codex", status=HANDOFF_REQUIRED)
        else:
            ownership[stage] = OwnershipRecord(actor="codex", status=HANDOFF_REQUIRED)
    return ownership


def _block_map_entry(block: DocumentBlock) -> dict[str, object]:
    return {
        "block_id": block.block_id,
        "index": block.index,
        "heading_hint": block.heading_hint,
        "char_count": block.char_count,
        "candidate_terms": list(block.candidate_terms),
        "matched_terms": [hit.as_dict() for hit in block.matched_terms],
        "matched_domains": list(block.matched_domains),
        "dominant_domain": block.dominant_domain,
        "unresolved": block.unresolved,
        "classification_profile": dict(block.classification_profile or {}),
    }


def _extract_candidate_terms(text: str, limit: int = 5) -> list[str]:
    candidates: list[str] = []
    for token in re.findall(r"[A-Za-z][A-Za-z-]{3,}", text.lower()):
        if token in STOPWORDS or token in candidates:
            continue
        candidates.append(token)
        if len(candidates) >= limit:
            break
    return candidates


def _record_stage(
    bundle: DocumentBundle,
    records: list[DocumentStageRecord],
    stage: str,
    status: str,
    message: str,
    details: Mapping[str, object] | None = None,
) -> None:
    record = DocumentStageRecord(stage=stage, status=status, actor="synthia", message=message, details=dict(details or {}))
    records.append(record)
    with bundle.stage_log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record.as_dict(), ensure_ascii=False) + "\n")


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _collapse_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _format_from_suffix(suffix: str) -> str:
    return SUPPORTED_INPUT_SUFFIXES.get(suffix.lower(), suffix.lower().lstrip(".") or "unknown")


def _exit_code_for_status(status: str) -> int:
    if status in {DONE_BY_SYNTHIA, DONE_BY_CODEX}:
        return 0
    if status in {HANDOFF_REQUIRED, MANUAL_FALLBACK}:
        return 2
    return 3


def _command_text(command: Sequence[str] | str) -> str:
    if isinstance(command, str):
        return command
    return f"python -m synthia_core.cli {shlex.join(list(command))}"


def _public_input_path(path: Path) -> str:
    resolved = path.resolve()
    name_only = resolved.name or "document"
    if looks_private_path(resolved):
        return "[private-input]"
    try:
        relative = resolved.relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        relative = name_only
    candidate = relative if not looks_private_path(relative) else name_only
    if looks_private_path(candidate):
        return "[private-input]"
    return candidate


def _public_command(input_path: str, profile_name: str, emit_lexicon: bool, emit_annex: bool) -> str:
    parts = [
        "python",
        "-m",
        "synthia_core.cli",
        "document",
        "pipeline",
        "--input",
        input_path,
        "--profile",
        profile_name,
        "--private-org",
        "[private-org]",
    ]
    if emit_lexicon:
        parts.append("--emit-lexicon")
    if emit_annex:
        parts.append("--emit-annex")
    return shlex.join(parts)
