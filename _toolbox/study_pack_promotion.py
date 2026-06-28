"""Local-only promotion of checked external study-pack responses."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
from typing import Any

from _toolbox import paths, security, study_pack_response


PROMOTION_SCHEMA_VERSION = 1
FINAL_STUDY_PACK_FILENAME = "final_study_pack.md"
PROMOTION_PROVENANCE_FILENAME = "final_study_pack_promotion_provenance.json"
PROMOTION_STATUS = "PROMOTED_TO_FINAL_STUDY_PACK"
CONFIRMATION_PHRASE = "PROMOTE FINAL STUDY PACK"


@dataclass(frozen=True)
class StudyPackPromotionPayload:
    """Validated study-pack promotion data prepared before final writes."""

    response_check_path: Path
    response_path: Path
    prompt_manifest_path: Path
    final_study_pack_path: Path
    provenance_path: Path
    response_bytes: bytes
    check_data: dict[str, Any]
    provenance: dict[str, Any]


@dataclass(frozen=True)
class StudyPackPromotionResult:
    """Result from promoting one checked study-pack response."""

    final_study_pack_path: Path
    provenance_path: Path
    response_check_path: Path
    response_path: Path
    prompt_manifest_path: Path
    promoted_byte_count: int
    promoted_char_count: int
    response_sha256: str
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


def long_path_string(path: Path) -> str:
    """Return a filesystem path string that is safe for long Windows paths."""

    resolved_path = str(path.resolve())
    if os.name != "nt" or resolved_path.startswith("\\\\?\\"):
        return resolved_path
    if resolved_path.startswith("\\\\"):
        return "\\\\?\\UNC\\" + resolved_path.lstrip("\\")
    return "\\\\?\\" + resolved_path


def resolve_workspace_record_path(
    workspace_root: Path,
    raw_path: str,
    field_name: str,
) -> Path:
    """Resolve a workspace-relative path recorded in a Step 17 check."""

    cleaned_path = raw_path.strip()
    if not cleaned_path:
        raise ValueError(f"Study-pack response check field {field_name} cannot be blank.")
    candidate = Path(cleaned_path)
    if not candidate.is_absolute():
        candidate = workspace_root / candidate
    return security.assert_safe_local_path(workspace_root, candidate)


def resolve_response_check_path(
    workspace_root: Path,
    module_dir: Path,
    response_check_path: Path,
) -> Path:
    """Validate a Step 17 response check path under the current module."""

    responses_root = study_pack_response.get_study_pack_responses_root(module_dir)
    security.assert_safe_local_path(workspace_root, responses_root)
    candidate = response_check_path
    if not candidate.is_absolute():
        candidate = workspace_root / candidate
    resolved = security.assert_safe_local_path(workspace_root, candidate)
    ensure_within_directory(responses_root, resolved)
    if resolved.name != study_pack_response.RESPONSE_CHECK_JSON_FILENAME:
        raise ValueError(
            f"Study-pack response check must be named "
            f"{study_pack_response.RESPONSE_CHECK_JSON_FILENAME}."
        )
    if not resolved.parent.name.startswith(study_pack_response.RESPONSE_DIR_PREFIX):
        raise ValueError("Study-pack response check must be inside a Step 17 response folder.")
    if not os.path.isfile(long_path_string(resolved)):
        raise FileNotFoundError(f"Study-pack response check not found: {resolved}")
    return resolved


def read_response_check(response_check_path: Path) -> dict[str, Any]:
    """Read a Step 17 response check JSON file."""

    try:
        with open(long_path_string(response_check_path), encoding="utf-8") as response_check_file:
            return json.load(response_check_file)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Study-pack response check is invalid JSON: {response_check_path}") from exc


def validate_response_check_data(
    workspace_root: Path,
    module_dir: Path,
    response_check_path: Path,
    check_data: dict[str, Any],
) -> None:
    """Validate fields actually written by Step 17."""

    required_values = {
        "schema_version": study_pack_response.STUDY_PACK_RESPONSE_SCHEMA_VERSION,
        "module_path": paths.relative_to_workspace(workspace_root, module_dir),
        "status": study_pack_response.RESPONSE_STATUS_READY_FOR_MANUAL_REVIEW,
        "local_only": True,
        "api_enabled": False,
        "network_enabled": False,
        "study_pack_generated": False,
        "final_study_pack_promoted": False,
        "summary_generated": False,
        "clinical_claims_rewritten": False,
        "clinical_truth_validated": False,
        "untrusted_external_text": True,
        "clinical_validation_performed": False,
    }
    for field_name, expected_value in required_values.items():
        if check_data.get(field_name) != expected_value:
            raise ValueError(
                f"Study-pack response check field {field_name} must be {expected_value!r}."
            )

    responses_root = study_pack_response.get_study_pack_responses_root(module_dir)
    response_dir = resolve_workspace_record_path(
        workspace_root,
        str(check_data.get("response_dir", "")),
        "response_dir",
    )
    ensure_within_directory(responses_root, response_dir)
    if paths.resolve_for_containment(response_dir) != paths.resolve_for_containment(
        response_check_path.parent
    ):
        raise ValueError("Study-pack response check folder does not match response_dir.")

    recorded_check_path = resolve_workspace_record_path(
        workspace_root,
        str(check_data.get("check_json_path", "")),
        "check_json_path",
    )
    if paths.resolve_for_containment(recorded_check_path) != paths.resolve_for_containment(
        response_check_path
    ):
        raise ValueError("Study-pack response check path does not match its location.")

    check_markdown_path = resolve_workspace_record_path(
        workspace_root,
        str(check_data.get("check_markdown_path", "")),
        "check_markdown_path",
    )
    ensure_within_directory(response_dir, check_markdown_path)
    if check_markdown_path.name != study_pack_response.RESPONSE_CHECK_MARKDOWN_FILENAME:
        raise ValueError("Study-pack response check markdown path is invalid.")

    response_path = resolve_workspace_record_path(
        workspace_root,
        str(check_data.get("response_path", "")),
        "response_path",
    )
    ensure_within_directory(response_dir, response_path)
    if response_path.name != study_pack_response.RESPONSE_FILENAME:
        raise ValueError("Study-pack response path is invalid.")


def resolve_checked_response_path(
    workspace_root: Path,
    module_dir: Path,
    check_data: dict[str, Any],
) -> Path:
    """Validate the copied response path from a Step 17 check."""

    response_path = resolve_workspace_record_path(
        workspace_root,
        str(check_data.get("response_path", "")),
        "response_path",
    )
    ensure_within_directory(study_pack_response.get_study_pack_responses_root(module_dir), response_path)
    if not os.path.isfile(long_path_string(response_path)):
        raise FileNotFoundError(f"Checked study-pack response file not found: {response_path}")
    return response_path


def resolve_checked_prompt_manifest_path(
    workspace_root: Path,
    module_dir: Path,
    check_data: dict[str, Any],
) -> Path:
    """Validate the Step 16 prompt manifest referenced by a Step 17 check."""

    prompt_manifest_path = resolve_workspace_record_path(
        workspace_root,
        str(check_data.get("prompt_manifest_path", "")),
        "prompt_manifest_path",
    )
    resolved_manifest_path = study_pack_response.resolve_prompt_manifest_path(
        workspace_root,
        module_dir,
        prompt_manifest_path,
    )
    prompt_manifest = study_pack_response.read_prompt_manifest(resolved_manifest_path)
    study_pack_response.validate_prompt_manifest(
        workspace_root,
        module_dir,
        resolved_manifest_path,
        prompt_manifest,
    )
    prompt_manifest_sha256 = check_data.get("prompt_manifest_sha256")
    if prompt_manifest_sha256 is not None:
        with open(long_path_string(resolved_manifest_path), "rb") as prompt_manifest_file:
            actual_sha256 = hashlib.sha256(prompt_manifest_file.read()).hexdigest()
        if prompt_manifest_sha256 != actual_sha256:
            raise ValueError("Study-pack response check prompt manifest SHA256 is stale.")
    return resolved_manifest_path


def read_checked_response_bytes(response_path: Path, check_data: dict[str, Any]) -> bytes:
    """Read checked response bytes and verify Step 17 hash/count fields when present."""

    with open(long_path_string(response_path), "rb") as response_file:
        response_bytes = response_file.read()
    try:
        response_text = response_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"Checked study-pack response must be UTF-8 text: {response_path}") from exc
    if not response_text.strip():
        raise ValueError(f"Checked study-pack response is empty: {response_path}")

    response_byte_count = check_data.get("response_byte_count")
    if response_byte_count is not None and response_byte_count != len(response_bytes):
        raise ValueError("Study-pack response check byte count is stale.")
    response_char_count = check_data.get("response_char_count")
    if response_char_count is not None and response_char_count != len(response_text):
        raise ValueError("Study-pack response check character count is stale.")
    response_sha256 = check_data.get("response_sha256")
    if response_sha256 is not None and response_sha256 != hashlib.sha256(response_bytes).hexdigest():
        raise ValueError("Study-pack response check SHA256 is stale.")
    return response_bytes


def build_promotion_provenance(
    workspace_root: Path,
    module_dir: Path,
    *,
    created_at: str,
    response_check_path: Path,
    response_path: Path,
    prompt_manifest_path: Path,
    final_study_pack_path: Path,
    provenance_path: Path,
    response_bytes: bytes,
    response_text: str,
    check_data: dict[str, Any],
) -> dict[str, Any]:
    """Build local provenance for a final study-pack promotion."""

    return {
        "schema_version": PROMOTION_SCHEMA_VERSION,
        "module_path": paths.relative_to_workspace(workspace_root, module_dir),
        "created_at": created_at,
        "status": PROMOTION_STATUS,
        "local_only": True,
        "api_enabled": False,
        "network_enabled": False,
        "study_pack_generated": False,
        "final_study_pack_promoted": True,
        "summary_generated": False,
        "clinical_claims_rewritten": False,
        "clinical_truth_validated": False,
        "clinical_validation_performed": False,
        "untrusted_external_text": True,
        "exact_copy": True,
        "source_status": check_data.get("status", ""),
        "response_check_path": paths.relative_to_workspace(workspace_root, response_check_path),
        "response_path": paths.relative_to_workspace(workspace_root, response_path),
        "prompt_manifest_path": paths.relative_to_workspace(workspace_root, prompt_manifest_path),
        "final_study_pack_path": paths.relative_to_workspace(workspace_root, final_study_pack_path),
        "provenance_path": paths.relative_to_workspace(workspace_root, provenance_path),
        "promoted_byte_count": len(response_bytes),
        "promoted_char_count": len(response_text),
        "response_sha256": hashlib.sha256(response_bytes).hexdigest(),
        "source_response_byte_count": check_data.get("response_byte_count"),
        "source_response_char_count": check_data.get("response_char_count"),
        "source_response_sha256": check_data.get("response_sha256"),
    }


def build_promotion_payload(
    workspace_root: Path,
    module_dir: Path,
    response_check_path: Path,
    *,
    created_at: str,
) -> StudyPackPromotionPayload:
    """Validate all final study-pack promotion inputs before writing files."""

    security.assert_safe_local_path(workspace_root, module_dir)
    resolved_check_path = resolve_response_check_path(
        workspace_root,
        module_dir,
        response_check_path,
    )
    check_data = read_response_check(resolved_check_path)
    validate_response_check_data(workspace_root, module_dir, resolved_check_path, check_data)
    response_path = resolve_checked_response_path(workspace_root, module_dir, check_data)
    prompt_manifest_path = resolve_checked_prompt_manifest_path(workspace_root, module_dir, check_data)
    response_bytes = read_checked_response_bytes(response_path, check_data)
    response_text = response_bytes.decode("utf-8")

    study_pack_dir = paths.get_module_paths(module_dir).study_pack_dir
    final_study_pack_path = study_pack_dir / FINAL_STUDY_PACK_FILENAME
    provenance_path = study_pack_dir / PROMOTION_PROVENANCE_FILENAME
    for output_path in (study_pack_dir, final_study_pack_path, provenance_path):
        security.assert_safe_local_path(workspace_root, output_path)
        ensure_within_directory(study_pack_dir, output_path)
    if os.path.exists(long_path_string(final_study_pack_path)):
        raise FileExistsError(f"Final study pack already exists: {final_study_pack_path}")
    if os.path.exists(long_path_string(provenance_path)):
        raise FileExistsError(f"Final study-pack promotion provenance already exists: {provenance_path}")

    provenance = build_promotion_provenance(
        workspace_root,
        module_dir,
        created_at=created_at,
        response_check_path=resolved_check_path,
        response_path=response_path,
        prompt_manifest_path=prompt_manifest_path,
        final_study_pack_path=final_study_pack_path,
        provenance_path=provenance_path,
        response_bytes=response_bytes,
        response_text=response_text,
        check_data=check_data,
    )
    return StudyPackPromotionPayload(
        response_check_path=resolved_check_path,
        response_path=response_path,
        prompt_manifest_path=prompt_manifest_path,
        final_study_pack_path=final_study_pack_path,
        provenance_path=provenance_path,
        response_bytes=response_bytes,
        check_data=check_data,
        provenance=provenance,
    )


def write_promotion_outputs(payload: StudyPackPromotionPayload) -> None:
    """Write final study pack and provenance through temporary files."""

    final_dir = payload.final_study_pack_path.parent
    final_dir_fs = long_path_string(final_dir)
    final_study_pack_fs = long_path_string(payload.final_study_pack_path)
    provenance_fs = long_path_string(payload.provenance_path)
    temp_final_path = final_dir / ".tmp_fsp.md"
    temp_provenance_path = final_dir / ".tmp_fsp_provenance.json"
    temp_final_fs = long_path_string(temp_final_path)
    temp_provenance_fs = long_path_string(temp_provenance_path)

    os.makedirs(final_dir_fs, exist_ok=True)
    final_written = False
    provenance_written = False
    try:
        if os.path.exists(final_study_pack_fs):
            raise FileExistsError(f"Final study pack already exists: {payload.final_study_pack_path}")
        if os.path.exists(provenance_fs):
            raise FileExistsError(
                f"Final study-pack promotion provenance already exists: {payload.provenance_path}"
            )
        if os.path.exists(temp_final_fs):
            os.unlink(temp_final_fs)
        if os.path.exists(temp_provenance_fs):
            os.unlink(temp_provenance_fs)
        with open(temp_final_fs, "wb") as final_handle:
            final_handle.write(payload.response_bytes)
        with open(temp_provenance_fs, "w", encoding="utf-8", newline="\n") as provenance_handle:
            provenance_handle.write(json.dumps(payload.provenance, indent=2, ensure_ascii=False))
            provenance_handle.write("\n")
        if not os.path.isfile(temp_final_fs):
            raise RuntimeError(f"Temporary final study pack was not created: {temp_final_path}")
        if not os.path.isfile(temp_provenance_fs):
            raise RuntimeError(
                f"Temporary final study-pack promotion provenance was not created: {temp_provenance_path}"
            )
        if os.path.exists(final_study_pack_fs):
            raise FileExistsError(f"Final study pack already exists: {payload.final_study_pack_path}")
        if os.path.exists(provenance_fs):
            raise FileExistsError(
                f"Final study-pack promotion provenance already exists: {payload.provenance_path}"
            )
        os.replace(temp_final_fs, final_study_pack_fs)
        final_written = True
        os.replace(temp_provenance_fs, provenance_fs)
        provenance_written = True
    except Exception:
        if os.path.exists(temp_final_fs):
            os.unlink(temp_final_fs)
        if os.path.exists(temp_provenance_fs):
            os.unlink(temp_provenance_fs)
        if final_written and not provenance_written and os.path.exists(final_study_pack_fs):
            os.unlink(final_study_pack_fs)
        raise


def promote_checked_response_to_final_study_pack(
    workspace_root: Path,
    module_dir: Path,
    response_check_path: Path,
    *,
    created_at: str,
) -> StudyPackPromotionResult:
    """Promote one checked Step 17 response to final study pack by exact byte copy."""

    payload = build_promotion_payload(
        workspace_root,
        module_dir,
        response_check_path,
        created_at=created_at,
    )
    write_promotion_outputs(payload)
    return StudyPackPromotionResult(
        final_study_pack_path=payload.final_study_pack_path,
        provenance_path=payload.provenance_path,
        response_check_path=payload.response_check_path,
        response_path=payload.response_path,
        prompt_manifest_path=payload.prompt_manifest_path,
        promoted_byte_count=len(payload.response_bytes),
        promoted_char_count=int(payload.provenance["promoted_char_count"]),
        response_sha256=str(payload.provenance["response_sha256"]),
        provenance=payload.provenance,
    )


def find_newest_eligible_response_check(workspace_root: Path, module_dir: Path) -> Path | None:
    """Return the newest Step 17 check eligible for final study-pack promotion."""

    responses_root = study_pack_response.get_study_pack_responses_root(module_dir)
    if not responses_root.exists():
        return None
    candidates: list[Path] = []
    for check_path in responses_root.glob(
        f"{study_pack_response.RESPONSE_DIR_PREFIX}*/"
        f"{study_pack_response.RESPONSE_CHECK_JSON_FILENAME}"
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
