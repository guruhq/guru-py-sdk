.PHONY: lint format format-check typecheck test check update-lock clean help

# =============================================================================
# Help — default target
# =============================================================================
help:
	@echo "Available commands:"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint         - Run ruff linter on src and tests"
	@echo "  format       - Format code with ruff"
	@echo "  format-check - Verify formatting without modifying files"
	@echo "  typecheck    - Run mypy strict type checker"
	@echo ""
	@echo "Testing:"
	@echo "  test        - Run pytest"
	@echo ""
	@echo "Combined:"
	@echo "  check        - Run lint + format-check + typecheck + test (CI gate)"
	@echo ""
	@echo "Utilities:"
	@echo "  update-lock - Regenerate uv.lock from pyproject.toml"
	@echo "  clean       - Remove build artifacts and caches"

# =============================================================================
# Code Quality
# =============================================================================
lint:
	ruff check src tests

format:
	ruff format src tests
	ruff check --fix src tests

format-check:
	ruff format --check src tests

typecheck:
	mypy src/guru_sdk/ --strict

# =============================================================================
# Testing
# =============================================================================
test:
	pytest

# =============================================================================
# Combined — the CI gate (mirrors guru-cli: pnpm lint && pnpm build && pnpm test)
# =============================================================================
check: lint format-check typecheck test

# =============================================================================
# Utilities
# =============================================================================
update-lock:
	uv lock

clean:
	rm -rf .venv .mypy_cache .pytest_cache .ruff_cache dist build src/*.egg-info
	find . -name '__pycache__' -type d -exec rm -rf {} +
