# Iteration 017 — QA Environment Support — Learnings

## What Worked

1. **Tiny iteration, clean scope**: Two files changed (`http.py` constant, `client.py` constructor logic), 8 tests, zero side effects. This is the platonic ideal of a focused iteration.

2. **Sentinel pattern via `None`**: Changing `base_url: str = DEFAULT_BASE_URL` to `base_url: str | None = None` lets us distinguish "caller passed a value" from "using default." This enables proper precedence: explicit arg → qa flag → env var → default. Without this, there's no way to know if the caller intended the default or just didn't pass anything.

3. **Conflict detection over silent precedence**: Rather than silently picking one when `qa=True` and `base_url` are both passed, we raise `ValueError`. This prevents subtle bugs where a customer thinks they're hitting QA but their explicit URL wins (or vice versa).

## What We Learned

1. **Env var naming convention**: `GURU_BASE_URL` follows the same `GURU_*` prefix as `GURU_USER` and `GURU_TOKEN`. This is consistent and discoverable. The py-sdk v1 used a `qa` parameter on the constructor — we preserve that interface while adding the env var for containerized/CI deployments where constructor args aren't practical.

2. **No export changes needed**: `QA_BASE_URL` and `DEFAULT_BASE_URL` are internal constants. The public interface is `qa=True` on the constructor. Customers don't need to import URL constants.

## Patterns for Future Iterations

- **Env var as fallback, not override**: The pattern `explicit arg → flag → env var → default` is a good general model for configuration resolution. Credentials already follow this pattern; now base URL does too.
- **Conflict detection for mutually exclusive options**: When two configuration paths are ambiguous, raise early rather than silently choosing one.
