"""Publish and verify the content-addressed Synthia public-shell assets.

Run ``--write`` after editing the currently published shell asset. It derives a
new filename from the file bytes, updates the manifest and all static routes,
then removes the superseded local asset. Run ``--check`` in CI or before a
cPanel deployment to reject stale fingerprints and unsafe copy ordering.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
LANDING_ROOT = REPOSITORY_ROOT / "web" / "landing"
ASSET_ROOT = LANDING_ROOT / "assets"
MANIFEST_PATH = ASSET_ROOT / "synthia-public-shell.manifest.json"
CPANEL_PATH = REPOSITORY_ROOT / ".cpanel.yml"
ROUTES = (
    LANDING_ROOT / "index.html",
    LANDING_ROOT / "trace-lab.html",
    LANDING_ROOT / "neutrosophic-lexicon.html",
)
ASSET_TYPES = {
    "stylesheet": ".css",
    "script": ".js",
}
REQUIRED_ROUTE_MARKERS = ("data-nav-toggle", "data-nav-menu", "data-action-dock")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_manifest() -> dict[str, object]:
    try:
        loaded = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot read public-shell manifest: {error}") from error
    if not isinstance(loaded, dict) or not isinstance(loaded.get("files"), dict):
        raise ValueError("public-shell manifest must contain a files object")
    return loaded


def asset_entry(manifest: dict[str, object], kind: str) -> dict[str, str]:
    files = manifest["files"]
    assert isinstance(files, dict)
    entry = files.get(kind)
    if not isinstance(entry, dict):
        raise ValueError(f"manifest is missing the {kind} entry")
    path = entry.get("path")
    digest = entry.get("sha256")
    if not isinstance(path, str) or not isinstance(digest, str):
        raise ValueError(f"manifest {kind} entry must contain path and sha256 strings")
    return {"path": path, "sha256": digest.lower()}


def expected_asset_name(kind: str, digest: str) -> str:
    return f"synthia-public-shell.{digest[:16]}{ASSET_TYPES[kind]}"


def write_manifest(manifest: dict[str, object]) -> None:
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def replace_exact(path: Path, old: str, new: str) -> None:
    contents = path.read_text(encoding="utf-8")
    if old not in contents:
        raise ValueError(f"cannot update {path.relative_to(REPOSITORY_ROOT)}: missing {old}")
    path.write_text(contents.replace(old, new), encoding="utf-8")


def publish(manifest: dict[str, object]) -> None:
    """Derive content-addressed asset names and synchronize static references."""

    files = manifest["files"]
    assert isinstance(files, dict)
    for kind in ASSET_TYPES:
        entry = asset_entry(manifest, kind)
        current_path = (ASSET_ROOT / entry["path"]).resolve()
        if current_path.parent != ASSET_ROOT.resolve() or not current_path.is_file():
            raise ValueError(f"published {kind} asset does not exist: {entry['path']}")

        digest = sha256_file(current_path)
        next_name = expected_asset_name(kind, digest)
        if next_name != current_path.name:
            next_path = ASSET_ROOT / next_name
            next_path.write_bytes(current_path.read_bytes())
            for route in ROUTES:
                replace_exact(route, f"assets/{current_path.name}", f"assets/{next_name}")
            replace_exact(CPANEL_PATH, f"web/landing/assets/{current_path.name}", f"web/landing/assets/{next_name}")
            current_path.unlink()

        entry_data = files[kind]
        assert isinstance(entry_data, dict)
        entry_data["path"] = next_name
        entry_data["sha256"] = digest.upper()

    write_manifest(manifest)


def check(manifest: dict[str, object]) -> list[str]:
    errors: list[str] = []
    entries: dict[str, dict[str, str]] = {}

    for kind in ASSET_TYPES:
        try:
            entry = asset_entry(manifest, kind)
        except ValueError as error:
            errors.append(str(error))
            continue
        entries[kind] = entry
        asset_path = ASSET_ROOT / entry["path"]
        if not asset_path.is_file():
            errors.append(f"missing {kind} asset: {entry['path']}")
            continue
        actual_digest = sha256_file(asset_path)
        if actual_digest != entry["sha256"]:
            errors.append(f"stale {kind} manifest hash for {entry['path']}")
        if asset_path.name != expected_asset_name(kind, actual_digest):
            errors.append(f"stale {kind} filename fingerprint for {asset_path.name}")

    for route in ROUTES:
        if not route.is_file():
            errors.append(f"missing public route: {route.name}")
            continue
        contents = route.read_text(encoding="utf-8")
        for marker in REQUIRED_ROUTE_MARKERS:
            if marker not in contents:
                errors.append(f"{route.name} is missing {marker}")
        if "support-widget" in contents or "paypal.securedme.ca" in contents:
            errors.append(f"{route.name} still imports a support or payment widget")
        for entry in entries.values():
            if f"assets/{entry['path']}" not in contents:
                errors.append(f"{route.name} does not reference {entry['path']}")

    index_contents = (LANDING_ROOT / "index.html").read_text(encoding="utf-8")
    if "data-primary-cta" not in index_contents:
        errors.append("index.html is missing data-primary-cta")

    if not CPANEL_PATH.is_file():
        errors.append("missing .cpanel.yml")
        return errors

    cpanel_lines = CPANEL_PATH.read_text(encoding="utf-8").splitlines()
    html_positions = [
        index
        for index, line in enumerate(cpanel_lines)
        if "web/landing/" in line and line.rstrip().endswith(".html /home/xacm7978/synthia.securedme.ca/")
    ]
    if not html_positions:
        errors.append(".cpanel.yml has no public HTML copy tasks")
        return errors
    first_html_position = min(html_positions)

    for entry in entries.values():
        expected_copy = f"web/landing/assets/{entry['path']}"
        positions = [index for index, line in enumerate(cpanel_lines) if expected_copy in line]
        if not positions:
            errors.append(f".cpanel.yml does not deploy {entry['path']}")
        elif min(positions) >= first_html_position:
            errors.append(f".cpanel.yml deploys {entry['path']} after HTML")

    manifest_positions = [
        index for index, line in enumerate(cpanel_lines)
        if "web/landing/assets/synthia-public-shell.manifest.json" in line
    ]
    if not manifest_positions or min(manifest_positions) >= first_html_position:
        errors.append(".cpanel.yml does not deploy the public-shell manifest before HTML")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="fail when fingerprints, route references, or deploy order are stale")
    mode.add_argument("--write", action="store_true", help="publish content-addressed shell assets and synchronize references")
    args = parser.parse_args(argv)

    try:
        manifest = load_manifest()
        if args.write:
            publish(manifest)
            manifest = load_manifest()
        errors = check(manifest)
    except ValueError as error:
        errors = [str(error)]

    if errors:
        print("FAIL: Synthia public-shell contract is stale.")
        for error in errors:
            print(f"- {error}")
        return 1

    print("PASS: Synthia public-shell fingerprints, route references, and cPanel asset order are current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
