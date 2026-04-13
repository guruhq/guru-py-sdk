# guru-py-sdk

Modern Python SDK for the Guru API. Typed, sync-first, async-ready. Architecturally mirrors [guru-cli](https://github.com/guruhq/guru-cli) — same vocabulary, same resource module pattern, same API spec.

## Project Structure
- `src/guru_sdk/` — Main package (`import guru_sdk`)
  - `client.py` — `Guru` facade class (entry point, credential resolution)
  - `http.py` — `HttpClient` (sync transport, httpx, Pydantic validation, pagination)
  - `errors.py` — Typed exception hierarchy (`GuruError`, `GuruApiError`, `NotFoundError`, etc.)
  - `_compat.py` — Internal helpers (UUID detection, input validation)
  - `_deprecation.py` — `@deprecated` decorator with removal version + migration guidance
  - `_version.py` — Single source of version truth
  - `models/` — Pydantic v2 models (generated from Swagger in Phase 2)
    - `_base.py` — `GuruModel` base class (`extra="ignore"`, `frozen=True`, `populate_by_name=True`)
  - `resources/` — One file per resource (mirrors guru-cli pattern)
    - `_base.py` — `BaseResource` with shared resolve/validation logic
  - `contrib/` — Higher-level utilities (Publisher, Bundle — Phase 4)
- `tests/` — Mirrors `src/` structure (TDD, 210+ tests)
- `scripts/` — `generate_models.py` (Swagger-to-Pydantic generator)
- `docs/` — Living documentation (see Documentation section)
- `swagger/` — Public API spec (source for model generation)

## Development Setup

This project uses `uv` for package management.

```bash
uv sync --all-extras       # install all deps (runtime + dev + codegen)
```

## Quality Gates (CRITICAL — Always Run Before Completion)

```bash
make check    # runs all three gates in sequence
```

Or individually:

```bash
make lint       # ruff check (style, imports, unused vars)
make typecheck  # mypy --strict (zero errors)
make test       # pytest (all tests must pass)
```

**Why this sequence matters:**
- **ruff**: Catches style issues, import organization, unused variables
- **mypy**: Strict type checking, catches type errors at compile time
- **pytest**: Runtime validation, behavior verification

Additional Makefile targets:

```bash
make format      # ruff format + ruff check --fix (auto-fix)
make update-lock # regenerate uv.lock from pyproject.toml
make clean       # remove build artifacts and caches
```

## Testing Philosophy (TDD)

We work TDD style. Write tests first, then implement.

### Test file structure
Tests mirror the `src/` directory structure under `tests/`. Every source file with testable logic gets a corresponding test file at the same relative path with a `.test` or `test_` prefix.

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

### Testing patterns for this project
- Mock HTTP via `pytest-httpx` — never hit real endpoints
- Use fixtures in `conftest.py` for shared setup (http_client, proxy clearing)
- Mock `sys.exit` when testing error paths to prevent test runner from dying

## Code Organization

### Two-Layer Architecture
The codebase follows a clean two-layer separation (mirrors guru-cli):
1. **`src/guru_sdk/`** — Reusable SDK layer. Uses the Resource Module Pattern (like Stripe SDK, Octokit, OpenAI SDK). `Guru` is a facade: `g.cards.get()`, `g.folders.list()`.
2. **Resources** receive `HttpClient` via constructor injection — never instantiate their own transport.

**Dependency rule**: No circular imports. Resources depend on `http`, `models`, and `errors` — never on `client.py` or each other.

### Adding a New Resource
1. Create `src/guru_sdk/resources/<resource>.py` with a `<Resource>Resource` class that receives `HttpClient` in constructor
2. Add the resource to `Guru` in `src/guru_sdk/client.py`
3. Export from `src/guru_sdk/__init__.py` if public
4. Mirror test file in `tests/resources/test_<resource>.py`
5. Update `docs/architecture/overview.md`

### Function Organization — PUBLIC FIRST
- **Public methods FIRST** — all public/interface methods appear before private methods
- **Private methods LAST** — all implementation details come after
- **Reasoning**: External callers need to see the interface immediately

### Section Header Comments — REQUIRED
Use delimited section comments to separate functional areas:
```python
# =============================================================================
# Section Name - Brief Description
# =============================================================================
```

### Line-Level Commentary — PREFERRED
- **Focus**: Detailed line-level comments explaining purpose and reasoning
- **Avoid**: Redundant docstrings that just repeat the code
- **Include**: WHY each line exists, not just WHAT it does

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
# Download latest spec
curl -o swagger/swagger.json https://api.getguru.com/api/v1/swagger.json
# Generate models
python scripts/generate_models.py
# Review, test, commit
```
Generated code is committed — inspectable, diffable, reviewable. The generator applies `GuruModel` base class, field aliases, and filters out deprecated schemas.

### Manual Models for Internal API
Models for endpoints not in the public Swagger spec live in `models/_manual.py` — hand-written but following the same conventions as generated models (GuruModel base, snake_case fields with camelCase aliases, all fields optional). Currently covers: `PageDraft`, `PagePermission`, `PageDraftCollaborator`. Add `_manual.py` to ruff per-file-ignores for `TCH001` since Pydantic needs runtime imports for field types.

## Documentation (Compound Engineering)

Every unit of work should compound into the next. Documentation is not optional — it's how the system learns.

### docs/architecture/
**What**: The current state of the system. Always up-to-date. No version history — just what IS.
**When to update**: After ANY change to system architecture, components, interfaces, or patterns.

### docs/decisions/
**What**: Architecture Decision Records. When we choose X over Y, document WHY.
**Format**: `NNN-short-title.md` with sections: Context, Decision, Consequences.
**When to update**: When making a significant design choice (technology, pattern, approach).

### docs/implementation/
**What**: Iteration records, structured like epics/stories. What we set out to build, what we actually built, what changed.
**Format**: `NNN-iteration-title.md`
**When to update**: At the start and end of each implementation iteration.

### docs/learnings/
**What**: Post-iteration retrospectives. What worked, what didn't, what we'd do differently, what patterns emerged.
**Format**: `NNN-iteration-title-learnings.md`
**When to update**: After completing an iteration. Be honest. This is how the system compounds.

### docs/examples/
**What**: Usage examples for manual testing and documentation.
**When to update**: After adding or changing a resource module.

## Patterns and Rules

(This section grows over time as we learn. New rules get added here after each iteration.)

### Credential Resolution
The `Guru` client resolves credentials in order: explicit args → `GURU_USER`/`GURU_TOKEN` env vars → `PYGURU_USER`/`PYGURU_TOKEN` legacy env vars. The legacy fallback exists for backward compatibility with `py-sdk` users.

### Resource Module Pattern
Each resource is a class that receives `HttpClient` via constructor. Methods follow consistent naming: `get`, `list`, `create`, `update`, `delete`. This mirrors guru-cli exactly, so knowledge transfers between the two codebases.

### Name Resolution
Resources accept either UUIDs or human-readable names. When a non-UUID is passed, the resource lists all instances and matches by name (case-insensitive). The `is_uuid()` helper in `_compat.py` determines which path to take.

### Model Strategy
- Read models (API responses) are Pydantic models generated from Swagger
- Write operations accept keyword arguments, not model instances
- `extra="ignore"` ensures forward compatibility — new API fields don't break old SDK versions
- `frozen=True` prevents in-place mutation — mutations go through resource methods

### Versioning
Semver strict. Deprecated features survive one full minor cycle, removed in next major. The `@deprecated` decorator emits `DeprecationWarning` with migration guidance. Single version source of truth in `_version.py`.

### Error Handling
HTTP errors map to typed exceptions: 401 → `AuthenticationError`, 403 → `ForbiddenError`, 404 → `NotFoundError`, 429 → `RateLimitError`. All inherit from `GuruApiError` which carries `status_code`, `message`, and `body`.

### Generated Code Rules
- Generated models live in `src/guru_sdk/models/_generated.py` — **never edit by hand**
- Re-generate with `python scripts/generate_models.py` after updating `swagger/swagger.json`
- `models/__init__.py` is the re-export layer — add new models there when consumers need them
- Generated code gets per-file ruff ignores in `pyproject.toml` (N815 camelCase, TCH003 type-checking imports)
- Field names are snake_case (Pythonic); camelCase from the API spec is preserved as `Field(alias=...)` for API compat
- Three-way field access: create from API dicts via camelCase alias, access via snake_case field name, serialize to API via `model_dump(by_alias=True)`
- Tests for generated models use realistic API shapes (real UUIDs, correct enum values, required fields)

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

Resources never touch httpx directly — all HTTP goes through these methods.

### Resource Validation Pattern
Every public resource method validates inputs at the top, before any HTTP call:
- IDs, names, structured values → `validate_input()` (strict: rejects `?`, `#`, `%xx`, traversal)
- User-authored text (comments, HTML content, search terms) → `validate_free_text()` (lenient: only rejects control chars)
- Emails in URL paths → `quote(email, safe="")` to percent-encode `@`
- JSON body fields (colors, descriptions, enums) → no URL-path validation; Pydantic validates on the response side

### Builtin Name Shadowing — `list`, `dict`, `set` Methods
Resource classes that define a method named `list()` (or `dict`, `set`, etc.) shadow the builtin type within that class scope. mypy resolves `list[Foo]` in annotations to the *method*, not the builtin — even with `from __future__ import annotations`. **Fix**: Add `import builtins` inside a `TYPE_CHECKING` block and use `builtins.list[...]` in all return/parameter annotations that appear *after* the shadowing method. The `list()` method's own return annotation is fine — it shadows *after* its own definition.

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

**When to apply**: Every resource class that has a `list()` method. Check all annotations in that class that use `list[...]` after the `list()` definition.

### Empty String Validation
`validate_input()` rejects empty strings (resource IDs, names). `validate_free_text()` does NOT — search methods that require a query must add explicit empty-string validation: `if not value.strip(): raise ValidationError(...)` before calling `validate_free_text()`.

### Enum Values — Check Generated Models
Always check the actual enum definitions in `_generated.py` when writing tests or docstrings that reference enum values. API documentation may use different names than the Swagger spec (e.g., `COLLECTION_OWNER` in docs vs `COLL_ADMIN` in the spec).

### Test Data Realism
Test fixtures must include all required fields for nested models. E.g., `User` requires `firstName` and `lastName` — a minimal `{"id": "x", "email": "y"}` will fail Pydantic validation. Always check required fields on generated models before writing fixtures.
