# ADR-009: Targeted Optional-Field Overrides in Codegen

## Date

2026-10-16

## Status

Accepted. Partially supersedes the deferral of backlog 018 (Codegen Override Mechanism).

## Context

Once pagination followed Guru's `rel="next-page"` links (iteration 031), a live export of a large QA collection reached page 2 of `GET /folders` and failed:

```
102.lastModifiedBy.firstName  Field required
102.lastModifiedBy.lastName   Field required
```

The folder's `lastModifiedBy` was a pending invite (`status: PENDING`), which has an email but no name yet. The spec marks `User.firstName` and `User.lastName` required, so the generated model rejected the whole page. guru-cli marks both optional ("undefined for pending invites").

`_generated.py` is never edited by hand, and backlog 018 had deferred an override mechanism "until a regeneration actually breaks something". A model stricter than live data, one that breaks `folders.list()` and `collections.home_folder()`, is that trigger.

## Options

1. **Make every generated field optional** (`--force-optional`). This matches guru-cli's posture and prevents the whole class of failure, but it turns every required field in 28 schemas into `X | None`. That pushes `None` checks onto every SDK user and drops the type guarantees the spec does give.
2. **Targeted overrides.** Keep the spec's required fields, but list the specific fields the live API is known to omit, with the evidence beside each, and drop them from `required` before codegen.
3. **Lenient validation at the HTTP layer.** Rejected: it hides real contract changes and differs per call site.

## Decision

Option 2. `scripts/generate_models.py` gains `OPTIONAL_FIELD_OVERRIDES: dict[str, set[str]]`, applied in `load_and_filter_spec`. The first entry is `User: {firstName, lastName}`. The generator fails loudly if a listed schema disappears or a listed field is no longer required, so stale entries get removed.

## Consequences

- `User.first_name` and `User.last_name` are `str | None`. No SDK code read them; callers that did must handle `None`.
- Regenerating on datamodel-code-generator 0.81 produced no other changes, so the diff is exactly the override.
- New entries need live evidence (a captured payload or a failing live call), not a guess. If the list grows past a handful, revisit option 1.
- `tests/models/test_generated.py::TestOptionalFieldOverrides` pins the behaviour, including that `email` stays required.
