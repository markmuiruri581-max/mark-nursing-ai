"""Local-only keyword search helpers for MNCH Manager v5."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any

from _toolbox import extraction, library, paths, security


SEARCH_INDEX_SCHEMA_VERSION = 1
SEARCH_INDEX_FILENAME = "index.json"
TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


@dataclass(frozen=True)
class SearchIndexResult:
    """Result from building a local keyword index."""

    index_path: Path
    indexed_source_count: int
    document_count: int
    term_count: int


@dataclass(frozen=True)
class SearchMatch:
    """One keyword search match."""

    source_id: str
    original_filename: str
    stored_filename: str
    match_count: int
    matched_terms: list[str]
    snippet: str
    metadata_path: str
    extracted_text_path: str


def tokenize_text(text: str) -> list[str]:
    """Return lowercase keyword tokens from local text."""

    return TOKEN_PATTERN.findall(text.lower())


def unique_query_terms(query: str) -> list[str]:
    """Return de-duplicated query terms in input order."""

    terms: list[str] = []
    seen: set[str] = set()
    for term in tokenize_text(query):
        if term not in seen:
            terms.append(term)
            seen.add(term)
    return terms


def get_search_index_path(module_dir: Path) -> Path:
    """Return the generated search index path for one module."""

    return paths.get_research_module_paths(module_dir).search_index_dir / SEARCH_INDEX_FILENAME


def resolve_workspace_relative_file(workspace_root: Path, relative_path: str) -> Path:
    """Resolve a workspace-relative file path safely."""

    cleaned_path = relative_path.strip()
    if not cleaned_path:
        raise ValueError("Workspace-relative path cannot be blank.")
    resolved = security.assert_safe_local_path(workspace_root, workspace_root / cleaned_path)
    if not resolved.is_file():
        raise FileNotFoundError(f"Local file does not exist: {resolved}")
    return resolved


def is_within_directory(parent: Path, child: Path) -> bool:
    """Return True when child is inside parent."""

    try:
        child.relative_to(parent.resolve(strict=False))
    except ValueError:
        return False
    return True


def resolve_extracted_text_file(
    workspace_root: Path,
    module_dir: Path,
    relative_path: str,
) -> Path:
    """Resolve an extracted text path only when it stays in 10_extracted_text."""

    text_path = resolve_workspace_relative_file(workspace_root, relative_path)
    extracted_text_dir = paths.get_research_module_paths(module_dir).extracted_text_dir
    if not is_within_directory(extracted_text_dir, text_path):
        raise ValueError(f"Extracted text path is outside 10_extracted_text: {text_path}")
    return text_path


def build_snippet(text: str, query_terms: list[str], radius: int = 80) -> str:
    """Return compact context around the first keyword match."""

    normalized_text = " ".join(text.split())
    if not normalized_text:
        return ""
    lowered_text = normalized_text.lower()
    first_match = None
    for term in query_terms:
        match = re.search(re.escape(term), lowered_text)
        if match and (first_match is None or match.start() < first_match.start()):
            first_match = match
    if first_match is None:
        return normalized_text[: radius * 2].strip()

    start = max(0, first_match.start() - radius)
    end = min(len(normalized_text), first_match.end() + radius)
    prefix = "..." if start > 0 else ""
    suffix = "..." if end < len(normalized_text) else ""
    return f"{prefix}{normalized_text[start:end].strip()}{suffix}"


def build_index_document(
    workspace_root: Path,
    module_dir: Path,
    source_record: dict[str, Any],
) -> tuple[dict[str, Any], Counter[str]] | None:
    """Build one index document from an extracted source record."""

    if source_record.get("extraction_status") != extraction.EXTRACTION_STATUS_EXTRACTED:
        return None
    extracted_text_path = str(source_record.get("extracted_text_path", "")).strip()
    if not extracted_text_path:
        return None

    try:
        text_path = resolve_extracted_text_file(workspace_root, module_dir, extracted_text_path)
    except (FileNotFoundError, ValueError):
        return None

    text = text_path.read_text(encoding="utf-8", errors="replace")
    term_counts = Counter(tokenize_text(text))
    source_id = str(source_record.get("source_id", "")).strip()
    metadata_path = str(source_record.get("metadata_path", "")).strip()
    document = {
        "source_id": source_id,
        "original_filename": str(source_record.get("original_filename", "")),
        "stored_filename": str(source_record.get("stored_filename", "")),
        "metadata_path": metadata_path,
        "extracted_text_path": extracted_text_path,
        "text_char_count": len(text),
        "token_count": sum(term_counts.values()),
    }
    return document, term_counts


def build_index_data(
    workspace_root: Path,
    module_dir: Path,
    *,
    built_at: str,
) -> dict[str, Any]:
    """Build local keyword index data from extracted text records."""

    research_paths = paths.get_research_module_paths(module_dir)
    manifest = library.read_library_manifest(research_paths.manifest)
    documents: list[dict[str, Any]] = []
    terms: dict[str, dict[str, int]] = {}
    for source_record in library.get_manifest_sources(manifest):
        document_and_terms = build_index_document(workspace_root, module_dir, source_record)
        if document_and_terms is None:
            continue
        document, term_counts = document_and_terms
        source_id = document["source_id"]
        documents.append(document)
        for term, count in term_counts.items():
            terms.setdefault(term, {})[source_id] = count

    documents.sort(key=lambda document: document["source_id"])
    return {
        "schema_version": SEARCH_INDEX_SCHEMA_VERSION,
        "module_path": paths.relative_to_workspace(workspace_root, module_dir),
        "built_at": built_at,
        "local_only": True,
        "api_enabled": False,
        "network_enabled": False,
        "indexed_source_count": len(documents),
        "document_count": len(documents),
        "term_count": len(terms),
        "documents": documents,
        "terms": dict(sorted(terms.items())),
    }


def write_search_index(index_path: Path, index_data: dict[str, Any]) -> None:
    """Write or refresh the generated local search index."""

    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(
        json.dumps(index_data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def build_local_search_index(
    workspace_root: Path,
    module_dir: Path,
    *,
    built_at: str,
) -> SearchIndexResult:
    """Build and store a local keyword index for one module."""

    security.assert_safe_local_path(workspace_root, module_dir)
    index_path = get_search_index_path(module_dir)
    security.assert_safe_local_path(workspace_root, index_path)
    index_data = build_index_data(workspace_root, module_dir, built_at=built_at)
    write_search_index(index_path, index_data)
    return SearchIndexResult(
        index_path=index_path,
        indexed_source_count=int(index_data["indexed_source_count"]),
        document_count=int(index_data["document_count"]),
        term_count=int(index_data["term_count"]),
    )


def read_search_index(index_path: Path) -> dict[str, Any]:
    """Read a generated local search index."""

    return json.loads(index_path.read_text(encoding="utf-8"))


def search_local_index(
    workspace_root: Path,
    module_dir: Path,
    query: str,
    *,
    limit: int = 10,
) -> list[SearchMatch]:
    """Search a generated local keyword index."""

    query_terms = unique_query_terms(query)
    if not query_terms:
        return []

    index_path = get_search_index_path(module_dir)
    security.assert_safe_local_path(workspace_root, index_path)
    index_data = read_search_index(index_path)
    terms = index_data.get("terms", {})
    if not isinstance(terms, dict):
        return []
    documents = {
        document.get("source_id"): document
        for document in index_data.get("documents", [])
        if isinstance(document, dict)
    }

    source_matches: dict[str, dict[str, Any]] = {}
    for term in query_terms:
        source_counts = terms.get(term, {})
        if not isinstance(source_counts, dict):
            continue
        for source_id, count in source_counts.items():
            match = source_matches.setdefault(
                str(source_id),
                {"match_count": 0, "matched_terms": []},
            )
            match["match_count"] += int(count)
            match["matched_terms"].append(term)

    matches: list[SearchMatch] = []
    for source_id, match_data in source_matches.items():
        document = documents.get(source_id)
        if not document:
            continue
        text_path = resolve_extracted_text_file(
            workspace_root,
            module_dir,
            str(document.get("extracted_text_path", "")),
        )
        text = text_path.read_text(encoding="utf-8", errors="replace")
        matched_terms = list(dict.fromkeys(match_data["matched_terms"]))
        matches.append(
            SearchMatch(
                source_id=source_id,
                original_filename=str(document.get("original_filename", "")),
                stored_filename=str(document.get("stored_filename", "")),
                match_count=int(match_data["match_count"]),
                matched_terms=matched_terms,
                snippet=build_snippet(text, matched_terms),
                metadata_path=str(document.get("metadata_path", "")),
                extracted_text_path=str(document.get("extracted_text_path", "")),
            )
        )

    return sorted(matches, key=lambda match: (-match.match_count, match.source_id))[:limit]
