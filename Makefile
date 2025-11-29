.PHONY: help
help: ## Show this help message
	@awk 'BEGIN {FS = ":.*##"; printf "Available targets:\n"} /^[a-zA-Z0-9_-]+:.*##/ {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: all
all: fix ci ## Run formatting fixes and all checks/tests (fix + check)


.PHONY: fix
fix: ## Auto-fix lint/format issues via Ruff and Black (will modify code!)
	uv run pyproject-fmt pyproject.toml
	uv run ruff check --fix .
	uv run ruff format .
	uv run black .


.PHONY: check-lint
check-lint: ## Ruff lint (check only)
	uv run ruff check .


.PHONY: check-fmt
check-fmt: ## Black dry-run (check only)
	uv run black --check --diff .


.PHONY: check-type
check-type: ## Pyright type checking (check only)
	uv run pyright


.PHONY: check-pyproject.toml
check-pyproject.toml: ## Check pyproject.toml formatting (check only)
	uv run pyproject-fmt --check pyproject.toml


.PHONY: test
test: ## Pytest
	uv run pytest -v --cov=uvlink


.PHONY: ci
ci: check-pyproject.toml check-lint check-fmt check-type test ## Run lint, format check, type check, and tests (check only)


.PHONY: pre-commit
pre-commit: ## Run pre-commit hooks (only works after `git add`)
	uv run pre-commit run --all-files


.PHONY: install-pre-commit
install-pre-commit: ## Install pre-commit hooks
	uv run pre-commit install


.PHONY: docs-serve-local
docs-serve-local: ## Serve documentation locally
	uv run zensical serve

