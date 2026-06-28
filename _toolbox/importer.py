"""Copy-only import contracts for existing v4 outputs.

This module will later plan and perform imports from `outputs_v4` into the
organized module folder structure. It must never move, delete, or overwrite
existing outputs.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import shutil


OLD_V4_PROJECT_FOLDER_NAME = "mnch_batch_source_card_automator_v4"
DEFAULT_OUTPUTS_V4_FOLDER_NAME = "outputs_v4"
REQUIRED_OUTPUT_FILES = (
    "all_source_cards_combined.md",
    "stage2_final_synthesis_prompt.md",
    "module_master_synthesis.md",
)


@dataclass(frozen=True)
class ImportPlan:
    """Planned copy-only import from an existing output folder."""

    source_folder: Path
    destination_module_folder: Path
    planned_copies: dict[Path, Path]


@dataclass(frozen=True)
class CopiedFile:
    """A file copied during a v4 import."""

    source: Path
    destination: Path
    bytes_copied: int


def resolve_for_containment(path: Path) -> Path:
    """Resolve paths for containment checks without requiring the target to exist."""

    return path.resolve(strict=False)


def is_within_directory(parent: Path, candidate: Path) -> bool:
    """Return whether `candidate` resolves inside `parent`."""

    resolved_parent = resolve_for_containment(parent)
    resolved_candidate = resolve_for_containment(candidate)
    try:
        common_path = Path(os.path.commonpath((resolved_parent, resolved_candidate)))
    except ValueError:
        return False
    return common_path == resolved_parent


def get_default_v4_project_root(workspace_root: Path) -> Path:
    """Return the expected old v4 project root next to the v5 workspace."""

    return workspace_root.parent / OLD_V4_PROJECT_FOLDER_NAME


def get_default_outputs_v4_dir(workspace_root: Path) -> Path:
    """Return the expected default old v4 `outputs_v4` directory."""

    return get_default_v4_project_root(workspace_root) / DEFAULT_OUTPUTS_V4_FOLDER_NAME


def validate_outputs_v4_source(outputs_v4_dir: Path, allowed_v4_root: Path) -> None:
    """Validate that an import source is exactly the old v4 `outputs_v4` folder."""

    if not allowed_v4_root.exists() or not allowed_v4_root.is_dir():
        raise FileNotFoundError(f"Old v4 project root does not exist: {allowed_v4_root}")
    expected_outputs_v4_dir = resolve_for_containment(
        allowed_v4_root / DEFAULT_OUTPUTS_V4_FOLDER_NAME
    )
    resolved_outputs_v4_dir = resolve_for_containment(outputs_v4_dir)
    if resolved_outputs_v4_dir != expected_outputs_v4_dir:
        raise ValueError(
            "Step 5 only imports from the exact default outputs_v4 folder: "
            f"{expected_outputs_v4_dir}"
        )
    if not outputs_v4_dir.exists() or not outputs_v4_dir.is_dir():
        raise FileNotFoundError(f"outputs_v4 source folder does not exist: {outputs_v4_dir}")


def build_outputs_v4_import_plan(
    outputs_v4_dir: Path,
    module_dir: Path,
    *,
    allowed_v4_root: Path | None = None,
) -> ImportPlan:
    """Build a copy-only plan for importing existing `outputs_v4` files."""

    validate_outputs_v4_source(outputs_v4_dir, allowed_v4_root or outputs_v4_dir.parent)

    source_cards = sorted(
        source_card
        for source_card in outputs_v4_dir.glob("*_source_cards.md")
        if source_card.is_file()
    )
    if not source_cards:
        raise FileNotFoundError(f"No *_source_cards.md files found in: {outputs_v4_dir}")

    missing_required = [
        required_file
        for required_file in REQUIRED_OUTPUT_FILES
        if not (outputs_v4_dir / required_file).is_file()
    ]
    if missing_required:
        missing = ", ".join(missing_required)
        raise FileNotFoundError(f"Required outputs_v4 files are missing: {missing}")

    planned_copies: dict[Path, Path] = {}
    for source_card in source_cards:
        planned_copies[source_card] = module_dir / "01_source_cards" / source_card.name

    planned_copies[outputs_v4_dir / "all_source_cards_combined.md"] = (
        module_dir / "02_combined" / "all_source_cards_combined.md"
    )
    planned_copies[outputs_v4_dir / "stage2_final_synthesis_prompt.md"] = (
        module_dir / "03_stage2_prompt" / "stage2_final_synthesis_prompt.md"
    )
    planned_copies[outputs_v4_dir / "module_master_synthesis.md"] = (
        module_dir / "04_final_synthesis" / "module_master_synthesis.md"
    )
    return ImportPlan(
        source_folder=outputs_v4_dir,
        destination_module_folder=module_dir,
        planned_copies=planned_copies,
    )


def import_outputs_v4_copy_only(plan: ImportPlan) -> list[CopiedFile]:
    """Execute a future copy-only import plan."""

    conflicts = would_overwrite_existing_files(plan)
    if conflicts:
        conflict_list = ", ".join(str(conflict) for conflict in conflicts)
        raise FileExistsError(f"Refusing to overwrite existing import destination files: {conflict_list}")

    copied_files: list[CopiedFile] = []
    for source, destination in plan.planned_copies.items():
        if not source.is_file():
            raise FileNotFoundError(f"Planned import source file is missing: {source}")
        if destination.exists():
            raise FileExistsError(f"Refusing to overwrite existing file: {destination}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        copied_files.append(
            CopiedFile(
                source=source,
                destination=destination,
                bytes_copied=destination.stat().st_size,
            )
        )
    return copied_files


def would_overwrite_existing_files(plan: ImportPlan) -> list[Path]:
    """Return destination files that already exist for an import plan."""

    return [destination for destination in plan.planned_copies.values() if destination.exists()]
