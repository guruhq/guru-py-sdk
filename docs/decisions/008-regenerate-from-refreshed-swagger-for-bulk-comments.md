# ADR-008: Refresh Vendored Swagger Spec + Regenerate Models Instead of Hand-Authoring Bulk Comment Types

## Date

2026-07-17

## Status

Accepted

## Context

sc-157622 asked for a way to bulk-retrieve card comment threads team-wide,
backing a new `CardResource.bulk_get_comments()` method. The endpoint needed
is `GET /api/v1/comments` — a team-wide comment listing, distinct from the
existing per-card `GET /cards/{cardId}/comments` endpoints already modeled by
`CardComment` / `CardCommentReply`.

At the time this ticket was scoped, `swagger/swagger.json` (the vendored copy
of the public Guru API spec, last refreshed for iteration 002/003) did not
contain this endpoint or its response shape. The original plan (recorded in
the ticket as US-001) was to hand-author the new response model —
tentatively `CardCommentResult`, with a nested card reference — directly in
`src/guru_sdk/models/_manual.py`, following the same pattern already used for
`PageDraft`, `PagePermission`, and `PageDraftCollaborator` (internal-API
models not present in the public spec).

Before writing that hand-authored model, we checked whether the live public
spec (`https://api.getguru.com/api/v1/swagger.json`) had since been updated.
It had: the live spec now publishes `GET /api/v1/comments`, together with two
schemas that match the endpoint's response shape — `CardCommentResult` (flat
comment fields plus a nested `card` reference) and `CardReference`
(`id` / `preferredPhrase` / `slug`). The vendored copy in this repo had simply
gone stale relative to the live spec.

## Decision

Refresh `swagger/swagger.json` from the live public spec and regenerate
`src/guru_sdk/models/_generated.py` via `python scripts/generate_models.py`
(done in US-001, commit `7e8e442`), rather than hand-authoring
`CardCommentResult` / `CardReference` in `_manual.py`.

### Why

- **`_manual.py` is reserved for endpoints genuinely absent from the public
  spec** (see `docs/conventions.md` — "Manual Models for Internal API").
  Once it was confirmed the live spec already publishes these schemas,
  hand-authoring them would violate that boundary and create a model that
  immediately diverges from the generator's next run — the next
  `generate_models.py` invocation would produce a second, conflicting
  `CardCommentResult` in `_generated.py`.
- **Generated code is the source of truth for public-API models.** Per
  `docs/conventions.md`, generated models are inspectable, diffable, and
  regenerated deterministically from the spec. A hand-authored duplicate
  would need to be kept in sync manually and risks silently drifting from the
  real API shape (field names, optionality, enum values).
- **Lower long-term maintenance cost.** Refreshing the spec is a mechanical,
  repeatable operation (`curl` + `generate_models.py`) already exercised in
  iterations 002/003. Hand-authoring risks a one-off model that nobody
  remembers to reconcile the next time the spec is refreshed.

## Consequences

- `swagger/swagger.json` moved forward from its iteration-003 vintage to the
  current live spec, which changed unrelated generated output too (diff
  touched `src/guru_sdk/contrib/publisher.py` and
  `src/guru_sdk/contrib/workflows.py` for downstream call-site adjustments,
  and regenerated ~2000 lines of `_generated.py`). This is expected: a stale
  vendored spec accumulates drift across every iteration since it was last
  refreshed, not just this feature's models.
- `CardCommentResult` and `CardReference` are exported from
  `src/guru_sdk/models/__init__.py` as regular generated models, with no
  special-casing.
- Future contributors adding endpoints should check the *live* spec before
  assuming an endpoint belongs in `_manual.py` — staleness in the vendored
  copy, not spec incompleteness, was the actual cause here.
- No hand-authored model was ever merged for this feature; this ADR documents
  the decision honestly as made *before* `bulk_get_comments()` was
  implemented (this story, US-002), even though the original ticket framing
  assumed hand-authoring would be necessary.

## References

- `docs/conventions.md` — "Swagger-Driven Model Generation" and "Manual
  Models for Internal API" sections.
- `docs/implementation/002-swagger-model-generation.md`,
  `docs/implementation/003-snake-case-field-aliasing.md` — prior spec
  regeneration iterations.
- `docs/implementation/025-bulk-card-comments.md` — this feature's
  implementation record (US-001 + US-002).
- Commit `7e8e442` — "US-001: Refresh vendored swagger spec and regenerate
  models".
