"""Safety constants and repository hygiene helpers."""

from __future__ import annotations

from pathlib import Path

HIERARCHY = "I -> I_system^S -> H_lex -> G_lex -> I_lexicon"
PRIVATE_MARKERS = ("gmail", "auth.json", "token", "password", "private_evidence", "unpublished")


def looks_private_path(path: str | Path) -> bool:
    text = str(path).replace("\\", "/").lower()
    return any(marker in text for marker in PRIVATE_MARKERS)


def assert_public_path(path: str | Path) -> None:
    if looks_private_path(path):
        raise ValueError(f"refusing to write private-looking path into public repo: {path}")
