import json
from pathlib import Path

from synthia_core.cli import main
from synthia_core.safety import assert_public_path
from synthia_core.soul import build_public_soul_summary


def test_public_path_rejects_private_markers():
    try:
        assert_public_path("private_evidence/gmail_aguilar_evidence.json")
    except ValueError as exc:
        assert "private-looking" in str(exc)
    else:
        raise AssertionError("private path should be rejected")


def test_public_soul_summary_filters_private_evidence(tmp_path: Path):
    private_org = tmp_path / "Synthia_organisation"
    soul_dir = private_org / "01_soul_and_storyline"
    soul_dir.mkdir(parents=True)
    (soul_dir / "synthia_soul.md").write_text(
        "Public line\nRaw private correspondence stays in private_evidence.\n",
        encoding="utf-8",
    )

    summary = build_public_soul_summary(private_org)

    assert "Public line" in summary
    assert "private_evidence" not in summary


def test_cli_lexicon_classify_smoke(capsys):
    code = main(
        [
            "lexicon",
            "classify",
            "--text",
            "AI-assisted traceability supports human review.",
            "--domain",
            "ai_governance",
        ]
    )

    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["matched_terms"][0]["term"] == "AI-assisted traceability"


def test_cli_taxonomy_packet_smoke(capsys):
    code = main(["taxonomy", "aburria-packet"])

    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["formal_name"] == "Aburria aburri"
