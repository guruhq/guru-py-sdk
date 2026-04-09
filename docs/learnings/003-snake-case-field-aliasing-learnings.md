# Learnings: Iteration 003 — Snake_case Field Aliasing

**Date**: 2026-04-09

## What Worked

- **`--snake-case-field` flag**: `datamodel-code-generator` handles the entire conversion natively — camelCase to snake_case field names with automatic `Field(alias='originalName')` annotations. Zero custom post-processing needed. We should have checked the tool's flags before planning a custom pipeline.
- **Pydantic's `populate_by_name=True`** (set in `GuruModel`) combined with the generated aliases means both access patterns work out of the box: create from API dicts using camelCase, access fields using snake_case.
- **`model_dump(by_alias=True)`** gives us clean round-tripping: API response → Model (via alias) → API request body (via `by_alias=True`). This is exactly what resource methods will need.
- **Doing this before resources**: the entire iteration was self-contained — one flag, one re-generation, test updates. If we'd done this after writing CardResource, we'd have been renaming fields across multiple files.

## What Didn't Work

- **Enum members also got snake_cased**: `--snake-case-field` converts everything, including enum member names (`TRUSTED` → `trusted`). The values are preserved so it works, but it's cosmetically non-standard for Python enums (convention is UPPER_CASE).

## Patterns That Emerged

- **Three-way field access pattern**: This is how fields work across the SDK now:
  1. **Creation from API**: `Card(preferredPhrase="...")` — camelCase alias from JSON
  2. **Python access**: `card.preferred_phrase` — snake_case field name
  3. **Serialization to API**: `card.model_dump(by_alias=True)` — back to camelCase
  Resource methods will use pattern 1 (building models from API responses) and pattern 3 (sending data to the API).

## What We'd Do Differently

- Would have added `--snake-case-field` in iteration 002 from the start. There was no reason to generate camelCase first and convert later — the flag was already available. The lesson: read the full `--help` output before designing a custom solution.
