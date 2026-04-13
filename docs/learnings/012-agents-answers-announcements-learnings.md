# Learnings — Iteration 012: Agents + Answers + Announcements

## What Worked

1. **Three resources in one iteration**: The patterns are now so well-established that implementing three resources (15 methods total, 51 tests) was straightforward. TDD continues to be the fastest path to correct code.

2. **Generated models as response types**: Unlike guru-cli which flattens everything, using Pydantic models directly eliminates a whole layer of boilerplate. Callers get rich typed objects instead of flat dicts.

3. **Name resolution pattern**: `resolve()` on AgentResource was clean to implement — `is_uuid()` already existed, the list/match pattern mirrors guru-cli exactly.

## What We Learned

1. **Check enum values BEFORE writing test data**: `AgentType` has `DEEP_AGENT`/`LEGACY`, not `STANDARD`. `Role2` has `ADMIN`/`EXPERT`/`VIEWER`, not `MEMBER`. Every iteration we hit enum mismatches — always check `_generated.py` first.

2. **Check required fields on nested models**: `Document.document_type` and `Card.preferred_phrase` are required (not optional). When a generated model appears as a nested field in test data, its required fields must be present. The error messages from Pydantic are clear but catching these upfront saves a debug cycle.

3. **Generated model shapes differ from guru-cli's flattened schemas**: `AnnouncementUser` is a flat user object with `email` at the top level + announcement timestamps. guru-cli's Zod schema wraps a user object inside the read-user entry, then flattens. The py-sdk skips that — the generated model IS the shape.

## Patterns Confirmed

- **builtins.list shadowing**: Both AgentResource and AnnouncementResource have `list()` methods — both correctly use the `TYPE_CHECKING` + `builtins.list[...]` pattern.
- **Free-text validation for questions**: Questions use `validate_free_text()` + explicit empty-string check, same as search terms and titles.
- **Group body format**: Agent group access and announcement creation both use `[{"id": gid}]` format for groups in the POST body, matching guru-cli.

## Pattern to Add to CLAUDE.md

**Enum Values — Check Generated Models**: Always check the actual enum definitions in `_generated.py` when writing tests or docstrings that reference enum values. API documentation may use different names than the Swagger spec (e.g., `STANDARD` in docs vs `DEEP_AGENT` in spec, `MEMBER` in docs vs `VIEWER` in spec).
