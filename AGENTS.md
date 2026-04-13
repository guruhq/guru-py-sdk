# guru-py-sdk

Modern Python SDK for the Guru API. Typed, sync-first, async-ready. Mirrors [guru-cli](https://github.com/guruhq/guru-cli) architecture.

## Commands

```bash
uv sync --all-extras       # install all deps
make check                 # lint + typecheck + test (ALWAYS run before completion)
make lint                  # ruff check
make typecheck             # mypy --strict
make test                  # pytest
make format                # ruff format + fix
```

## Architecture

Two-layer separation: `src/guru_sdk/` (SDK core) and `src/commands/` never exist — resources are the API.

- `src/guru_sdk/client.py` — `Guru` facade: `g.cards.get()`, `g.folders.list()`
- `src/guru_sdk/http.py` — `HttpClient` (only file that touches httpx)
- `src/guru_sdk/resources/` — One file per resource, receives `HttpClient` via constructor
- `src/guru_sdk/models/` — Pydantic v2 models generated from Swagger (`_generated.py` — never edit by hand)
- `src/guru_sdk/contrib/` — Higher-level utilities (Publisher, Bundle, workflows, content helpers)
- `tests/` — Mirrors `src/` structure (TDD, 669+ tests)

## Key Rules

- **TDD**: Write tests first, then implement. Tests are sacred — if a test fails, the code is wrong.
- **Quality gates**: `make check` must pass before any task is complete (ruff + mypy + pytest).
- **Public first**: Public methods before private in every file.
- **No circular imports**: Resources depend on `http`, `models`, `errors` — never on `client.py` or each other.
- **Two validation modes**: `validate_input()` for IDs/names (strict), `validate_free_text()` for natural language (lenient).
- **Name resolution**: Resources accept UUIDs or names, resolve transparently.

## Documentation

For detailed conventions, patterns, and rules, read `docs/conventions.md`.
For system architecture, read `docs/architecture/overview.md`.
For decision records, see `docs/decisions/`.
For iteration history, see `docs/implementation/`.
For learnings, see `docs/learnings/`.

## Compound Engineering

Every unit of work compounds into the next. After completing work:
1. Update `docs/architecture/` if architecture changed
2. Record decisions in `docs/decisions/` (ADR format)
3. Write implementation record in `docs/implementation/`
4. Write learnings in `docs/learnings/`
5. Update `docs/implementation/backlog.md`

## Skills and Commands

The canonical location for skills is `.agents/skills/`.
When reading, creating, or updating skills, use `.agents/skills/`.
Do NOT write to `.cursor/skills/` or `.claude/skills/` directly.
