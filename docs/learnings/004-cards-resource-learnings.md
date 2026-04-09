# Learnings: Iteration 004 — Cards Resource

**Date**: 2026-04-09

## What Worked

- **guru-cli as blueprint**: Studying the TypeScript `CardsResource` first gave us the exact API surface — endpoints, HTTP methods, request bodies, response shapes. Zero guessing, zero API exploration needed. The "mirror guru-cli" strategy pays dividends.
- **TDD caught real issues**: Writing tests first (68 of them) with realistic API shapes immediately revealed that the `User` model requires `firstName` and `lastName` fields. If we'd implemented first, this would have been a debugging session instead of a data-fix.
- **HttpClient extension was clean**: Adding 4 new methods (`put_empty`, `put_no_content`, `put_list`, `post_list`) was straightforward because the existing pattern was clear. Each new method follows the same shape: make request → check status → validate response.
- **Generated models Just Worked**: Every model we needed (Card, CardComment, CardCommentReply, CardCollaborator, CardVerifier, Folder, Tag) was already generated and had the right fields. The Swagger-driven model generation from iteration 002 paid off immediately.
- **Two validation modes**: Having `validate_input()` and `validate_free_text()` already built meant we could correctly validate card IDs (strict) vs. comment content (lenient) without any new infrastructure.

## What Didn't Work

- **Name resolution is limited**: Using `/cards/verificationmgr` as the card listing source only returns cards in the verification queue, not all cards. A proper implementation needs the search endpoint (iteration 007) or a different listing approach. This is adequate for proving the pattern but will need to be enhanced.
- **Test data realism matters**: Initially used `{"id": "user-1", "email": "author@example.com"}` for User objects. Pydantic rightfully rejected it because the generated User model requires `firstName` and `lastName`. Lesson: always check required fields on nested models.

## Patterns That Emerged

- **Resource method → HttpClient method mapping**: Every API pattern maps to a specific HttpClient method. This is now a clear taxonomy:
  - GET single → `http.get(path, Model)`
  - GET list → `http.get_list(path, Model)` (handles 204 as empty)
  - POST → `http.post(path, body, Model)`
  - POST no response → `http.post_no_content(path, body)`
  - POST list response → `http.post_list(path, body, Model)`
  - PUT → `http.put(path, body, Model)`
  - PUT no body → `http.put_empty(path, Model)`
  - PUT no response → `http.put_no_content(path, body?)`
  - PUT list response → `http.put_list(path, Model, body?)`
  - DELETE → `http.delete(path)`
- **Validation placement**: Validation always runs at the top of public methods, before any HTTP call. Two modes: `validate_input()` for IDs/names, `validate_free_text()` for user-authored content.
- **Resolve pattern**: Every card method calls `_resolve_card()` first. UUID → direct passthrough. Title → list + case-insensitive match. This pattern will repeat for folders, collections, groups, etc.
- **Email in URL paths needs encoding**: `remove_collaborator` must `quote(email, safe="")` because `@` is not valid in URL path segments.

## What We'd Do Differently

- Would have checked the `User` model's required fields before writing all the test fixtures. A 30-second check would have saved a test-fix cycle.
- The name resolution approach needs to be designed holistically across all resources, not per-resource. When we build FolderResource and GroupResource (iterations 005-006), we should establish a shared `_resolve_by_name()` pattern in `BaseResource`.

## Architecture Decisions Surfaced

- **HttpClient is the exhaustive HTTP vocabulary**: Rather than having resources make raw `httpx` calls for unusual patterns, we extend HttpClient. This keeps the "only file that touches httpx" contract intact and makes the full set of API patterns discoverable in one place.
