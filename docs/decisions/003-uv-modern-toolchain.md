# ADR-003: uv + Modern Python Toolchain

**Date**: 2026-04-09
**Status**: Accepted

## Context

The project needs a consistent, fast, reproducible development environment. The guru-agent repo uses `uv` for package management alongside a Makefile for standard development targets. We want guru-py-sdk to follow the same patterns for cross-repo consistency.

## Decision

Adopt `uv` as the package manager with the following toolchain:

- **uv** for dependency resolution, lockfile generation, and virtual environment management
- **uv.lock** committed to the repo for reproducible installs
- **.python-version** file pinning the dev environment to 3.11 (matches guru-agent)
- **Makefile** with standard targets: `lint`, `format`, `typecheck`, `test`, `check` (all three), `update-lock`, `clean`
- **ruff** for both linting and formatting (replaces flake8 + isort + black in one tool)
- **mypy --strict** for type checking
- **hatchling** as build backend (uv works with any PEP 517 backend)
- **PEP 735 `[dependency-groups]`** for uv-native dev dependency management

Divergences from guru-agent (intentional):
- **ruff format** instead of black — ruff's formatter is the modern replacement, one tool instead of two
- **mypy strict** instead of non-strict — a public SDK warrants stricter type safety
- **Python 3.10+ requires-python** — SDK needs wider compat than an internal application

## Consequences

**Positive:**
- `uv sync --all-extras` installs everything in seconds
- `make check` runs the full quality gate (lint + typecheck + test)
- Cross-repo consistency with guru-agent — same Makefile targets, same workflow
- `uv.lock` ensures reproducible builds across machines and CI

**Negative:**
- Developers need `uv` installed (not yet as universal as pip)
- `.python-version` may conflict if developers use a different Python version manager
