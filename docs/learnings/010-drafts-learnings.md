# Learnings — Iteration 010: Drafts

## What Worked

1. **Cleanest iteration yet**: CRD scope is small and well-defined. No name resolution, no pagination, no complex response shapes. 4 methods, 14 tests, done.

2. **Domain knowledge from stakeholder**: Mark's context about MPS/YJS collaborative editing prevented us from implementing a naive update that would conflict with real-time editing sessions. This is exactly the kind of thing you can't discover from API specs alone.

## What We Learned

1. **Collaborative editing changes the update contract**: Traditional REST update (PUT) doesn't work when the resource can be under real-time collaborative control. The "politely fail" pattern needs to:
   - Detect whether a draft is in active editing mode
   - Return a clear signal (not a generic 409) so the caller knows *why* it failed
   - Distinguish between "draft exists and is dormant" (safe to update) vs "draft is being edited" (must fail)

2. **DraftCard model is already generated**: No new model needed for reads. Write operations use keyword args → dict body (same pattern as cards, collections).

3. **validate_input now catches empty strings globally**: The fix from iteration 009 meant we didn't need any special empty-string handling in drafts — validate_input catches it automatically. The feedback loop worked.

## Patterns Confirmed

- **CRD without U is a valid delivery**: Shipping create/read/delete without update was the right call. The update has genuine architectural complexity that would have blocked the iteration.
- **Keyword-only create args**: `create(*, title, content=None, ...)` with keyword-only params keeps the API clean and self-documenting.
