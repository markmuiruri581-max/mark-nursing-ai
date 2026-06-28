"""Path helpers for the MNCH Coursera automation workspace.

This module defines the future path contract for course and module folders.
It should stay side-effect free: build Path objects, but do not create, move,
delete, or overwrite files.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import re
import unicodedata


INVALID_FOLDER_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]+')
SLUG_SEPARATOR = "-"
MODULE_DIRECTORY_NAMES = (
    "00_inputs",
    "01_source_cards",
    "02_combined",
    "03_stage2_prompt",
    "04_final_synthesis",
    "05_study_pack",
    "06_manual_fallback_prompts",
    "07_external_llm_batch_prompts",
    "08_logs",
)
RESEARCH_DIRECTORY_NAMES = (
    "09_sources",
    "09_sources/raw",
    "10_extracted_text",
    "11_metadata",
    "12_summaries",
    "13_qa",
    "14_search_index",
    "15_review",
    "16_notes",
    "17_translation",
    "18_synthesis_candidates",
    "19_synthesis_prompts",
    "20_synthesis_prompt_packages",
    "21_external_synthesis_responses",
)


@dataclass(frozen=True)
class ModulePaths:
    """Named paths for a single course module workspace."""

    urls: Path
    source_cards_dir: Path
    combined_file: Path
    stage2_prompt: Path
    final_synthesis: Path
    study_pack_dir: Path
    manual_fallback_dir: Path
    external_prompts_dir: Path
    logs_dir: Path
    run_log: Path
    module_status: Path
    next_step: Path


@dataclass(frozen=True)
class ModuleCreationPaths:
    """Paths needed to create a new module workspace."""

    course_dir: Path
    module_dir: Path
    module_paths: ModulePaths


@dataclass(frozen=True)
class ResearchModulePaths:
    """Named research-library paths for a single module workspace."""

    sources_dir: Path
    raw_sources_dir: Path
    manifest: Path
    extracted_text_dir: Path
    metadata_dir: Path
    summaries_dir: Path
    qa_dir: Path
    search_index_dir: Path
    review_dir: Path
    notes_dir: Path
    translation_dir: Path
    synthesis_candidates_dir: Path
    synthesis_prompts_dir: Path
    synthesis_prompt_packages_dir: Path
    external_synthesis_responses_dir: Path


def get_workspace_root() -> Path:
    """Return the MNCH workspace root based on this module location."""

    return Path(__file__).resolve().parents[1]


def resolve_for_containment(path: Path) -> Path:
    """Resolve a path for containment checks without requiring it to exist."""

    return path.resolve(strict=False)


def ensure_within_workspace(workspace_root: Path, candidate: Path) -> Path:
    """Return `candidate` if it stays inside `workspace_root`; otherwise fail."""

    resolved_root = resolve_for_containment(workspace_root)
    resolved_candidate = resolve_for_containment(candidate)
    try:
        common = Path(os.path.commonpath((resolved_root, resolved_candidate)))
    except ValueError as exc:
        raise ValueError(f"Path is outside workspace: {candidate}") from exc
    if common != resolved_root:
        raise ValueError(f"Path is outside workspace: {candidate}")
    return resolved_candidate


def relative_to_workspace(workspace_root: Path, candidate: Path) -> str:
    """Return a stable POSIX-style path relative to the workspace root."""

    resolved_candidate = ensure_within_workspace(workspace_root, candidate)
    relative_path = resolved_candidate.relative_to(resolve_for_containment(workspace_root))
    return relative_path.as_posix()


def get_relative_workspace_path(workspace_root: Path, target: Path) -> str:
    """Compatibility alias for `relative_to_workspace`."""

    return relative_to_workspace(workspace_root, target)


def get_courses_root(workspace_root: Path) -> Path:
    """Return the future courses root path."""

    return ensure_within_workspace(workspace_root, workspace_root / "courses")


def safe_folder_name(name: str) -> str:
    """Return a slugged, filesystem-safe folder name for a course or module label."""

    normalized = unicodedata.normalize("NFKD", name)
    ascii_name = normalized.encode("ascii", "ignore").decode("ascii")
    cleaned = INVALID_FOLDER_CHARS.sub(SLUG_SEPARATOR, ascii_name.lower())
    cleaned = re.sub(r"[^a-z0-9]+", SLUG_SEPARATOR, cleaned)
    cleaned = cleaned.strip(SLUG_SEPARATOR)
    return cleaned or "untitled"


def get_course_dir(workspace_root: Path, course_name: str) -> Path:
    """Return the folder path for a course name."""

    return ensure_within_workspace(
        workspace_root, get_courses_root(workspace_root) / safe_folder_name(course_name)
    )


def get_module_dir(workspace_root: Path, course_name: str, module_name: str) -> Path:
    """Return the folder path for a module within a course."""

    return ensure_within_workspace(
        workspace_root, get_course_dir(workspace_root, course_name) / safe_folder_name(module_name)
    )


def get_standard_module_dirs(module_dir: Path) -> tuple[Path, ...]:
    """Return the standard directories for a module folder."""

    return tuple(module_dir / directory_name for directory_name in MODULE_DIRECTORY_NAMES)


def get_standard_module_directories(module_dir: Path) -> tuple[Path, ...]:
    """Compatibility alias for `get_standard_module_dirs`."""

    return get_standard_module_dirs(module_dir)


def get_research_module_dirs(module_dir: Path) -> tuple[Path, ...]:
    """Return the additive research directories for a module folder."""

    return tuple(module_dir / directory_name for directory_name in RESEARCH_DIRECTORY_NAMES)


def get_module_paths(module_dir: Path) -> ModulePaths:
    """Return all standard paths for a module folder."""

    return ModulePaths(
        urls=module_dir / "00_inputs" / "urls.txt",
        source_cards_dir=module_dir / "01_source_cards",
        combined_file=module_dir / "02_combined" / "all_source_cards_combined.md",
        stage2_prompt=module_dir / "03_stage2_prompt" / "stage2_final_synthesis_prompt.md",
        final_synthesis=module_dir / "04_final_synthesis" / "module_master_synthesis.md",
        study_pack_dir=module_dir / "05_study_pack",
        manual_fallback_dir=module_dir / "06_manual_fallback_prompts",
        external_prompts_dir=module_dir / "07_external_llm_batch_prompts",
        logs_dir=module_dir / "08_logs",
        run_log=module_dir / "08_logs" / "run_log.txt",
        module_status=module_dir / "MODULE_STATUS.md",
        next_step=module_dir / "NEXT_STEP.md",
    )


def get_research_module_paths(module_dir: Path) -> ResearchModulePaths:
    """Return all additive research-library paths for a module folder."""

    return ResearchModulePaths(
        sources_dir=module_dir / "09_sources",
        raw_sources_dir=module_dir / "09_sources" / "raw",
        manifest=module_dir / "09_sources" / "manifest.json",
        extracted_text_dir=module_dir / "10_extracted_text",
        metadata_dir=module_dir / "11_metadata",
        summaries_dir=module_dir / "12_summaries",
        qa_dir=module_dir / "13_qa",
        search_index_dir=module_dir / "14_search_index",
        review_dir=module_dir / "15_review",
        notes_dir=module_dir / "16_notes",
        translation_dir=module_dir / "17_translation",
        synthesis_candidates_dir=module_dir / "18_synthesis_candidates",
        synthesis_prompts_dir=module_dir / "19_synthesis_prompts",
        synthesis_prompt_packages_dir=module_dir / "20_synthesis_prompt_packages",
        external_synthesis_responses_dir=module_dir / "21_external_synthesis_responses",
    )


def build_module_creation_paths(
    workspace_root: Path, course_name: str, module_name: str
) -> ModuleCreationPaths:
    """Build all paths needed for creating a module, without filesystem writes."""

    course_dir = get_course_dir(workspace_root, course_name)
    module_dir = get_module_dir(workspace_root, course_name, module_name)
    ensure_within_workspace(workspace_root, module_dir)
    return ModuleCreationPaths(
        course_dir=course_dir,
        module_dir=module_dir,
        module_paths=get_module_paths(module_dir),
    )
