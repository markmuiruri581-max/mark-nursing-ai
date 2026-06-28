"""State helpers for the MNCH Coursera automation workspace.

This module owns the future course index and per-module status contract.
Write operations are intentionally stubs for now; the next implementation step
should add safe write behavior with overwrite checks.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Sequence
import json
import tempfile

from _toolbox import paths


SCHEMA_VERSION = 1
ALLOWED_STATUSES = (
    "NEW",
    "URLS_ADDED",
    "STAGE1_RUNNING",
    "STAGE1_COMPLETE",
    "SOURCE_REVIEW_NEEDED",
    "SOURCE_REPAIRED",
    "COMBINED_READY",
    "STAGE2_COMPLETE",
    "STUDY_PACK_PROMPT_READY",
    "STUDY_PACK_COMPLETE",
    "MODULE_COMPLETE",
)
DEFAULT_STATUS = "NEW"


def validate_status(status: str) -> str:
    """Return a valid module status or raise a clear error."""

    normalized = status.strip().upper()
    if normalized not in ALLOWED_STATUSES:
        allowed = ", ".join(ALLOWED_STATUSES)
        raise ValueError(f"Invalid module status '{status}'. Expected one of: {allowed}.")
    return normalized


def get_course_index_path(workspace_root: Path) -> Path:
    """Return the course index path inside the workspace."""

    return paths.ensure_within_workspace(workspace_root, workspace_root / "course_index.json")


def normalize_course_index(raw_index: dict[str, Any] | None) -> dict[str, Any]:
    """Normalize course index data to schema version 1."""

    index = raw_index if isinstance(raw_index, dict) else {}
    raw_courses = index.get("courses", [])
    courses = raw_courses if isinstance(raw_courses, list) else []

    normalized_courses: list[dict[str, Any]] = []
    for course in courses:
        if not isinstance(course, dict):
            continue
        course_name = str(course.get("name", "")).strip()
        safe_name = str(course.get("safe_name", "")).strip()
        course_path = str(course.get("path", "")).strip()
        raw_modules = course.get("modules", [])
        modules = raw_modules if isinstance(raw_modules, list) else []
        normalized_modules: list[dict[str, Any]] = []
        for module in modules:
            if not isinstance(module, dict):
                continue
            status = validate_status(str(module.get("status", DEFAULT_STATUS)))
            module_name = str(module.get("name", "")).strip()
            display_name = str(module.get("display_name") or module_name).strip()
            created = str(module.get("created", "")).strip()
            created_at = str(module.get("created_at") or created).strip()
            updated_at = str(module.get("updated_at", "")).strip()
            source_count = module.get("source_count", 0)
            if not isinstance(source_count, int):
                source_count = 0
            raw_paths = module.get("paths", {})
            module_paths = raw_paths if isinstance(raw_paths, dict) else {}
            normalized_modules.append(
                {
                    "name": module_name,
                    "display_name": display_name,
                    "safe_name": str(module.get("safe_name", "")).strip(),
                    "path": str(module.get("path", "")).strip(),
                    "status": status,
                    "created": created,
                    "created_at": created_at,
                    "updated_at": updated_at,
                    "source_count": source_count,
                    "source_status": str(module.get("source_status", "")).strip(),
                    "library_manifest": str(module.get("library_manifest", "")).strip(),
                    "privacy_status": str(module.get("privacy_status", "")).strip(),
                    "paths": {
                        str(path_name): str(path_value)
                        for path_name, path_value in module_paths.items()
                    },
                }
            )
        normalized_courses.append(
            {
                "name": course_name,
                "safe_name": safe_name,
                "path": course_path,
                "modules": normalized_modules,
            }
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "courses": normalized_courses,
    }


def read_course_index(workspace_root: Path) -> dict[str, Any]:
    """Read and normalize `course_index.json` from the workspace root."""

    index_path = get_course_index_path(workspace_root)
    if not index_path.exists():
        return normalize_course_index({})
    return normalize_course_index(json.loads(index_path.read_text(encoding="utf-8")))


def safe_write_text(path: Path, content: str, *, overwrite: bool = False) -> None:
    """Write UTF-8 text while avoiding accidental overwrites by default."""

    if path.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing file: {path}")
    path.write_text(content, encoding="utf-8", newline="\n")


def atomic_write_json(path: Path, data: dict[str, Any]) -> None:
    """Write JSON through a same-directory temporary file, then replace."""

    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(data, indent=2, ensure_ascii=False)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="\n", dir=path.parent, delete=False
    ) as handle:
        handle.write(content)
        handle.write("\n")
        temp_path = Path(handle.name)
    temp_path.replace(path)


def write_course_index(workspace_root: Path, index: dict[str, Any]) -> None:
    """Write normalized `course_index.json` as UTF-8 JSON."""

    index_path = get_course_index_path(workspace_root)
    normalized_index = normalize_course_index(index)
    atomic_write_json(index_path, normalized_index)


def write_module_status(
    module_dir: Path,
    status: str,
    *,
    course_name: str,
    module_name: str,
    created_at: str,
    notes: Sequence[str] | None = None,
    overwrite: bool = False,
) -> None:
    """Write `MODULE_STATUS.md` for a module."""

    validated_status = validate_status(status)
    status_notes = notes or (
        "Module folder was created by MNCH Coursera Automation Manager v5.",
        "No source-card generation has run yet.",
    )
    notes_content = "".join(f"* {note}\n" for note in status_notes)
    content = (
        "# Module Status\n\n"
        f"Status: {validated_status}\n\n"
        f"Course: {course_name}\n"
        f"Module: {module_name}\n\n"
        f"Created: {created_at}\n\n"
        "Notes:\n\n"
        f"{notes_content}"
    )
    safe_write_text(module_dir / "MODULE_STATUS.md", content, overwrite=overwrite)


def write_next_step(
    module_dir: Path,
    next_step: str | None = None,
    *,
    recommended_menu_option: str = "2. Paste or edit URLs for the current module",
    overwrite: bool = False,
) -> None:
    """Write `NEXT_STEP.md` for a module."""

    step = next_step or "Add URLs for this module."
    content = (
        "# Next Step\n\n"
        f"{step}\n\n"
        "Recommended menu option:\n"
        f"{recommended_menu_option}\n"
    )
    safe_write_text(module_dir / "NEXT_STEP.md", content, overwrite=overwrite)


def build_module_index_entry(
    workspace_root: Path,
    course_name: str,
    module_name: str,
    module_dir: Path,
    *,
    status: str = DEFAULT_STATUS,
    created_at: str,
) -> dict[str, Any]:
    """Build a course-index entry for one module."""

    module_paths = paths.get_module_paths(module_dir)
    relative_module_dir = paths.relative_to_workspace(workspace_root, module_dir)
    return {
        "name": module_name,
        "display_name": module_name,
        "safe_name": module_dir.name,
        "path": relative_module_dir,
        "status": validate_status(status),
        "created": created_at,
        "created_at": created_at,
        "paths": {
            "module_dir": relative_module_dir,
            "urls": paths.relative_to_workspace(workspace_root, module_paths.urls),
            "status": paths.relative_to_workspace(workspace_root, module_paths.module_status),
            "next_step": paths.relative_to_workspace(workspace_root, module_paths.next_step),
            "run_log": paths.relative_to_workspace(workspace_root, module_paths.run_log),
        },
    }


def register_module(
    workspace_root: Path,
    course_name: str,
    module_name: str,
    module_dir: Path,
    *,
    created_at: str,
    status: str = DEFAULT_STATUS,
) -> dict[str, Any]:
    """Add a module to `course_index.json` and return its index entry."""

    index = read_course_index(workspace_root)
    course_dir = module_dir.parent
    course_safe_name = course_dir.name
    course_relative_path = paths.relative_to_workspace(workspace_root, course_dir)
    module_entry = build_module_index_entry(
        workspace_root,
        course_name,
        module_name,
        module_dir,
        status=status,
        created_at=created_at,
    )

    matching_course: dict[str, Any] | None = None
    for course in index["courses"]:
        if course.get("path") == course_relative_path:
            matching_course = course
            break

    if matching_course is None:
        matching_course = {
            "name": course_name,
            "safe_name": course_safe_name,
            "path": course_relative_path,
            "modules": [],
        }
        index["courses"].append(matching_course)

    for module in matching_course["modules"]:
        if module.get("path") == module_entry["path"]:
            raise ValueError(f"Module is already registered: {module_entry['path']}")

    matching_course["modules"].append(module_entry)
    write_course_index(workspace_root, index)
    return module_entry


def update_registered_module_status(
    workspace_root: Path,
    module_dir: Path,
    status: str,
    *,
    updated_at: str,
) -> dict[str, Any]:
    """Update one registered module status in `course_index.json`."""

    validated_status = validate_status(status)
    module_path = paths.relative_to_workspace(workspace_root, module_dir)
    index = read_course_index(workspace_root)
    for course in index["courses"]:
        for module in course["modules"]:
            if module.get("path") == module_path:
                module["status"] = validated_status
                module["updated_at"] = updated_at
                write_course_index(workspace_root, index)
                return module
    raise ValueError(f"Module is not registered in course_index.json: {module_path}")


def update_registered_module_library_fields(
    workspace_root: Path,
    module_dir: Path,
    *,
    library_manifest: str,
    source_count: int,
    source_status: str,
    privacy_status: str,
    updated_at: str,
) -> dict[str, Any]:
    """Update library fields for one registered module in `course_index.json`."""

    module_path = paths.relative_to_workspace(workspace_root, module_dir)
    index = read_course_index(workspace_root)
    for course in index["courses"]:
        for module in course["modules"]:
            if module.get("path") == module_path:
                module["library_manifest"] = library_manifest
                module["source_count"] = source_count
                module["source_status"] = source_status
                module["privacy_status"] = privacy_status
                module["updated_at"] = updated_at
                write_course_index(workspace_root, index)
                return module
    raise ValueError(f"Module is not registered in course_index.json: {module_path}")


def compute_next_recommended_step(status: str) -> str:
    """Return a plain-language next step for a module status."""

    # TODO: Refine this mapping after the manager menu flow is implemented.
    next_steps = {
        "NEW": "Add URLs for this module.",
        "URLS_ADDED": "Run Stage 1 source-card generation.",
        "STAGE1_RUNNING": "Wait for Stage 1 to finish or review the run log.",
        "STAGE1_COMPLETE": "Check source-card completeness and quality.",
        "SOURCE_REVIEW_NEEDED": "Repair or manually approve flagged source cards.",
        "SOURCE_REPAIRED": "Rebuild the combined source-card file.",
        "COMBINED_READY": "Run Stage 2 final synthesis.",
        "STAGE2_COMPLETE": "Create the study-pack generation prompt.",
        "STUDY_PACK_PROMPT_READY": "Generate and save the final study pack.",
        "STUDY_PACK_COMPLETE": "Mark the module complete after final review.",
        "MODULE_COMPLETE": "Start the next Coursera module.",
    }
    return next_steps.get(status, "Review module status before continuing.")
