"""Local source library manifest helpers for MNCH Manager v5."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
from typing import Any

from _toolbox import paths, security


MANIFEST_SCHEMA_VERSION = 1
SOURCE_STATUS_EMPTY = "LIBRARY_READY"
SOURCE_STATUS_SOURCES_REGISTERED = "SOURCES_REGISTERED"
PRIVACY_STATUS_LOCAL_ONLY = "LOCAL_ONLY"
SOURCE_TYPE_LOCAL_FILE = "local_file"
SOURCE_TYPE_URL = "url"
SOURCE_TYPE_DOI = "doi"
SOURCE_TYPE_MANUAL_CITATION = "manual_citation"
SOURCE_RECORD_STATUS_IMPORTED = "IMPORTED"
SOURCE_RECORD_STATUS_REGISTERED = "REGISTERED"


def make_source_id(sequence_number: int) -> str:
    """Return a stable local source ID such as SRC-0001."""

    if sequence_number < 1:
        raise ValueError("Source sequence number must be 1 or greater.")
    return f"SRC-{sequence_number:04d}"


def next_source_id(manifest: dict[str, Any]) -> str:
    """Return the next source ID for a manifest."""

    sources = manifest.get("sources", [])
    if not isinstance(sources, list):
        sources = []
    return make_source_id(len(sources) + 1)


def calculate_sha256(path: Path) -> str:
    """Return the SHA256 hash for a local file without modifying it."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def get_manifest_sources(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    """Return normalized manifest sources."""

    raw_sources = manifest.get("sources", [])
    if not isinstance(raw_sources, list):
        return []
    return [source for source in raw_sources if isinstance(source, dict)]


def append_source_record(
    manifest_path: Path,
    record_fields: dict[str, Any],
    *,
    added_at: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Append one source record to a library manifest."""

    manifest = read_library_manifest(manifest_path)
    sources = get_manifest_sources(manifest)
    record = {
        "source_id": make_source_id(len(sources) + 1),
        **record_fields,
        "added_at": added_at,
    }
    sources.append(record)
    manifest["sources"] = sources
    manifest["source_count"] = len(sources)
    manifest["updated_at"] = added_at
    write_library_manifest(manifest_path, manifest, overwrite=True)
    return record, manifest


def find_source_record(manifest: dict[str, Any], source_id: str) -> dict[str, Any]:
    """Return one source record by source ID."""

    for source in get_manifest_sources(manifest):
        if source.get("source_id") == source_id:
            return source
    raise ValueError(f"Source ID is not registered in library manifest: {source_id}")


def update_source_record(
    manifest_path: Path,
    source_id: str,
    updates: dict[str, Any],
    *,
    updated_at: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Update one source record while preserving source IDs and source count."""

    manifest = read_library_manifest(manifest_path)
    sources = get_manifest_sources(manifest)
    for index, source in enumerate(sources):
        if source.get("source_id") == source_id:
            updated_source = {**source, **updates}
            sources[index] = updated_source
            manifest["sources"] = sources
            manifest["source_count"] = len(sources)
            manifest["updated_at"] = updated_at
            write_library_manifest(manifest_path, manifest, overwrite=True)
            return updated_source, manifest
    raise ValueError(f"Source ID is not registered in library manifest: {source_id}")


def build_manifest_only_record(
    source_type: str,
    *,
    status: str = SOURCE_RECORD_STATUS_REGISTERED,
) -> dict[str, Any]:
    """Return common empty file fields for manifest-only source records."""

    return {
        "source_type": source_type,
        "original_filename": "",
        "stored_filename": "",
        "relative_stored_path": "",
        "file_size": 0,
        "sha256": "",
        "status": status,
    }


def build_manifest(
    workspace_root: Path,
    module_dir: Path,
    *,
    created_at: str,
) -> dict[str, Any]:
    """Build a new local-only library manifest for a module."""

    research_paths = paths.get_research_module_paths(module_dir)
    return {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "module_path": paths.relative_to_workspace(workspace_root, module_dir),
        "created_at": created_at,
        "updated_at": created_at,
        "source_count": 0,
        "sources": [],
        "privacy": {
            "local_only": True,
            "api_enabled": False,
            "network_enabled": False,
        },
        "folders": {
            "raw_sources": paths.relative_to_workspace(workspace_root, research_paths.raw_sources_dir),
            "metadata": paths.relative_to_workspace(workspace_root, research_paths.metadata_dir),
            "extracted_text": paths.relative_to_workspace(
                workspace_root, research_paths.extracted_text_dir
            ),
            "summaries": paths.relative_to_workspace(workspace_root, research_paths.summaries_dir),
            "qa": paths.relative_to_workspace(workspace_root, research_paths.qa_dir),
            "search_index": paths.relative_to_workspace(
                workspace_root, research_paths.search_index_dir
            ),
            "review": paths.relative_to_workspace(workspace_root, research_paths.review_dir),
            "notes": paths.relative_to_workspace(workspace_root, research_paths.notes_dir),
            "translation": paths.relative_to_workspace(
                workspace_root, research_paths.translation_dir
            ),
        },
    }


def read_library_manifest(path: Path) -> dict[str, Any]:
    """Read a UTF-8 JSON library manifest."""

    return json.loads(path.read_text(encoding="utf-8"))


def write_library_manifest(path: Path, manifest: dict[str, Any], overwrite: bool = False) -> None:
    """Write a UTF-8 JSON library manifest without accidental overwrite."""

    if path.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing library manifest: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def import_local_source_file(
    workspace_root: Path,
    module_dir: Path,
    source_file: Path,
    *,
    added_at: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Copy one local source file into `09_sources/raw/` and register it."""

    security.assert_safe_local_path(workspace_root, module_dir)
    research_paths = paths.get_research_module_paths(module_dir)
    resolved_source = source_file.expanduser().resolve(strict=True)
    if not resolved_source.is_file():
        raise FileNotFoundError(f"Local source file does not exist: {source_file}")
    if not resolved_source.name:
        raise ValueError(f"Local source file must have a filename: {source_file}")

    destination = research_paths.raw_sources_dir / resolved_source.name
    security.assert_safe_local_path(workspace_root, destination)
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite existing raw source file: {destination}")

    initialize_library_manifest(workspace_root, module_dir, created_at=added_at, overwrite=False)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(resolved_source, destination)
    record_fields = {
        "source_type": SOURCE_TYPE_LOCAL_FILE,
        "original_filename": resolved_source.name,
        "stored_filename": destination.name,
        "relative_stored_path": paths.relative_to_workspace(workspace_root, destination),
        "file_size": destination.stat().st_size,
        "sha256": calculate_sha256(destination),
        "status": SOURCE_RECORD_STATUS_IMPORTED,
    }
    return append_source_record(research_paths.manifest, record_fields, added_at=added_at)


def register_url_source(
    workspace_root: Path,
    module_dir: Path,
    url: str,
    *,
    added_at: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Register a URL as a manifest-only source without downloading it."""

    security.assert_safe_local_path(workspace_root, module_dir)
    cleaned_url = url.strip()
    if not cleaned_url:
        raise ValueError("URL cannot be blank.")
    research_paths = paths.get_research_module_paths(module_dir)
    initialize_library_manifest(workspace_root, module_dir, created_at=added_at, overwrite=False)
    record_fields = build_manifest_only_record(SOURCE_TYPE_URL)
    record_fields["url"] = cleaned_url
    return append_source_record(research_paths.manifest, record_fields, added_at=added_at)


def register_doi_source(
    workspace_root: Path,
    module_dir: Path,
    doi: str,
    *,
    added_at: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Register a DOI as a manifest-only source without resolving it online."""

    security.assert_safe_local_path(workspace_root, module_dir)
    cleaned_doi = doi.strip()
    if not cleaned_doi:
        raise ValueError("DOI cannot be blank.")
    research_paths = paths.get_research_module_paths(module_dir)
    initialize_library_manifest(workspace_root, module_dir, created_at=added_at, overwrite=False)
    record_fields = build_manifest_only_record(SOURCE_TYPE_DOI)
    record_fields["doi"] = cleaned_doi
    return append_source_record(research_paths.manifest, record_fields, added_at=added_at)


def register_manual_citation_source(
    workspace_root: Path,
    module_dir: Path,
    citation: str,
    *,
    added_at: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Register a manual citation as a manifest-only source."""

    security.assert_safe_local_path(workspace_root, module_dir)
    cleaned_citation = citation.strip()
    if not cleaned_citation:
        raise ValueError("Manual citation cannot be blank.")
    research_paths = paths.get_research_module_paths(module_dir)
    initialize_library_manifest(workspace_root, module_dir, created_at=added_at, overwrite=False)
    record_fields = build_manifest_only_record(SOURCE_TYPE_MANUAL_CITATION)
    record_fields["citation"] = cleaned_citation
    return append_source_record(research_paths.manifest, record_fields, added_at=added_at)


def initialize_library_manifest(
    workspace_root: Path,
    module_dir: Path,
    *,
    created_at: str,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Create research folders and initialize a module library manifest."""

    security.assert_safe_local_path(workspace_root, module_dir)
    research_paths = paths.get_research_module_paths(module_dir)
    for directory_path in paths.get_research_module_dirs(module_dir):
        security.assert_safe_local_path(workspace_root, directory_path)
        directory_path.mkdir(parents=True, exist_ok=True)

    if research_paths.manifest.exists() and not overwrite:
        return read_library_manifest(research_paths.manifest)

    manifest = build_manifest(workspace_root, module_dir, created_at=created_at)
    write_library_manifest(research_paths.manifest, manifest, overwrite=overwrite)
    return manifest


def build_library_privacy_report(workspace_root: Path, module_dir: Path) -> dict[str, Any]:
    """Return a local-only privacy report for a module library."""

    security.assert_safe_local_path(workspace_root, module_dir)
    report = security.build_privacy_report(module_dir)
    report["module_path"] = paths.relative_to_workspace(workspace_root, module_dir)
    return report
