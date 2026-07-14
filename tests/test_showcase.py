from __future__ import annotations

import json

import pytest

from synthia_core.cli import main
from synthia_core.showcase import (
    PUBLIC_HIERARCHY,
    SHOWCASE_SCHEMA_VERSION,
    assert_public_showcase_trace,
    build_aburria_showcase_trace,
    build_showcase_trace,
    write_showcase_trace,
)


def test_aburria_trace_has_stable_public_contract() -> None:
    trace = build_aburria_showcase_trace()

    assert trace["schema_version"] == SHOWCASE_SCHEMA_VERSION
    assert trace["formal_authority"] == "Lesson, 1828"
    assert trace["hierarchy"] == PUBLIC_HIERARCHY
    assert trace["human_review_required"] is True
    assert trace["ai_role"] == "traceability_support_only"
    assert [event["year"] for event in trace["timeline"]] == [1828, 2012, 2026]
    assert set(trace["locales"]) == {"en", "fr", "es", "it"}


def test_aburria_trace_contains_no_private_or_fractal_layer() -> None:
    serialized = json.dumps(build_aburria_showcase_trace()).lower()

    for marker in ("gmail", "gdoc.", "drive.google.com", "private_evidence", "c:\\users\\"):
        assert marker not in serialized
    for field in ('"d_f"', '"df"', '"i_fractal"'):
        assert field not in serialized


def test_public_guard_fails_closed() -> None:
    trace = build_aburria_showcase_trace()
    trace["source_registry"][0]["private_evidence"] = "hidden"

    with pytest.raises(ValueError, match="private marker"):
        assert_public_showcase_trace(trace)


def test_unknown_showcase_case_is_rejected() -> None:
    with pytest.raises(ValueError, match="unsupported showcase case"):
        build_showcase_trace("unknown")


def test_writer_is_deterministic(tmp_path) -> None:
    output = tmp_path / "nested" / "trace.json"

    write_showcase_trace("aburria", output, pretty=True)
    first = output.read_bytes()
    write_showcase_trace("aburria", output, pretty=True)

    assert output.read_bytes() == first
    assert json.loads(first)["schema_version"] == SHOWCASE_SCHEMA_VERSION


def test_showcase_cli_writes_trace(tmp_path, capsys) -> None:
    output = tmp_path / "trace.json"

    exit_code = main(
        [
            "showcase",
            "export",
            "--case",
            "aburria",
            "--output",
            str(output),
            "--pretty",
        ]
    )

    result = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert result["schema_version"] == SHOWCASE_SCHEMA_VERSION
    assert json.loads(output.read_text(encoding="utf-8"))["case_id"] == (
        "aburria-aburri-memory-repair"
    )
