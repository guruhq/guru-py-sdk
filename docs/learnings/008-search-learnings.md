# Learnings — Iteration 008: Search

## What Worked

1. **guru-cli audit first**: Reading guru-cli's SearchResource before designing gave a clear picture of the endpoint landscape and helped identify which endpoints are public vs non-public.

2. **Swagger-first model discovery**: Checking the actual Swagger spec response schemas (NLQSearchResponse vs DocumentSearchResponse) prevented wrong model choices. The GET and POST on `/search/documents` return *different* response types.

3. **Small, focused iteration**: 4 methods, 25 tests, clean implementation. No scope creep.

## What We Learned

1. **DocumentType enum values**: The generated `DocumentType` enum uses `GURU`, `SOURCE`, `GURU_ATTACHMENT`, `WEB`, `MCP` — not `CARD`. Always check enum values in `_generated.py` before writing test fixtures. This pattern was documented in iteration 006 but still tripped us up.

2. **validate_free_text doesn't reject empty strings**: It only checks control chars. Search methods need explicit empty-string validation. This is a gap worth considering — should `validate_free_text` gain an optional `allow_empty=False` parameter?

3. **httpx URL encoding vs test URL matching**: httpx encodes spaces as `%20`, not `+`. Exact URL matching in pytest-httpx fails for queries with spaces. Solution: use broad `method="GET"` matching and assert on URL fragments instead.

4. **Public vs non-public search endpoints**: guru-cli uses `/search/cards` and `/search/semantic/*` endpoints that aren't in the public Swagger. The py-sdk uses `/search/cardmgr` and `/search/documents` instead. Different paths, same data.

5. **GET /search/documents is semantic, POST is keyword**: Counter-intuitive — the GET endpoint (`naturalLanguageDocumentSearch`) does NLQ/semantic search, while POST (`keywordDocumentSearch`) does keyword search. Operation IDs in Swagger are the clue.

## Patterns Established

- **Empty string validation pattern**: `if not value.strip(): raise ValidationError(...)` before `validate_free_text()` for required search inputs.
- **Shared body builder**: Static `_build_search_body()` method for constructing SearchQuerySpec dicts from keyword args. Keeps the public methods clean.
- **All-optional browse pattern**: `sources()` has all optional params, supporting both search and browse use cases.
