# ADR-001: Mirror guru-cli Architecture

**Date**: 2026-04-09
**Status**: Accepted

## Context

Guru has two developer tools: `guru-cli` (TypeScript, agent-friendly CLI) and the legacy `py-sdk` (Python SDK, monolithic God-class). The legacy SDK is a single 3,738-line file with 132+ methods, no type hints, and no structural alignment with modern Guru APIs.

We need to build a new Python SDK (`guru-sdk`) that can be maintained alongside the CLI without duplicating design decisions.

## Decision

Mirror guru-cli's two-layer architecture: transport (`HttpClient`) + resource modules (`*Resource`) composed by a facade (`Guru`). Use the same vocabulary (`get`, `list`, `create`, `update`, `delete`), same resolve pattern (accept IDs or names), and same API spec (Swagger-driven).

Key choices:
- **Resource module pattern** (like Stripe, OpenAI SDKs) — `g.cards.get()`, not `g.get_card()`
- **Constructor injection** — resources receive `HttpClient`, never build their own
- **Pydantic v2 models** generated from Swagger, not hand-written
- **httpx** for HTTP (sync now, async-ready later)
- **Same credential resolution** — `GURU_USER`/`GURU_TOKEN` env vars

## Consequences

**Positive:**
- Knowledge transfers between CLI and SDK — same patterns, same vocabulary
- Architecture decisions from CLI (15 ADRs) inform SDK design
- Resource additions follow a mechanical pattern in both codebases
- Future agents can switch between CLI and SDK with minimal context switching

**Negative:**
- Some Python-idiomatic patterns are deferred in favor of cross-language consistency (e.g., `g.cards.list()` returns a list, not a generator — pagination generators come later)
- Must stay in sync when guru-cli makes architectural changes

**Future:**
- Async support (`AsyncGuru`) can be added without changing any existing sync code
- Model generation keeps SDK in sync with API spec mechanically
