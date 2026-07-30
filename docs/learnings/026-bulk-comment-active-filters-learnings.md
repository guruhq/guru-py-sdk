# Iteration 026 — Bulk Comment Active Filters: Learnings

## What Worked

- **Renaming tests first surfaced the exact failure mode.** Running
  `-k BulkGetComments` immediately after renaming the three tests' kwargs
  (before touching `cards.py`) produced
  `TypeError: got an unexpected keyword argument 'active_after'` — a clean,
  unambiguous signal that the tests were exercising the intended rename and
  not accidentally passing for an unrelated reason.
- **A prior spec-refresh story (US-001) de-risked this one.** Because
  US-001 had already confirmed `CardCommentResult`/`CardReference`/
  `CardComment` field sets were unchanged by the `swagger.json` refresh, this
  story could proceed as a pure kwarg/query-param rename with zero
  model-shape investigation needed.
- **Keyword-only params meant a clean rename with no shim.** Since
  `bulk_get_comments()`'s params sit after a bare `*`, there are no
  positional callers to worry about, and the package being unreleased
  (`0.1.0`, nothing shipped in `CHANGELOG.md` for this method) meant no
  deprecation shim was warranted — straight rename, documented as a breaking
  change in the changelog for anyone building against the pre-release API.

## What Didn't Work

- Nothing notable. The rename touched exactly the lines the plan identified
  — no surprises in `cards.py` or the test file.

## Patterns That Emerged

- **Kwarg names that describe server-side semantics drift silently.** When a
  kwarg name (like `created_after`) is chosen to describe what a query param
  *means* on the server, and the server later renames that query param (here,
  `createdAfter` → `activeAfter`), the SDK's kwarg can silently fall out of
  sync — with no test or runtime error forcing the issue. The `/comments`
  endpoint's silent-ignore-unknown-params behavior means the old kwargs kept
  working (no exception, no 400), they just stopped filtering: a request with
  `created_after="2026-01-01"` sent an unrecognized `createdAfter` param that
  the server dropped, so every comment came back regardless of date. This
  class of drift is invisible without either (a) reading the vendored spec
  after every refresh for renamed query params, not just added/removed
  fields, or (b) integration tests against a live/staging server that would
  catch a filter silently not filtering.

- **Positional codegen names are a silent-correctness hazard, not just a
  readability one.** Review of this PR turned up that the refresh renumbered
  18 surviving anonymous enum names onto *different* member sets — `Op10`
  went from `EQ`/`NE` to `AND`/`OR`, `Op17` from `EXISTS`/`NOTEXISTS` to
  `ISPUBLIC`/`ISNOTPUBLIC`, `Op20` from 2 members to 12. Every model *field's*
  allowed value set was preserved, which is what "value-preserving" in the
  grooming plan actually meant; the plan's stronger claim that all affected
  *classes* were value-preserving was not accurate. Nothing broke only because
  `Type8` — the sole numbered name referenced outside `_generated.py`
  (`contrib/publisher.py`, `contrib/workflows.py`) — happened to be stable.
  Had it shifted, the annotation would still have type-checked and validation
  would still have passed: `mypy --strict` and all 719 tests would have stayed
  green while folder/card dispatch compared against the wrong enum.

## What We'd Do Differently

- **Guard the positional names, don't just document them.**
  `docs/conventions.md` already warned that numbered enum names can shift on
  regeneration, but a prose warning in a conventions doc is not load-bearing —
  it did not stop this refresh from shipping an unverified `Type8` dependency.
  Added `PINNED_ANONYMOUS_ENUMS` in `tests/models/test_generated.py`: a pin
  table asserting the exact members of every numbered enum referenced by name,
  plus `test_every_referenced_anonymous_enum_is_pinned`, which scans `src/` and
  fails if a new by-name reference is added without a pin. The rule now
  enforces itself rather than depending on someone reading the docs. Verified
  by mutation — emptying the table, corrupting the expected members, and
  simulating a renumbered-away name each produce a distinct, actionable
  failure. The pin's failure message deliberately says *repoint the consumer*,
  not *update the pin*, since updating the pin to match would hide exactly the
  bug it exists to catch.
- The better long-term fix is to not depend on positional names at all —
  resolve the enum through its parent model's field annotation, or match on
  the string value. Pinning makes the dependency safe; removing it makes the
  dependency unnecessary.
- For the broader codebase: a recurring post-spec-refresh check for renamed
  (not just added/removed) query params on existing methods would catch this
  class of drift earlier, before a story like sc-158926 has to trace it back
  manually. Now written up as a post-refresh checklist in
  `docs/conventions.md` covering all four failure modes seen here: renamed
  query params, renumbered enums, removed definitions, and narrowed enums.
