import json
from pathlib import Path

from synthia_core.assets import (
    LEXICON_HIERARCHY,
    approval_packet,
    build_inventory,
    classify_manifest,
    manifest_sha256,
    validate_manifest,
)
from synthia_core.cli import main


def make_suite(tmp_path: Path) -> Path:
    tool = tmp_path / "VisualAlgorithmDesigner"
    (tool / "assets" / "logo").mkdir(parents=True)
    (tool / "docs").mkdir()
    logo = tool / "assets" / "logo" / "visual-algorithm-logo-light.png"
    logo.write_bytes(b"fake-image")
    (tool / "docs" / "index.md").write_text("![logo](../assets/logo/visual-algorithm-logo-light.png)", encoding="utf-8")
    return tmp_path


def test_inventory_preserves_synthia_hierarchy_and_registry(tmp_path):
    root = make_suite(tmp_path)
    payload = build_inventory(root)

    assert payload["hierarchy"] == LEXICON_HIERARCHY
    assert payload["summary"]["tool_count"] == 11
    visual = next(tool for tool in payload["tools"] if tool["slug"] == "visual-algorithm")
    assert visual["exists"] is True
    assert visual["asset_count"] == 1
    assert visual["assets"][0]["classification"]["role"] == "logo"


def test_classify_missing_quantech_observation_quarantines_images(tmp_path):
    root = make_suite(tmp_path)
    payload = classify_manifest(root)
    visual = next(tool for tool in payload["tools"] if tool["slug"] == "visual-algorithm")
    asset = visual["assets"][0]

    assert payload["classification_mode"] == "static-fail-closed"
    assert asset["classification"]["review_required"] is True
    assert asset["classification"]["state"] == "quarantine"
    assert asset["classification"]["lexicon_layer"] == "I_lexicon"


def test_manifest_validation_and_approval_hash(tmp_path):
    root = make_suite(tmp_path)
    payload = build_inventory(root)
    validation = validate_manifest(payload)
    approval = approval_packet(payload, "human-reviewer")

    assert validation["ok"] is True
    assert approval["manifest_sha256"] == manifest_sha256(payload)


def test_cli_assets_inventory_writes_json(tmp_path):
    root = make_suite(tmp_path)
    out = tmp_path / "manifest.json"

    assert main(["assets", "inventory", "--root", str(root), "--out", str(out)]) == 0
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["kind"] == "synthia.education_assets.manifest"
    assert payload["summary"]["asset_count"] == 1


def test_cli_apply_rejects_review_packet_without_approval_kind(tmp_path):
    root = make_suite(tmp_path)
    manifest = build_inventory(root)
    manifest_path = tmp_path / "manifest.json"
    review_path = tmp_path / "review.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    review_path.write_text(json.dumps({"manifest_sha256": manifest_sha256(manifest)}), encoding="utf-8")

    assert main(["assets", "apply", "--manifest", str(manifest_path), "--approval", str(review_path)]) == 1
