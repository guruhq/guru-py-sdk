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

## What We'd Do Differently

- Nothing material for this story's scope. For the broader codebase: a
  recurring post-spec-refresh check for renamed (not just added/removed)
  query params on existing methods would catch this class of drift earlier,
  before a story like sc-158926 has to trace it back manually.
