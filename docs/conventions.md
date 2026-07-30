# Conventions and Patterns

Detailed conventions for working in this codebase. Referenced from AGENTS.md — agents read this on demand when relevant.

## Project Structure

```
src/guru_sdk/
├── client.py            — Guru facade (entry point, credential resolution)
├── http.py              — HttpClient (sync transport, httpx, Pydantic validation, pagination)
├── errors.py            — Typed exception hierarchy (GuruError, GuruApiError, NotFoundError, etc.)
├── _compat.py           — Internal helpers (UUID detection, input validation)
├── _deprecation.py      — @deprecated decorator with removal version + migration guidance
├── _version.py          — Single source of version truth
├── models/
│   ├── _base.py         — GuruModel base class (extra="ignore", frozen=True, populate_by_name=True)
│   ├── _generated.py    — Auto-generated from Swagger (never edit by hand)
│   ├── _manual.py       — Hand-written models for internal API types
│   └── __init__.py      — Re-export layer
├── resources/
│   └── _base.py         — BaseResource with shared resolve/validation logic
└── contrib/             — Higher-level utilities (Publisher, Bundle, workflows, content)

tests/                   — Mirrors src/ structure (TDD, pytest-httpx)
scripts/                 — generate_models.py (Swagger-to-Pydantic generator)
docs/                    — Living documentation
swagger/                 — Public API spec (source for model generation)
```

## Testing Philosophy (TDD)

We work TDD style. Write tests first, then implement.

### Test file structure

Tests mirror the `src/` directory structure under `tests/`:

```
src/guru_sdk/client.py              →  tests/test_client.py
src/guru_sdk/http.py                →  tests/test_http.py
src/guru_sdk/errors.py              →  tests/test_errors.py
src/guru_sdk/models/_base.py        →  tests/models/test_base.py
src/guru_sdk/resources/cards.py     →  tests/resources/test_cards.py
```

When you create or move a source file, create or move its test file to match.

### What to test

- **Functional behavior**: Does this function/module do what it's supposed to?
- **Execution paths**: Cover the happy path, alternate paths, and error/edge cases
- **Error conditions**: What happens with bad input, missing config, API failures?
- **Contracts between components**: Does the client return the right shape? Does output format correctly?

### What NOT to test

- Don't write tests just to have tests. No "does this class exist" tests.
- Don't test implementation details — test behavior. If internals change but the contract holds, tests should still pass.

### Tests are sacred

Tests are regression contracts. They exist so future agents can verify they didn't break existing functionality.

**When an existing test fails after a code change:**
1. **Default assumption: the code is wrong, not the test.** The test was written with a purpose.
2. Only modify an existing test if the *purpose* of the code it tests has genuinely changed.
3. If you're tempted to change a test to make it pass, stop and ask: "Was my change supposed to change this behavior?" If not, fix your code.
4. Never delete or weaken a test to get a build green.

### Testing patterns

- Mock HTTP via `pytest-httpx` — never hit real endpoints
- Use fixtures in `conftest.py` for shared setup (http_client, proxy clearing)
- Mock `sys.exit` when testing error paths to prevent test runner from dying

## Code Organization

### Two-Layer Architecture

1. **`src/guru_sdk/`** — Reusable SDK layer. Resource Module Pattern (like Stripe SDK, Octokit, OpenAI SDK). `Guru` is a facade.
2. **Resources** receive `HttpClient` via constructor injection — never instantiate their own transport.

**Dependency rule**: No circular imports. Resources depend on `http`, `models`, and `errors` — never on `client.py` or each other.

### Adding a New Resource

1. Create `src/guru_sdk/resources/<resource>.py` with a `<Resource>Resource` class that receives `HttpClient`
2. Add the resource to `Guru` in `src/guru_sdk/client.py`
3. Export from `src/guru_sdk/__init__.py` if public
4. Mirror test file in `tests/resources/test_<resource>.py`
5. Update `docs/architecture/overview.md`

### Function Organization — PUBLIC FIRST

- Public methods FIRST — all public/interface methods appear before private methods
- Private methods LAST — all implementation details come after

### Section Header Comments — REQUIRED

```python
# =============================================================================
# Section Name - Brief Description
# =============================================================================
```

### Line-Level Commentary — PREFERRED

- Focus on WHY each line exists, not just WHAT it does
- Avoid redundant docstrings that just repeat the code

## SDK Design Principles

- Sync-first, async-ready — `httpx.Client` now, `httpx.AsyncClient` later without breaking changes
- Pydantic v2 models — `extra="ignore"` for forward compatibility, `frozen=True` for immutability
- Constructor injection — resources receive `HttpClient`, never build their own
- Resolve pattern — accept IDs or names, resolve transparently (matches guru-cli)
- Input validation — defends against agent hallucination (control chars, path traversal, `?#`, percent-encoding)
- Two validation modes: `validate_input()` for IDs/names (strict), `validate_free_text()` for natural language (lenient)
- Typed exceptions — callers use `try/except NotFoundError`, not status code checks
- Response validation — every API response is validated through Pydantic models

## Swagger-Driven Model Generation

Models are generated from the Guru public API spec, not hand-written:

```bash
curl -o swagger/swagger.json https://api.getguru.com/api/v1/swagger.json
python scripts/generate_models.py
```

Generated code is committed — inspectable, diffable, reviewable. The generator applies `GuruModel` base class, field aliases, and filters out deprecated schemas.

### Post-Refresh Checklist

A refresh diff is large but mostly meaningless — the server emits Swagger properties in a nondeterministic order, so thousands of lines churn with no semantic change. Do not try to read it line by line. Check these instead:

1. **`make check` is green** — ruff, `mypy --strict`, and the full suite. The pin tests below live here.
2. **Renamed query params on endpoints you already call.** Diff the `paths` block, not just `definitions`. This is the failure mode iteration 026 existed to fix: `/comments` renamed `createdAfter` → `activeAfter`, and because the endpoint ignores unknown query params, the SDK's filters silently stopped applying instead of erroring. Added/removed fields are the easy case; renames are the dangerous one.
3. **Numbered enums you reference by name** — see the pinning rule under *Generated Code Rules*.
4. **Removed or narrowed definitions.** Grep `src/`, `tests/`, and `examples/` for anything the refresh dropped. A narrowed enum can also be a latent break: if a response can still carry the removed member, validation will now reject it even though nothing fails today.

### Manual Models for Internal API

Models for endpoints not in the public Swagger spec live in `models/_manual.py` — hand-written but following the same conventions as generated models. Currently covers: `PageDraft`, `PagePermission`, `PageDraftCollaborator`.

### Generated Code Rules

- Generated models live in `src/guru_sdk/models/_generated.py` — **never edit by hand**
- Re-generate with `python scripts/generate_models.py` after updating `swagger/swagger.json`
- `models/__init__.py` is the re-export layer — add new models there when consumers need them
- Generated code gets per-file ruff ignores in `pyproject.toml` (N815 camelCase, TCH003 type-checking imports)
- Field names are snake_case (Pythonic); camelCase from the API spec is preserved as `Field(alias=...)` for API compat
- Three-way field access: create from API dicts via camelCase alias, access via snake_case field name, serialize to API via `model_dump(by_alias=True)`
- Tests for generated models use realistic API shapes (real UUIDs, correct enum values, required fields)
- **No override mechanism yet** — if a regeneration breaks something, that's the signal to add `swagger/overrides.json` with post-processing rules. Until then, `EXCLUDED_SCHEMAS` in the generator and `models/_manual.py` are sufficient.
- **`Type1`, `Op2`, ... numbered enums** — the Swagger spec has inline enums without explicit names (e.g., the `type` field on `FolderItem` can be `"card"` or `"folder"`). Since these enums aren't named in the spec, `datamodel-code-generator` assigns sequential names like `Type9` or `Op12`. The numbers are arbitrary — they reflect the order the enum was encountered during generation and can change on regeneration. When working with these, check `_generated.py` for the actual enum values rather than guessing from the name. If this becomes a readability problem, the deferred codegen override mechanism (iteration 018) could rename them in post-processing.

- **Pin any numbered enum you reference by name.** Renumbering is not just a readability problem — it is a *silent correctness* problem. Because the names are positional, an unrelated upstream spec change can hand a surviving name a completely different member set, and both the annotation and validation still pass. The iteration 026 spec refresh did exactly this: 18 names changed meaning (`Op10` went from `EQ`/`NE` to `AND`/`OR`, `Op17` from `EXISTS`/`NOTEXISTS` to `ISPUBLIC`/`ISNOTPUBLIC`), with no mypy error and no failing test. Nothing broke only because `Type8` — the one name referenced outside `_generated.py` — happened to be stable.

  So: **if you reference a numbered class by name outside `_generated.py`, add it to `PINNED_ANONYMOUS_ENUMS` in `tests/models/test_generated.py`** with its expected members and a note on where it is used. `test_every_referenced_anonymous_enum_is_pinned` scans `src/` and fails if you forget, so this rule enforces itself.

  When a pin fails after a spec refresh, **do not update the pin to match the new values** — that hides the bug. The name was renumbered onto a different enum; find the class that now holds the expected members and repoint the consumers at it. Prefer resolving the enum via its parent model's field annotation (or matching on the string value) over importing a numbered name, so there is nothing positional to pin in the first place.

## Patterns and Rules

### Credential Resolution

The `Guru` client resolves credentials in order: explicit args → `GURU_USER`/`GURU_TOKEN` env vars → `PYGURU_USER`/`PYGURU_TOKEN` legacy env vars.

### Base URL Resolution

Explicit `base_url` arg → `qa=True` flag (→ `QA_BASE_URL`) → `GURU_BASE_URL` env var → `DEFAULT_BASE_URL`. Passing both `qa=True` and `base_url` raises `ValueError`.

### Resource Module Pattern

Each resource receives `HttpClient` via constructor. Methods follow consistent naming: `get`, `list`, `create`, `update`, `delete`. Mirrors guru-cli exactly.

### Name Resolution

Resources accept either UUIDs or human-readable names. Non-UUID → list all + case-insensitive match. `is_uuid()` in `_compat.py` determines which path.

### Model Strategy

- Read models (API responses) are Pydantic models generated from Swagger
- Write operations accept keyword arguments, not model instances
- `extra="ignore"` for forward compatibility, `frozen=True` for immutability

### Versioning

Semver strict. Deprecated features survive one full minor cycle, removed in next major. `@deprecated` decorator emits `DeprecationWarning`. Single version in `_version.py`.

### Branch-Based Installation

Until PyPI publishing is live, users install directly from GitHub branches (`pip install git+...@branch`). Switching branches via `pip install` cleanly replaces the package code — no residual state. **Known edge case**: if a branch adds or removes a dependency in `pyproject.toml`, pip installs new deps but won't automatically uninstall removed ones. If this ever causes issues, `pip install --force-reinstall` resolves it. If this becomes a recurring problem, add a note to the README's Install section.

### Error Handling

HTTP errors → typed exceptions: 401 → `AuthenticationError`, 403 → `ForbiddenError`, 404 → `NotFoundError`, 429 → `RateLimitError`. All inherit from `GuruApiError` with `status_code`, `message`, `body`.

### HttpClient Method Taxonomy

Every API pattern maps to a specific HttpClient method:

- `get(path, Model)` → GET single resource
- `get_list(path, Model)` → GET list (handles 204 as empty list)
- `get_paginated(path, Model)` → GET all pages via Link headers
- `post(path, body, Model)` → POST with JSON body, validated response
- `post_no_content(path, body?)` → POST expecting 204
- `post_list(path, body, Model)` → POST returning a list
- `put(path, body, Model)` → PUT with JSON body, validated response
- `put_empty(path, Model)` → PUT with no body, validated response
- `put_no_content(path, body?)` → PUT expecting 204
- `put_list(path, Model, body?)` → PUT returning a list
- `delete(path)` → DELETE, no response body
- `post_file(path, field_name, filename, file_bytes, mimetype)` → POST multipart file upload

Resources never touch httpx directly — all HTTP goes through these methods.

### Resource Validation Pattern

Every public resource method validates inputs at the top, before any HTTP call:

- IDs, names, structured values → `validate_input()` (strict)
- User-authored text → `validate_free_text()` (lenient: only rejects control chars)
- Emails in URL paths → `quote(email, safe="")` to percent-encode `@`
- JSON body fields → no URL-path validation; Pydantic validates on the response side

### Builtin Name Shadowing — `list`, `dict`, `set` Methods

Resource classes that define `list()` shadow the builtin. Fix: `import builtins` in a `TYPE_CHECKING` block and use `builtins.list[...]` in annotations after the shadowing method.

```python
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import builtins

class FooResource(BaseResource):
    def list(self) -> list[Foo]:          # OK — list not yet shadowed
        ...
    def items(self) -> builtins.list[Foo]:  # Required — list is now the method above
        ...
```

### Empty String Validation

`validate_input()` rejects empty strings. `validate_free_text()` does NOT — search methods must add explicit empty-string validation before calling `validate_free_text()`.

### Enum Values — Check Generated Models

Always check actual enum definitions in `_generated.py` when writing tests. API docs may use different names than the Swagger spec (e.g., `COLLECTION_OWNER` in docs vs `COLL_ADMIN` in spec).

### Test Data Realism

Test fixtures must include all required fields for nested models. E.g., `User` requires `firstName` and `lastName`. Always check required fields on generated models before writing fixtures.

## Documentation (Compound Engineering)

### docs/architecture/
The current state of the system. Always up-to-date. Update after ANY architecture change.

### docs/decisions/
Architecture Decision Records. Format: `NNN-short-title.md` (Context, Decision, Consequences).

### docs/implementation/
Iteration records. Format: `NNN-iteration-title.md`. Update at start and end of each iteration.

### docs/learnings/
Post-iteration retrospectives. Format: `NNN-iteration-title-learnings.md`. Be honest.

### docs/examples/
Usage examples for manual testing and documentation.
