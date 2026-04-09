# Learnings: Iteration 001 — Foundation

**Date**: 2026-04-09

## What Worked

- **Mirroring guru-cli architecture** made every design decision faster — most questions were already answered by the CLI's 15 ADRs and proven patterns.
- **Starting with the error hierarchy and input validation** before resources meant the contract was clear before any business logic was written.
- **Pydantic v2 `extra="ignore"`** is the right default — it means model generation doesn't need to be perfect on day one, because extra fields are silently dropped rather than causing failures.
- **pytest-httpx** for HTTP mocking is clean and ergonomic — better than manually patching `httpx.Client`.

## What Didn't Work

- **hatchling + uv interaction** required understanding that they're complementary (build backend vs. package manager), not competing. This wasn't obvious initially.
- **mypy compiled binary** can segfault on certain aarch64/Python 3.10 combos — not a code issue, but something to be aware of in CI.

## Patterns That Emerged

- **Two validation modes** (`validate_input` vs. `validate_free_text`) is a pattern worth documenting prominently — future resource authors need to know which to use where.
- **Section header comments** (the `# ===` delimiters) help AI agents navigate large files — worth standardizing across all files.
- **Constructor injection** of `HttpClient` into resources is the right pattern — it makes testing trivial (just pass a mock) and keeps the dependency graph clean.

## What We'd Do Differently

- Should have created the AI-native repo structure (CLAUDE.md, docs/, ADRs) from the very first commit — not retrofitted after Phase 1 was "done." The compound engineering loop works best when it starts at iteration zero.
- The `scripts/generate_models.py` stub should have been a real generator from day one — even a minimal one that produces one model file would have validated the generation pipeline early.
