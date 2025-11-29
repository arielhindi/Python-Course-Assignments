# GitHub Copilot instructions — Python-Course-Assignments

These instructions are written for an assistant (Copilot / AA) working on this
repository. They describe the project, how to run and test it, and conventions to
follow when suggesting or generating edits.

## Repository overview
- This repository contains short Python course assignments organized by day
  (e.g., `day02`, `day03`, `day04`). Each `dayXX` folder is a small, mostly
  self-contained project (CLI, GUI, downloader, or tests).
- Notable subprojects:
  - `day02` — baking conversion scripts (CLI + GUI examples)
  - `day03` — refactored baking conversion code with modules, tests, and
    persistence
  - `day04` — IMS stargazing recommender: `ims_downloader.py`, `business_logic.py`,
    and the GUI under `day04/ui/`

## What Copilot should help with
- Implementing small features and bug fixes within the `dayXX` folders.
- Writing or updating unit tests (pytest) for changed behavior.
- Improving documentation (README files) and run instructions.
- Refactoring for readability and modularity (prefer minimal, safe changes).

Avoid making large, invasive changes across many files without an explicit
request from the repo owner.

## How to run locally (developer guidance)
1. Create and activate a virtualenv from the repo root:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies for a given day (example for day04):
   ```bash
   pip install -r day04/requirements.txt
   ```
3. Run the GUI for the stargazing recommender (from repo root):
   ```bash
   python -m day04.ui.gui
   ```
4. Run tests (from repo root):
   ```bash
   pytest -q
   ```

## Code style & conventions
- Target Python 3.8+.
- Use absolute imports within packages (e.g., `from day04 import business_logic`) to
  avoid module resolution issues when running as a module.
- Keep functions small and pure where reasonable. Add docstrings to public
  functions and modules.
- Use type hints if adding new public functions, but don't add them retroactively
  across the whole repo unless requested.
- Tests should be small, deterministic, and fast. Use pytest fixtures for shared
  setup.

## Working with external APIs and secrets
- Do not hard-code API tokens or secrets. Use environment variables (e.g.,
  `IMS_API_TOKEN`) and document them in the README or a `.env.example` file.
- If a feature requires an API token and the token is not provided, fall back to
  the existing HTML-scraping approach and clearly display a reliability note to
  the user.

## When to ask the user / require human review
- Large architectural changes (new packaging structure, new top-level
  dependencies, or migrations) should be proposed first and reviewed before
  implementation.
- Any change that affects how user data is stored (new persistence format,
  migration) requires human confirmation.

## Commit message style
- Use short, imperative style: "fix: correct parser for IMS cloudiness section"
- When adding tests or features, include a short description and mention the
  related file(s).

## Provenance and generated content
- Some files in this repo were created or assisted by an AI based on user
  prompts. See `day04/README.md` for a copy of the prompts and a brief
  provenance note. If you edit AI-generated content, prefer small, incremental
  improvements and keep the user-informed about behavioral changes.

## Safety and security
- Never add secrets to the repository. If credentials are needed for local
  testing, instruct the user to set environment variables or use a local
  credentials file that is listed in `.gitignore`.

## Helpful reminders for Copilot suggestions
- Prefer minimal diffs. Keep existing function signatures unless evolving
  them is necessary.
- When adding a new dependency, update the matching `requirements.txt` and
  document why the dependency is needed.
- When a change could affect how a GUI is launched, include the tested
  invocation (for instance, `python -m day04.ui.gui`).

---

If you need additional context, open the README under the affected `dayXX`
folder and the top-level README. If behavior is unclear, ask the repository
owner before making large changes.
