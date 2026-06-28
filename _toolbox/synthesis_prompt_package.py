"""Local-only chunked external synthesis prompt packages for MNCH Manager v5."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
import re
import shutil
from typing import Any

from _toolbox import paths, readiness, security, synthesis_prompt


PACKAGE_MANIFEST_SCHEMA_VERSION = 1
DEFAULT_CHUNK_CHAR_LIMIT = 12000
INSTRUCTIONS_FILENAME = "instructions.md"
PACKAGE_MANIFEST_FILENAME = "package_manifest.json"
PACKAGE_DIR_PREFIX = "package_"
TEMP_PACKAGE_DIR_PREFIX = ".tmp_package_"


@dataclass(frozen=True)
class PreparedChunk:
    """One source chunk prepared for a package."""

    chunk_id: str
    relative_chunk_path: str
    text: str
    char_start: int
    char_end: int


@dataclass(frozen=True)
class PreparedPackageSource:
    """One validated source prepared for chunked package output."""

    source_entry: dict[str, Any]
    chunks: list[PreparedChunk]


@dataclass(frozen=True)
class SynthesisPromptPackageResult:
    """Result from writing a local chunked prompt package."""

    package_dir: Path
    instructions_path: Path
    manifest_path: Path
    source_count: int
    chunk_count: int
    manifest: dict[str, Any]


def get_packages_root(module_dir: Path) -> Path:
    """Return the generated chunked package root for a module."""

    return paths.get_research_module_paths(module_dir).synthesis_prompt_packages_dir


def sanitize_package_timestamp(created_at: str) -> str:
    """Return a Windows-safe package timestamp such as YYYYMMDDTHHMMSS."""

    try:
        parsed = datetime.fromisoformat(created_at)
        return parsed.strftime("%Y%m%dT%H%M%S")
    except ValueError:
        cleaned = re.sub(r"[^0-9T]", "", created_at)
        match = re.search(r"(\d{8}T\d{6})", cleaned)
        if match:
            return match.group(1)
    return datetime.now().astimezone().strftime("%Y%m%dT%H%M%S")


def build_unique_package_dir(packages_root: Path, created_at: str) -> Path:
    """Return a final package directory path without overwriting existing output."""

    base_name = f"{PACKAGE_DIR_PREFIX}{sanitize_package_timestamp(created_at)}"
    candidate = packages_root / base_name
    if not candidate.exists():
        return candidate
    for sequence_number in range(2, 1000):
        candidate = packages_root / f"{base_name}_{sequence_number:02d}"
        if not candidate.exists():
            return candidate
    raise FileExistsError(f"Could not choose a unique package folder for: {base_name}")


def split_long_text(text: str, limit: int, *, start_offset: int) -> list[tuple[str, int, int]]:
    """Split one over-limit text segment into hard character chunks."""

    chunks: list[tuple[str, int, int]] = []
    offset = 0
    while offset < len(text):
        chunk_text = text[offset : offset + limit]
        chunk_start = start_offset + offset
        chunks.append((chunk_text, chunk_start, chunk_start + len(chunk_text)))
        offset += len(chunk_text)
    return chunks


def paragraph_spans(text: str) -> list[tuple[str, int, int]]:
    """Return paragraph spans from normalized text."""

    spans: list[tuple[str, int, int]] = []
    offset = 0
    for paragraph in text.split("\n\n"):
        start = offset
        end = start + len(paragraph)
        if paragraph:
            spans.append((paragraph, start, end))
        offset = end + 2
    return spans


def chunk_text_by_paragraphs(text: str, chunk_char_limit: int) -> list[tuple[str, int, int]]:
    """Chunk normalized text, preferring paragraph boundaries."""

    if chunk_char_limit <= 0:
        raise ValueError("Chunk char limit must be greater than zero.")
    if not text:
        return []

    chunks: list[tuple[str, int, int]] = []
    current_parts: list[str] = []
    current_start = 0
    current_end = 0

    def flush_current() -> None:
        nonlocal current_parts, current_start, current_end
        if current_parts:
            chunk_text = "\n\n".join(current_parts)
            chunks.append((chunk_text, current_start, current_end))
            current_parts = []

    for paragraph, paragraph_start, paragraph_end in paragraph_spans(text):
        if len(paragraph) > chunk_char_limit:
            flush_current()
            chunks.extend(split_long_text(paragraph, chunk_char_limit, start_offset=paragraph_start))
            continue

        separator_length = 2 if current_parts else 0
        current_length = sum(len(part) for part in current_parts) + max(0, len(current_parts) - 1) * 2
        if current_parts and current_length + separator_length + len(paragraph) > chunk_char_limit:
            flush_current()

        if not current_parts:
            current_start = paragraph_start
        current_parts.append(paragraph)
        current_end = paragraph_end

    flush_current()
    return chunks


def build_prepared_package_sources(
    workspace_root: Path,
    module_dir: Path,
    candidates: list[dict[str, Any]],
    current_readiness_by_source: dict[str, dict[str, Any]],
    *,
    chunk_char_limit: int,
    package_dir: Path,
) -> list[PreparedPackageSource]:
    """Build validated package source data and chunks without writing files."""

    prepared_sources: list[PreparedPackageSource] = []
    for candidate in candidates:
        source_id, extracted_text_path = synthesis_prompt.validate_candidate_record(
            workspace_root,
            module_dir,
            candidate,
            current_readiness_by_source,
        )
        source_text = extracted_text_path.read_text(encoding="utf-8")
        normalized_text = synthesis_prompt.normalize_excerpt_text(source_text)
        chunk_spans = chunk_text_by_paragraphs(normalized_text, chunk_char_limit)
        chunks: list[PreparedChunk] = []
        chunk_entries: list[dict[str, Any]] = []
        for index, (chunk_text, char_start, char_end) in enumerate(chunk_spans, start=1):
            chunk_id = f"{source_id}_CHUNK-{index:04d}"
            chunk_path = package_dir / "sources" / source_id / f"{chunk_id}.md"
            relative_chunk_path = paths.relative_to_workspace(workspace_root, chunk_path)
            chunks.append(
                PreparedChunk(
                    chunk_id=chunk_id,
                    relative_chunk_path=relative_chunk_path,
                    text=chunk_text,
                    char_start=char_start,
                    char_end=char_end,
                )
            )
            chunk_entries.append(
                {
                    "chunk_id": chunk_id,
                    "chunk_path": relative_chunk_path,
                    "char_start": char_start,
                    "char_end": char_end,
                    "char_count": len(chunk_text),
                }
            )
        prepared_sources.append(
            PreparedPackageSource(
                source_entry={
                    "source_id": source_id,
                    "source_type": str(candidate.get("source_type", "")),
                    "review_status": str(candidate.get("review_status", "")),
                    "extraction_status": str(candidate.get("extraction_status", "")),
                    "original_filename": str(candidate.get("original_filename", "")),
                    "stored_filename": str(candidate.get("stored_filename", "")),
                    "metadata_path": synthesis_prompt.safe_manifest_path(
                        workspace_root,
                        str(candidate.get("metadata_path", "")),
                    ),
                    "extracted_text_path": str(candidate.get("extracted_text_path", "")).strip(),
                    "source_text_char_count": len(source_text),
                    "chunk_count": len(chunks),
                    "chunks": chunk_entries,
                },
                chunks=chunks,
            )
        )
    return prepared_sources


def build_manifest_data(
    workspace_root: Path,
    module_dir: Path,
    *,
    created_at: str,
    candidate_manifest_path: Path,
    package_dir: Path,
    instructions_path: Path,
    prepared_sources: list[PreparedPackageSource],
    chunk_char_limit: int,
) -> dict[str, Any]:
    """Build package manifest data without writing it."""

    chunk_count = sum(len(source.chunks) for source in prepared_sources)
    return {
        "schema_version": PACKAGE_MANIFEST_SCHEMA_VERSION,
        "module_path": paths.relative_to_workspace(workspace_root, module_dir),
        "created_at": created_at,
        "candidate_manifest_path": paths.relative_to_workspace(
            workspace_root,
            candidate_manifest_path,
        ),
        "instructions_path": paths.relative_to_workspace(workspace_root, instructions_path),
        "package_dir": paths.relative_to_workspace(workspace_root, package_dir),
        "local_only": True,
        "api_enabled": False,
        "network_enabled": False,
        "chunk_char_limit": chunk_char_limit,
        "source_count": len(prepared_sources),
        "chunk_count": chunk_count,
        "sources": [source.source_entry for source in prepared_sources],
    }


def build_instructions_text(manifest: dict[str, Any]) -> str:
    """Build external LLM package instructions without generating synthesis."""

    source_lines = []
    for source in manifest["sources"]:
        chunk_ids = ", ".join(chunk["chunk_id"] for chunk in source["chunks"])
        source_lines.append(
            f"- {source['source_id']}: {source['chunk_count']} chunks; chunks: {chunk_ids}"
        )
    source_index = "\n".join(source_lines) if source_lines else "- No READY sources were included."
    return (
        "# Chunked External Synthesis Prompt Package\n\n"
        "## Instructions for the external LLM\n\n"
        "Synthesize the module topic using only the included chunk files. Do not use "
        "outside knowledge, network access, DOI lookup, web browsing, or any source "
        "not included in this package. Cite every factual claim with the chunk ID in "
        "square brackets, for example [SRC-0005_CHUNK-0001]. Do not invent uncited "
        "claims. If the package chunks do not support a point, say the included chunks "
        "do not provide enough evidence.\n\n"
        "Do not include local file paths, review JSON content, or manual note text in "
        "the synthesized answer. The source and chunk index is provided only to track "
        "which local extracted text chunks are included.\n\n"
        "## Recommended External LLM Workflow\n\n"
        "Upload or paste `instructions.md` first, then upload or paste all files under "
        "`sources/`. Ask the external LLM to follow these instructions exactly. This "
        "package can be used with ChatGPT, Claude, Gemini, or another LLM that accepts "
        "multiple files or pasted text.\n\n"
        "## Local-Only Provenance\n\n"
        "This package was generated from already-extracted local text files referenced "
        "by READY records in the local synthesis candidate manifest. No APIs, network "
        "requests, URL downloads, DOI resolution, AI summarization, semantic search, "
        "vector search, Q&A generation, synthesis generation, or study-pack generation "
        "ran while building this package.\n\n"
        "## Source And Chunk Index\n\n"
        f"- Candidate manifest: {manifest['candidate_manifest_path']}\n"
        f"- Package directory: {manifest['package_dir']}\n"
        f"- Source count: {manifest['source_count']}\n"
        f"- Chunk count: {manifest['chunk_count']}\n"
        f"- Chunk char limit: {manifest['chunk_char_limit']}\n\n"
        f"{source_index}\n"
    )


def build_package_data(
    workspace_root: Path,
    module_dir: Path,
    *,
    created_at: str,
    chunk_char_limit: int = DEFAULT_CHUNK_CHAR_LIMIT,
) -> tuple[Path, Path, Path, str, dict[str, Any], list[PreparedPackageSource]]:
    """Validate candidates and build all package payloads without writing files."""

    if chunk_char_limit <= 0:
        raise ValueError("Chunk char limit must be greater than zero.")

    security.assert_safe_local_path(workspace_root, module_dir)
    packages_root = get_packages_root(module_dir)
    security.assert_safe_local_path(workspace_root, packages_root)
    package_dir = build_unique_package_dir(packages_root, created_at)
    instructions_path = package_dir / INSTRUCTIONS_FILENAME
    manifest_path = package_dir / PACKAGE_MANIFEST_FILENAME
    candidate_manifest_path = readiness.get_candidate_manifest_path(module_dir)
    security.assert_safe_local_path(workspace_root, candidate_manifest_path)
    security.assert_safe_local_path(workspace_root, package_dir)
    security.assert_safe_local_path(workspace_root, instructions_path)
    security.assert_safe_local_path(workspace_root, manifest_path)

    candidate_manifest = synthesis_prompt.read_candidate_manifest(candidate_manifest_path)
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
    prepared_sources = build_prepared_package_sources(
        workspace_root,
        module_dir,
        candidates,
        current_readiness_by_source,
        chunk_char_limit=chunk_char_limit,
        package_dir=package_dir,
    )
    manifest = build_manifest_data(
        workspace_root,
        module_dir,
        created_at=created_at,
        candidate_manifest_path=candidate_manifest_path,
        package_dir=package_dir,
        instructions_path=instructions_path,
        prepared_sources=prepared_sources,
        chunk_char_limit=chunk_char_limit,
    )
    instructions_text = build_instructions_text(manifest)
    temp_package_dir = packages_root / f"{TEMP_PACKAGE_DIR_PREFIX}{package_dir.name}"
    security.assert_safe_local_path(workspace_root, temp_package_dir)
    return package_dir, temp_package_dir, manifest_path, instructions_text, manifest, prepared_sources


def write_package_outputs(
    package_dir: Path,
    temp_package_dir: Path,
    manifest_path: Path,
    instructions_text: str,
    manifest: dict[str, Any],
    prepared_sources: list[PreparedPackageSource],
) -> None:
    """Write package files through a temporary directory, then rename atomically."""

    if package_dir.exists():
        raise FileExistsError(f"Refusing to overwrite existing package folder: {package_dir}")
    if temp_package_dir.exists():
        shutil.rmtree(temp_package_dir)
    try:
        temp_package_dir.mkdir(parents=True, exist_ok=False)
        (temp_package_dir / INSTRUCTIONS_FILENAME).write_text(
            instructions_text,
            encoding="utf-8",
            newline="\n",
        )
        for source in prepared_sources:
            source_dir = temp_package_dir / "sources" / source.source_entry["source_id"]
            source_dir.mkdir(parents=True, exist_ok=True)
            for chunk in source.chunks:
                chunk_path = source_dir / f"{chunk.chunk_id}.md"
                chunk_path.write_text(chunk.text, encoding="utf-8", newline="\n")
        (temp_package_dir / PACKAGE_MANIFEST_FILENAME).write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        temp_package_dir.rename(package_dir)
    except Exception:
        if temp_package_dir.exists():
            shutil.rmtree(temp_package_dir)
        raise


def build_chunked_synthesis_prompt_package(
    workspace_root: Path,
    module_dir: Path,
    *,
    created_at: str,
    chunk_char_limit: int = DEFAULT_CHUNK_CHAR_LIMIT,
) -> SynthesisPromptPackageResult:
    """Build and write a local-only chunked external synthesis prompt package."""

    package_dir, temp_package_dir, manifest_path, instructions_text, manifest, prepared_sources = (
        build_package_data(
            workspace_root,
            module_dir,
            created_at=created_at,
            chunk_char_limit=chunk_char_limit,
        )
    )
    write_package_outputs(
        package_dir,
        temp_package_dir,
        manifest_path,
        instructions_text,
        manifest,
        prepared_sources,
    )
    return SynthesisPromptPackageResult(
        package_dir=package_dir,
        instructions_path=package_dir / INSTRUCTIONS_FILENAME,
        manifest_path=package_dir / PACKAGE_MANIFEST_FILENAME,
        source_count=int(manifest["source_count"]),
        chunk_count=int(manifest["chunk_count"]),
        manifest=manifest,
    )
