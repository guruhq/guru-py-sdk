# ADR-002: Pydantic v2 Models with extra="ignore"

**Date**: 2026-04-09
**Status**: Accepted

## Context

The SDK needs data models that validate API responses, provide IDE autocompletion, and don't break when the Guru API adds new fields. The legacy `py-sdk` uses raw dicts and manual attribute assignment with no validation.

## Decision

Use Pydantic v2 as the model layer with a `GuruModel` base class that sets three key behaviors:

1. **`extra="ignore"`** — Unknown fields from the API are silently dropped. An older SDK version talking to a newer API doesn't raise `ValidationError`.
2. **`frozen=True`** — Models are immutable. Mutations go through resource methods (`g.cards.update()`), not in-place assignment. This prevents local/server state divergence.
3. **`populate_by_name=True`** — Accepts both JSON aliases (`preferredPhrase`) and Pythonic field names (`title`).

Models are generated from the Guru public Swagger spec via `datamodel-code-generator`, committed to the repo (not generated at install time), and formatted with `ruff`.

## Consequences

**Positive:**
- Forward-compatible: new API fields don't break existing SDK versions
- Full type safety and IDE support
- Model generation keeps SDK in sync with API spec (5-minute re-gen)
- `frozen=True` makes data flow explicit — models come from API, mutations go through resources

**Negative:**
- `frozen=True` means no `card.title = "New Title"` — some users may find this surprising
- Generated code needs post-processing (base class injection, alias mapping, deprecated schema filtering)
- Pydantic v2 is a hard dependency (~adds to install size)
