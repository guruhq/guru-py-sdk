# Iteration 005 — Folders + Collections Learnings

**Date**: 2026-04-10

## What Worked

1. **Pattern repeatability confirmed.** The resource module pattern from iteration 004 (Cards) transferred cleanly to Folders and Collections. Same structure: CRUD → specialized operations → name resolution → input validation. Building these two resources took a fraction of the time Cards did.

2. **Test-first caught real bugs.** Writing tests before implementation revealed three issues during quality gates that would have been subtle production bugs:
   - `validate_input()` rejecting hex colors with `#` characters
   - Docstrings using `COLLECTION_OWNER` when the Swagger-generated enum actually uses `COLL_ADMIN`
   - Missing `_folder_json()` test helper causing `F821 Undefined name` lint failure

3. **HttpClient's method taxonomy held up.** Only needed one small extension (`delete()` now accepts `**params` for query parameters) to support folder `removeType`. The taxonomy from iteration 004 proved comprehensive.

## What We'd Do Differently

1. **Validate enum values against generated models before writing tests.** The `COLLECTION_OWNER` vs `COLL_ADMIN` mismatch came from assuming the API role names without checking the actual generated `Role4` enum. Lesson: always inspect `_generated.py` enum definitions when writing test fixtures that include enum fields.

2. **Don't `validate_input()` non-ID fields.** Color hex codes, descriptions, and other free-form fields shouldn't use the strict ID validation that rejects `#` and `?`. The validation taxonomy should be: IDs/names → `validate_input()`, user text → `validate_free_text()`, everything else (colors, enums, etc.) → skip or use field-specific validation.

## Patterns Discovered

### validate_input() scope
`validate_input()` is specifically for fields that go into URL paths — resource IDs, names used for resolution, group IDs. Fields that are part of JSON request bodies (like `color`, `description`, `role`) don't need URL-path-safe validation. They go through Pydantic model validation on the response side instead.

### Home folder pattern
Collections don't have a direct "get home folder" endpoint. The pattern is: list folders filtered by collection, find the one with `home=True`. This is a read-only convenience method that composes two API concepts (folder listing + home flag filtering). Worth noting as a pattern for future convenience methods — composing existing endpoints rather than requiring new ones.

### Folder removeType as query parameter
The folder delete endpoint uses a query parameter (`?removeType=FOLDERS_ONLY`) rather than a request body to control deletion behavior. This required extending `HttpClient.delete()` to pass `**params`. Query parameters on DELETE requests are uncommon but the Guru API uses them here.

## Test Count Progression

| Iteration | New Tests | Running Total |
|-----------|-----------|---------------|
| 001 | 95 | 95 |
| 002 | 42 | 137 |
| 003 | 5 | 142 |
| 004 | 95 | 237 |
| 005 | 71 | 308 |
