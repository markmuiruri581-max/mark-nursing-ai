"""Local-only manual review helpers for MNCH Manager v5."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any

from _toolbox import library, paths, security


REVIEW_SCHEMA_VERSION = 1
REVIEW_STATUS_UNREAD = "UNREAD"
REVIEW_STATUS_IN_REVIEW = "IN_REVIEW"
REVIEW_STATUS_REVIEWED = "REVIEWED"
REVIEW_STATUS_REJECTED = "REJECTED"
REVIEW_STATUS_NEEDS_FOLLOW_UP = "NEEDS_FOLLOW_UP"
SOURCE_ID_PATTERN = re.compile(r"^SRC-[0-9]{4}$")
VALID_REVIEW_STATUSES = {
    REVIEW_STATUS_UNREAD,
    REVIEW_STATUS_IN_REVIEW,
    REVIEW_STATUS_REVIEWED,
    REVIEW_STATUS_REJECTED,
    REVIEW_STATUS_NEEDS_FOLLOW_UP,
}


@dataclass(frozen=True)
class ReviewStatusResult:
    """Result from writing or reading a source review record."""

    review_path: Path
    record: dict[str, Any]


@dataclass(frozen=True)
class ManualNoteResult:
    """Result from appending one manual note."""

    review_path: Path
    notes_path: Path
    record: dict[str, Any]


def validate_review_status(status: str) -> str:
    """Return a normalized review status or raise a clear error."""

    normalized_status = status.strip().upper().replace("-", "_").replace(" ", "_")
    if normalized_status not in VALID_REVIEW_STATUSES:
        valid_statuses = ", ".join(sorted(VALID_REVIEW_STATUSES))
        raise ValueError(f"Invalid review status: {status}. Choose one of: {valid_statuses}")
    return normalized_status


def validate_source_id(source_id: str) -> str:
    """Return a normalized source ID or raise a clear error."""

    normalized_source_id = source_id.strip()
    if not SOURCE_ID_PATTERN.fullmatch(normalized_source_id):
        raise ValueError(f"Invalid source ID: {source_id}. Expected format: SRC-0001")
    return normalized_source_id


def get_review_path(module_dir: Path, source_id: str) -> Path:
    """Return the review JSON path for one source ID."""

    validated_source_id = validate_source_id(source_id)
    return paths.get_research_module_paths(module_dir).review_dir / f"{validated_source_id}.review.json"


def get_notes_path(module_dir: Path, source_id: str) -> Path:
    """Return the manual notes path for one source ID."""

    validated_source_id = validate_source_id(source_id)
    return paths.get_research_module_paths(module_dir).notes_dir / f"{validated_source_id}.md"


def get_source_record(workspace_root: Path, module_dir: Path, source_id: str) -> dict[str, Any]:
    """Read the manifest and return one source record."""

    validated_source_id = validate_source_id(source_id)
    manifest_path = paths.get_research_module_paths(module_dir).manifest
    security.assert_safe_local_path(workspace_root, manifest_path)
    manifest = library.read_library_manifest(manifest_path)
    return library.find_source_record(manifest, validated_source_id)


def build_review_record(
    workspace_root: Path,
    module_dir: Path,
    source_record: dict[str, Any],
    *,
    status: str,
    updated_at: str,
    created_at: str | None = None,
) -> dict[str, Any]:
    """Build one local-only source review record."""

    source_id = validate_source_id(str(source_record.get("source_id", "")))
    review_path = get_review_path(module_dir, source_id)
    notes_path = get_notes_path(module_dir, source_id)
    return {
        "schema_version": REVIEW_SCHEMA_VERSION,
        "source_id": source_id,
        "review_status": validate_review_status(status),
        "created_at": created_at or updated_at,
        "updated_at": updated_at,
        "original_filename": str(source_record.get("original_filename", "")),
        "stored_filename": str(source_record.get("stored_filename", "")),
        "metadata_path": str(source_record.get("metadata_path", "")),
        "extracted_text_path": str(source_record.get("extracted_text_path", "")),
        "notes_path": paths.relative_to_workspace(workspace_root, notes_path),
        "review_path": paths.relative_to_workspace(workspace_root, review_path),
        "local_only": True,
        "api_enabled": False,
        "network_enabled": False,
    }


def read_review_record(path: Path) -> dict[str, Any]:
    """Read one source review JSON file."""

    return json.loads(path.read_text(encoding="utf-8"))


def write_review_record(path: Path, record: dict[str, Any]) -> None:
    """Write a source review JSON file."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(record, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def read_or_build_review_record(
    workspace_root: Path,
    module_dir: Path,
    source_record: dict[str, Any],
    *,
    read_at: str,
) -> dict[str, Any]:
    """Return existing review state or an in-memory UNREAD default."""

    source_id = validate_source_id(str(source_record.get("source_id", "")))
    review_path = get_review_path(module_dir, source_id)
    security.assert_safe_local_path(workspace_root, review_path)
    if review_path.exists():
        record = read_review_record(review_path)
        record["review_status"] = validate_review_status(str(record.get("review_status", "")))
        return record
    return build_review_record(
        workspace_root,
        module_dir,
        source_record,
        status=REVIEW_STATUS_UNREAD,
        updated_at=read_at,
    )


def set_source_review_status(
    workspace_root: Path,
    module_dir: Path,
    source_id: str,
    status: str,
    *,
    updated_at: str,
) -> ReviewStatusResult:
    """Set one source's local manual review status."""

    source_record = get_source_record(workspace_root, module_dir, source_id)
    review_path = get_review_path(module_dir, source_id)
    security.assert_safe_local_path(workspace_root, review_path)
    created_at = None
    if review_path.exists():
        existing_record = read_review_record(review_path)
        created_at = str(existing_record.get("created_at", "")) or updated_at
    record = build_review_record(
        workspace_root,
        module_dir,
        source_record,
        status=status,
        created_at=created_at,
        updated_at=updated_at,
    )
    write_review_record(review_path, record)
    return ReviewStatusResult(review_path=review_path, record=record)


def append_manual_note(
    workspace_root: Path,
    module_dir: Path,
    source_id: str,
    note_text: str,
    *,
    added_at: str,
) -> ManualNoteResult:
    """Append a user-entered manual note for one source."""

    cleaned_note = note_text.strip()
    if not cleaned_note:
        raise ValueError("Manual note cannot be blank.")

    source_record = get_source_record(workspace_root, module_dir, source_id)
    review_path = get_review_path(module_dir, source_id)
    notes_path = get_notes_path(module_dir, source_id)
    security.assert_safe_local_path(workspace_root, review_path)
    security.assert_safe_local_path(workspace_root, notes_path)
    current_record = read_or_build_review_record(
        workspace_root,
        module_dir,
        source_record,
        read_at=added_at,
    )
    record = build_review_record(
        workspace_root,
        module_dir,
        source_record,
        status=str(current_record.get("review_status", REVIEW_STATUS_UNREAD)),
        created_at=str(current_record.get("created_at", "")) or added_at,
        updated_at=added_at,
    )

    notes_path.parent.mkdir(parents=True, exist_ok=True)
    if notes_path.exists():
        existing_content = notes_path.read_text(encoding="utf-8")
    else:
        existing_content = (
            f"# Notes for {source_id}\n\n"
            f"Source: {source_record.get('original_filename') or source_record.get('stored_filename')}\n"
            f"Metadata: {record['metadata_path']}\n"
            f"Extracted text: {record['extracted_text_path']}\n"
        )
    separator = "" if existing_content.endswith("\n") else "\n"
    updated_content = f"{existing_content}{separator}\n## {added_at}\n\n{cleaned_note}\n"
    notes_path.write_text(updated_content, encoding="utf-8", newline="\n")
    write_review_record(review_path, record)
    return ManualNoteResult(review_path=review_path, notes_path=notes_path, record=record)


def list_source_review_records(
    workspace_root: Path,
    module_dir: Path,
    *,
    read_at: str,
) -> list[dict[str, Any]]:
    """Return review records for every manifest source."""

    manifest_path = paths.get_research_module_paths(module_dir).manifest
    security.assert_safe_local_path(workspace_root, manifest_path)
    manifest = library.read_library_manifest(manifest_path)
    records: list[dict[str, Any]] = []
    for source_record in library.get_manifest_sources(manifest):
        records.append(
            read_or_build_review_record(
                workspace_root,
                module_dir,
                source_record,
                read_at=read_at,
            )
        )
    return records
