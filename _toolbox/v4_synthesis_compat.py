"""Compatibility provenance for imported v4 final synthesis files."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any

from _toolbox import paths, security, synthesis_promotion


COMPAT_SCHEMA_VERSION = 1
COMPAT_PROVENANCE_FILENAME = "imported_v4_synthesis_provenance.json"
COMPAT_STATUS = "IMPORTED_V4_FINAL_SYNTHESIS"
CONFIRMATION_PHRASE = "ADOPT IMPORTED V4 SYNTHESIS"


@dataclass(frozen=True)
class ImportedV4SynthesisPayload:
    """Validated imported-v4 synthesis compatibility data before writing."""

    final_synthesis_path: Path
    provenance_path: Path
    final_synthesis_bytes: bytes
    final_synthesis_text: str
    provenance: dict[str, Any]


@dataclass(frozen=True)
class ImportedV4SynthesisResult:
    """Result from writing imported-v4 synthesis compatibility provenance."""

    final_synthesis_path: Path
    provenance_path: Path
    byte_count: int
    char_count: int
    sha256: str
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


def resolve_workspace_record_path(
    workspace_root: Path,
    raw_path: str,
    field_name: str,
) -> Path:
    """Resolve a workspace-relative path from imported-v4 provenance."""

    cleaned_path = raw_path.strip()
    if not cleaned_path:
        raise ValueError(f"Imported-v4 provenance field {field_name} cannot be blank.")
    candidate = Path(cleaned_path)
    if not candidate.is_absolute():
        candidate = workspace_root / candidate
    return security.assert_safe_local_path(workspace_root, candidate)


def read_final_synthesis_bytes(final_synthesis_path: Path) -> tuple[bytes, str]:
    """Read final synthesis as bytes and UTF-8 text without changing content."""

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


def validate_import_evidence(module_dir: Path) -> None:
    """Require evidence left by option 13's copy-only v4 import."""

    module_paths = paths.get_module_paths(module_dir)
    status_text = module_paths.module_status.read_text(encoding="utf-8")
    run_log_text = module_paths.run_log.read_text(encoding="utf-8")
    if "Status: STAGE2_COMPLETE" not in status_text:
        raise ValueError("Imported-v4 compatibility requires module status STAGE2_COMPLETE.")
    if "Existing v4 outputs were imported copy-only." not in status_text:
        raise ValueError("Module status does not show option 13 v4 import evidence.")
    required_log_markers = (
        "Import started.",
        "Source folder:",
        "module_master_synthesis.md",
        "Total files copied:",
        "Status: STAGE2_COMPLETE",
        "No API, Gemini, Stage 1, or Stage 2 logic ran.",
    )
    for marker in required_log_markers:
        if marker not in run_log_text:
            raise ValueError(f"Run log is missing option 13 import evidence: {marker}")


def build_imported_v4_provenance(
    workspace_root: Path,
    module_dir: Path,
    *,
    created_at: str,
    final_synthesis_path: Path,
    provenance_path: Path,
    final_synthesis_bytes: bytes,
    final_synthesis_text: str,
) -> dict[str, Any]:
    """Build imported-v4 compatibility provenance without validating clinical truth."""

    module_paths = paths.get_module_paths(module_dir)
    return {
        "schema_version": COMPAT_SCHEMA_VERSION,
        "module_path": paths.relative_to_workspace(workspace_root, module_dir),
        "created_at": created_at,
        "status": COMPAT_STATUS,
        "source_type": "imported_v4_outputs",
        "local_only": True,
        "api_enabled": False,
        "network_enabled": False,
        "synthesis_generated": False,
        "synthesis_generated_in_v5": False,
        "summary_generated": False,
        "clinical_claims_rewritten": False,
        "clinical_truth_validated": False,
        "clinical_validation_performed": False,
        "untrusted_external_text": True,
        "final_synthesis_path": paths.relative_to_workspace(workspace_root, final_synthesis_path),
        "provenance_path": paths.relative_to_workspace(workspace_root, provenance_path),
        "module_status_path": paths.relative_to_workspace(workspace_root, module_paths.module_status),
        "run_log_path": paths.relative_to_workspace(workspace_root, module_paths.run_log),
        "final_synthesis_byte_count": len(final_synthesis_bytes),
        "final_synthesis_char_count": len(final_synthesis_text),
        "final_synthesis_sha256": hashlib.sha256(final_synthesis_bytes).hexdigest(),
    }


def build_imported_v4_synthesis_payload(
    workspace_root: Path,
    module_dir: Path,
    *,
    created_at: str,
) -> ImportedV4SynthesisPayload:
    """Validate imported-v4 compatibility inputs before writing provenance."""

    security.assert_safe_local_path(workspace_root, module_dir)
    module_paths = paths.get_module_paths(module_dir)
    final_synthesis_path = module_paths.final_synthesis
    final_synthesis_dir = final_synthesis_path.parent
    step15_provenance_path = final_synthesis_dir / synthesis_promotion.PROMOTION_PROVENANCE_FILENAME
    provenance_path = final_synthesis_dir / COMPAT_PROVENANCE_FILENAME
    for output_path in (
        final_synthesis_dir,
        final_synthesis_path,
        step15_provenance_path,
        provenance_path,
    ):
        security.assert_safe_local_path(workspace_root, output_path)
        ensure_within_directory(module_dir, output_path)

    if step15_provenance_path.exists():
        raise FileExistsError(f"Step 15 promotion provenance already exists: {step15_provenance_path}")
    if provenance_path.exists():
        raise FileExistsError(f"Imported-v4 synthesis provenance already exists: {provenance_path}")

    validate_import_evidence(module_dir)
    final_synthesis_bytes, final_synthesis_text = read_final_synthesis_bytes(final_synthesis_path)
    provenance = build_imported_v4_provenance(
        workspace_root,
        module_dir,
        created_at=created_at,
        final_synthesis_path=final_synthesis_path,
        provenance_path=provenance_path,
        final_synthesis_bytes=final_synthesis_bytes,
        final_synthesis_text=final_synthesis_text,
    )
    return ImportedV4SynthesisPayload(
        final_synthesis_path=final_synthesis_path,
        provenance_path=provenance_path,
        final_synthesis_bytes=final_synthesis_bytes,
        final_synthesis_text=final_synthesis_text,
        provenance=provenance,
    )


def write_imported_v4_synthesis_provenance(payload: ImportedV4SynthesisPayload) -> None:
    """Write imported-v4 provenance through a temporary file, with no overwrite."""

    final_dir = payload.provenance_path.parent
    final_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        newline="\n",
        dir=final_dir,
        delete=False,
        prefix=".tmp_imported_v4_synthesis_provenance_",
        suffix=".json",
    ) as provenance_handle:
        provenance_handle.write(json.dumps(payload.provenance, indent=2, ensure_ascii=False))
        provenance_handle.write("\n")
        temp_provenance_path = Path(provenance_handle.name)
    try:
        if payload.provenance_path.exists():
            raise FileExistsError(
                f"Imported-v4 synthesis provenance already exists: {payload.provenance_path}"
            )
        temp_provenance_path.rename(payload.provenance_path)
    except Exception:
        if temp_provenance_path.exists():
            temp_provenance_path.unlink()
        raise


def prepare_imported_v4_synthesis(
    workspace_root: Path,
    module_dir: Path,
    *,
    created_at: str,
) -> ImportedV4SynthesisResult:
    """Create compatibility provenance for a copied v4 final synthesis."""

    payload = build_imported_v4_synthesis_payload(
        workspace_root,
        module_dir,
        created_at=created_at,
    )
    write_imported_v4_synthesis_provenance(payload)
    return ImportedV4SynthesisResult(
        final_synthesis_path=payload.final_synthesis_path,
        provenance_path=payload.provenance_path,
        byte_count=len(payload.final_synthesis_bytes),
        char_count=len(payload.final_synthesis_text),
        sha256=str(payload.provenance["final_synthesis_sha256"]),
        provenance=payload.provenance,
    )


def read_imported_v4_synthesis_provenance(provenance_path: Path) -> dict[str, Any]:
    """Read imported-v4 synthesis compatibility provenance."""

    if not provenance_path.exists():
        raise FileNotFoundError(f"Imported-v4 synthesis provenance not found: {provenance_path}")
    if not provenance_path.is_file():
        raise ValueError(f"Imported-v4 synthesis provenance is not a file: {provenance_path}")
    try:
        return json.loads(provenance_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Imported-v4 synthesis provenance is invalid JSON: {provenance_path}"
        ) from exc


def validate_imported_v4_synthesis_provenance(
    workspace_root: Path,
    module_dir: Path,
    *,
    provenance_path: Path,
    final_synthesis_path: Path,
    final_synthesis_bytes: bytes,
    final_synthesis_text: str,
    provenance: dict[str, Any],
) -> None:
    """Validate imported-v4 compatibility provenance against current synthesis bytes."""

    expected_values = {
        "schema_version": COMPAT_SCHEMA_VERSION,
        "module_path": paths.relative_to_workspace(workspace_root, module_dir),
        "status": COMPAT_STATUS,
        "source_type": "imported_v4_outputs",
        "local_only": True,
        "api_enabled": False,
        "network_enabled": False,
        "synthesis_generated": False,
        "synthesis_generated_in_v5": False,
        "summary_generated": False,
        "clinical_claims_rewritten": False,
        "clinical_truth_validated": False,
        "clinical_validation_performed": False,
        "untrusted_external_text": True,
    }
    for field_name, expected_value in expected_values.items():
        if provenance.get(field_name) != expected_value:
            raise ValueError(
                f"Imported-v4 provenance field {field_name} must be {expected_value!r}."
            )

    recorded_final_synthesis_path = resolve_workspace_record_path(
        workspace_root,
        str(provenance.get("final_synthesis_path", "")),
        "final_synthesis_path",
    )
    if paths.resolve_for_containment(recorded_final_synthesis_path) != paths.resolve_for_containment(
        final_synthesis_path
    ):
        raise ValueError("Imported-v4 provenance final synthesis path does not match this module.")

    recorded_provenance_path = resolve_workspace_record_path(
        workspace_root,
        str(provenance.get("provenance_path", "")),
        "provenance_path",
    )
    if paths.resolve_for_containment(recorded_provenance_path) != paths.resolve_for_containment(
        provenance_path
    ):
        raise ValueError("Imported-v4 provenance path does not match its location.")

    for field_name in ("module_status_path", "run_log_path"):
        recorded_path = resolve_workspace_record_path(
            workspace_root,
            str(provenance.get(field_name, "")),
            field_name,
        )
        ensure_within_directory(module_dir, recorded_path)
        if not recorded_path.is_file():
            raise FileNotFoundError(f"Imported-v4 provenance referenced file not found: {recorded_path}")

    recorded_byte_count = provenance.get("final_synthesis_byte_count")
    if not isinstance(recorded_byte_count, int) or recorded_byte_count != len(final_synthesis_bytes):
        raise ValueError("Imported-v4 provenance final synthesis byte count is stale.")
    recorded_char_count = provenance.get("final_synthesis_char_count")
    if not isinstance(recorded_char_count, int) or recorded_char_count != len(final_synthesis_text):
        raise ValueError("Imported-v4 provenance final synthesis character count is stale.")
    recorded_sha256 = str(provenance.get("final_synthesis_sha256", "")).strip()
    if hashlib.sha256(final_synthesis_bytes).hexdigest() != recorded_sha256:
        raise ValueError("Imported-v4 provenance final synthesis SHA256 is stale.")
