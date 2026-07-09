import json
from pathlib import Path
import shutil

import pytest

from synthia_core.cli import main
from synthia_core.document_pipeline import BLOCKED, DONE_BY_SYNTHIA, HANDOFF_REQUIRED


FIXTURES = Path(__file__).resolve().parent / "fixtures"


def _artifact_path(payload: dict[str, object], private_org: Path, key: str) -> Path:
    return private_org.resolve() / Path(payload["artifact_paths"][key])


def _artifact_json(payload: dict[str, object], private_org: Path, key: str) -> dict[str, object]:
    path = _artifact_path(payload, private_org, key)
    return json.loads(path.read_text(encoding="utf-8"))


def _artifact_text(payload: dict[str, object], private_org: Path, key: str) -> str:
    path = _artifact_path(payload, private_org, key)
    return path.read_text(encoding="utf-8")


def _assert_bundle_paths(payload: dict[str, object], private_org: Path) -> None:
    required = (
        "bundle_dir",
        "decision",
        "stage_log",
        "normalized_document",
        "block_map",
        "lexicon_summary",
        "taxonomy_annex",
        "handoff",
    )
    private_root = private_org.resolve()
    for key in required:
        relpath = Path(payload["artifact_paths"][key])
        assert not relpath.is_absolute()
        path = private_root / relpath
        assert path.exists()
        assert path.is_relative_to(private_root)


@pytest.mark.parametrize(
    ("fixture_name", "expected_format"),
    [
        ("document_pipeline_taxonomy_review.md", "md"),
        ("document_pipeline_taxonomy_review.txt", "txt"),
        ("document_pipeline_taxonomy_review.docx", "docx"),
    ],
)
def test_document_pipeline_success_formats(capsys, tmp_path: Path, fixture_name: str, expected_format: str):
    private_org = tmp_path / "Synthia_organisation"
    fixture = FIXTURES / fixture_name

    code = main(
        [
            "document",
            "pipeline",
            "--input",
            str(fixture),
            "--profile",
            "taxonomy-review",
            "--private-org",
            str(private_org),
        ]
    )

    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["overall_status"] == DONE_BY_SYNTHIA
    assert payload["input_format"] == expected_format
    assert payload["stop_stage"] == "handoff"
    assert payload["next_actor"] == "codex"
    assert payload["public_summary"]["block_count"] > 0
    _assert_bundle_paths(payload, private_org)

    normalized = _artifact_json(payload, private_org, "normalized_document")
    block_map = _artifact_json(payload, private_org, "block_map")
    lexicon_summary = _artifact_json(payload, private_org, "lexicon_summary")
    handoff = _artifact_json(payload, private_org, "handoff")
    annex_text = _artifact_text(payload, private_org, "taxonomy_annex")

    assert normalized["block_count"] >= 4
    assert block_map["dominant_domain_counts"]["taxonomy"] >= 1
    assert block_map["dominant_domain_counts"]["phylocode_nomenclature"] >= 1
    assert block_map["dominant_domain_counts"]["conservation"] >= 1
    assert block_map["dominant_domain_counts"]["ai_governance"] >= 1
    assert lexicon_summary["term_count"] >= 4
    assert handoff["overall_status"] == DONE_BY_SYNTHIA
    assert "Formal nomenclatural authority remains governed" in annex_text
    assert "Synthia-owned stages" in annex_text


def test_document_pipeline_unsupported_input_handoffs(capsys, tmp_path: Path):
    private_org = tmp_path / "Synthia_organisation"
    fixture = FIXTURES / "document_pipeline_unsupported.csv"

    code = main(
        [
            "document",
            "pipeline",
            "--input",
            str(fixture),
            "--profile",
            "taxonomy-review",
            "--private-org",
            str(private_org),
        ]
    )

    assert code == 2
    payload = json.loads(capsys.readouterr().out)
    assert payload["overall_status"] == HANDOFF_REQUIRED
    assert payload["stop_stage"] == "ingest"
    assert payload["message"].startswith("Synthia does not support the input format")
    _assert_bundle_paths(payload, private_org)

    handoff = _artifact_json(payload, private_org, "handoff")
    assert handoff["reason"] == "unsupported_format"
    assert ".docx" in " ".join(handoff["next_steps"])


def test_document_pipeline_empty_input_blocks(capsys, tmp_path: Path):
    private_org = tmp_path / "Synthia_organisation"
    fixture = FIXTURES / "document_pipeline_empty.md"

    code = main(
        [
            "document",
            "pipeline",
            "--input",
            str(fixture),
            "--profile",
            "taxonomy-review",
            "--private-org",
            str(private_org),
        ]
    )

    assert code == 3
    payload = json.loads(capsys.readouterr().out)
    assert payload["overall_status"] == BLOCKED
    assert payload["stop_stage"] == "ingest"
    _assert_bundle_paths(payload, private_org)

    decision = _artifact_json(payload, private_org, "decision")
    stage_log = _artifact_path(payload, private_org, "stage_log").read_text(encoding="utf-8")
    assert decision["message"] == payload["message"]
    assert "no_extractable_text" in stage_log


def test_document_pipeline_stdout_is_public_safe(capsys, tmp_path: Path):
    source_dir = tmp_path / "private_evidence" / "gmail_source"
    source_dir.mkdir(parents=True)
    source = source_dir / "source.md"
    shutil.copyfile(FIXTURES / "document_pipeline_taxonomy_review.md", source)
    private_org = tmp_path / "private_org_bundle"

    code = main(
        [
            "document",
            "pipeline",
            "--input",
            str(source),
            "--profile",
            "taxonomy-review",
            "--private-org",
            str(private_org),
        ]
    )

    assert code == 0
    raw_output = capsys.readouterr().out
    payload = json.loads(raw_output)
    assert "private_evidence" not in raw_output.lower()
    assert "private_org_bundle" not in raw_output.lower()
    assert payload["input_path"] == "[private-input]"
    assert "[private-org]" in payload["command"]
    _assert_bundle_paths(payload, private_org)
