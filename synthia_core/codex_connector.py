"""Codex/OpenAI connector boundary using native Codex auth."""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CodexStatus:
    available: bool
    path: str | None
    returncode: int | None
    stdout: str
    stderr: str

    def as_dict(self) -> dict[str, object]:
        return {
            "available": self.available,
            "path": self.path,
            "returncode": self.returncode,
            "stdout_tail": self.stdout[-2000:],
            "stderr_tail": self.stderr[-2000:],
            "raw_token_stored_by_synthia": False,
        }


def codex_status(timeout: int = 20) -> CodexStatus:
    path = shutil.which("codex")
    if not path:
        return CodexStatus(False, None, None, "", "codex CLI is not installed on PATH")
    try:
        proc = subprocess.run(
            (path, "login", "status"),
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return CodexStatus(True, path, None, exc.stdout or "", "codex login status timed out")
    return CodexStatus(True, path, proc.returncode, proc.stdout, proc.stderr)


def build_wake_prompt(private_org: str | Path) -> str:
    soul_path = Path(private_org) / "01_soul_and_storyline" / "synthia_soul.md"
    soul = soul_path.read_text(encoding="utf-8") if soul_path.exists() else "Synthia soul file not found."
    return "\n".join(
        [
            "You are Codex connected to the Synthia base build.",
            "Use Codex native ChatGPT/browser authentication or the existing Codex session.",
            "Do not request or store OpenAI API keys inside Synthia.",
            "Preserve the boundary: AI is traceability support, not taxonomic authority.",
            "Preserve hierarchy: I -> I_system^S -> D_f -> dF -> i_fractal.",
            "",
            "Synthia soul excerpt:",
            soul[:4000],
        ]
    )
