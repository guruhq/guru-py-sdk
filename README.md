# guru-sdk

Modern Python SDK for the [Guru API](https://developer.getguru.com). Typed, sync-first, async-ready, and architecturally aligned with [guru-cli](https://github.com/guruhq/guru-cli).

> **Status:** Phase 1 (Foundation) complete. The transport layer, error handling, model base, and client facade are in place. Resource modules (cards, folders, collections, etc.) are coming in Phase 2.

## Install

```bash
pip install guru-sdk
```

Requires Python 3.10+.

## Quick Start

```python
from guru_sdk import Guru

g = Guru()  # reads GURU_USER + GURU_TOKEN from env
card = g.cards.get("card-id")          # coming in Phase 2
folders = g.folders.list()             # coming in Phase 2
```

Credentials are resolved in order:

1. Explicit arguments: `Guru(username="...", api_token="...")`
2. Environment variables: `GURU_USER` / `GURU_TOKEN`
3. Legacy env vars: `PYGURU_USER` / `PYGURU_TOKEN` (backward compat with `py-sdk`)

## What's Here (Phase 1)

**`Guru` client** (`guru_sdk.client`) — the public entry point. Composes all resource modules (added in Phase 2) and manages the HTTP lifecycle. Supports context manager usage:

```python
with Guru() as g:
    # resources will be available here
    pass
```

**`HttpClient`** (`guru_sdk.http`) — synchronous transport layer built on `httpx`. Handles auth, tracking headers, JSON serialization, Pydantic model validation, Link-header pagination, and typed error mapping. This is the only file that touches `httpx` — resource classes never see raw HTTP.

**`GuruModel`** (`guru_sdk.models`) — Pydantic v2 base class for all API models:

- `extra="ignore"` — unknown API fields are silently dropped, so older SDK versions don't break against newer APIs
- `frozen=True` — models are immutable; mutations go through resource methods
- `populate_by_name=True` — accepts both JSON aliases (`preferredPhrase`) and Pythonic field names (`title`)

**Error hierarchy** (`guru_sdk.errors`):

- `GuruError` — base for all SDK errors
- `GuruApiError` — HTTP error with `status_code`, `message`, `body`
  - `AuthenticationError` (401)
  - `ForbiddenError` (403)
  - `NotFoundError` (404)
  - `RateLimitError` (429)
- `ValidationError` — client-side input validation failure (never hits the API)

**Input validation** (`guru_sdk._compat`) — defends against agent hallucination patterns (control chars, path traversal, query/fragment injection, percent-encoding). Two modes: `validate_input()` for resource IDs (strict) and `validate_free_text()` for natural language (lenient).

**Deprecation framework** (`guru_sdk._deprecation`) — `@deprecated` decorator that emits `DeprecationWarning` with the removal version and what to use instead. Built in from day one so we never ship a breaking change without warning.

## Architecture

Mirrors the guru-cli two-layer pattern:

```
guru-cli (TypeScript)              guru-sdk (Python)
─────────────────────              ────────────────────
GuruHttp (transport)        →      HttpClient (httpx sync)
*Resource classes            →      *Resource classes
GuruClient (facade)          →      Guru (facade)
Zod schemas (validation)     →      Pydantic v2 models
```

Resource modules use constructor injection — each receives `HttpClient` and provides typed CRUD methods. The `Guru` facade wires them together. Knowledge transfers between the CLI and SDK because they share the same vocabulary (`get`, `list`, `create`, `update`, `delete`) and the same resolve pattern (accept IDs or names).

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Quality gates (run all three before any PR)
ruff check src/ tests/       # lint + import sorting
mypy src/guru_sdk/ --strict  # type checking
pytest                       # 95 tests
```

## What's Next

- **Phase 2:** Core resource modules (cards, folders, collections, groups, members, tags) + Swagger-driven model generation
- **Phase 3:** Extended resources (search, sources, drafts, pages, agents, answers, announcements)
- **Phase 4:** `contrib/publisher` and `contrib/bundle`, migration guide, PyPI publish

## License

MIT
