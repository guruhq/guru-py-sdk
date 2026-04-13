# Learnings — Iteration 009: Sources

## What Worked

1. **Clean iteration**: Straightforward resource with no name resolution needed (sources only accept UUIDs). Made for a compact implementation.

2. **Existing models covered everything**: `Source`, `ObjectType`, `GroupedSourceConnection` were all already in `_generated.py` — no model gaps.

## What We Learned

1. **validate_input didn't reject empty strings**: This was a latent bug affecting ALL resources. Empty IDs would pass validation and produce malformed URLs like `/sources/`. Fixed by adding `if not value.strip()` as the first check. This should have been caught in iteration 004 (cards) but no tests covered it.

2. **SyncStatus enum values**: The API uses `SYNCING`, `SYNCED`, `FAILED`, `INVALID` — not `COMPLETED` as you might guess. Always check `_generated.py` enum definitions. (Same lesson as iterations 006 and 008.)

3. **Public Swagger gaps**: `GET /sources` and `GET /sources/{id}` aren't in the public Swagger spec, but guru-cli uses them under its "public API only" rule. These endpoints work in practice — the Swagger spec is incomplete rather than the endpoints being internal.

4. **Facet discovery is non-public**: The facet endpoints (`/sources/{id}/facets/{facetId}/values` and `/hierarchies`) aren't in the Swagger spec and their response shapes aren't in generated models. guru-cli uses passthrough schemas for these. Deferred until response models can be defined or generated.

## Patterns Established

- **Empty-string validation**: `validate_input()` now rejects empty strings globally. No individual resource methods need their own empty-string checks for IDs/names.
- **Swagger-incomplete endpoints**: Some endpoints work but aren't documented. When guru-cli uses them under the same "public only" constraint, they're safe to use.
