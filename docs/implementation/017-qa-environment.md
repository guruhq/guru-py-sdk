# Iteration 017 — QA Environment Support

**Status**: Complete
**Date**: 2026-04-13

## Goal

Add `qa=True` convenience flag and `GURU_BASE_URL` env var support to the `Guru` constructor, so internal teams can easily target the QA environment without hardcoding URLs. The `qa` flag is internal-only — customers don't have access to `qaapi.getguru.com`. The `GURU_BASE_URL` env var is a general-purpose override for any environment.

## Architecture

### Changes to `http.py`

Added `QA_BASE_URL = "https://qaapi.getguru.com/api/v1"` constant alongside the existing `DEFAULT_BASE_URL`.

### Changes to `client.py`

Updated `Guru.__init__` signature:

```python
def __init__(
    self,
    username: str | None = None,
    api_token: str | None = None,
    *,
    base_url: str | None = None,   # was: str = DEFAULT_BASE_URL
    qa: bool = False,              # NEW
    timeout: float = 30.0,
) -> None:
```

**Base URL resolution order** (highest priority first):
1. Explicit `base_url` argument
2. `qa=True` → `QA_BASE_URL`
3. `GURU_BASE_URL` environment variable
4. `DEFAULT_BASE_URL` (production)

**Conflict detection**: Passing both `qa=True` and `base_url` raises `ValueError` — the intent is ambiguous.

**Breaking change note**: `base_url` changed from `str = DEFAULT_BASE_URL` to `str | None = None`. This is backward-compatible because:
- Callers who passed `base_url="..."` explicitly still work (now `str | None`, still accepts `str`)
- Callers who relied on the default still get production URL (resolved internally)
- The only difference: callers who passed `base_url=DEFAULT_BASE_URL` explicitly now go through the same path as omitting it

## Scope

| Component | Change |
|-----------|--------|
| `http.py` | Added `QA_BASE_URL` constant |
| `client.py` | Added `qa` param, `GURU_BASE_URL` env var resolution, conflict validation |
| Tests | 8 new tests for QA flag, env var, conflict, and precedence |

## Test Summary

8 new tests:
- **qa=True sets QA URL**: Verifies `_http._base_url` is `qaapi.getguru.com`
- **qa=False uses default**: Confirms production URL when qa omitted
- **GURU_BASE_URL env var**: Env var overrides default
- **Explicit base_url overrides env var**: Argument wins over env
- **qa=True overrides env var**: QA flag wins over env var
- **qa + explicit base_url raises ValueError**: Conflict detection
- **qa=True ignores GURU_BASE_URL**: QA flag always wins over env
- **No env var uses production**: Default behavior unchanged

Total: 669 tests (661 → 669, +8)

## Quality Gates

```
ruff check   ✅ (zero errors)
mypy         ⏭ (segfaults in sandbox — verify on Mac)
pytest       ✅ 669 passed in 9.10s
```
