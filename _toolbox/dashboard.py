"""Dashboard text helpers for the MNCH Coursera automation manager.

This module will later prepare terminal-friendly status output. Functions
return strings so the future manager can decide how to print or log them.
"""

from __future__ import annotations

from pathlib import Path


def show_current_module_status(module_dir: Path) -> str:
    """Return a display string for the current module status."""

    # TODO: Read MODULE_STATUS.md and summarize source-card/stage progress.
    return f"Module status dashboard is not implemented yet: {module_dir}"


def show_course_dashboard(course_dir: Path) -> str:
    """Return a display string for a course-level dashboard."""

    # TODO: Summarize modules, completion states, and next recommended work.
    return f"Course dashboard is not implemented yet: {course_dir}"


def show_next_recommended_step(module_dir: Path) -> str:
    """Return a display string for the next recommended step."""

    # TODO: Read NEXT_STEP.md or compute the next step from module state.
    return f"Next recommended step is not implemented yet: {module_dir}"
