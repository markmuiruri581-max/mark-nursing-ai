"""Quality scanning contracts for MNCH source-card files.

This module defines bad-text patterns, weak-file thresholds, and report shapes.
The scanning functions are skeletons for now and should remain read-only when
implemented.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


BAD_TEXT_PATTERNS = (
    "URL not accessible",
    "RESOURCE_EXHAUSTED",
    "Empty model response",
    "Traceback",
    "[PASTE",
    "429",
    "503",
    "manual fallback",
)
WEAK_FILE_THRESHOLD_BYTES = 1500


@dataclass(frozen=True)
class SourceCardFinding:
    """Quality finding for one source-card file."""

    path: Path
    bad_patterns: list[str]
    is_weak: bool
    size_bytes: int


@dataclass(frozen=True)
class QualityReport:
    """Aggregate quality report for a module's source cards."""

    scanned_files: list[Path]
    bad_files: list[Path]
    weak_files: list[Path]
    findings: list[SourceCardFinding]
    summary: str


def scan_source_card_file(path: Path) -> SourceCardFinding:
    """Scan one source-card file for bad text and weak length."""

    # TODO: Implement read-only file scanning.
    raise NotImplementedError("Single-file quality scanning is not implemented in the skeleton.")


def scan_source_cards(source_cards_dir: Path) -> QualityReport:
    """Scan all source-card files in a module source-card folder."""

    # TODO: Find markdown source-card files and return exact bad/weak file lists.
    raise NotImplementedError("Source-card folder scanning is not implemented in the skeleton.")


def is_weak_file(path: Path) -> bool:
    """Return whether a file is below the weak source-card threshold."""

    # TODO: Implement using WEAK_FILE_THRESHOLD_BYTES without modifying the file.
    raise NotImplementedError("Weak-file detection is not implemented in the skeleton.")


def contains_bad_text(text: str) -> list[str]:
    """Return bad-text patterns found in a text block."""

    # TODO: Decide whether matching should be case-sensitive.
    return [pattern for pattern in BAD_TEXT_PATTERNS if pattern in text]


def build_quality_report(findings: list[SourceCardFinding]) -> QualityReport:
    """Build a quality report from individual source-card findings."""

    # TODO: Add final report wording and pass/fail semantics.
    scanned_files = [finding.path for finding in findings]
    bad_files = [finding.path for finding in findings if finding.bad_patterns]
    weak_files = [finding.path for finding in findings if finding.is_weak]
    return QualityReport(
        scanned_files=scanned_files,
        bad_files=bad_files,
        weak_files=weak_files,
        findings=findings,
        summary="Quality report skeleton.",
    )
