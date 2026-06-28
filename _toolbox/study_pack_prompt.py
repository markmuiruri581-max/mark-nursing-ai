"""Local-only study-pack prompt packages from promoted final synthesis."""

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

from _toolbox import paths, security, synthesis_promotion, synthesis_response, v4_synthesis_compat


PROMPT_PACKAGE_SCHEMA_VERSION = 1
PROMPT_PACKAGE_DIR_PREFIX = "prompt_package_"
TEMP_PROMPT_PACKAGE_DIR_PREFIX = ".tmp_sp_"
STUDY_PACK_PROMPT_FILENAME = "study_pack_prompt.md"
FINAL_SYNTHESIS_INPUT_FILENAME = "final_synthesis_input.md"
PROMPT_MANIFEST_FILENAME = "prompt_manifest.json"
PROMPT_PACKAGE_STATUS = "STUDY_PACK_PROMPT_PACKAGE_READY"


@dataclass(frozen=True)
class StudyPackPromptPackageResult:
    """Result from writing one local study-pack prompt package."""

    package_dir: Path
    prompt_path: Path
    final_synthesis_input_path: Path
    manifest_path: Path
    final_synthesis_char_count: int
    final_synthesis_byte_count: int
    manifest: dict[str, Any]


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


def sanitize_prompt_package_timestamp(created_at: str) -> str:
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


def build_unique_prompt_package_dir(study_pack_root: Path, created_at: str) -> Path:
    """Return a final package folder path without overwriting existing output."""

    base_name = f"{PROMPT_PACKAGE_DIR_PREFIX}{sanitize_prompt_package_timestamp(created_at)}"
    candidate = study_pack_root / base_name
    if not candidate.exists():
        return candidate
    for sequence_number in range(2, 1000):
        candidate = study_pack_root / f"{base_name}_{sequence_number:02d}"
        if not candidate.exists():
            return candidate
    raise FileExistsError(f"Could not choose a unique prompt package folder for: {base_name}")


def build_temp_prompt_package_dir(study_pack_root: Path, package_dir: Path) -> Path:
    """Return a short same-folder temp package path for atomic rename."""

    package_suffix = package_dir.name.removeprefix(PROMPT_PACKAGE_DIR_PREFIX)
    return study_pack_root / f"{TEMP_PROMPT_PACKAGE_DIR_PREFIX}{package_suffix}"


def resolve_workspace_record_path(workspace_root: Path, raw_path: str, field_name: str) -> Path:
    """Resolve and validate one workspace-relative path recorded in provenance."""

    cleaned_path = raw_path.strip()
    if not cleaned_path:
        raise ValueError(f"Promotion provenance field {field_name} cannot be blank.")
    candidate = Path(cleaned_path)
    if not candidate.is_absolute():
        candidate = workspace_root / candidate
    return security.assert_safe_local_path(workspace_root, candidate)


def read_final_synthesis(final_synthesis_path: Path) -> tuple[bytes, str]:
    """Read the promoted final synthesis as exact bytes and UTF-8 text."""

    if not final_synthesis_path.exists():
        raise FileNotFoundError(f"Final synthesis not found: {final_synthesis_path}")
    if not final_synthesis_path.is_file():
        raise ValueError(f"Final synthesis is not a file: {final_synthesis_path}")
    final_synthesis_bytes = final_synthesis_path.read_bytes()
    try:
        final_synthesis_text = final_synthesis_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"Final synthesis must be UTF-8 text: {final_synthesis_path}") from exc
    if not final_synthesis_text.strip():
        raise ValueError(f"Final synthesis is empty: {final_synthesis_path}")
    return final_synthesis_bytes, final_synthesis_text


def read_promotion_provenance(provenance_path: Path) -> dict[str, Any]:
    """Read Step 15 promotion provenance JSON."""

    if not provenance_path.exists():
        raise FileNotFoundError(f"Promotion provenance not found: {provenance_path}")
    if not provenance_path.is_file():
        raise ValueError(f"Promotion provenance is not a file: {provenance_path}")
    try:
        return json.loads(provenance_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Promotion provenance is invalid JSON: {provenance_path}") from exc


def read_json_provenance(provenance_path: Path, provenance_label: str) -> dict[str, Any]:
    """Read a JSON provenance file with a source-specific error label."""

    if not provenance_path.exists():
        raise FileNotFoundError(f"{provenance_label} not found: {provenance_path}")
    if not provenance_path.is_file():
        raise ValueError(f"{provenance_label} is not a file: {provenance_path}")
    try:
        return json.loads(provenance_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{provenance_label} is invalid JSON: {provenance_path}") from exc


def validate_promotion_provenance(
    workspace_root: Path,
    module_dir: Path,
    *,
    provenance_path: Path,
    final_synthesis_path: Path,
    final_synthesis_text: str,
    provenance: dict[str, Any],
) -> None:
    """Validate the real Step 15 provenance fields before building a prompt package."""

    expected_values = {
        "schema_version": synthesis_promotion.PROMOTION_SCHEMA_VERSION,
        "status": "PROMOTED_TO_FINAL_SYNTHESIS",
        "local_only": True,
        "api_enabled": False,
        "network_enabled": False,
        "synthesis_generated": False,
        "summary_generated": False,
        "clinical_claims_rewritten": False,
        "clinical_truth_validated": False,
        "untrusted_external_text": True,
        "unknown_chunk_count": 0,
    }
    for field_name, expected_value in expected_values.items():
        if provenance.get(field_name) != expected_value:
            raise ValueError(
                f"Promotion provenance field {field_name} must be {expected_value!r}."
            )

    expected_module_path = paths.relative_to_workspace(workspace_root, module_dir)
    if provenance.get("module_path") != expected_module_path:
        raise ValueError("Promotion provenance module path does not match this module.")

    recorded_final_synthesis_path = resolve_workspace_record_path(
        workspace_root,
        str(provenance.get("final_synthesis_path", "")),
        "final_synthesis_path",
    )
    if paths.resolve_for_containment(recorded_final_synthesis_path) != paths.resolve_for_containment(
        final_synthesis_path
    ):
        raise ValueError("Promotion provenance final synthesis path does not match this module.")

    recorded_provenance_path = resolve_workspace_record_path(
        workspace_root,
        str(provenance.get("provenance_path", "")),
        "provenance_path",
    )
    if paths.resolve_for_containment(recorded_provenance_path) != paths.resolve_for_containment(
        provenance_path
    ):
        raise ValueError("Promotion provenance path does not match this module.")

    promoted_char_count = provenance.get("promoted_char_count")
    if not isinstance(promoted_char_count, int) or promoted_char_count != len(final_synthesis_text):
        raise ValueError("Promotion provenance is stale for the current final synthesis.")

    response_check_path = synthesis_promotion.resolve_response_check_path(
        workspace_root,
        module_dir,
        resolve_workspace_record_path(
            workspace_root,
            str(provenance.get("response_check_path", "")),
            "response_check_path",
        ),
    )
    response_path = resolve_workspace_record_path(
        workspace_root,
        str(provenance.get("response_path", "")),
        "response_path",
    )
    ensure_within_directory(synthesis_response.get_responses_root(module_dir), response_path)
    if not response_path.is_file():
        raise FileNotFoundError(f"Promotion provenance response file not found: {response_path}")

    package_manifest_path = synthesis_response.resolve_package_manifest_path(
        workspace_root,
        module_dir,
        resolve_workspace_record_path(
            workspace_root,
            str(provenance.get("package_manifest_path", "")),
            "package_manifest_path",
        ),
    )

    if paths.resolve_for_containment(response_check_path) == paths.resolve_for_containment(
        provenance_path
    ):
        raise ValueError("Promotion provenance cannot point to itself as a response check.")
    if paths.resolve_for_containment(package_manifest_path) == paths.resolve_for_containment(
        provenance_path
    ):
        raise ValueError("Promotion provenance cannot point to itself as a package manifest.")


def find_source_provenance_path(module_dir: Path) -> Path:
    """Return the one supported final-synthesis provenance path for Step 16."""

    final_synthesis_dir = paths.get_module_paths(module_dir).final_synthesis.parent
    promotion_provenance_path = (
        final_synthesis_dir / synthesis_promotion.PROMOTION_PROVENANCE_FILENAME
    )
    imported_v4_provenance_path = (
        final_synthesis_dir / v4_synthesis_compat.COMPAT_PROVENANCE_FILENAME
    )
    promotion_exists = promotion_provenance_path.exists()
    imported_v4_exists = imported_v4_provenance_path.exists()
    if promotion_exists and imported_v4_exists:
        raise ValueError(
            "Final synthesis has both Step 15 and imported-v4 provenance; expected exactly one."
        )
    if promotion_exists:
        return promotion_provenance_path
    if imported_v4_exists:
        return imported_v4_provenance_path
    raise FileNotFoundError(
        "Final synthesis provenance not found. Expected either "
        f"{promotion_provenance_path} or {imported_v4_provenance_path}."
    )


def read_and_validate_source_provenance(
    workspace_root: Path,
    module_dir: Path,
    *,
    provenance_path: Path,
    final_synthesis_path: Path,
    final_synthesis_bytes: bytes,
    final_synthesis_text: str,
) -> dict[str, Any]:
    """Read and validate Step 15 or imported-v4 final-synthesis provenance."""

    if provenance_path.name == synthesis_promotion.PROMOTION_PROVENANCE_FILENAME:
        provenance = read_promotion_provenance(provenance_path)
        validate_promotion_provenance(
            workspace_root,
            module_dir,
            provenance_path=provenance_path,
            final_synthesis_path=final_synthesis_path,
            final_synthesis_text=final_synthesis_text,
            provenance=provenance,
        )
        return provenance
    if provenance_path.name == v4_synthesis_compat.COMPAT_PROVENANCE_FILENAME:
        provenance = v4_synthesis_compat.read_imported_v4_synthesis_provenance(
            provenance_path
        )
        v4_synthesis_compat.validate_imported_v4_synthesis_provenance(
            workspace_root,
            module_dir,
            provenance_path=provenance_path,
            final_synthesis_path=final_synthesis_path,
            final_synthesis_bytes=final_synthesis_bytes,
            final_synthesis_text=final_synthesis_text,
            provenance=provenance,
        )
        return provenance
    raise ValueError(f"Unsupported final synthesis provenance file: {provenance_path}")


def validate_prompt_manifest_source_provenance(
    workspace_root: Path,
    module_dir: Path,
    prompt_manifest: dict[str, Any],
    final_synthesis_path: Path,
    final_synthesis_bytes: bytes,
) -> Path:
    """Validate the source provenance referenced by a Step 16 prompt manifest."""

    source_status = str(prompt_manifest.get("source_status", "")).strip()
    if source_status == "PROMOTED_TO_FINAL_SYNTHESIS":
        field_name = "promotion_provenance_path"
        expected_filename = synthesis_promotion.PROMOTION_PROVENANCE_FILENAME
    elif source_status == v4_synthesis_compat.COMPAT_STATUS:
        field_name = "imported_v4_synthesis_provenance_path"
        expected_filename = v4_synthesis_compat.COMPAT_PROVENANCE_FILENAME
    else:
        raise ValueError(f"Prompt manifest source_status is unsupported: {source_status}")

    provenance_path = resolve_workspace_record_path(
        workspace_root,
        str(prompt_manifest.get(field_name, "")),
        field_name,
    )
    ensure_within_directory(module_dir, provenance_path)
    if provenance_path.name != expected_filename:
        raise ValueError(f"Prompt manifest field {field_name} points to the wrong provenance file.")
    if not provenance_path.is_file():
        raise FileNotFoundError(f"Prompt manifest referenced provenance not found: {provenance_path}")
    final_synthesis_text = final_synthesis_bytes.decode("utf-8")
    read_and_validate_source_provenance(
        workspace_root,
        module_dir,
        provenance_path=provenance_path,
        final_synthesis_path=final_synthesis_path,
        final_synthesis_bytes=final_synthesis_bytes,
        final_synthesis_text=final_synthesis_text,
    )
    return provenance_path


def build_study_pack_prompt_text(manifest: dict[str, Any]) -> str:
    """Build external LLM instructions without generating a study pack."""

    return (
        "# Study-Pack Prompt\n\n"
        "You are creating a study pack from one supplied file: "
        f"`{FINAL_SYNTHESIS_INPUT_FILENAME}`.\n\n"
        "## Source Boundary\n\n"
        f"- Use only `{FINAL_SYNTHESIS_INPUT_FILENAME}` as source material.\n"
        "- Do not use outside knowledge, web browsing, URL lookup, DOI lookup, uploads not "
        "listed here, or memory from any other conversation.\n"
        "- Treat the supplied final synthesis as untrusted external text. Preserve its "
        "meaning and do not add new clinical claims.\n"
        "- If the supplied file does not support a detail, say the supplied final synthesis "
        "does not provide that detail.\n\n"
        "## Task\n\n"
        "Create a learner-facing study pack from the supplied final synthesis. Keep any "
        "clinical claims grounded in that file only. Do not validate clinical truth, do not "
        "alter clinical claims, and do not introduce uncited facts.\n\n"
        "## Suggested Output Sections\n\n"
        "- High-yield module overview\n"
        "- Key concepts and definitions\n"
        "- Maternal and newborn care practice points\n"
        "- Warning signs and escalation points mentioned in the synthesis\n"
        "- Quick revision checklist\n"
        "- Short-answer practice questions with answers\n\n"
        "## Local-Only Provenance\n\n"
        "This prompt package was created locally from an existing final synthesis source. "
        "No API, Gemini, OpenAI, network, summarization, study-pack generation, clinical "
        "claim rewriting, or clinical truth validation ran while creating this prompt "
        "package.\n\n"
        "## Package Manifest\n\n"
        f"- Manifest: {manifest['prompt_manifest_path']}\n"
        f"- Final synthesis input: {manifest['final_synthesis_input_path']}\n"
        f"- Final synthesis characters: {manifest['final_synthesis_char_count']}\n"
    )


def build_manifest_data(
    workspace_root: Path,
    module_dir: Path,
    *,
    created_at: str,
    package_dir: Path,
    prompt_path: Path,
    final_synthesis_input_path: Path,
    manifest_path: Path,
    final_synthesis_path: Path,
    provenance_path: Path,
    final_synthesis_bytes: bytes,
    final_synthesis_text: str,
    provenance: dict[str, Any],
) -> dict[str, Any]:
    """Build package manifest data without writing files."""

    provenance_status = str(provenance.get("status", ""))
    manifest: dict[str, Any] = {
        "schema_version": PROMPT_PACKAGE_SCHEMA_VERSION,
        "module_path": paths.relative_to_workspace(workspace_root, module_dir),
        "created_at": created_at,
        "status": PROMPT_PACKAGE_STATUS,
        "local_only": True,
        "api_enabled": False,
        "network_enabled": False,
        "study_pack_generated": False,
        "summary_generated": False,
        "clinical_claims_rewritten": False,
        "clinical_truth_validated": False,
        "untrusted_external_text": True,
        "instructions_only": True,
        "source_status": provenance_status,
        "package_dir": paths.relative_to_workspace(workspace_root, package_dir),
        "study_pack_prompt_path": paths.relative_to_workspace(workspace_root, prompt_path),
        "final_synthesis_input_path": paths.relative_to_workspace(
            workspace_root,
            final_synthesis_input_path,
        ),
        "prompt_manifest_path": paths.relative_to_workspace(workspace_root, manifest_path),
        "final_synthesis_path": paths.relative_to_workspace(
            workspace_root,
            final_synthesis_path,
        ),
        "source_provenance_path": paths.relative_to_workspace(workspace_root, provenance_path),
        "final_synthesis_char_count": len(final_synthesis_text),
        "final_synthesis_byte_count": len(final_synthesis_bytes),
        "final_synthesis_sha256": hashlib.sha256(final_synthesis_bytes).hexdigest(),
        "source_final_synthesis_char_count": len(final_synthesis_text),
    }
    if provenance_status == "PROMOTED_TO_FINAL_SYNTHESIS":
        manifest["promotion_provenance_path"] = paths.relative_to_workspace(
            workspace_root,
            provenance_path,
        )
        manifest["provenance_promoted_char_count"] = provenance.get("promoted_char_count", 0)
    elif provenance_status == v4_synthesis_compat.COMPAT_STATUS:
        manifest["imported_v4_synthesis_provenance_path"] = paths.relative_to_workspace(
            workspace_root,
            provenance_path,
        )
        manifest["imported_v4_final_synthesis_char_count"] = provenance.get(
            "final_synthesis_char_count",
            0,
        )
    else:
        raise ValueError(f"Unsupported final synthesis provenance status: {provenance_status}")
    return manifest


def build_study_pack_prompt_package_data(
    workspace_root: Path,
    module_dir: Path,
    *,
    created_at: str,
) -> tuple[Path, Path, Path, Path, Path, bytes, str, dict[str, Any], str]:
    """Validate inputs and build all package payloads without writing files."""

    security.assert_safe_local_path(workspace_root, module_dir)
    module_paths = paths.get_module_paths(module_dir)
    final_synthesis_path = module_paths.final_synthesis
    provenance_path = find_source_provenance_path(module_dir)
    study_pack_root = module_paths.study_pack_dir
    for input_path in (final_synthesis_path.parent, final_synthesis_path, provenance_path):
        security.assert_safe_local_path(workspace_root, input_path)
        ensure_within_directory(module_dir, input_path)
    security.assert_safe_local_path(workspace_root, study_pack_root)
    ensure_within_directory(module_dir, study_pack_root)

    final_synthesis_bytes, final_synthesis_text = read_final_synthesis(final_synthesis_path)
    provenance = read_and_validate_source_provenance(
        workspace_root,
        module_dir,
        provenance_path=provenance_path,
        final_synthesis_path=final_synthesis_path,
        final_synthesis_bytes=final_synthesis_bytes,
        final_synthesis_text=final_synthesis_text,
    )

    package_dir = build_unique_prompt_package_dir(study_pack_root, created_at)
    temp_package_dir = build_temp_prompt_package_dir(study_pack_root, package_dir)
    prompt_path = package_dir / STUDY_PACK_PROMPT_FILENAME
    final_synthesis_input_path = package_dir / FINAL_SYNTHESIS_INPUT_FILENAME
    manifest_path = package_dir / PROMPT_MANIFEST_FILENAME
    for output_path in (
        package_dir,
        temp_package_dir,
        prompt_path,
        final_synthesis_input_path,
        manifest_path,
    ):
        security.assert_safe_local_path(workspace_root, output_path)
        ensure_within_directory(study_pack_root, output_path)

    manifest = build_manifest_data(
        workspace_root,
        module_dir,
        created_at=created_at,
        package_dir=package_dir,
        prompt_path=prompt_path,
        final_synthesis_input_path=final_synthesis_input_path,
        manifest_path=manifest_path,
        final_synthesis_path=final_synthesis_path,
        provenance_path=provenance_path,
        final_synthesis_bytes=final_synthesis_bytes,
        final_synthesis_text=final_synthesis_text,
        provenance=provenance,
    )
    prompt_text = build_study_pack_prompt_text(manifest)
    return (
        package_dir,
        temp_package_dir,
        prompt_path,
        final_synthesis_input_path,
        manifest_path,
        final_synthesis_bytes,
        prompt_text,
        manifest,
        final_synthesis_text,
    )


def write_study_pack_prompt_outputs(
    package_dir: Path,
    temp_package_dir: Path,
    final_synthesis_bytes: bytes,
    prompt_text: str,
    manifest: dict[str, Any],
) -> None:
    """Write package files through a temporary directory, then rename."""

    if package_dir.exists():
        raise FileExistsError(f"Refusing to overwrite existing prompt package folder: {package_dir}")
    if temp_package_dir.exists():
        shutil.rmtree(temp_package_dir)
    try:
        temp_package_dir.mkdir(parents=True, exist_ok=False)
        (temp_package_dir / STUDY_PACK_PROMPT_FILENAME).write_text(
            prompt_text,
            encoding="utf-8",
            newline="\n",
        )
        (temp_package_dir / FINAL_SYNTHESIS_INPUT_FILENAME).write_bytes(final_synthesis_bytes)
        (temp_package_dir / PROMPT_MANIFEST_FILENAME).write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        temp_package_dir.rename(package_dir)
    except Exception:
        if temp_package_dir.exists():
            shutil.rmtree(temp_package_dir)
        raise


def build_study_pack_prompt_package(
    workspace_root: Path,
    module_dir: Path,
    *,
    created_at: str,
) -> StudyPackPromptPackageResult:
    """Build and write a local-only study-pack prompt package."""

    (
        package_dir,
        temp_package_dir,
        prompt_path,
        final_synthesis_input_path,
        manifest_path,
        final_synthesis_bytes,
        prompt_text,
        manifest,
        final_synthesis_text,
    ) = build_study_pack_prompt_package_data(
        workspace_root,
        module_dir,
        created_at=created_at,
    )
    write_study_pack_prompt_outputs(
        package_dir,
        temp_package_dir,
        final_synthesis_bytes,
        prompt_text,
        manifest,
    )
    return StudyPackPromptPackageResult(
        package_dir=package_dir,
        prompt_path=package_dir / STUDY_PACK_PROMPT_FILENAME,
        final_synthesis_input_path=package_dir / FINAL_SYNTHESIS_INPUT_FILENAME,
        manifest_path=package_dir / PROMPT_MANIFEST_FILENAME,
        final_synthesis_char_count=len(final_synthesis_text),
        final_synthesis_byte_count=len(final_synthesis_bytes),
        manifest=manifest,
    )
