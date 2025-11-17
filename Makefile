.PHONY: all fix check-lint check-fmt check-type check-pyproject.toml test ci pre-commit help


help: ## Show this help message
	@awk 'BEGIN {FS = ":.*##"; printf "Available targets:\n"} /^[a-zA-Z0-9_-]+:.*##/ {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)


all: fix ci ## Run formatting fixes and all checks/tests (fix + check)


fix: ## Auto-fix lint/format issues via Ruff and Black (will modify code!)
	uv run pyproject-fmt pyproject.toml
	uv run ruff check --fix .
	uv run ruff format .
	uv run black .


check-lint: ## Ruff lint (check only)
	uv run ruff check .


check-fmt: ## Black dry-run (check only)
	uv run black --check --diff .


check-type: ## Pyright type checking (check only)
	uv run pyright


check-pyproject.toml: ## Check pyproject.toml formatting (check only)
	uv run pyproject-fmt --check pyproject.toml


test: ## Pytest
	uv run pytest


ci: check-pyproject.toml check-lint check-fmt check-type test ## Run lint, format check, type check, and tests (check only)


pre-commit: ## Run pre-commit hooks (only works after `git add`)
	uv run pre-commit run --all-files
