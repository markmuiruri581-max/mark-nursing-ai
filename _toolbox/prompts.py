"""Prompt-building helpers for manual fallback and external LLM batches.

This module will later generate model-agnostic prompts for source cards and
fallback repair. It must not call external APIs.
"""

from __future__ import annotations

from typing import Sequence


COMMON_BATCH_SIZES = (1, 2, 3)


def split_urls_into_batches(urls: Sequence[str], batch_size: int) -> list[list[str]]:
    """Split URLs into batches using a positive custom batch size."""

    validate_batch_size(batch_size)
    return [list(urls[index : index + batch_size]) for index in range(0, len(urls), batch_size)]


def validate_batch_size(batch_size: int) -> None:
    """Validate supported batch sizes: 1, 2, 3, or any custom positive integer."""

    # TODO: Add interactive guidance in the manager for 1, 2, 3, and custom modes.
    if batch_size < 1:
        raise ValueError("batch_size must be a positive integer")


def generate_manual_fallback_prompt(module_name: str, urls: Sequence[str], source_range: str) -> str:
    """Generate a manual fallback prompt for failed or inaccessible URLs."""

    # TODO: Build the final fallback prompt text from the approved source-card format.
    raise NotImplementedError("Manual fallback prompt generation is not implemented in the skeleton.")


def generate_external_llm_batch_prompt(
    module_name: str,
    urls: Sequence[str],
    batch_number: int,
    start_index: int,
) -> str:
    """Generate a model-agnostic external LLM batch prompt."""

    # TODO: Build prompt text for ChatGPT, Gemini web, Claude, Perplexity, or any LLM.
    raise NotImplementedError("External LLM batch prompt generation is not implemented in the skeleton.")
