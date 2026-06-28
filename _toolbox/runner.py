"""Stage runner contracts for MNCH Coursera automation.

This module will later coordinate safe Stage 1 and Stage 2 execution. The
skeleton contains only constants and classification helpers; it does not call
Gemini, the network, subprocesses, or the copied v4 script.
"""

from __future__ import annotations

from pathlib import Path


QUOTA_STOP_PATTERNS = (
    "429",
    "RESOURCE_EXHAUSTED",
    "quota",
    "rate limit",
)
RETRYABLE_PATTERNS = (
    "503",
    "UNAVAILABLE",
    "Empty model response",
    "temporarily",
    "timeout",
)


def is_quota_stop_error(error_text: str) -> bool:
    """Return whether an error should stop immediately for quota safety."""

    lowered = error_text.lower()
    return any(pattern.lower() in lowered for pattern in QUOTA_STOP_PATTERNS)


def is_retryable_error(error_text: str) -> bool:
    """Return whether an error is potentially retryable."""

    lowered = error_text.lower()
    return any(pattern.lower() in lowered for pattern in RETRYABLE_PATTERNS)


def run_stage1(module_dir: Path) -> None:
    """Run Stage 1 source-card generation for a module."""

    # TODO: Implement safe Stage 1 orchestration without changing v4.
    raise NotImplementedError("Stage 1 execution is not implemented in the skeleton.")


def run_stage2(module_dir: Path) -> None:
    """Run Stage 2 final synthesis for a module."""

    # TODO: Implement Stage 2 only after quality gates are in place.
    raise NotImplementedError("Stage 2 execution is not implemented in the skeleton.")
