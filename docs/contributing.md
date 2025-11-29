---
icon: lucide/git-pull-request
---

# Contributing

## Discussion
Feel free to make comments/discussion at

- [Reddit Post](https://www.reddit.com/r/Python/comments/1p662t0/uvlink_a_cli_to_keep_venv_in_a_centralized_cache/)
- [Hacker News Post](https://news.ycombinator.com/item?id=46042792)

## Contributing
We welcome contributions! Please follow these guidelines to ensure a smooth process:

## Project Structure

-   **`src/uvlink/`**: Source code.
    -   `cli.py`: Typer CLI entry point.
    -   `project.py`: Project and cache helpers.
-   **`tests/`**: Test suite (mirrors `src` layout).
-   **`pyproject.toml`**: Configuration and metadata.
-   **`README.md`** & **`docs/`**: Documentation.

## Development Workflow

We use [uv](https://docs.astral.sh/uv/) for dependency management and running tasks.

### Common Commands

```bash
# Run tests
uv run pytest

# Lint code
uv run ruff check .

# Format code
uv run black .

# Run all checks (lint, format, typecheck, tests)
make ci

# Auto-fix formatting and lint issues
make fix
```

## Coding Style

-   **Python Version**: 3.12+
-   **Formatting**: Black (default settings).
-   **Linting**: Ruff (rules in `pyproject.toml`).
-   **Conventions**:
    -   Snake_case for functions/variables.
    -   Google-style docstrings.
    -   Prefer `pathlib.Path` over `os.path`.

## Testing

-   Use **Pytest**.
-   File naming: `test_<module>.py`.
-   Function naming: `test_<behavior>`.
-   **Mocking**: Mock filesystem access where possible to avoid touching the real cache during tests.
-   **Coverage**: Aim to cover all Typer command paths, including `--dry-run`.

## Pull Requests

1.  Follow **Conventional Commits** (`feat:`, `fix:`, `chore:`).
2.  Describe the problem and the fix.
3.  Note platform-specific implications (especially for symlinks).
4.  Ensure `make ci` passes before requesting review.

## Platform Notes

Symlink creation on Windows may require Developer Mode or an elevated shell. Please document any Windows-specific behavior if you modify linking logic.
