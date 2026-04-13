# Iteration 013 — Contrib: Workflows — Learnings

## What Worked

1. **Free functions over methods**: Taking `Guru` as the first argument keeps the core client clean. Users import only what they need from `contrib.workflows`. No surface area bloat on the Guru class.

2. **Mock-at-resource-level testing**: Using `MagicMock` for the Guru client and its resource attributes made tests fast and focused. We're testing workflow logic (sequencing, error handling, batching) without needing to mock HTTP responses. The underlying resource methods are already thoroughly tested in their own test files.

3. **Results dict pattern for batch ops**: Returning `dict[str, bool]` for batch operations (batch_add, add_to_groups, remove_from_groups) gives callers fine-grained feedback without raising on partial failures. This matches the legacy py-sdk behavior and is more useful than a simple bool.

4. **TDD red-green cycle was clean**: Tests wrote naturally — the function signatures and expected behaviors were clear from the legacy audit. No test rewrites needed during implementation.

## What We Learned

1. **Internal API endpoints are not for contrib either**: `move_folder_to_folder` and `set_item_save_folder` use the internal `/folders/{slug}/action` endpoint with `item_id` and `legacyType: "BOARD"` — fields that don't exist in the public swagger. These were correctly dropped from scope. The rule "if a capability requires an internal endpoint, don't build it" applies to contrib too, not just core resources.

2. **Generated model fields are `str | None`**: Pydantic models from the swagger spec have optional ID fields (`id: str | None`). Workflow functions that chain operations (create → use ID → next call) need explicit null checks to satisfy mypy. This is a pattern that will recur in contrib — any function that reads `.id` from a model return value needs a guard.

3. **Batch retry strategy from legacy py-sdk is sound**: The halving/reduction strategy for batch retries (100 → smaller → 1 → give up) handles both "some emails are bad" and "API is temporarily overwhelmed" cases. Worth keeping.

## Patterns for Future Iterations

- **Contrib function signature**: `def workflow(g: Guru, ...) -> ReturnType` — always Guru client first, keyword args for optional params
- **Null guard pattern for model IDs**: `if model.id is None: raise NotFoundError(...)` before using model.id in downstream calls
- **Batch result dict**: `dict[str, bool]` for any operation that processes a list of items with possible partial failures
