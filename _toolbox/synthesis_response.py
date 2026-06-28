"""Local-only external synthesis response intake checks for MNCH Manager v5."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
import os
from pathlib import Path
import re
import shutil
from typing import Any

from _toolbox import paths, security, synthesis_prompt_package


RESPONSE_CHECK_SCHEMA_VERSION = 1
RESPONSE_STATUS_READY_FOR_MANUAL_REVIEW = "READY_FOR_MANUAL_REVIEW"
RESPONSE_STATUS_NEEDS_FIX = "NEEDS_FIX"
RESPONSE_FILENAME = "external_synthesis_response.md"
RESPONSE_CHECK_JSON_FILENAME = "response_check.json"
RESPONSE_CHECK_MARKDOWN_FILENAME = "response_check.md"
RESPONSE_DIR_PREFIX = "response_"
TEMP_RESPONSE_DIR_PREFIX = ".tmp_response_"
ALLOWED_RESPONSE_SUFFIXES = (".md", ".txt")
CHUNK_CITATION_PATTERN = re.compile(r"\bSRC-\d{4}_CHUNK-\d{4}\b")


@dataclass(frozen=True)
class ExternalSynthesisResponseResult:
    """Result from importing and checking one external response."""

    response_dir: Path
    response_path: Path
    check_json_path: Path
    check_markdown_path: Path
    status: str
    valid_chunk_ids: list[str]
    unknown_chunk_ids: list[str]
    uncited_package_chunk_ids: list[str]
    check_data: dict[str, Any]


def get_responses_root(module_dir: Path) -> Path:
    """Return the generated external response intake root for a module."""

    return paths.get_research_module_paths(module_dir).external_synthesis_responses_dir


def sanitize_response_timestamp(created_at: str) -> str:
    """Return a Windows-safe response timestamp such as YYYYMMDDTHHMMSS."""

    try:
        parsed = datetime.fromisoformat(created_at)
        return parsed.strftime("%Y%m%dT%H%M%S")
    except ValueError:
        cleaned = re.sub(r"[^0-9T]", "", created_at)
        match = re.search(r"(\d{8}T\d{6})", cleaned)
        if match:
            return match.group(1)
    return datetime.now().astimezone().strftime("%Y%m%dT%H%M%S")


def build_unique_response_dir(responses_root: Path, created_at: str) -> Path:
    """Return a final response directory path without overwriting existing output."""

    base_name = f"{RESPONSE_DIR_PREFIX}{sanitize_response_timestamp(created_at)}"
    candidate = responses_root / base_name
    if not candidate.exists():
        return candidate
    for sequence_number in range(2, 1000):
        candidate = responses_root / f"{base_name}_{sequence_number:02d}"
        if not candidate.exists():
            return candidate
    raise FileExistsError(f"Could not choose a unique response folder for: {base_name}")


def ensure_within_directory(parent: Path, candidate: Path) -> Path:
    """Return a resolved candidate only when it stays inside parent."""

    resolved_parent = paths.resolve_for_containment(parent)
    resolved_candidate = paths.resolve_for_containment(candidate)
    try:
        common = Path(os.path.commonpath((resolved_parent, resolved_candidate)))
    except ValueError as exc:
        raise ValueError(f"Path is outside expected folder: {candidate}") from exc
    if common != resolved_parent:
        raise ValueError(f"Path is outside expected folder: {candidate}")
    return resolved_candidate


def resolve_package_manifest_path(
    workspace_root: Path,
    module_dir: Path,
    package_manifest_path: Path,
) -> Path:
    """Validate a package manifest under the current module package folder."""

    packages_root = synthesis_prompt_package.get_packages_root(module_dir)
    security.assert_safe_local_path(workspace_root, packages_root)
    candidate = package_manifest_path
    if not candidate.is_absolute():
        candidate = workspace_root / candidate
    resolved = security.assert_safe_local_path(workspace_root, candidate)
    ensure_within_directory(packages_root, resolved)
    if resolved.name != synthesis_prompt_package.PACKAGE_MANIFEST_FILENAME:
        raise ValueError(
            f"Package manifest must be named {synthesis_prompt_package.PACKAGE_MANIFEST_FILENAME}."
        )
    if not resolved.is_file():
        raise FileNotFoundError(f"Package manifest not found: {resolved}")
    return resolved


def find_newest_package_manifest(module_dir: Path) -> Path | None:
    """Return the newest package manifest under the module package folder."""

    packages_root = synthesis_prompt_package.get_packages_root(module_dir)
    if not packages_root.exists():
        return None
    manifests = [
        manifest_path
        for manifest_path in packages_root.glob(
            f"{synthesis_prompt_package.PACKAGE_DIR_PREFIX}*/"
            f"{synthesis_prompt_package.PACKAGE_MANIFEST_FILENAME}"
        )
        if manifest_path.is_file()
    ]
    if not manifests:
        return None
    return sorted(
        manifests,
        key=lambda manifest_path: (manifest_path.parent.name, manifest_path.stat().st_mtime),
        reverse=True,
    )[0]


def resolve_response_input_path(response_file_path: Path) -> Path:
    """Validate an existing local UTF-8 Markdown or text response file."""

    resolved = response_file_path.resolve(strict=True)
    if not resolved.is_file():
        raise FileNotFoundError(f"Response file not found: {resolved}")
    if resolved.suffix.lower() not in ALLOWED_RESPONSE_SUFFIXES:
        allowed = ", ".join(ALLOWED_RESPONSE_SUFFIXES)
        raise ValueError(f"Response file must use one of these extensions: {allowed}.")
    return resolved


def read_response_text(response_file_path: Path) -> str:
    """Read response text as UTF-8 and normalize line endings."""

    try:
        text = response_file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"Response file must be UTF-8 text: {response_file_path}") from exc
    return text.replace("\r\n", "\n").replace("\r", "\n")


def read_package_manifest(package_manifest_path: Path) -> dict[str, Any]:
    """Read and minimally validate a Step 13 package manifest."""

    manifest = json.loads(package_manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != synthesis_prompt_package.PACKAGE_MANIFEST_SCHEMA_VERSION:
        raise ValueError("Package manifest schema version is not supported.")
    if manifest.get("local_only") is not True:
        raise ValueError("Package manifest must be local-only.")
    if manifest.get("api_enabled") is not False:
        raise ValueError("Package manifest must have api_enabled set to false.")
    if manifest.get("network_enabled") is not False:
        raise ValueError("Package manifest must have network_enabled set to false.")
    if not isinstance(manifest.get("sources"), list):
        raise ValueError("Package manifest sources must be a list.")
    return manifest


def get_manifest_chunk_ids(package_manifest: dict[str, Any]) -> list[str]:
    """Return all chunk IDs declared by a package manifest."""

    chunk_ids: list[str] = []
    for source in package_manifest.get("sources", []):
        if not isinstance(source, dict):
            raise ValueError("Package manifest contains a non-object source.")
        chunks = source.get("chunks", [])
        if not isinstance(chunks, list):
            raise ValueError("Package manifest source chunks must be a list.")
        for chunk in chunks:
            if not isinstance(chunk, dict):
                raise ValueError("Package manifest contains a non-object chunk.")
            chunk_id = str(chunk.get("chunk_id", "")).strip()
            if not CHUNK_CITATION_PATTERN.fullmatch(chunk_id):
                raise ValueError(f"Invalid package chunk ID: {chunk_id}")
            chunk_ids.append(chunk_id)
    if not chunk_ids:
        raise ValueError("Package manifest does not declare any chunk IDs.")
    return chunk_ids


def unique_preserving_order(values: list[str]) -> list[str]:
    """Return values without duplicates while preserving first-seen order."""

    seen: set[str] = set()
    unique_values: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        unique_values.append(value)
    return unique_values


def extract_chunk_citations(response_text: str) -> list[str]:
    """Extract all chunk citation IDs from response text."""

    return CHUNK_CITATION_PATTERN.findall(response_text)


def build_response_check_data(
    workspace_root: Path,
    module_dir: Path,
    *,
    created_at: str,
    package_manifest_path: Path,
    package_manifest: dict[str, Any],
    response_dir: Path,
    response_path: Path,
    check_json_path: Path,
    check_markdown_path: Path,
    response_file_path: Path,
    response_text: str,
) -> dict[str, Any]:
    """Build response check data without writing files."""

    package_chunk_ids = get_manifest_chunk_ids(package_manifest)
    expected_chunk_id_set = set(package_chunk_ids)
    cited_chunk_ids = extract_chunk_citations(response_text)
    unique_cited_chunk_ids = unique_preserving_order(cited_chunk_ids)
    valid_chunk_ids = [
        chunk_id for chunk_id in unique_cited_chunk_ids if chunk_id in expected_chunk_id_set
    ]
    unknown_chunk_ids = [
        chunk_id for chunk_id in unique_cited_chunk_ids if chunk_id not in expected_chunk_id_set
    ]
    uncited_package_chunk_ids = [
        chunk_id for chunk_id in package_chunk_ids if chunk_id not in set(valid_chunk_ids)
    ]
    status = (
        RESPONSE_STATUS_READY_FOR_MANUAL_REVIEW
        if valid_chunk_ids and not unknown_chunk_ids
        else RESPONSE_STATUS_NEEDS_FIX
    )

    return {
        "schema_version": RESPONSE_CHECK_SCHEMA_VERSION,
        "module_path": paths.relative_to_workspace(workspace_root, module_dir),
        "created_at": created_at,
        "status": status,
        "local_only": True,
        "api_enabled": False,
        "network_enabled": False,
        "synthesis_generated": False,
        "summary_generated": False,
        "untrusted_external_text": True,
        "package_manifest_path": paths.relative_to_workspace(
            workspace_root,
            package_manifest_path,
        ),
        "package_dir": paths.relative_to_workspace(workspace_root, package_manifest_path.parent),
        "response_dir": paths.relative_to_workspace(workspace_root, response_dir),
        "response_path": paths.relative_to_workspace(workspace_root, response_path),
        "check_json_path": paths.relative_to_workspace(workspace_root, check_json_path),
        "check_markdown_path": paths.relative_to_workspace(workspace_root, check_markdown_path),
        "source_response_file": str(response_file_path),
        "response_char_count": len(response_text),
        "package_source_count": int(package_manifest.get("source_count", 0)),
        "package_chunk_count": len(package_chunk_ids),
        "citation_count": len(cited_chunk_ids),
        "unique_cited_chunk_count": len(unique_cited_chunk_ids),
        "valid_chunk_count": len(valid_chunk_ids),
        "unknown_chunk_count": len(unknown_chunk_ids),
        "uncited_package_chunk_count": len(uncited_package_chunk_ids),
        "cited_chunk_ids": unique_cited_chunk_ids,
        "valid_chunk_ids": valid_chunk_ids,
        "unknown_chunk_ids": unknown_chunk_ids,
        "uncited_package_chunk_ids": uncited_package_chunk_ids,
    }


def build_response_check_markdown(check_data: dict[str, Any]) -> str:
    """Build a local check report without summarizing the imported response."""

    unknown = check_data["unknown_chunk_ids"]
    uncited = check_data["uncited_package_chunk_ids"]
    warnings = []
    if uncited:
        warnings.append(
            f"- {len(uncited)} package chunk(s) were not cited by the response. "
            "This is a warning only."
        )
    if not warnings:
        warnings.append("- No warning-only gaps were detected.")

    unknown_section = (
        "\n".join(f"- {chunk_id}" for chunk_id in unknown)
        if unknown
        else "- No unknown chunk citations detected."
    )
    warning_section = "\n".join(warnings)
    return (
        "# External Synthesis Response Check\n\n"
        f"Status: {check_data['status']}\n\n"
        "This report checks only local chunk-citation discipline. It does not verify "
        "clinical correctness and does not summarize the imported response.\n\n"
        "## Local-Only Safety\n\n"
        "- API enabled: false\n"
        "- Network enabled: false\n"
        "- Synthesis generated: false\n"
        "- Summary generated: false\n"
        "- Imported response text is untrusted external user-provided text.\n\n"
        "## Files\n\n"
        f"- Package manifest: {check_data['package_manifest_path']}\n"
        f"- Copied response: {check_data['response_path']}\n"
        f"- JSON check: {check_data['check_json_path']}\n\n"
        "## Citation Counts\n\n"
        f"- Package chunks: {check_data['package_chunk_count']}\n"
        f"- Total chunk citations found: {check_data['citation_count']}\n"
        f"- Unique chunk citations found: {check_data['unique_cited_chunk_count']}\n"
        f"- Valid package chunk citations: {check_data['valid_chunk_count']}\n"
        f"- Unknown chunk citations: {check_data['unknown_chunk_count']}\n"
        f"- Package chunks not cited: {check_data['uncited_package_chunk_count']}\n\n"
        "## Unknown Chunk Citations\n\n"
        f"{unknown_section}\n\n"
        "## Warnings\n\n"
        f"{warning_section}\n"
    )


def build_response_intake_data(
    workspace_root: Path,
    module_dir: Path,
    package_manifest_path: Path,
    response_file_path: Path,
    *,
    created_at: str,
) -> tuple[Path, Path, Path, Path, Path, str, dict[str, Any], str]:
    """Validate input and build all response intake payloads without writing files."""

    security.assert_safe_local_path(workspace_root, module_dir)
    responses_root = get_responses_root(module_dir)
    security.assert_safe_local_path(workspace_root, responses_root)
    resolved_manifest_path = resolve_package_manifest_path(
        workspace_root,
        module_dir,
        package_manifest_path,
    )
    resolved_response_file_path = resolve_response_input_path(response_file_path)
    package_manifest = read_package_manifest(resolved_manifest_path)
    response_text = read_response_text(resolved_response_file_path)

    response_dir = build_unique_response_dir(responses_root, created_at)
    temp_response_dir = responses_root / f"{TEMP_RESPONSE_DIR_PREFIX}{response_dir.name}"
    response_path = response_dir / RESPONSE_FILENAME
    check_json_path = response_dir / RESPONSE_CHECK_JSON_FILENAME
    check_markdown_path = response_dir / RESPONSE_CHECK_MARKDOWN_FILENAME
    for output_path in (response_dir, temp_response_dir, response_path, check_json_path, check_markdown_path):
        security.assert_safe_local_path(workspace_root, output_path)

    check_data = build_response_check_data(
        workspace_root,
        module_dir,
        created_at=created_at,
        package_manifest_path=resolved_manifest_path,
        package_manifest=package_manifest,
        response_dir=response_dir,
        response_path=response_path,
        check_json_path=check_json_path,
        check_markdown_path=check_markdown_path,
        response_file_path=resolved_response_file_path,
        response_text=response_text,
    )
    check_markdown = build_response_check_markdown(check_data)
    return (
        response_dir,
        temp_response_dir,
        response_path,
        check_json_path,
        check_markdown_path,
        response_text,
        check_data,
        check_markdown,
    )


def write_response_outputs(
    response_dir: Path,
    temp_response_dir: Path,
    response_text: str,
    check_data: dict[str, Any],
    check_markdown: str,
) -> None:
    """Write response intake files through a temporary directory, then rename."""

    if response_dir.exists():
        raise FileExistsError(f"Refusing to overwrite existing response folder: {response_dir}")
    if temp_response_dir.exists():
        shutil.rmtree(temp_response_dir)
    try:
        temp_response_dir.mkdir(parents=True, exist_ok=False)
        (temp_response_dir / RESPONSE_FILENAME).write_text(
            response_text,
            encoding="utf-8",
            newline="\n",
        )
        (temp_response_dir / RESPONSE_CHECK_JSON_FILENAME).write_text(
            json.dumps(check_data, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        (temp_response_dir / RESPONSE_CHECK_MARKDOWN_FILENAME).write_text(
            check_markdown,
            encoding="utf-8",
            newline="\n",
        )
        temp_response_dir.rename(response_dir)
    except Exception:
        if temp_response_dir.exists():
            shutil.rmtree(temp_response_dir)
        raise


def import_external_synthesis_response(
    workspace_root: Path,
    module_dir: Path,
    package_manifest_path: Path,
    response_file_path: Path,
    *,
    created_at: str,
) -> ExternalSynthesisResponseResult:
    """Import and check one local external synthesis response."""

    (
        response_dir,
        temp_response_dir,
        response_path,
        check_json_path,
        check_markdown_path,
        response_text,
        check_data,
        check_markdown,
    ) = build_response_intake_data(
        workspace_root,
        module_dir,
        package_manifest_path,
        response_file_path,
        created_at=created_at,
    )
    write_response_outputs(
        response_dir,
        temp_response_dir,
        response_text,
        check_data,
        check_markdown,
    )
    return ExternalSynthesisResponseResult(
        response_dir=response_dir,
        response_path=response_path,
        check_json_path=check_json_path,
        check_markdown_path=check_markdown_path,
        status=str(check_data["status"]),
        valid_chunk_ids=list(check_data["valid_chunk_ids"]),
        unknown_chunk_ids=list(check_data["unknown_chunk_ids"]),
        uncited_package_chunk_ids=list(check_data["uncited_package_chunk_ids"]),
        check_data=check_data,
    )
