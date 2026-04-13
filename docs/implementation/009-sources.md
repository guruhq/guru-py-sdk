# Iteration 009 — Sources

**Status**: Complete
**Date**: 2026-04-10

## Goal

Add SourceResource for read-only access to Guru sources (external data connectors like Confluence, Jira, Slack, etc.).

## Scope

### Endpoints

| Method | Endpoint | Description | Response Model | Swagger |
|--------|----------|-------------|----------------|---------|
| GET | /sources | List all sources | `list[Source]` | No* |
| GET | /sources/{sourceId} | Get a source | `Source` | No* |
| GET | /sources/{sourceId}/objecttypes | Object types for a source | `list[ObjectType]` | Yes |
| GET | /sources/groups | List grouped connections | `list[GroupedSourceConnection]` | Yes |
| GET | /sources/groups/{groupId} | Get grouped connection | `GroupedSourceConnection` | Yes |

*Not in public Swagger but used by guru-cli (which also mandates public-only). These endpoints work in practice.

### Public API (5 methods)

- `list()` → `list[Source]`
- `get(source_id)` → `Source`
- `object_types(source_id)` → `list[ObjectType]`
- `connections()` → `list[GroupedSourceConnection]`
- `get_connection(group_id)` → `GroupedSourceConnection`

### Not included (deferred)

- Facet discovery (facet_values, facet_hierarchy) — not in public Swagger, response models not generated
- Object sync/update operations (PUT endpoints) — write operations for custom source builders
- Source filter endpoint (GET /search/sourcemgr/filters/sources) — already covered by SearchResource

## Implementation

### New Files
- `src/guru_sdk/resources/sources.py` — SourceResource (5 public methods)
- `tests/resources/test_sources.py` — 16 tests

### Modified Files
- `src/guru_sdk/_compat.py` — Added empty-string rejection to `validate_input()`
- `src/guru_sdk/client.py` — Added `self.sources = SourceResource(self._http)`
- `src/guru_sdk/__init__.py` — Added `SourceResource` to exports
- `src/guru_sdk/models/__init__.py` — Added `GroupedSourceConnection`, `ObjectType` to exports

### Fixes applied across codebase
- **`validate_input()` now rejects empty strings** — this was a gap that affected all resources. An empty resource ID should never be valid. Added `if not value.strip(): raise ValidationError(...)` as the first check.
- **`builtins.list` for method shadowing** — Fixed mypy errors in groups.py, folders.py, collections.py where the `list()` method shadowed the builtin `list` type in annotations.
- **`dict[str, Any]` for get_paginated params** — Fixed mypy error in members.py where `dict[str, str]` conflicted with `max_pages: int` keyword param.

## Test Summary

- 16 new tests (412 total)
- TestList: 3 tests (basic, empty, nested fields)
- TestGet: 3 tests (by ID, empty validation, control chars)
- TestObjectTypes: 5 tests (basic, facets, fields, empty, validation)
- TestConnections: 2 tests (basic, empty)
- TestGetConnection: 3 tests (by ID, empty validation, control chars)

## Quality Gates

- ruff: ✅ clean
- pytest: ✅ 412 passed
- mypy: ⏭ verify on Mac (segfaults in sandbox)
