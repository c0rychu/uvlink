# Repository Guidelines

## Project Structure & Module Organization
Source lives under `src/uvlink/`, with the Typer CLI in `cli.py` and project/cache helpers in `project.py`. Configuration and packaging metadata sit in `pyproject.toml`, while `README.md` and `CHANGELOG.md` document behavior and history. Tests should reside in `tests/` (create it if missing) and mirror the `src/uvlink` layout for easy discovery. Keep auxiliary tooling such as `Makefile` tasks or UV lockfiles at the repo root to avoid polluting module directories.

## Build, Test, and Development Commands
Use [uv](https://docs.astral.sh/uv/) for repeatable environments:

```bash
$ uv run pytest                # run the test suite
$ uv run ruff check .          # lint
$ uv run black .               # format
$ make ci                      # run all checks (lint, format, typecheck, tests)
$ make fix                     # auto-fix formatting and lint issues
```

## Coding Style & Naming Conventions
Code targets Python 3.12+ and follows Black’s default formatting plus Ruff’s lint rules; both tools run through pre-commit. Use descriptive module-level constants and snake_case for functions, attributes, and variables. Public CLIs should expose Typer commands with concise verbs (`link`, `ls`, `gc`). Docstrings follow the Google style already used throughout `src/uvlink`. When handling paths, prefer `pathlib.Path` over `os.path` helpers.

## Testing Guidelines
Author tests with Pytest, naming files `test_<module>.py` and functions `test_<behavior>`. Focus on validating cross-platform behavior: cache path resolution, symlink creation/removal, and garbage-collection logic. Mock filesystem access where possible so tests run on CI without touching the real cache. Aim to cover every Typer command path, including `--dry-run`.

## Commit & Pull Request Guidelines
Existing commits follow Conventional-Commit style (`feat:`, `fix:`, `chore:`). Keep messages imperative and scoped to one change set. Pull requests should describe the problem, outline the fix, and note any platform-specific implications (e.g., Windows symlink requirements). Link related issues, include reproduction steps or command output when relevant, and confirm that `uv run pytest` and the pre-commit hooks pass before requesting review.

## Platform Notes
Symlink creation currently requires Windows Developer Mode or an elevated shell. Mention this in PRs that touch linking behavior, and double-check cache paths resolve sensibly on `%LOCALAPPDATA%` when modifying `get_uvlink_dir`.
