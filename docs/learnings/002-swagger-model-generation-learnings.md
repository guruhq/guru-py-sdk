# Learnings: Iteration 002 — Swagger Model Generation

**Date**: 2026-04-09

## What Worked

- **Extract-and-filter approach** for Swagger 2.0: rather than fighting `datamodel-code-generator` to understand Swagger 2.0 directly, extracting the `definitions` section as a standalone JSON Schema document was clean and reliable. The generator handles JSON Schema perfectly.
- **Post-processing as a separate step** is the right pattern. The generator does the heavy lifting (253 schemas with cross-references, enums, nested types), and post-processing handles the SDK-specific concerns (GuruModel base class, imports, docstring). Each step is independently testable.
- **Single generated file** turned out to be the right call. The models reference each other heavily (229 of 253 schemas contain `$ref`). Splitting into per-resource files would create circular imports. The `models/__init__.py` re-export layer gives consumers the clean interface they expect.
- **Testing generated models** with realistic API shapes caught three issues immediately: enum fields return enum instances (not strings), UUID fields validate strictly, and some models have required fields we didn't expect (like `WhoAmI.tokenType`). These tests will catch regressions when we re-generate.

## What Didn't Work

- **`datamodel-code-generator --input-file-type swagger`** doesn't exist — it's `openapi`, but that expects OpenAPI 3.0 `components/schemas`, not Swagger 2.0 `definitions`. Had to use the `jsonschema` input type with extracted definitions.
- **`--output` to a directory** doesn't work with JSON Schema input (it tries to write the output path as a file). Single-file output only.
- **Dangling `$ref` pointers** after filtering: when we removed `Board` from definitions, any schema that referenced `Board` via `$ref` would fail. Had to add a tree-walking nullifier that replaces excluded `$ref` pointers with `{"type": "object"}` (becomes `Any` in the generated code).

## Patterns That Emerged

- **Generated code gets ruff per-file ignores**: the `N815` (camelCase) and `TCH003` (type-checking imports) rules fire on every field in the generated file. Rather than fighting the generator, add per-file ignores in `pyproject.toml`. This is the right boundary — generated code has different rules than hand-written code.
- **Test with actual API shapes, not idealized data**: initial tests used `id="agent-123"` which fails because the generated model validates UUIDs strictly. Using realistic UUIDs in tests catches these mismatches early.
- **Re-export layer pattern**: `models/__init__.py` imports from `_generated.py` and re-exports only the models consumers need. This decouples the public API from the generation structure. If we later split the generated file or change the generator, the public imports don't change.

## What We'd Do Differently

- Should have tested `datamodel-code-generator` with a small subset of the spec first (e.g., just Card + User + Tag) before running the full 253 schemas. Would have discovered the Swagger 2.0 / JSON Schema workaround faster.
- Snake_case field aliasing (e.g., `preferred_phrase` with alias `preferredPhrase`) should be tackled in a dedicated iteration before resource modules start using the models heavily. Once resources are written against camelCase field names, switching to snake_case becomes a breaking change.
