"""Education-suite asset inventory, classification, and manifest governance."""

from __future__ import annotations

import hashlib
import json
import mimetypes
import os
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from .plithogenic import TIF
from .safety import HIERARCHY

ASSET_SCHEMA_VERSION = 1
ASSET_MANIFEST_KIND = "synthia.education_assets.manifest"
CLASSIFIER_VERSION = "synthia-assets-v1"
QUANTECH_OBSERVER = "quantech-vid-local-observer"
LEXICON_HIERARCHY = "I -> I_system^S -> H_lex -> G_lex -> I_lexicon"

ROLE_VALUES = (
    "logo",
    "banner",
    "icon",
    "badge",
    "mascot",
    "illustration",
    "diagram",
    "screenshot",
    "social-card",
    "video",
    "audio",
    "source-document",
    "archive",
    "unknown",
)

STATE_VALUES = (
    "official-candidate",
    "alternate",
    "draft",
    "legacy",
    "generated",
    "shared-suite",
    "quarantine",
    "unknown",
)

SUITE_TOOLS: tuple[dict[str, str], ...] = (
    {"slug": "visual-algorithm", "path": "VisualAlgorithmDesigner", "name": "Visual Algorithm Designer"},
    {"slug": "vot-guardian", "path": "V.O.T-Guardian", "name": "V.O.T Guardian"},
    {"slug": "algorithm-builder", "path": "algorithm-builder-app", "name": "Algorithm Builder"},
    {"slug": "fnpqnn", "path": "FNP-QNN-MVP/FNP-QNN-MVP", "name": "FNP-QNN"},
    {"slug": "gateway", "path": "FNP-QNN-MVP/fnpqnn_gateway_MVP", "name": "FNP-QNN Gateway"},
    {"slug": "ffed-qlc", "path": "FfeD-QLC-MVP", "name": "FfeD-QLC"},
    {"slug": "quanthor", "path": "QuaNThoR", "name": "QuaNThoR"},
    {"slug": "synthia", "path": "Synthia/Synthia", "name": "Synthia"},
    {"slug": "scholarium", "path": "securedme-scholarium", "name": "SecuredMe Scholarium"},
    {"slug": "market-guardian", "path": "market-guardian-retailguard", "name": "Market Guardian"},
    {"slug": "tesla-workbench", "path": "tesla-resonance-recovery-workbench", "name": "Tesla Workbench"},
)

ASSET_ROOT_NAMES = {
    "assets",
    "docs/assets",
    "site/assets",
    "src/assets",
    "frontend/src/assets",
    "app/assets",
    "apps/web/src/assets",
    "public/assets",
    "static/assets",
    "web/landing/assets",
}

SKIP_PARTS = {
    ".git",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "site-packages",
    "dist",
    "build",
    ".cache",
    ".mypy_cache",
    ".pytest_cache",
    "__pycache__",
}

REFERENCE_EXTENSIONS = {
    ".md",
    ".mdx",
    ".html",
    ".css",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".py",
    ".yml",
    ".yaml",
    ".json",
    ".toml",
}

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".svg"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".webm", ".avi", ".mkv"}
AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".ogg", ".flac"}
SOURCE_EXTENSIONS = {".psd", ".ai", ".fig", ".sketch", ".zip", ".docx", ".pptx", ".xlsx", ".pdf"}

ROLE_KEYWORDS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("banner", ("banner", "hero", "mural")),
    ("logo", ("logo", "brandmark", "wordmark")),
    ("icon", ("icon", "favicon", "appicon")),
    ("badge", ("badge", "stamp", "seal")),
    ("mascot", ("mascot", "mascotte", "guardian")),
    ("social-card", ("social", "og", "twitter-card", "card")),
    ("diagram", ("diagram", "schema", "graph", "architecture")),
    ("screenshot", ("screenshot", "screen", "capture")),
    ("illustration", ("illustration", "infographic", "infographique", "background")),
)


@dataclass(frozen=True)
class ToolRoot:
    slug: str
    path: Path
    relative_path: str
    name: str
    exists: bool

    def as_dict(self) -> dict[str, object]:
        return {
            "slug": self.slug,
            "path": self.relative_path,
            "name": self.name,
            "exists": self.exists,
        }


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def default_suite_root() -> Path:
    return Path(__file__).resolve().parents[2].parent


def normalize_rel(path: Path) -> str:
    return path.as_posix()


def is_skipped(path: Path) -> bool:
    return bool(set(path.parts) & SKIP_PARTS)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_git(repo: Path, args: list[str]) -> str:
    try:
        proc = subprocess.run(["git", *args], cwd=str(repo), text=True, capture_output=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return proc.stdout.strip() if proc.returncode == 0 else ""


def git_state(repo: Path) -> dict[str, object]:
    status = run_git(repo, ["status", "--short", "--branch"])
    lines = [line for line in status.splitlines() if line.strip()]
    return {
        "branch": run_git(repo, ["branch", "--show-current"]) or "unknown",
        "remote": run_git(repo, ["remote", "get-url", "origin"]),
        "status": lines,
        "dirty": [line for line in lines[1:]],
        "dirty_policy": "preserve-user-changes" if len(lines) > 1 else "clean",
    }


def suite_registry(root: Path) -> list[ToolRoot]:
    tools: list[ToolRoot] = []
    for item in SUITE_TOOLS:
        rel = item["path"]
        path = root / rel
        tools.append(ToolRoot(item["slug"], path, rel, item["name"], path.exists()))
    return tools


def asset_root_role(relative: Path) -> str:
    rel = normalize_rel(relative)
    if rel == "assets":
        return "canonical-source"
    if rel.startswith("docs/assets") or rel.startswith("site/assets"):
        return "consumer-copy"
    if rel.startswith("web/landing/assets") or rel.endswith("/src/assets") or "/src/assets" in rel:
        return "application-consumer"
    if "dist/" in rel or "build/" in rel:
        return "generated"
    return "candidate-source"


def find_asset_roots(tool: ToolRoot) -> list[dict[str, object]]:
    roots: list[dict[str, object]] = []
    if not tool.exists:
        return roots
    for root_name in sorted(ASSET_ROOT_NAMES):
        candidate = tool.path / root_name
        if candidate.is_dir() and not is_skipped(candidate.relative_to(tool.path)):
            roots.append({"path": root_name, "role": asset_root_role(Path(root_name))})
    return roots


def iter_asset_files(tool: ToolRoot) -> Iterable[Path]:
    for root_meta in find_asset_roots(tool):
        asset_dir = tool.path / str(root_meta["path"])
        for path in sorted(asset_dir.rglob("*"), key=lambda p: p.as_posix().lower()):
            if path.is_file() and not is_skipped(path.relative_to(tool.path)):
                yield path


def detect_windows_collision(relative_paths: Iterable[str]) -> list[dict[str, object]]:
    groups: dict[str, list[str]] = {}
    for rel in relative_paths:
        key = re.sub(r"[()\s]+", "-", rel.lower())
        key = key.replace("\\", "/")
        groups.setdefault(key, []).append(rel)
    return [{"normalized": key, "paths": sorted(values)} for key, values in groups.items() if len(values) > 1]


def scan_references(tool: ToolRoot, asset_rels: list[str]) -> dict[str, list[str]]:
    refs = {asset: [] for asset in asset_rels}
    if not tool.exists or not asset_rels:
        return refs
    candidates = [
        path
        for path in tool.path.rglob("*")
        if path.is_file() and path.suffix.lower() in REFERENCE_EXTENSIONS and not is_skipped(path.relative_to(tool.path))
    ]
    for source in candidates:
        try:
            text = source.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        source_rel = normalize_rel(source.relative_to(tool.path))
        for asset in asset_rels:
            name = Path(asset).name
            if asset in text or name in text:
                refs[asset].append(source_rel)
    return refs


def infer_role(path: Path, observation: dict[str, object] | None = None) -> tuple[str, list[str]]:
    rel = normalize_rel(path).lower()
    name = path.name.lower()
    suffix = path.suffix.lower()
    evidence: list[str] = []
    if suffix in VIDEO_EXTENSIONS:
        return "video", ["extension:video"]
    if suffix in AUDIO_EXTENSIONS:
        return "audio", ["extension:audio"]
    if suffix in SOURCE_EXTENSIONS:
        return "source-document", ["extension:source-document"]
    for role, terms in ROLE_KEYWORDS:
        for term in terms:
            if term in rel or term in name:
                evidence.append(f"path-token:{term}")
                return role, evidence
    if observation:
        width = int(observation.get("width") or observation.get("dimensions", {}).get("width") or 0)
        height = int(observation.get("height") or observation.get("dimensions", {}).get("height") or 0)
        has_alpha = bool(observation.get("has_alpha") or observation.get("hasAlpha"))
        if width and height:
            ratio = width / max(1, height)
            if ratio >= 2.5:
                return "banner", [f"ratio:{ratio:.2f}"]
            if has_alpha and max(width, height) <= 512:
                return "icon", ["alpha-small-image"]
    if suffix in IMAGE_EXTENSIONS:
        return "illustration", ["extension:image-fallback"]
    return "unknown", ["no-role-evidence"]


def infer_state(path: Path, root_role: str, consumers: list[str], role: str) -> tuple[str, list[str]]:
    rel = normalize_rel(path).lower()
    evidence: list[str] = []
    if root_role == "generated":
        return "generated", ["asset-root:generated"]
    if "legacy" in rel or "old" in rel:
        return "legacy", ["path-token:legacy"]
    if "draft" in rel or "1th draft" in rel or "first draft" in rel:
        return "draft", ["path-token:draft"]
    if "alternate" in rel or "alt" in rel:
        return "alternate", ["path-token:alternate"]
    if "suite" in rel or "securedme" in rel:
        return "shared-suite", ["path-token:shared-suite"]
    if role == "unknown":
        return "quarantine", ["unknown-role"]
    if root_role == "canonical-source" and consumers:
        evidence.append("canonical-source-with-consumers")
        return "official-candidate", evidence
    if root_role == "canonical-source":
        return "official-candidate", ["canonical-source"]
    return "unknown", ["consumer-or-unproven-source"]


def classification_tif(role: str, state: str, evidence_count: int, consumer_count: int) -> dict[str, object]:
    indeterminacy = 0.15
    if role == "unknown" or state in {"unknown", "quarantine"}:
        indeterminacy = 0.85
    elif evidence_count == 0:
        indeterminacy = 0.65
    elif consumer_count == 0 and state == "official-candidate":
        indeterminacy = 0.35
    truth = max(0.0, 1.0 - indeterminacy)
    falsity = 0.1 if role != "unknown" else 0.35
    return TIF(T=truth, I=indeterminacy, F=falsity, I_system=indeterminacy, H_lex=indeterminacy, G_lex=indeterminacy, I_lexicon=indeterminacy).as_dict()


def asset_metadata(path: Path, tool: ToolRoot, root_role: str, consumers: list[str]) -> dict[str, object]:
    rel = normalize_rel(path.relative_to(tool.path))
    role, role_evidence = infer_role(Path(rel))
    state, state_evidence = infer_state(Path(rel), root_role, consumers, role)
    review_required = role == "unknown" or state in {"unknown", "quarantine"} or not consumers
    return {
        "tool_slug": tool.slug,
        "path": rel,
        "sha256": sha256_file(path),
        "bytes": path.stat().st_size,
        "extension": path.suffix.lower(),
        "mime": mimetypes.guess_type(path.name)[0] or "application/octet-stream",
        "asset_root_role": root_role,
        "consumers": consumers,
        "classification": {
            "role": role,
            "state": state,
            "variant": variant_for_path(Path(rel)),
            "review_required": review_required,
            "evidence": role_evidence + state_evidence,
            "tif": classification_tif(role, state, len(role_evidence + state_evidence), len(consumers)),
            "lexicon_layer": "I_lexicon",
            "classifier": CLASSIFIER_VERSION,
        },
    }


def variant_for_path(path: Path) -> str:
    text = normalize_rel(path).lower()
    if "dark" in text:
        return "dark"
    if "light" in text:
        return "light"
    if "large" in text:
        return "large"
    if "small" in text or "min" in text:
        return "small"
    return "default"


def build_inventory(root: str | Path | None = None) -> dict[str, object]:
    suite_root = Path(root) if root else default_suite_root()
    tools = suite_registry(suite_root)
    out_tools: list[dict[str, object]] = []
    all_hashes: dict[str, list[str]] = {}
    for tool in tools:
        asset_roots = find_asset_roots(tool)
        files = [path for path in iter_asset_files(tool)]
        rels = [normalize_rel(path.relative_to(tool.path)) for path in files]
        references = scan_references(tool, rels)
        file_payloads = []
        for path in files:
            rel = normalize_rel(path.relative_to(tool.path))
            root_role = "candidate-source"
            for root_meta in asset_roots:
                root_path = str(root_meta["path"]).replace("\\", "/")
                if rel == root_path or rel.startswith(root_path + "/"):
                    root_role = str(root_meta["role"])
                    break
            entry = asset_metadata(path, tool, root_role, references.get(rel, []))
            file_payloads.append(entry)
            all_hashes.setdefault(str(entry["sha256"]), []).append(f"{tool.slug}:{rel}")
        out_tools.append(
            {
                **tool.as_dict(),
                "git": git_state(tool.path) if tool.exists and (tool.path / ".git").exists() else {},
                "asset_roots": asset_roots,
                "asset_count": len(file_payloads),
                "assets": file_payloads,
                "windows_collisions": detect_windows_collision(rels),
            }
        )
    duplicates = [{"sha256": digest, "paths": sorted(paths)} for digest, paths in all_hashes.items() if len(paths) > 1]
    return {
        "schema_version": ASSET_SCHEMA_VERSION,
        "kind": ASSET_MANIFEST_KIND,
        "created_at": utc_now(),
        "suite_root": str(suite_root),
        "tools": out_tools,
        "summary": {
            "tool_count": len(out_tools),
            "existing_tool_count": sum(1 for tool in out_tools if tool["exists"]),
            "asset_count": sum(int(tool["asset_count"]) for tool in out_tools),
            "duplicate_sha256_count": len(duplicates),
            "review_required_count": sum(
                1
                for tool in out_tools
                for asset in tool["assets"]
                if asset["classification"]["review_required"]
            ),
        },
        "duplicates": duplicates,
        "roles": list(ROLE_VALUES),
        "states": list(STATE_VALUES),
        "hierarchy": LEXICON_HIERARCHY,
        "fractal_hierarchy_guard": "I -> I_system^S -> D_f -> dF -> i_fractal",
        "authority_boundary": "Quantech observes; Synthia proposes; human approval decides official identity.",
    }


def load_observations(path: str | None) -> dict[str, dict[str, object]]:
    if not path:
        return {}
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    observations = payload.get("observations", payload if isinstance(payload, list) else [])
    out: dict[str, dict[str, object]] = {}
    for item in observations:
        if isinstance(item, dict):
            key = str(item.get("path") or item.get("relative_path") or "")
            if key:
                out[key.replace("\\", "/")] = item
    return out


def classify_manifest(root: str | Path | None = None, observations_path: str | None = None) -> dict[str, object]:
    manifest = build_inventory(root)
    observations = load_observations(observations_path)
    observed = 0
    for tool in manifest["tools"]:
        for asset in tool["assets"]:
            key = f"{tool['slug']}:{asset['path']}"
            observation = observations.get(key) or observations.get(str(asset["path"]))
            if observation:
                observed += 1
                role, evidence = infer_role(Path(str(asset["path"])), observation)
                if role != asset["classification"]["role"]:
                    asset["classification"]["role"] = role
                    asset["classification"]["evidence"].extend([f"quantech:{item}" for item in evidence])
                asset["quantech_observation"] = observation
            elif str(asset["extension"]).lower() in IMAGE_EXTENSIONS:
                asset["classification"]["review_required"] = True
                asset["classification"]["state"] = "quarantine"
                asset["classification"]["evidence"].append("quantech-observation-missing")
    manifest["summary"]["quantech_observed_count"] = observed
    manifest["summary"]["quantech_unobserved_image_count"] = sum(
        1
        for tool in manifest["tools"]
        for asset in tool["assets"]
        if str(asset["extension"]).lower() in IMAGE_EXTENSIONS and "quantech_observation" not in asset
    )
    manifest["classification_mode"] = "quantech-assisted" if observations else "static-fail-closed"
    return manifest


def validate_manifest(manifest: dict[str, object]) -> dict[str, object]:
    issues: list[str] = []
    if manifest.get("kind") != ASSET_MANIFEST_KIND:
        issues.append("invalid-kind")
    if manifest.get("hierarchy") != LEXICON_HIERARCHY:
        issues.append("invalid-i-lexicon-hierarchy")
    paths = set()
    for tool in manifest.get("tools", []):
        if not isinstance(tool, dict):
            issues.append("tool-not-object")
            continue
        for asset in tool.get("assets", []):
            if not isinstance(asset, dict):
                issues.append("asset-not-object")
                continue
            key = f"{tool.get('slug')}:{asset.get('path')}"
            if key in paths:
                issues.append(f"duplicate-manifest-path:{key}")
            paths.add(key)
            classification = asset.get("classification", {})
            if classification.get("role") not in ROLE_VALUES:
                issues.append(f"invalid-role:{key}")
            if classification.get("state") not in STATE_VALUES:
                issues.append(f"invalid-state:{key}")
            if classification.get("lexicon_layer") != "I_lexicon":
                issues.append(f"invalid-lexicon-layer:{key}")
    return {"ok": not issues, "issues": issues, "checked_at": utc_now()}


def manifest_sha256(manifest: dict[str, object]) -> str:
    encoded = json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def approval_packet(manifest: dict[str, object], approver: str) -> dict[str, object]:
    return {
        "schema_version": ASSET_SCHEMA_VERSION,
        "kind": "synthia.education_assets.approval",
        "manifest_sha256": manifest_sha256(manifest),
        "approver": approver,
        "approved_at": utc_now(),
        "valid_only_for_exact_manifest_hash": True,
        "authority_boundary": "Human approval is required before migration.",
    }


def proposed_migration(manifest: dict[str, object]) -> dict[str, object]:
    entries = []
    name_counts: dict[tuple[str, str], int] = {}
    for tool in manifest.get("tools", []):
        slug = str(tool.get("slug"))
        for asset in tool.get("assets", []):
            if asset.get("asset_root_role") not in {"canonical-source", "candidate-source"}:
                continue
            classification = asset.get("classification", {})
            role = str(classification.get("role", "unknown"))
            state = str(classification.get("state", "unknown"))
            variant = str(classification.get("variant", "default"))
            old_path = str(asset.get("path"))
            ext = Path(old_path).suffix.lower()
            bucket = role_bucket(role, state)
            base_name = f"{slug}-{role}-{variant}"
            key = (slug, f"assets/{bucket}/{base_name}{ext}")
            name_counts[key] = name_counts.get(key, 0) + 1
            suffix = "" if name_counts[key] == 1 else f"-alt-{name_counts[key]:02d}"
            new_name = f"{base_name}{suffix}{ext}" if ext else f"{base_name}{suffix}"
            entries.append(
                {
                    "tool_slug": slug,
                    "old_path": old_path,
                    "new_path": f"assets/{bucket}/{new_name}",
                    "sha256": asset.get("sha256"),
                    "consumers": asset.get("consumers", []),
                    "review_required": classification.get("review_required", True),
                    "rollback": {"from": f"assets/{bucket}/{new_name}", "to": old_path},
                }
            )
    return {
        "schema_version": ASSET_SCHEMA_VERSION,
        "kind": "synthia.education_assets.migration_plan",
        "created_at": utc_now(),
        "entries": entries,
        "requires_approval": True,
        "source_only": True,
    }


def role_bucket(role: str, state: str) -> str:
    if state in {"legacy", "draft", "alternate", "quarantine"}:
        return f"archive/{state}"
    if role in {"logo", "banner", "icon", "badge", "mascot"}:
        return f"brand/{role}"
    if role in {"video", "audio"}:
        return f"media/{role}"
    if role == "social-card":
        return "marketing/social"
    if role in {"illustration", "diagram", "screenshot"}:
        return f"product/{role}"
    if role == "source-document":
        return "source"
    return "archive/unknown"


def write_json(path: str | Path, payload: dict[str, object]) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return target


def loopback_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise ValueError("Only http loopback Quantech targets are allowed.")
    return value.rstrip("/")


def request_quantech_observation(base_url: str, token: str, tool_slug: str, path: Path, relative: str) -> dict[str, object]:
    payload = json.dumps(
        {
            "toolSlug": tool_slug,
            "path": str(path),
            "relativePath": relative,
            "sha256": sha256_file(path),
            "expectedType": "image",
        }
    ).encode("utf-8")
    request = Request(
        f"{base_url}/api/plugin/analyze-image",
        data=payload,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
        method="POST",
    )
    with urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def classify_education_assets(
    root: str | Path | None = None,
    quantech_url: str | None = None,
    quantech_token: str | None = None,
) -> dict[str, object]:
    suite_root = Path(root) if root else default_suite_root()
    observations: list[dict[str, object]] = []
    observer_status = {"available": False, "mode": "static-only"}
    if quantech_url and quantech_token:
        base_url = loopback_url(quantech_url)
        observer_status = {"available": True, "mode": QUANTECH_OBSERVER, "url": base_url}
        for tool in suite_registry(suite_root):
            if not tool.exists:
                continue
            for path in iter_asset_files(tool):
                if path.suffix.lower() not in IMAGE_EXTENSIONS:
                    continue
                rel = normalize_rel(path.relative_to(tool.path))
                try:
                    item = request_quantech_observation(base_url, quantech_token, tool.slug, path, rel)
                    item["path"] = f"{tool.slug}:{rel}"
                    observations.append(item)
                except (OSError, URLError, TimeoutError, ValueError) as exc:
                    observer_status = {"available": False, "mode": "quantech-failed-closed", "error": str(exc)}
                    observations = []
                    break
            if observations == [] and observer_status.get("mode") == "quantech-failed-closed":
                break
    manifest = build_inventory(suite_root)
    if observations:
        temp_observations = {"observations": observations}
        for tool in manifest["tools"]:
            for asset in tool["assets"]:
                key = f"{tool['slug']}:{asset['path']}"
                observation = next((item for item in temp_observations["observations"] if item.get("path") == key), None)
                if observation:
                    asset["quantech_observation"] = observation
    else:
        manifest = classify_manifest(suite_root)
    manifest["observer_status"] = observer_status
    manifest["validation"] = validate_manifest(manifest)
    manifest["migration_plan"] = proposed_migration(manifest)
    return manifest
