"""Local-only external study-pack response intake checks."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
from typing import Any

from _toolbox import paths, security, study_pack_prompt


STUDY_PACK_RESPONSE_SCHEMA_VERSION = 1
RESPONSE_STATUS_READY_FOR_MANUAL_REVIEW = "READY_FOR_MANUAL_REVIEW"
RESPONSE_FILENAME = "external_study_pack_response.md"
RESPONSE_CHECK_JSON_FILENAME = "study_pack_response_check.json"
RESPONSE_CHECK_MARKDOWN_FILENAME = "study_pack_response_check.md"
RESPONSES_DIRNAME = "study_pack_responses"
RESPONSE_DIR_PREFIX = "response_"
TEMP_RESPONSE_DIRNAME = ".tmp_r"
ALLOWED_RESPONSE_SUFFIXES = (".md", ".txt")


@dataclass(frozen=True)
class StudyPackResponseResult:
    """Result from importing and checking one external study-pack response."""

    response_dir: Path
    response_path: Path
    check_json_path: Path
    check_markdown_path: Path
    status: str
    response_char_count: int
    response_byte_count: int
    check_data: dict[str, Any]


def get_study_pack_responses_root(module_dir: Path) -> Path:
    """Return the generated study-pack response intake root for a module."""

    return paths.get_module_paths(module_dir).study_pack_dir / RESPONSES_DIRNAME


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
    raise FileExistsError(f"Could not choose a unique study-pack response folder for: {base_name}")


def resolve_workspace_manifest_path(
    workspace_root: Path,
    raw_path: str,
    field_name: str,
) -> Path:
    """Resolve and validate one workspace-relative manifest path."""

    cleaned_path = raw_path.strip()
    if not cleaned_path:
        raise ValueError(f"Prompt manifest field {field_name} cannot be blank.")
    candidate = Path(cleaned_path)
    if not candidate.is_absolute():
        candidate = workspace_root / candidate
    return security.assert_safe_local_path(workspace_root, candidate)


def resolve_prompt_manifest_path(
    workspace_root: Path,
    module_dir: Path,
    prompt_manifest_path: Path,
) -> Path:
    """Validate a Step 16 prompt manifest under the current module study-pack folder."""

    study_pack_root = paths.get_module_paths(module_dir).study_pack_dir
    security.assert_safe_local_path(workspace_root, study_pack_root)
    candidate = prompt_manifest_path
    if not candidate.is_absolute():
        candidate = workspace_root / candidate
    resolved = security.assert_safe_local_path(workspace_root, candidate)
    ensure_within_directory(study_pack_root, resolved)
    if resolved.name != study_pack_prompt.PROMPT_MANIFEST_FILENAME:
        raise ValueError(
            f"Prompt manifest must be named {study_pack_prompt.PROMPT_MANIFEST_FILENAME}."
        )
    if resolved.parent.name.startswith(study_pack_prompt.PROMPT_PACKAGE_DIR_PREFIX) is False:
        raise ValueError("Prompt manifest must be inside a Step 16 prompt package folder.")
    if not resolved.is_file():
        raise FileNotFoundError(f"Prompt manifest not found: {resolved}")
    return resolved


def find_newest_prompt_manifest(module_dir: Path) -> Path | None:
    """Return the newest Step 16 prompt manifest under the module study-pack folder."""

    study_pack_root = paths.get_module_paths(module_dir).study_pack_dir
    if not study_pack_root.exists():
        return None
    manifests = [
        manifest_path
        for manifest_path in study_pack_root.glob(
            f"{study_pack_prompt.PROMPT_PACKAGE_DIR_PREFIX}*/"
            f"{study_pack_prompt.PROMPT_MANIFEST_FILENAME}"
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


def read_prompt_manifest(prompt_manifest_path: Path) -> dict[str, Any]:
    """Read and minimally validate JSON syntax for a Step 16 prompt manifest."""

    try:
        return json.loads(prompt_manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Prompt manifest is invalid JSON: {prompt_manifest_path}") from exc


def validate_prompt_manifest(
    workspace_root: Path,
    module_dir: Path,
    prompt_manifest_path: Path,
    prompt_manifest: dict[str, Any],
) -> None:
    """Validate real Step 16 prompt manifest fields before response intake."""

    expected_values = {
        "schema_version": study_pack_prompt.PROMPT_PACKAGE_SCHEMA_VERSION,
        "status": study_pack_prompt.PROMPT_PACKAGE_STATUS,
        "local_only": True,
        "api_enabled": False,
        "network_enabled": False,
        "study_pack_generated": False,
        "summary_generated": False,
        "clinical_claims_rewritten": False,
        "clinical_truth_validated": False,
        "untrusted_external_text": True,
        "instructions_only": True,
    }
    for field_name, expected_value in expected_values.items():
        if prompt_manifest.get(field_name) != expected_value:
            raise ValueError(f"Prompt manifest field {field_name} must be {expected_value!r}.")

    expected_module_path = paths.relative_to_workspace(workspace_root, module_dir)
    if prompt_manifest.get("module_path") != expected_module_path:
        raise ValueError("Prompt manifest module path does not match this module.")

    study_pack_root = paths.get_module_paths(module_dir).study_pack_dir
    package_dir = resolve_workspace_manifest_path(
        workspace_root,
        str(prompt_manifest.get("package_dir", "")),
        "package_dir",
    )
    ensure_within_directory(study_pack_root, package_dir)
    if paths.resolve_for_containment(package_dir) != paths.resolve_for_containment(
        prompt_manifest_path.parent
    ):
        raise ValueError("Prompt manifest package folder does not match its location.")

    recorded_manifest_path = resolve_workspace_manifest_path(
        workspace_root,
        str(prompt_manifest.get("prompt_manifest_path", "")),
        "prompt_manifest_path",
    )
    if paths.resolve_for_containment(recorded_manifest_path) != paths.resolve_for_containment(
        prompt_manifest_path
    ):
        raise ValueError("Prompt manifest path does not match its location.")

    prompt_path = resolve_workspace_manifest_path(
        workspace_root,
        str(prompt_manifest.get("study_pack_prompt_path", "")),
        "study_pack_prompt_path",
    )
    final_input_path = resolve_workspace_manifest_path(
        workspace_root,
        str(prompt_manifest.get("final_synthesis_input_path", "")),
        "final_synthesis_input_path",
    )
    final_synthesis_path = resolve_workspace_manifest_path(
        workspace_root,
        str(prompt_manifest.get("final_synthesis_path", "")),
        "final_synthesis_path",
    )
    for recorded_path in (prompt_path, final_input_path, final_synthesis_path):
        ensure_within_directory(module_dir, recorded_path)
        if not recorded_path.is_file():
            raise FileNotFoundError(f"Prompt manifest referenced file not found: {recorded_path}")

    ensure_within_directory(package_dir, prompt_path)
    ensure_within_directory(package_dir, final_input_path)

    final_input_bytes = final_input_path.read_bytes()
    final_synthesis_bytes = final_synthesis_path.read_bytes()
    recorded_byte_count = prompt_manifest.get("final_synthesis_byte_count")
    if not isinstance(recorded_byte_count, int) or recorded_byte_count != len(final_input_bytes):
        raise ValueError("Prompt manifest final_synthesis_input byte count is stale.")
    recorded_sha256 = str(prompt_manifest.get("final_synthesis_sha256", "")).strip()
    if hashlib.sha256(final_input_bytes).hexdigest() != recorded_sha256:
        raise ValueError("Prompt manifest final_synthesis_input SHA256 is stale.")
    if final_input_bytes != final_synthesis_bytes:
        raise ValueError("Prompt manifest final_synthesis_input is stale for the current final synthesis.")

    study_pack_prompt.validate_prompt_manifest_source_provenance(
        workspace_root,
        module_dir,
        prompt_manifest,
        final_synthesis_path,
        final_synthesis_bytes,
    )


def resolve_response_input_path(response_file_path: Path) -> Path:
    """Validate an existing local UTF-8 Markdown or text study-pack response file."""

    resolved = response_file_path.resolve(strict=True)
    if not resolved.is_file():
        raise FileNotFoundError(f"Study-pack response file not found: {resolved}")
    if resolved.suffix.lower() not in ALLOWED_RESPONSE_SUFFIXES:
        allowed = ", ".join(ALLOWED_RESPONSE_SUFFIXES)
        raise ValueError(f"Study-pack response file must use one of these extensions: {allowed}.")
    return resolved


def read_response_bytes_and_text(response_file_path: Path) -> tuple[bytes, str]:
    """Read response bytes exactly and decode as UTF-8 without line-ending changes."""

    response_bytes = response_file_path.read_bytes()
    try:
        response_text = response_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"Study-pack response file must be UTF-8 text: {response_file_path}") from exc
    if not response_text.strip():
        raise ValueError(f"Study-pack response file is empty: {response_file_path}")
    return response_bytes, response_text


def build_response_check_data(
    workspace_root: Path,
    module_dir: Path,
    *,
    created_at: str,
    prompt_manifest_path: Path,
    prompt_manifest: dict[str, Any],
    response_dir: Path,
    response_path: Path,
    check_json_path: Path,
    check_markdown_path: Path,
    response_file_path: Path,
    response_bytes: bytes,
    response_text: str,
) -> dict[str, Any]:
    """Build local-only response check data without writing files."""

    return {
        "schema_version": STUDY_PACK_RESPONSE_SCHEMA_VERSION,
        "module_path": paths.relative_to_workspace(workspace_root, module_dir),
        "created_at": created_at,
        "status": RESPONSE_STATUS_READY_FOR_MANUAL_REVIEW,
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
        "prompt_manifest_path": paths.relative_to_workspace(workspace_root, prompt_manifest_path),
        "prompt_package_dir": paths.relative_to_workspace(workspace_root, prompt_manifest_path.parent),
        "response_dir": paths.relative_to_workspace(workspace_root, response_dir),
        "response_path": paths.relative_to_workspace(workspace_root, response_path),
        "check_json_path": paths.relative_to_workspace(workspace_root, check_json_path),
        "check_markdown_path": paths.relative_to_workspace(workspace_root, check_markdown_path),
        "source_response_file": str(response_file_path),
        "response_char_count": len(response_text),
        "response_byte_count": len(response_bytes),
        "response_sha256": hashlib.sha256(response_bytes).hexdigest(),
        "prompt_manifest_sha256": hashlib.sha256(
            prompt_manifest_path.read_bytes()
        ).hexdigest(),
        "prompt_package_status": prompt_manifest.get("status", ""),
    }


def build_response_check_markdown(check_data: dict[str, Any]) -> str:
    """Build a local check report without summarizing the imported response."""

    return (
        "# External Study-Pack Response Check\n\n"
        f"Status: {check_data['status']}\n\n"
        "This report only confirms local intake and prompt-package consistency. It does "
        "not clinically validate the study pack, does not summarize the response, and "
        "does not prove the external model followed the prompt.\n\n"
        "## Local-Only Safety\n\n"
        "- API enabled: false\n"
        "- Network enabled: false\n"
        "- Study pack generated locally: false\n"
        "- Final study pack promoted: false\n"
        "- Summary generated: false\n"
        "- Clinical claims rewritten: false\n"
        "- Clinical truth validated: false\n"
        "- Imported response text is untrusted external user-provided text.\n\n"
        "## Files\n\n"
        f"- Prompt manifest: {check_data['prompt_manifest_path']}\n"
        f"- Copied response: {check_data['response_path']}\n"
        f"- JSON check: {check_data['check_json_path']}\n\n"
        "## Response Counts\n\n"
        f"- Characters: {check_data['response_char_count']}\n"
        f"- Bytes: {check_data['response_byte_count']}\n"
    )


def build_response_intake_data(
    workspace_root: Path,
    module_dir: Path,
    prompt_manifest_path: Path,
    response_file_path: Path,
    *,
    created_at: str,
) -> tuple[Path, Path, Path, Path, Path, bytes, dict[str, Any], str]:
    """Validate input and build all study-pack response intake payloads."""

    security.assert_safe_local_path(workspace_root, module_dir)
    responses_root = get_study_pack_responses_root(module_dir)
    security.assert_safe_local_path(workspace_root, responses_root)
    study_pack_prompt.ensure_within_directory(paths.get_module_paths(module_dir).study_pack_dir, responses_root)
    resolved_manifest_path = resolve_prompt_manifest_path(
        workspace_root,
        module_dir,
        prompt_manifest_path,
    )
    prompt_manifest = read_prompt_manifest(resolved_manifest_path)
    validate_prompt_manifest(workspace_root, module_dir, resolved_manifest_path, prompt_manifest)
    resolved_response_file_path = resolve_response_input_path(response_file_path)
    response_bytes, response_text = read_response_bytes_and_text(resolved_response_file_path)

    response_dir = build_unique_response_dir(responses_root, created_at)
    temp_response_dir = responses_root / TEMP_RESPONSE_DIRNAME
    response_path = response_dir / RESPONSE_FILENAME
    check_json_path = response_dir / RESPONSE_CHECK_JSON_FILENAME
    check_markdown_path = response_dir / RESPONSE_CHECK_MARKDOWN_FILENAME
    for output_path in (
        response_dir,
        temp_response_dir,
        response_path,
        check_json_path,
        check_markdown_path,
    ):
        security.assert_safe_local_path(workspace_root, output_path)
        ensure_within_directory(responses_root, output_path)

    check_data = build_response_check_data(
        workspace_root,
        module_dir,
        created_at=created_at,
        prompt_manifest_path=resolved_manifest_path,
        prompt_manifest=prompt_manifest,
        response_dir=response_dir,
        response_path=response_path,
        check_json_path=check_json_path,
        check_markdown_path=check_markdown_path,
        response_file_path=resolved_response_file_path,
        response_bytes=response_bytes,
        response_text=response_text,
    )
    check_markdown = build_response_check_markdown(check_data)
    return (
        response_dir,
        temp_response_dir,
        response_path,
        check_json_path,
        check_markdown_path,
        response_bytes,
        check_data,
        check_markdown,
    )


def write_response_outputs(
    response_dir: Path,
    temp_response_dir: Path,
    response_bytes: bytes,
    check_data: dict[str, Any],
    check_markdown: str,
) -> None:
    """Write response intake files through a temporary directory, then rename."""

    response_dir_fs = long_path_string(response_dir)
    temp_response_dir_fs = long_path_string(temp_response_dir)
    responses_root_fs = long_path_string(temp_response_dir.parent)

    if os.path.exists(response_dir_fs):
        raise FileExistsError(f"Refusing to overwrite existing study-pack response folder: {response_dir}")
    os.makedirs(responses_root_fs, exist_ok=True)
    if os.path.exists(temp_response_dir_fs):
        shutil.rmtree(temp_response_dir_fs)
    try:
        os.makedirs(temp_response_dir_fs, exist_ok=False)
        if not os.path.isdir(temp_response_dir_fs):
            raise RuntimeError(f"Temporary study-pack response folder was not created: {temp_response_dir}")
        with open(os.path.join(temp_response_dir_fs, RESPONSE_FILENAME), "wb") as response_file:
            response_file.write(response_bytes)
        with open(
            os.path.join(temp_response_dir_fs, RESPONSE_CHECK_JSON_FILENAME),
            "w",
            encoding="utf-8",
            newline="\n",
        ) as check_json_file:
            check_json_file.write(json.dumps(check_data, indent=2, ensure_ascii=False) + "\n")
        with open(
            os.path.join(temp_response_dir_fs, RESPONSE_CHECK_MARKDOWN_FILENAME),
            "w",
            encoding="utf-8",
            newline="\n",
        ) as check_markdown_file:
            check_markdown_file.write(check_markdown)
        os.replace(temp_response_dir_fs, response_dir_fs)
    except Exception:
        if os.path.exists(temp_response_dir_fs):
            shutil.rmtree(temp_response_dir_fs)
        raise


def import_external_study_pack_response(
    workspace_root: Path,
    module_dir: Path,
    prompt_manifest_path: Path,
    response_file_path: Path,
    *,
    created_at: str,
) -> StudyPackResponseResult:
    """Import and check one local external study-pack response."""

    (
        response_dir,
        temp_response_dir,
        response_path,
        check_json_path,
        check_markdown_path,
        response_bytes,
        check_data,
        check_markdown,
    ) = build_response_intake_data(
        workspace_root,
        module_dir,
        prompt_manifest_path,
        response_file_path,
        created_at=created_at,
    )
    write_response_outputs(
        response_dir,
        temp_response_dir,
        response_bytes,
        check_data,
        check_markdown,
    )
    return StudyPackResponseResult(
        response_dir=response_dir,
        response_path=response_path,
        check_json_path=check_json_path,
        check_markdown_path=check_markdown_path,
        status=str(check_data["status"]),
        response_char_count=int(check_data["response_char_count"]),
        response_byte_count=int(check_data["response_byte_count"]),
        check_data=check_data,
    )
