"""Local-only promotion of checked external synthesis responses."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
import os
from pathlib import Path
import shutil
import tempfile
from typing import Any

from _toolbox import paths, security, synthesis_prompt_package, synthesis_response


PROMOTION_SCHEMA_VERSION = 1
PROMOTION_PROVENANCE_FILENAME = "promotion_provenance.json"
CONFIRMATION_PHRASE = "PROMOTE FINAL SYNTHESIS"


@dataclass(frozen=True)
class PromotionPayload:
    """Validated promotion data prepared before any final synthesis writes."""

    response_check_path: Path
    response_path: Path
    package_manifest_path: Path
    final_synthesis_path: Path
    provenance_path: Path
    response_text: str
    check_data: dict[str, Any]
    provenance: dict[str, Any]


@dataclass(frozen=True)
class PromotionResult:
    """Result from promoting one checked response to final synthesis."""

    final_synthesis_path: Path
    provenance_path: Path
    response_check_path: Path
    response_path: Path
    package_manifest_path: Path
    promoted_char_count: int
    provenance: dict[str, Any]


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


def resolve_workspace_manifest_path(workspace_root: Path, raw_path: str) -> Path:
    """Resolve a workspace-relative manifest path from a check record."""

    cleaned_path = raw_path.strip()
    if not cleaned_path:
        raise ValueError("Check record path cannot be blank.")
    candidate = Path(cleaned_path)
    if not candidate.is_absolute():
        candidate = workspace_root / candidate
    return security.assert_safe_local_path(workspace_root, candidate)


def resolve_response_check_path(
    workspace_root: Path,
    module_dir: Path,
    response_check_path: Path,
) -> Path:
    """Validate a response check JSON path under the current module response folder."""

    responses_root = synthesis_response.get_responses_root(module_dir)
    security.assert_safe_local_path(workspace_root, responses_root)
    candidate = response_check_path
    if not candidate.is_absolute():
        candidate = workspace_root / candidate
    resolved = security.assert_safe_local_path(workspace_root, candidate)
    ensure_within_directory(responses_root, resolved)
    if resolved.name != synthesis_response.RESPONSE_CHECK_JSON_FILENAME:
        raise ValueError(
            f"Response check must be named {synthesis_response.RESPONSE_CHECK_JSON_FILENAME}."
        )
    if not resolved.is_file():
        raise FileNotFoundError(f"Response check not found: {resolved}")
    return resolved


def read_response_check(response_check_path: Path) -> dict[str, Any]:
    """Read a response check JSON file."""

    return json.loads(response_check_path.read_text(encoding="utf-8"))


def validate_response_check_data(check_data: dict[str, Any]) -> None:
    """Validate response check status and local-only safety fields."""

    required_values = {
        "schema_version": synthesis_response.RESPONSE_CHECK_SCHEMA_VERSION,
        "status": synthesis_response.RESPONSE_STATUS_READY_FOR_MANUAL_REVIEW,
        "local_only": True,
        "api_enabled": False,
        "network_enabled": False,
        "synthesis_generated": False,
        "summary_generated": False,
        "untrusted_external_text": True,
    }
    for field_name, expected_value in required_values.items():
        if check_data.get(field_name) != expected_value:
            raise ValueError(
                f"Response check field {field_name} must be {expected_value!r}."
            )

    valid_chunk_count = check_data.get("valid_chunk_count", 0)
    unknown_chunk_count = check_data.get("unknown_chunk_count", 0)
    if not isinstance(valid_chunk_count, int) or valid_chunk_count <= 0:
        raise ValueError("Response check must contain at least one valid chunk citation.")
    if unknown_chunk_count != 0:
        raise ValueError("Response check must not contain unknown chunk citations.")


def resolve_checked_response_path(
    workspace_root: Path,
    module_dir: Path,
    check_data: dict[str, Any],
) -> Path:
    """Validate the copied response path from a response check record."""

    response_path = resolve_workspace_manifest_path(
        workspace_root,
        str(check_data.get("response_path", "")),
    )
    ensure_within_directory(synthesis_response.get_responses_root(module_dir), response_path)
    if not response_path.is_file():
        raise FileNotFoundError(f"Checked response file not found: {response_path}")
    return response_path


def resolve_checked_package_manifest_path(
    workspace_root: Path,
    module_dir: Path,
    check_data: dict[str, Any],
) -> Path:
    """Validate the package manifest path from a response check record."""

    package_manifest_path = resolve_workspace_manifest_path(
        workspace_root,
        str(check_data.get("package_manifest_path", "")),
    )
    return synthesis_response.resolve_package_manifest_path(
        workspace_root,
        module_dir,
        package_manifest_path,
    )


def read_checked_response_text(response_path: Path) -> str:
    """Read checked response text as UTF-8 without altering content."""

    try:
        return response_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"Checked response file must be UTF-8 text: {response_path}") from exc


def build_promotion_provenance(
    workspace_root: Path,
    module_dir: Path,
    *,
    created_at: str,
    response_check_path: Path,
    response_path: Path,
    package_manifest_path: Path,
    final_synthesis_path: Path,
    provenance_path: Path,
    response_text: str,
    check_data: dict[str, Any],
) -> dict[str, Any]:
    """Build local provenance for a promotion without rewriting response text."""

    return {
        "schema_version": PROMOTION_SCHEMA_VERSION,
        "module_path": paths.relative_to_workspace(workspace_root, module_dir),
        "created_at": created_at,
        "status": "PROMOTED_TO_FINAL_SYNTHESIS",
        "local_only": True,
        "api_enabled": False,
        "network_enabled": False,
        "synthesis_generated": False,
        "summary_generated": False,
        "clinical_claims_rewritten": False,
        "clinical_truth_validated": False,
        "untrusted_external_text": True,
        "source_status": check_data.get("status", ""),
        "response_check_path": paths.relative_to_workspace(
            workspace_root,
            response_check_path,
        ),
        "response_path": paths.relative_to_workspace(workspace_root, response_path),
        "package_manifest_path": paths.relative_to_workspace(
            workspace_root,
            package_manifest_path,
        ),
        "final_synthesis_path": paths.relative_to_workspace(
            workspace_root,
            final_synthesis_path,
        ),
        "provenance_path": paths.relative_to_workspace(workspace_root, provenance_path),
        "promoted_char_count": len(response_text),
        "valid_chunk_count": check_data.get("valid_chunk_count", 0),
        "unknown_chunk_count": check_data.get("unknown_chunk_count", 0),
        "valid_chunk_ids": check_data.get("valid_chunk_ids", []),
        "cited_chunk_ids": check_data.get("cited_chunk_ids", []),
    }


def build_promotion_payload(
    workspace_root: Path,
    module_dir: Path,
    response_check_path: Path,
    *,
    created_at: str,
) -> PromotionPayload:
    """Validate all promotion inputs and build payloads before writing files."""

    security.assert_safe_local_path(workspace_root, module_dir)
    resolved_check_path = resolve_response_check_path(
        workspace_root,
        module_dir,
        response_check_path,
    )
    check_data = read_response_check(resolved_check_path)
    validate_response_check_data(check_data)
    response_path = resolve_checked_response_path(workspace_root, module_dir, check_data)
    package_manifest_path = resolve_checked_package_manifest_path(
        workspace_root,
        module_dir,
        check_data,
    )
    response_text = read_checked_response_text(response_path)

    module_paths = paths.get_module_paths(module_dir)
    final_synthesis_path = module_paths.final_synthesis
    provenance_path = final_synthesis_path.parent / PROMOTION_PROVENANCE_FILENAME
    for output_path in (final_synthesis_path.parent, final_synthesis_path, provenance_path):
        security.assert_safe_local_path(workspace_root, output_path)
    if final_synthesis_path.exists():
        raise FileExistsError(f"Final synthesis already exists: {final_synthesis_path}")
    if provenance_path.exists():
        raise FileExistsError(f"Promotion provenance already exists: {provenance_path}")

    provenance = build_promotion_provenance(
        workspace_root,
        module_dir,
        created_at=created_at,
        response_check_path=resolved_check_path,
        response_path=response_path,
        package_manifest_path=package_manifest_path,
        final_synthesis_path=final_synthesis_path,
        provenance_path=provenance_path,
        response_text=response_text,
        check_data=check_data,
    )
    return PromotionPayload(
        response_check_path=resolved_check_path,
        response_path=response_path,
        package_manifest_path=package_manifest_path,
        final_synthesis_path=final_synthesis_path,
        provenance_path=provenance_path,
        response_text=response_text,
        check_data=check_data,
        provenance=provenance,
    )


def write_promotion_outputs(payload: PromotionPayload) -> None:
    """Write final synthesis and provenance through temporary files."""

    final_dir = payload.final_synthesis_path.parent
    final_dir.mkdir(parents=True, exist_ok=True)
    final_written = False
    provenance_written = False
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        newline="\n",
        dir=final_dir,
        delete=False,
        prefix=".tmp_module_master_synthesis_",
        suffix=".md",
    ) as final_handle:
        final_handle.write(payload.response_text)
        temp_final_path = Path(final_handle.name)
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        newline="\n",
        dir=final_dir,
        delete=False,
        prefix=".tmp_promotion_provenance_",
        suffix=".json",
    ) as provenance_handle:
        provenance_handle.write(json.dumps(payload.provenance, indent=2, ensure_ascii=False))
        provenance_handle.write("\n")
        temp_provenance_path = Path(provenance_handle.name)
    try:
        if payload.final_synthesis_path.exists():
            raise FileExistsError(f"Final synthesis already exists: {payload.final_synthesis_path}")
        if payload.provenance_path.exists():
            raise FileExistsError(f"Promotion provenance already exists: {payload.provenance_path}")
        temp_final_path.rename(payload.final_synthesis_path)
        final_written = True
        temp_provenance_path.rename(payload.provenance_path)
        provenance_written = True
    except Exception:
        if temp_final_path.exists():
            temp_final_path.unlink()
        if temp_provenance_path.exists():
            temp_provenance_path.unlink()
        if final_written and not provenance_written and payload.final_synthesis_path.exists():
            payload.final_synthesis_path.unlink()
        raise


def promote_checked_response_to_final_synthesis(
    workspace_root: Path,
    module_dir: Path,
    response_check_path: Path,
    *,
    created_at: str,
) -> PromotionResult:
    """Promote one checked response to final synthesis by exact local copy."""

    payload = build_promotion_payload(
        workspace_root,
        module_dir,
        response_check_path,
        created_at=created_at,
    )
    write_promotion_outputs(payload)
    return PromotionResult(
        final_synthesis_path=payload.final_synthesis_path,
        provenance_path=payload.provenance_path,
        response_check_path=payload.response_check_path,
        response_path=payload.response_path,
        package_manifest_path=payload.package_manifest_path,
        promoted_char_count=len(payload.response_text),
        provenance=payload.provenance,
    )


def find_newest_eligible_response_check(workspace_root: Path, module_dir: Path) -> Path | None:
    """Return the newest response check eligible for final synthesis promotion."""

    responses_root = synthesis_response.get_responses_root(module_dir)
    if not responses_root.exists():
        return None
    candidates: list[Path] = []
    for check_path in responses_root.glob(
        f"{synthesis_response.RESPONSE_DIR_PREFIX}*/{synthesis_response.RESPONSE_CHECK_JSON_FILENAME}"
    ):
        if not check_path.is_file():
            continue
        try:
            build_promotion_payload(
                workspace_root,
                module_dir,
                check_path,
                created_at=datetime.now().astimezone().isoformat(timespec="seconds"),
            )
        except (FileNotFoundError, FileExistsError, OSError, ValueError, json.JSONDecodeError):
            continue
        candidates.append(check_path)
    if not candidates:
        return None
    return sorted(
        candidates,
        key=lambda check_path: (check_path.parent.name, check_path.stat().st_mtime),
        reverse=True,
    )[0]
