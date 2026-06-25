"""Source scanning helpers with private/public separation."""

from __future__ import annotations

import json
from pathlib import Path


PUBLIC_EXTENSIONS = {".md", ".py", ".toml", ".txt", ".yml", ".yaml", ".json"}


def scan_root(root: str | Path) -> dict[str, object]:
    root_path = Path(root)
    files = []
    for item in sorted(root_path.iterdir(), key=lambda path: path.name.lower()):
        if item.name == "Synthia":
            kind = "public_repo"
        elif item.name == "Synthia_organisation":
            kind = "private_organisation"
        elif item.is_dir():
            kind = "directory"
        else:
            kind = "source_artifact"
        files.append(
            {
                "name": item.name,
                "kind": kind,
                "size": item.stat().st_size if item.is_file() else None,
                "public_safe_extension": item.suffix.lower() in PUBLIC_EXTENSIONS,
            }
        )
    return {"root": str(root_path), "items": files}


def load_source_ledger(private_org: str | Path) -> dict[str, object]:
    ledger_path = Path(private_org) / "00_source_inventory" / "source_ledger.json"
    return json.loads(ledger_path.read_text(encoding="utf-8"))
