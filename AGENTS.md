# MNCH Coursera Automation Workspace

## Project Purpose

This workspace organizes the MNCH Coursera automation workflow for source-card generation, module synthesis, study-pack creation, prompt export, and future guided module management.

The immediate purpose of this workspace is scaffolding only. It preserves the existing working v4 tool and creates a clean place for future v5 manager work without changing current v4 outputs.

## Main Folders

- `_toolbox/` contains copied helper scripts and proven tools. The current copied script is `mnh_batch_source_card_automator_v4.py`.
- `courses/` will hold organized Coursera course folders when the v5 manager is implemented.
- Future module folders should keep inputs, source cards, combined files, Stage 2 prompts, final synthesis files, study packs, manual fallback prompts, external LLM batch prompts, and logs separated.
- Future logs should live inside each module folder so progress can be audited without touching completed outputs.

## Main Commands

Use these commands from the workspace root when the relevant files exist:

```powershell
python .\_toolbox\mnh_batch_source_card_automator_v4.py
```

Future v5 manager command placeholder:

```powershell
python .\mnch_course_module_manager_v5.py
```

Future self-test command placeholder:

```powershell
python .\mnch_course_module_manager_v5.py --self-test
```

Keep API keys in environment variables, not in project files.

## Verification After Changes

After any change to this workspace:

- Confirm expected files and folders exist.
- Confirm the copied v4 script still matches the original by file hash or file size when the copy is expected to be unchanged.
- Confirm `course_index.json` parses as valid JSON.
- Confirm the original v4 folder still contains the original script and existing output folders.
- Confirm existing `outputs_v4`, backup output folders, completed module folders, final synthesis files, and study-pack files were not moved, deleted, or overwritten.
- Run only the smallest relevant check for the change. Prefer fast syntax or self-test checks before running API calls.

## Coding Conventions

- Make small additive changes.
- Avoid broad refactors unless explicitly approved.
- Preserve the working v4 script unless the user explicitly asks for a v4 change.
- Keep secrets out of code, prompts, logs, and committed files.
- Read API keys from environment variables such as `GEMINI_API_KEY`.
- Prefer explicit paths and predictable folder names.
- Preserve UTF-8 text files.
- Do not add new dependencies unless they are clearly necessary.
- Keep terminal output practical and focused on the next recommended step.

## Git Worktrees And Sub-Agents

Use a Git worktree when a future change is risky, broad, or experimental, such as a large v5 manager redesign, migration logic, or a new output strategy that could affect completed course work.

Use sub-agents only for isolated review or research tasks, such as reviewing a plan, checking prompt wording, or inspecting a narrow module. Do not use sub-agents for destructive file operations, secrets handling, or changes that could affect completed outputs.

## Do Not Change Without Asking

Do not change these without explicit user approval:

- The original `mnch_batch_source_card_automator_v4` project folder.
- The original `mnh_batch_source_card_automator_v4.py` script.
- Existing `outputs_v4` files.
- Existing backup output folders.
- Completed module folders.
- Environment files or API keys.
- Final synthesis files.
- Study-pack files.
- Any previously approved module outputs.

Do not move, delete, rename, reset, clean up, or overwrite existing v4 outputs unless the user explicitly requests that exact action.
