# Iteration 001 — Foundation

**Date**: 2026-04-09
**Status**: Complete

## Goal

Stand up the guru-py-sdk repo with transport, error handling, model base, input validation, and client facade — everything needed before resource modules can be built.

## What We Set Out to Build
- Repository skeleton with `pyproject.toml`, src-layout, test structure
- `HttpClient` — synchronous httpx transport with auth, pagination, error mapping
- `GuruModel` — Pydantic v2 base class with `extra="ignore"`, `frozen=True`
- `Guru` — client facade with credential resolution
- Exception hierarchy (`GuruError` → `GuruApiError` → `NotFoundError`, etc.)
- Input validation (`validate_input`, `validate_free_text`)
- `@deprecated` decorator
- `BaseResource` class
- `scripts/generate_models.py` stub

## What We Actually Built

All planned deliverables were completed:

- **HttpClient** (`http.py`) — full sync transport with `get`, `get_list`, `post`, `put`, `delete`, `get_paginated`. Pydantic model validation on every response. Link-header pagination. Typed error mapping (401/403/404/429).
- **GuruModel** (`models/_base.py`) — Pydantic v2 base with forward-compatible config.
- **Guru** (`client.py`) — facade with three-tier credential resolution (args → env → legacy env). Context manager support.
- **Errors** (`errors.py`) — full hierarchy with `status_code`, `message`, `body` on API errors.
- **Validation** (`_compat.py`) — `is_uuid()`, `validate_input()` (strict), `validate_free_text()` (lenient). Defends against control chars, path traversal, query/fragment injection, percent-encoding.
- **Deprecation** (`_deprecation.py`) — `@deprecated(removal_version=..., alternative=...)` decorator.
- **BaseResource** (`resources/_base.py`) — constructor injection of `HttpClient`.
- **95 tests** covering all modules.

Additionally completed (not originally planned):
- AI-native repo setup: CLAUDE.md, docs/ structure, ADRs, Makefile, uv.lock
- `.python-version` for consistent dev environments

## What Changed From Plan
- Build backend stayed as `hatchling` (plan mentioned uv — uv is the package manager, hatchling is the build backend; these are complementary)
- Added Makefile and uv.lock (not in original Phase 1 plan, pulled forward from tooling concerns)

## Test Coverage
- 95 tests across 6 test files
- All modules tested: client, http, errors, compat, deprecation, models
- Mock HTTP via `pytest-httpx` — zero network calls
- Covers happy paths, error conditions, edge cases (empty responses, malformed input, missing credentials)
