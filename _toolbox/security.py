"""Local-only security and privacy helpers for MNCH Manager v5.

These helpers are defensive checks only. They do not encrypt data, call APIs,
or scan outside the requested module folder.
"""

from __future__ import annotations

from pathlib import Path
import re
from typing import Any

from _toolbox import paths


SECRET_PATTERNS = (
    re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?([A-Za-z0-9_\-]{12,})"),
    re.compile(r"AIza[0-9A-Za-z_\-]{20,}"),
    re.compile(r"sk-[A-Za-z0-9_\-]{20,}"),
)


def contains_possible_secret(text: str) -> bool:
    """Return True when text appears to contain an obvious secret-like value."""

    return any(pattern.search(text) for pattern in SECRET_PATTERNS)


def redact_secret_text(text: str) -> str:
    """Redact obvious secret-like values from text."""

    redacted = text
    redacted = re.sub(
        r"(?i)((api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?)([A-Za-z0-9_\-]{12,})",
        r"\1[REDACTED]",
        redacted,
    )
    redacted = re.sub(r"AIza[0-9A-Za-z_\-]{20,}", "[REDACTED]", redacted)
    redacted = re.sub(r"sk-[A-Za-z0-9_\-]{20,}", "[REDACTED]", redacted)
    return redacted


def assert_safe_local_path(workspace_root: Path, candidate: Path) -> Path:
    """Return a resolved candidate path only when it is inside the workspace."""

    return paths.ensure_within_workspace(workspace_root, candidate)


def build_privacy_report(module_dir: Path) -> dict[str, Any]:
    """Build a simple local-only privacy report for one module folder."""

    files_scanned = 0
    possible_secret_files: list[str] = []
    if module_dir.exists():
        for file_path in module_dir.rglob("*"):
            if not file_path.is_file():
                continue
            files_scanned += 1
            try:
                content = file_path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if contains_possible_secret(content):
                possible_secret_files.append(file_path.relative_to(module_dir).as_posix())

    return {
        "module_path": str(module_dir),
        "local_only": True,
        "api_enabled": False,
        "network_enabled": False,
        "encryption_enabled": False,
        "encryption_note": "Deferred; no local dependency has been selected for encryption.",
        "files_scanned": files_scanned,
        "possible_secret_files": possible_secret_files,
        "possible_secret_count": len(possible_secret_files),
    }
