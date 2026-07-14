# Iteration 024 — Draft Group Collaborators

**Date**: 2026-07-14
**Status**: Complete
**Ticket**: sc-156806 (epic 156474 — "Add Collaborator to drafts for agentic tools")

## Goal

Add first-class support for adding and removing **User Group** collaborators on
card drafts in `DraftResource`, matching guru-cli's `addGroupCollaborators`, and
fix the `DraftCollaborator` model so group collaborators actually parse.

## Background

Iteration 021 added user-based collaborator methods (`list_collaborators`,
`add_collaborators`, `remove_collaborator`). A caller *could* hand-build a group
payload via `add_collaborators`, but there was no ergonomic method and — more
importantly — the response model could not parse group collaborators, because it
used a `group` field where card drafts return `userGroup`.

## Key finding — card drafts use `userGroup`, page drafts use `group` (ADR-014)

From guru-cli `src/guru/types.ts` (`DraftCollaboratorSchema`):

- **Card drafts** (`POST /drafts/{id}/collaborators`): group payload is
  `{ "type": "user-group", "userGroup": { "id": <groupId> } }`; response field is
  **`userGroup`**.
- **Page drafts** (`POST /pagedrafts/{id}/collaborators`): payload/field is
  **`group`** (already modeled on `PageDraftCollaborator`).

These are intentionally **not** converged (different backends). `PageDraftCollaborator.group`
was left untouched.

## What We Built

- **`DraftCollaborator` model fix** (`src/guru_sdk/models/_manual.py`): renamed the
  `group` field to `user_group` (alias `userGroup`), typed as the generated
  `UserGroup` model instead of a raw dict — matching how `_generated.py` already
  models `userGroup` fields (`UserGroupCollaborator`). This is the core
  correctness fix: user-group collaborators returned by the API now populate.
- **`DraftResource.add_group_collaborators(draft_id, group_ids)`** (`drafts.py`):
  validates `draft_id` and each group ID, then POSTs
  `{"collaborators": [{"type": "user-group", "userGroup": {"id": gid}}, ...]}`
  via `post_list`, returning `list[DraftCollaborator]`. Mirrors the CLI.
- **`DraftResource.remove_group_collaborator(draft_id, group_id)`**: thin alias
  over `remove_collaborator` — for a user-group collaborator the collaborator ID
  *is* the group ID, so it hits the same DELETE endpoint. Added for agent-tool
  clarity. `remove_collaborator`'s docstring now documents the group case.
- **8 new tests** in `tests/resources/test_drafts.py` (698 → 706 total).

## What Changed From Plan

- **Typed `UserGroup`, not a raw dict.** The plan said "a group object with `id`
  and optional `name`." Rather than a `dict[str, str | None]`, we reused the
  generated `UserGroup` model (all fields optional), which is more idiomatic and
  matches the existing `UserGroupCollaborator` pattern in `_generated.py`. Callers
  get typed `.user_group.id` / `.user_group.name` access.
- **Field is `user_group` (snake_case), alias `userGroup`.** The plan wrote
  "rename to `userGroup`"; the `_manual.py` convention is snake_case attributes
  with camelCase aliases, so the Python attribute is `user_group`.

## Design Decisions (kept from plan)

- **ID-based, name resolution out of scope.** guru-cli's `addGroupCollaborators`
  takes group IDs, and CLAUDE.md forbids resources depending on each other
  (`DraftResource` calling `GroupResource`). Name→UUID convenience, if wanted,
  belongs in `contrib/`. Callers can resolve via `g.groups` first.
- **Card drafts only.** The epic and guru-cli both scope this to card drafts;
  page drafts already accept raw group dicts and guru-cli has no dedicated
  page-draft group method, so page-draft parity was left out.

## Risks / Notes

- **Minor breaking change**: any caller reading `.group` on a *card*-draft
  collaborator must switch to `.user_group`. Group parsing never worked before
  (the field was misnamed), so real-world impact is near zero. Noted in the
  CHANGELOG.
- **`userGroup` write shape**: guru-cli sends only `{ "id": <groupId> }`; we match
  that. If the backend ever requires more fields it would surface in QA.

## Test Coverage

- `TestListCollaborators.test_list_parses_group_collaborator`: guards the model
  rename — a `user-group` collaborator populates `.type` and `.user_group`.
- `TestAddGroupCollaborators`: result parse, request-body shape assertion
  (`{type: user-group, userGroup: {id}}`), draft_id validation, group-id validation.
- `TestRemoveGroupCollaborator`: 204 delete by group ID, draft_id + group_id validation.
- All 706 tests pass; `ruff` and `mypy --strict` clean.
