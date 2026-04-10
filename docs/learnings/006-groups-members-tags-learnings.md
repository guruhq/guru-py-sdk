# Iteration 006 — Groups + Members + Tags Learnings

**Date**: 2026-04-10

## What Worked

1. **Three resources in one iteration.** Groups, Members, and Tags are simpler than Cards, so bundling them was the right call. The pattern is now thoroughly proven — resource file, test file, wire into facade, export. Total time was a fraction of iteration 004.

2. **Test-first caught the UUID hex bug.** The group test UUIDs used `g` characters which aren't valid hex. `is_uuid()` correctly rejected them, and the tests immediately showed the wrong code path being taken. Easy fix, but it would have been a confusing runtime bug without the test feedback.

3. **WhoAmI model discovery.** Initially assumed `/whoami` returns a `User` model, but checking the Swagger spec revealed it returns a separate `WhoAmI` schema with `team` (required), `user` (optional), and `tokenType`. This kind of spec-first verification prevents runtime surprises.

## What We'd Do Differently

1. **Use valid hex UUIDs from the start.** All test UUIDs should use only `0-9a-f` characters. The `eeeeeeee-...` and `ffffffff-...` patterns from earlier iterations happen to be valid hex; `gggggggg-...` is not. Establish a convention: use repeated hex pairs like `a0a0a0a0-...` for readability.

2. **Check Swagger response schemas before assuming model types.** The `/whoami` → `WhoAmI` model gap was caught during implementation but could have been caught during design. For future resources, always verify the response schema in the Swagger spec before choosing which Pydantic model to validate against.

## Patterns Discovered

### Team ID caching pattern
Tag endpoints require a team ID that comes from `/whoami`. Caching it at the instance level (not class level) ensures each `Guru` client talks to its own team. The `_get_team_id()` method is private and called lazily on first tag operation.

### Email in URL paths
Both MemberResource and GroupResource need email addresses in URL paths. The `@` character must be percent-encoded (`%40`). Using `quote(email, safe="")` ensures all special characters are encoded.

### get_paginated with initial params
The members list endpoint supports `?search=` but also paginates. Extended `get_paginated()` to accept `**params` that are only applied to the first page request — subsequent pages use the full URL from Link headers.

### Validate against the right model
Not every API endpoint returns the "obvious" model. `/whoami` returns `WhoAmI`, not `User`. The Swagger spec is the source of truth for response schemas — always check it.

## Test Count Progression

| Iteration | New Tests | Running Total |
|-----------|-----------|---------------|
| 001 | 95 | 95 |
| 002 | 42 | 137 |
| 003 | 5 | 142 |
| 004 | 95 | 237 |
| 005 | 71 | 308 |
| 006 | 63 | 371 |
