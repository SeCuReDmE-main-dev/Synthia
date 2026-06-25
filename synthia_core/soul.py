"""Soul document helpers."""

from __future__ import annotations

from pathlib import Path


def build_public_soul_summary(private_org: str | Path) -> str:
    soul_path = Path(private_org) / "01_soul_and_storyline" / "synthia_soul.md"
    soul = soul_path.read_text(encoding="utf-8")
    allowed_lines = [
        line
        for line in soul.splitlines()
        if "raw private correspondence" not in line.lower()
        and "private_evidence" not in line.lower()
    ]
    return "\n".join(allowed_lines).strip() + "\n"
