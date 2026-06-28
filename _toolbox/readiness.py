"""Local-only synthesis readiness helpers for MNCH Manager v5."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from _toolbox import extraction, library, paths, review, search, security


READINESS_SCHEMA_VERSION = 1
CANDIDATE_MANIFEST_FILENAME = "synthesis_candidates.json"

READINESS_STATUS_READY = "READY"
READINESS_STATUS_REJECTED = "REJECTED"
READINESS_STATUS_NEEDS_REVIEW = "NEEDS_REVIEW"
READINESS_STATUS_NEEDS_FOLLOW_UP = "NEEDS_FOLLOW_UP"
READINESS_STATUS_NEEDS_EXTRACTION = "NEEDS_EXTRACTION"
READINESS_STATUS_REGISTERED_ONLY = "REGISTERED_ONLY"

EXTRACTION_STATUS_MISSING = "MISSING"

SEARCH_INDEX_STATUS_INDEXED = "INDEXED"
SEARCH_INDEX_STATUS_NOT_INDEXED = "NOT_INDEXED"
SEARCH_INDEX_STATUS_INDEX_MISSING = "INDEX_MISSING"
SEARCH_INDEX_STATUS_INDEX_UNREADABLE = "INDEX_UNREADABLE"


@dataclass(frozen=True)
class ReadinessFilters:
    """Optional local filters for synthesis readiness records."""

    review_status: str = ""
    extraction_status: str = ""
    source_type: str = ""
    ready_only: bool = False


@dataclass(frozen=True)
class CandidateManifestResult:
    """Result from writing a local synthesis candidate manifest."""

    manifest_path: Path
    candidate_count: int
    source_count: int
    manifest: dict[str, Any]


def get_candidate_manifest_path(module_dir: Path) -> Path:
    """Return the generated synthesis candidate manifest path."""

    return (
        paths.get_research_module_paths(module_dir).synthesis_candidates_dir
        / CANDIDATE_MANIFEST_FILENAME
    )


def normalize_filters(filters: ReadinessFilters | None) -> ReadinessFilters:
    """Return filters with normalized enum-like values."""

    if filters is None:
        return ReadinessFilters()
    return ReadinessFilters(
        review_status=filters.review_status.strip().upper(),
        extraction_status=filters.extraction_status.strip().upper(),
        source_type=filters.source_type.strip(),
        ready_only=filters.ready_only,
    )


def load_indexed_source_ids(module_dir: Path) -> tuple[set[str], str]:
    """Return indexed source IDs and the module-wide search index status."""

    index_path = search.get_search_index_path(module_dir)
    if not index_path.exists():
        return set(), SEARCH_INDEX_STATUS_INDEX_MISSING

    try:
        index_data = search.read_search_index(index_path)
    except (OSError, json.JSONDecodeError):
        return set(), SEARCH_INDEX_STATUS_INDEX_UNREADABLE

    documents = index_data.get("documents", [])
    if not isinstance(documents, list):
        return set(), SEARCH_INDEX_STATUS_INDEX_UNREADABLE

    indexed_source_ids: set[str] = set()
    for document in documents:
        if not isinstance(document, dict):
            continue
        source_id = str(document.get("source_id", "")).strip()
        try:
            indexed_source_ids.add(review.validate_source_id(source_id))
        except ValueError:
            continue
    return indexed_source_ids, ""


def is_within_directory(parent: Path, candidate: Path) -> bool:
    """Return True when candidate stays inside parent."""

    try:
        candidate.relative_to(parent.resolve(strict=False))
    except ValueError:
        return False
    return True


def resolve_extracted_text_path(
    workspace_root: Path,
    module_dir: Path,
    relative_path: str,
) -> Path:
    """Resolve an extracted text path only when it stays in 10_extracted_text."""

    cleaned_path = relative_path.strip()
    if not cleaned_path:
        raise ValueError("Extracted text path cannot be blank.")
    extracted_text_path = security.assert_safe_local_path(workspace_root, workspace_root / cleaned_path)
    extracted_text_dir = paths.get_research_module_paths(module_dir).extracted_text_dir.resolve(
        strict=False
    )
    if not is_within_directory(extracted_text_dir, extracted_text_path):
        raise ValueError(f"Extracted text path is outside 10_extracted_text: {extracted_text_path}")
    if not extracted_text_path.is_file():
        raise FileNotFoundError(f"Extracted text file does not exist: {extracted_text_path}")
    return extracted_text_path


def source_search_index_status(
    source_id: str,
    indexed_source_ids: set[str],
    module_index_status: str,
) -> str:
    """Return informational local keyword index status for one source."""

    if module_index_status:
        return module_index_status
    if source_id in indexed_source_ids:
        return SEARCH_INDEX_STATUS_INDEXED
    return SEARCH_INDEX_STATUS_NOT_INDEXED


def source_extraction_status(source_record: dict[str, Any]) -> str:
    """Return a normalized extraction status for a manifest source."""

    extraction_status = str(source_record.get("extraction_status", "")).strip().upper()
    return extraction_status or EXTRACTION_STATUS_MISSING


def readiness_status_for_source(
    *,
    source_type: str,
    review_status: str,
    extraction_status: str,
    has_extracted_text_path: bool,
    extracted_text_path_valid: bool,
) -> str:
    """Return the readiness status for one source."""

    if review_status == review.REVIEW_STATUS_REJECTED:
        return READINESS_STATUS_REJECTED
    if review_status == review.REVIEW_STATUS_NEEDS_FOLLOW_UP:
        return READINESS_STATUS_NEEDS_FOLLOW_UP
    if review_status != review.REVIEW_STATUS_REVIEWED:
        return READINESS_STATUS_NEEDS_REVIEW
    if (
        extraction_status == extraction.EXTRACTION_STATUS_EXTRACTED
        and has_extracted_text_path
        and extracted_text_path_valid
    ):
        return READINESS_STATUS_READY
    if extraction_status == EXTRACTION_STATUS_MISSING and source_type != library.SOURCE_TYPE_LOCAL_FILE:
        return READINESS_STATUS_REGISTERED_ONLY
    return READINESS_STATUS_NEEDS_EXTRACTION


def build_blocking_reasons(
    *,
    source_type: str,
    review_status: str,
    extraction_status: str,
    has_extracted_text_path: bool,
    extracted_text_error: str,
) -> list[str]:
    """Return concise local blockers for later synthesis readiness."""

    reasons: list[str] = []
    if review_status == review.REVIEW_STATUS_REJECTED:
        reasons.append("Source is rejected in manual review.")
    elif review_status == review.REVIEW_STATUS_NEEDS_FOLLOW_UP:
        reasons.append("Source needs manual follow-up.")
    elif review_status != review.REVIEW_STATUS_REVIEWED:
        reasons.append("Source has not been manually reviewed.")

    if extraction_status != extraction.EXTRACTION_STATUS_EXTRACTED:
        if extraction_status == EXTRACTION_STATUS_MISSING and source_type != library.SOURCE_TYPE_LOCAL_FILE:
            reasons.append("Source is registered only and has no local extracted text.")
        else:
            reasons.append(f"Extraction status is {extraction_status}.")
    elif not has_extracted_text_path:
        reasons.append("Extracted text path is missing.")
    elif extracted_text_error:
        reasons.append(extracted_text_error)
    return reasons


def build_readiness_record(
    workspace_root: Path,
    module_dir: Path,
    source_record: dict[str, Any],
    *,
    read_at: str,
    indexed_source_ids: set[str],
    module_index_status: str,
) -> dict[str, Any]:
    """Build one source readiness record from local-only state."""

    source_id = review.validate_source_id(str(source_record.get("source_id", "")))
    review_record = review.read_or_build_review_record(
        workspace_root,
        module_dir,
        source_record,
        read_at=read_at,
    )
    review_status = review.validate_review_status(str(review_record.get("review_status", "")))
    extraction_status = source_extraction_status(source_record)
    source_type = str(source_record.get("source_type", "")).strip()
    extracted_text_path = str(source_record.get("extracted_text_path", "")).strip()
    has_extracted_text_path = bool(extracted_text_path)
    extracted_text_path_valid = False
    extracted_text_error = ""
    if has_extracted_text_path:
        try:
            resolve_extracted_text_path(workspace_root, module_dir, extracted_text_path)
            extracted_text_path_valid = True
        except (FileNotFoundError, ValueError) as exc:
            extracted_text_error = str(exc)

    notes_path = review.get_notes_path(module_dir, source_id)
    security.assert_safe_local_path(workspace_root, notes_path)
    readiness_status = readiness_status_for_source(
        source_type=source_type,
        review_status=review_status,
        extraction_status=extraction_status,
        has_extracted_text_path=has_extracted_text_path,
        extracted_text_path_valid=extracted_text_path_valid,
    )
    blocking_reasons = build_blocking_reasons(
        source_type=source_type,
        review_status=review_status,
        extraction_status=extraction_status,
        has_extracted_text_path=has_extracted_text_path,
        extracted_text_error=extracted_text_error,
    )
    return {
        "source_id": source_id,
        "source_type": source_type,
        "review_status": review_status,
        "extraction_status": extraction_status,
        "search_index_status": source_search_index_status(
            source_id,
            indexed_source_ids,
            module_index_status,
        ),
        "original_filename": str(source_record.get("original_filename", "")),
        "stored_filename": str(source_record.get("stored_filename", "")),
        "metadata_path": str(source_record.get("metadata_path", "")),
        "extracted_text_path": extracted_text_path,
        "notes_path": paths.relative_to_workspace(workspace_root, notes_path),
        "has_manual_notes": notes_path.is_file(),
        "readiness_status": readiness_status,
        "blocking_reasons": blocking_reasons,
    }


def matches_filters(record: dict[str, Any], filters: ReadinessFilters) -> bool:
    """Return True when a readiness record matches local filters."""

    if filters.ready_only and record.get("readiness_status") != READINESS_STATUS_READY:
        return False
    if filters.review_status and record.get("review_status") != filters.review_status:
        return False
    if filters.extraction_status and record.get("extraction_status") != filters.extraction_status:
        return False
    if filters.source_type and record.get("source_type") != filters.source_type:
        return False
    return True


def build_readiness_records(
    workspace_root: Path,
    module_dir: Path,
    *,
    read_at: str,
) -> tuple[list[dict[str, Any]], int]:
    """Build unfiltered readiness records for all manifest sources."""

    manifest_path = paths.get_research_module_paths(module_dir).manifest
    security.assert_safe_local_path(workspace_root, manifest_path)
    manifest = library.read_library_manifest(manifest_path)
    sources = library.get_manifest_sources(manifest)
    indexed_source_ids, module_index_status = load_indexed_source_ids(module_dir)
    records = [
        build_readiness_record(
            workspace_root,
            module_dir,
            source_record,
            read_at=read_at,
            indexed_source_ids=indexed_source_ids,
            module_index_status=module_index_status,
        )
        for source_record in sources
    ]
    records.sort(key=lambda record: record["source_id"])
    return records, int(manifest.get("source_count", len(sources)))


def list_synthesis_readiness(
    workspace_root: Path,
    module_dir: Path,
    *,
    read_at: str,
    filters: ReadinessFilters | None = None,
) -> list[dict[str, Any]]:
    """Return local synthesis readiness records without writing files."""

    normalized_filters = normalize_filters(filters)
    records, _ = build_readiness_records(workspace_root, module_dir, read_at=read_at)
    return [record for record in records if matches_filters(record, normalized_filters)]


def build_candidate_manifest_data(
    workspace_root: Path,
    module_dir: Path,
    *,
    created_at: str,
    filters: ReadinessFilters | None = None,
) -> dict[str, Any]:
    """Build candidate manifest data without writing it."""

    normalized_filters = normalize_filters(filters)
    if not normalized_filters.ready_only:
        normalized_filters = ReadinessFilters(
            review_status=normalized_filters.review_status,
            extraction_status=normalized_filters.extraction_status,
            source_type=normalized_filters.source_type,
            ready_only=True,
        )
    records, source_count = build_readiness_records(workspace_root, module_dir, read_at=created_at)
    candidates = [
        {key: record[key] for key in (
            "source_id",
            "source_type",
            "review_status",
            "extraction_status",
            "search_index_status",
            "original_filename",
            "stored_filename",
            "metadata_path",
            "extracted_text_path",
            "notes_path",
            "readiness_status",
            "blocking_reasons",
        )}
        for record in records
        if matches_filters(record, normalized_filters)
    ]
    return {
        "schema_version": READINESS_SCHEMA_VERSION,
        "module_path": paths.relative_to_workspace(workspace_root, module_dir),
        "created_at": created_at,
        "local_only": True,
        "api_enabled": False,
        "network_enabled": False,
        "filters": {
            "review_status": normalized_filters.review_status,
            "extraction_status": normalized_filters.extraction_status,
            "source_type": normalized_filters.source_type,
            "ready_only": normalized_filters.ready_only,
        },
        "source_count": source_count,
        "candidate_count": len(candidates),
        "candidates": candidates,
    }


def write_candidate_manifest(path: Path, manifest: dict[str, Any]) -> None:
    """Write the generated local synthesis candidate manifest."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def build_synthesis_candidate_manifest(
    workspace_root: Path,
    module_dir: Path,
    *,
    created_at: str,
    filters: ReadinessFilters | None = None,
) -> CandidateManifestResult:
    """Build and write the local synthesis candidate manifest."""

    security.assert_safe_local_path(workspace_root, module_dir)
    manifest_path = get_candidate_manifest_path(module_dir)
    security.assert_safe_local_path(workspace_root, manifest_path)
    manifest = build_candidate_manifest_data(
        workspace_root,
        module_dir,
        created_at=created_at,
        filters=filters,
    )
    write_candidate_manifest(manifest_path, manifest)
    return CandidateManifestResult(
        manifest_path=manifest_path,
        candidate_count=int(manifest["candidate_count"]),
        source_count=int(manifest["source_count"]),
        manifest=manifest,
    )
