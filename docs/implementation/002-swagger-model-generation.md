# Iteration 002 — Swagger Model Generation

**Date**: 2026-04-09
**Status**: Complete

## Goal

Get `generate_models.py` producing real Pydantic v2 models from the Guru public Swagger spec, so every resource module in Phase 2+ has typed models to work with.

## What We Set Out to Build
- Download and commit `swagger/swagger.json` (the Guru public API spec)
- Implement `scripts/generate_models.py` — full pipeline: load spec → filter deprecated schemas → generate Pydantic models → apply GuruModel base class → post-process field aliases → format with ruff
- Generate initial model set into `src/guru_sdk/models/`
- Validate generated models: import cleanly, inherit from GuruModel, pass mypy strict
- Tests for the generated models (instantiation, extra field handling, frozen behavior)
- Filter out deprecated/board-related schemas (Board, BoardGroup, Framework, Question, etc.)

## What We Actually Built

- **`scripts/generate_models.py`** — full 4-step pipeline:
  1. Load Swagger 2.0 spec, extract `definitions`, filter out 6 deprecated schemas, nullify dangling `$ref` pointers to excluded schemas
  2. Run `datamodel-code-generator` with JSON Schema input (Swagger 2.0 definitions extracted as JSON Schema)
  3. Post-process: replace `BaseModel` inheritance with `GuruModel`, add module docstring, fix imports
  4. Format with `ruff format` + `ruff check --fix`
- **`src/guru_sdk/models/_generated.py`** — 4,601 lines, 248 models, 122 enums. Single file (cross-references between models make split files impractical).
- **`src/guru_sdk/models/__init__.py`** — re-exports 32 key models (Card, Folder, CollectionModel, Tag, User, Team, KnowledgeAgent, etc.)
- **`tests/models/test_generated.py`** — 42 new tests covering GuruModel inheritance, extra="ignore", frozen=True, Card instantiation with nested objects, excluded schema verification
- **`swagger/swagger.json`** — 535KB public API spec committed to repo
- **Per-file ruff ignores** in `pyproject.toml` for generated code (N815 camelCase, TCH003 type-checking imports)

## What Changed From Plan
- **Single file output** instead of per-resource model files. `datamodel-code-generator` generates to one file because models reference each other heavily. Split files would create circular import issues. The `models/__init__.py` re-export layer gives consumers the clean API they need.
- **No snake_case aliases** in this iteration. Field names stay as camelCase from the API (e.g., `preferredPhrase`, `lastModified`). `GuruModel` has `populate_by_name=True` so both forms work. Snake_case aliasing is deferred — it's a post-processing step that needs careful field mapping and would delay the iteration without blocking resource work.
- **No mypy validation** of generated code. The compiled mypy binary segfaults on this sandbox's aarch64/Python 3.10 combo. CI will validate this. Lint and tests both pass.
- **Swagger 2.0 workaround**: `datamodel-code-generator` expected OpenAPI 3 `components/schemas`. We extract `definitions` from the Swagger 2.0 spec as a standalone JSON Schema document — works perfectly.

## Test Coverage
- 42 new tests (137 total, up from 95)
- Tests cover: GuruModel inheritance (10 core models), extra="ignore" behavior, frozen=True behavior, Card with all core fields, nested objects (User, CollectionModel, Tags), excluded schema verification (6 deprecated schemas)
- All tests use in-memory model instantiation — no HTTP mocking needed for model tests
