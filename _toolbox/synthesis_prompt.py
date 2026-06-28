"""Local-only external synthesis prompt builder for MNCH Manager v5."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any

from _toolbox import paths, readiness, review, security


SOURCE_MAP_SCHEMA_VERSION = 1
EXTERNAL_SYNTHESIS_PROMPT_FILENAME = "external_synthesis_prompt.md"
SOURCE_MAP_FILENAME = "source_map.json"
DEFAULT_EXCERPT_CHAR_LIMIT_PER_SOURCE = 4000
DEFAULT_TOTAL_EXCERPT_CHAR_LIMIT = 40000


@dataclass(frozen=True)
class PreparedSource:
    """One validated source prepared for the external synthesis prompt."""

    source_map_entry: dict[str, Any]
    excerpt: str


@dataclass(frozen=True)
class SynthesisPromptResult:
    """Result from writing the local external synthesis prompt files."""

    prompt_path: Path
    source_map_path: Path
    source_count: int
    source_map: dict[str, Any]


def get_prompt_path(module_dir: Path) -> Path:
    """Return the generated external synthesis prompt path."""

    return (
        paths.get_research_module_paths(module_dir).synthesis_prompts_dir
        / EXTERNAL_SYNTHESIS_PROMPT_FILENAME
    )


def get_source_map_path(module_dir: Path) -> Path:
    """Return the generated external synthesis source-map path."""

    return paths.get_research_module_paths(module_dir).synthesis_prompts_dir / SOURCE_MAP_FILENAME


def read_candidate_manifest(path: Path) -> dict[str, Any]:
    """Read the local synthesis candidate manifest."""

    return json.loads(path.read_text(encoding="utf-8"))


def normalize_excerpt_text(text: str) -> str:
    """Normalize local extracted text for prompt-readable excerpts."""

    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    normalized = "\n".join(re.sub(r"[ \t]+", " ", line).strip() for line in normalized.split("\n"))
    normalized = re.sub(r"\n{3,}", "\n\n", normalized).strip()
    return normalized


def safe_manifest_path(workspace_root: Path, raw_path: str) -> str:
    """Validate a non-empty manifest path without reading its content."""

    cleaned_path = raw_path.strip()
    if not cleaned_path:
        return ""
    security.assert_safe_local_path(workspace_root, workspace_root / cleaned_path)
    return cleaned_path


def validate_candidate_record(
    workspace_root: Path,
    module_dir: Path,
    candidate: dict[str, Any],
    current_readiness_by_source: dict[str, dict[str, Any]],
) -> tuple[str, Path]:
    """Validate one candidate and return its source ID and extracted text path."""

    source_id = review.validate_source_id(str(candidate.get("source_id", "")))
    if candidate.get("readiness_status") != readiness.READINESS_STATUS_READY:
        raise ValueError(f"Candidate is not READY: {source_id}")

    current_record = current_readiness_by_source.get(source_id)
    if current_record is None:
        raise ValueError(f"Candidate source is missing from current readiness: {source_id}")
    if current_record.get("readiness_status") != readiness.READINESS_STATUS_READY:
        raise ValueError(f"Current readiness is not READY for candidate: {source_id}")

    candidate_extracted_text_path = str(candidate.get("extracted_text_path", "")).strip()
    current_extracted_text_path = str(current_record.get("extracted_text_path", "")).strip()
    if candidate_extracted_text_path != current_extracted_text_path:
        raise ValueError(f"Candidate extracted text path is stale for {source_id}.")

    try:
        extracted_text_path = readiness.resolve_extracted_text_path(
            workspace_root,
            module_dir,
            candidate_extracted_text_path,
        )
    except (FileNotFoundError, ValueError) as exc:
        raise ValueError(f"Invalid extracted text path for candidate {source_id}: {exc}") from exc
    safe_manifest_path(workspace_root, str(candidate.get("metadata_path", "")))
    return source_id, extracted_text_path


def build_prepared_sources(
    workspace_root: Path,
    module_dir: Path,
    candidates: list[dict[str, Any]],
    current_readiness_by_source: dict[str, dict[str, Any]],
    *,
    excerpt_char_limit_per_source: int,
    total_excerpt_char_limit: int,
) -> list[PreparedSource]:
    """Build validated source-map entries and excerpts without writing files."""

    prepared_sources: list[PreparedSource] = []
    remaining_total_chars = total_excerpt_char_limit
    for candidate in candidates:
        source_id, extracted_text_path = validate_candidate_record(
            workspace_root,
            module_dir,
            candidate,
            current_readiness_by_source,
        )
        source_text = extracted_text_path.read_text(encoding="utf-8")
        normalized_excerpt_source = normalize_excerpt_text(source_text)
        allowed_chars = max(0, min(excerpt_char_limit_per_source, remaining_total_chars))
        excerpt = normalized_excerpt_source[:allowed_chars]
        remaining_total_chars -= len(excerpt)
        excerpt_truncated = len(excerpt) < len(normalized_excerpt_source)

        prepared_sources.append(
            PreparedSource(
                source_map_entry={
                    "source_id": source_id,
                    "source_type": str(candidate.get("source_type", "")),
                    "review_status": str(candidate.get("review_status", "")),
                    "extraction_status": str(candidate.get("extraction_status", "")),
                    "original_filename": str(candidate.get("original_filename", "")),
                    "stored_filename": str(candidate.get("stored_filename", "")),
                    "metadata_path": safe_manifest_path(
                        workspace_root,
                        str(candidate.get("metadata_path", "")),
                    ),
                    "extracted_text_path": str(candidate.get("extracted_text_path", "")).strip(),
                    "included_excerpt_char_count": len(excerpt),
                    "source_text_char_count": len(source_text),
                    "excerpt_truncated": excerpt_truncated,
                },
                excerpt=excerpt,
            )
        )
    return prepared_sources


def build_source_map_data(
    workspace_root: Path,
    module_dir: Path,
    *,
    created_at: str,
    candidate_manifest_path: Path,
    prompt_path: Path,
    prepared_sources: list[PreparedSource],
    excerpt_char_limit_per_source: int,
    total_excerpt_char_limit: int,
) -> dict[str, Any]:
    """Build source-map JSON data without writing it."""

    return {
        "schema_version": SOURCE_MAP_SCHEMA_VERSION,
        "module_path": paths.relative_to_workspace(workspace_root, module_dir),
        "created_at": created_at,
        "candidate_manifest_path": paths.relative_to_workspace(
            workspace_root,
            candidate_manifest_path,
        ),
        "prompt_path": paths.relative_to_workspace(workspace_root, prompt_path),
        "local_only": True,
        "api_enabled": False,
        "network_enabled": False,
        "excerpt_char_limit_per_source": excerpt_char_limit_per_source,
        "total_excerpt_char_limit": total_excerpt_char_limit,
        "source_count": len(prepared_sources),
        "sources": [source.source_map_entry for source in prepared_sources],
    }


def build_prompt_text(source_map: dict[str, Any], prepared_sources: list[PreparedSource]) -> str:
    """Build the external LLM prompt text without generating synthesis."""

    source_lines = []
    for source in prepared_sources:
        entry = source.source_map_entry
        source_lines.append(
            "- {source_id}: type={source_type}; review={review_status}; "
            "extraction={extraction_status}; original={original_filename}; "
            "excerpt_chars={included_excerpt_char_count}; truncated={excerpt_truncated}".format(
                **entry
            )
        )

    excerpt_blocks = []
    for source in prepared_sources:
        source_id = source.source_map_entry["source_id"]
        excerpt_blocks.append(f"## {source_id}\n\n{source.excerpt}")

    source_summary = "\n".join(source_lines) if source_lines else "- No READY sources were included."
    excerpts = "\n\n".join(excerpt_blocks) if excerpt_blocks else "No excerpts were included."
    return (
        "# External Synthesis Prompt\n\n"
        "## Instructions for the external LLM\n\n"
        "Synthesize the module topic using only the source excerpts included below. "
        "Do not use outside knowledge, network access, DOI lookup, web browsing, or any "
        "source that is not included in this prompt. Cite every factual claim with the "
        "source ID in square brackets, for example [SRC-0005]. Do not invent uncited "
        "claims. If the excerpts do not support a point, say that the included excerpts "
        "do not provide enough evidence.\n\n"
        "Do not include manual note text, review JSON content, or local file paths in "
        "the synthesized answer. The source map summary is provided only to track which "
        "local excerpts were included.\n\n"
        "## Local-Only Provenance\n\n"
        "This prompt was generated from already-extracted local text files referenced by "
        "READY records in the local synthesis candidate manifest. No APIs, network "
        "requests, URL downloads, DOI resolution, AI summarization, semantic search, "
        "vector search, Q&A generation, synthesis generation, or study-pack generation "
        "ran while building this prompt.\n\n"
        "## Source Map Summary\n\n"
        f"- Candidate manifest: {source_map['candidate_manifest_path']}\n"
        f"- Source map path: {source_map['prompt_path'].replace(EXTERNAL_SYNTHESIS_PROMPT_FILENAME, SOURCE_MAP_FILENAME)}\n"
        f"- Source count: {source_map['source_count']}\n"
        f"- Excerpt char limit per source: {source_map['excerpt_char_limit_per_source']}\n"
        f"- Total excerpt char limit: {source_map['total_excerpt_char_limit']}\n\n"
        f"{source_summary}\n\n"
        "## Bounded Source Excerpts\n\n"
        f"{excerpts}\n"
    )


def build_synthesis_prompt_data(
    workspace_root: Path,
    module_dir: Path,
    *,
    created_at: str,
    excerpt_char_limit_per_source: int = DEFAULT_EXCERPT_CHAR_LIMIT_PER_SOURCE,
    total_excerpt_char_limit: int = DEFAULT_TOTAL_EXCERPT_CHAR_LIMIT,
) -> tuple[Path, Path, str, dict[str, Any]]:
    """Validate candidates and build both output payloads without writing files."""

    if excerpt_char_limit_per_source < 0:
        raise ValueError("Excerpt char limit per source cannot be negative.")
    if total_excerpt_char_limit < 0:
        raise ValueError("Total excerpt char limit cannot be negative.")

    security.assert_safe_local_path(workspace_root, module_dir)
    candidate_manifest_path = readiness.get_candidate_manifest_path(module_dir)
    prompt_path = get_prompt_path(module_dir)
    source_map_path = get_source_map_path(module_dir)
    security.assert_safe_local_path(workspace_root, candidate_manifest_path)
    security.assert_safe_local_path(workspace_root, prompt_path)
    security.assert_safe_local_path(workspace_root, source_map_path)

    candidate_manifest = read_candidate_manifest(candidate_manifest_path)
    raw_candidates = candidate_manifest.get("candidates", [])
    if not isinstance(raw_candidates, list):
        raise ValueError("Candidate manifest candidates must be a list.")
    candidates = [candidate for candidate in raw_candidates if isinstance(candidate, dict)]
    if len(candidates) != len(raw_candidates):
        raise ValueError("Candidate manifest contains a non-object candidate.")

    current_records, _ = readiness.build_readiness_records(
        workspace_root,
        module_dir,
        read_at=created_at,
    )
    current_readiness_by_source = {
        record["source_id"]: record for record in current_records
    }
    prepared_sources = build_prepared_sources(
        workspace_root,
        module_dir,
        candidates,
        current_readiness_by_source,
        excerpt_char_limit_per_source=excerpt_char_limit_per_source,
        total_excerpt_char_limit=total_excerpt_char_limit,
    )
    source_map = build_source_map_data(
        workspace_root,
        module_dir,
        created_at=created_at,
        candidate_manifest_path=candidate_manifest_path,
        prompt_path=prompt_path,
        prepared_sources=prepared_sources,
        excerpt_char_limit_per_source=excerpt_char_limit_per_source,
        total_excerpt_char_limit=total_excerpt_char_limit,
    )
    prompt_text = build_prompt_text(source_map, prepared_sources)
    return prompt_path, source_map_path, prompt_text, source_map


def write_prompt_outputs(prompt_path: Path, source_map_path: Path, prompt_text: str, source_map: dict[str, Any]) -> None:
    """Write generated external synthesis prompt files."""

    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    prompt_path.write_text(prompt_text, encoding="utf-8", newline="\n")
    source_map_path.write_text(
        json.dumps(source_map, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def build_external_synthesis_prompt(
    workspace_root: Path,
    module_dir: Path,
    *,
    created_at: str,
    excerpt_char_limit_per_source: int = DEFAULT_EXCERPT_CHAR_LIMIT_PER_SOURCE,
    total_excerpt_char_limit: int = DEFAULT_TOTAL_EXCERPT_CHAR_LIMIT,
) -> SynthesisPromptResult:
    """Build and write local-only external synthesis prompt files."""

    prompt_path, source_map_path, prompt_text, source_map = build_synthesis_prompt_data(
        workspace_root,
        module_dir,
        created_at=created_at,
        excerpt_char_limit_per_source=excerpt_char_limit_per_source,
        total_excerpt_char_limit=total_excerpt_char_limit,
    )
    write_prompt_outputs(prompt_path, source_map_path, prompt_text, source_map)
    return SynthesisPromptResult(
        prompt_path=prompt_path,
        source_map_path=source_map_path,
        source_count=int(source_map["source_count"]),
        source_map=source_map,
    )
