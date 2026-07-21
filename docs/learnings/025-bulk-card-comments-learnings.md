# Iteration 025 — Bulk Card Comments: Learnings

## What Worked

- **Checking the live spec before hand-authoring.** The ticket's original plan
  (US-001) assumed `CardCommentResult` would need to be hand-written in
  `_manual.py`, since the vendored `swagger/swagger.json` predated the
  endpoint. Checking the *live* public spec first found it already published
  both `CardCommentResult` and `CardReference` — turning a hand-authored
  model into a routine spec refresh + regenerate. Always check the live spec
  before assuming an endpoint is "not public."
- **`get_paginated` already did all the hard work.** Because
  `HttpClient.get_paginated()` (used by folders, members, etc.) is generic
  over path/model, `bulk_get_comments()` needed zero new HTTP-layer code —
  just param-building and a single delegating call.
- **Mirroring `list_comments`'s validation exactly.** Reusing strict
  `validate_input()` for `status`/`created_after`/`created_before` (rather
  than inventing a new validation rule) kept the new method consistent with
  its closest sibling.

## What Didn't Work

- Nothing notable. The `.agents/skills/start-iteration` /
  `record-decision` / `complete-iteration` skills referenced by the task
  aren't registered in the global Skill-tool listing (they're project-local
  under `.agents/skills/`); reading and following their `SKILL.md` files
  directly worked fine as a substitute.

## Patterns That Emerged

- **Team-wide vs. per-card endpoint pairs.** `/comments` (team-wide) and
  `/cards/{cardId}/comments` (per-card) return overlapping-but-differently-
  shaped data (`CardCommentResult` nests `card`; `CardComment` has no card
  reference at all, since the card is already known from the URL). When a
  resource gets both a scoped and a global variant of the same concept, keep
  the global method card-id-free and skip `self._resolve_card()` entirely —
  don't force it through the per-card resolution path.

## What We'd Do Differently

- Nothing material. Scope stayed tight: one model regeneration (already
  done), one method, five tests.
