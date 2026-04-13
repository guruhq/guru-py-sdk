# Iteration 019 — Card Attachments

**Status**: Complete
**Date**: 2026-04-13

## Goal

Add `upload_file()` to `CardResource` so customers can upload images, PDFs, and other files for use in card content. Uses the `POST /attachments/upload` endpoint (see ADR-006).

## Architecture

### New HttpClient Method

`post_file(path, field_name, filename, file_bytes, mimetype) -> dict`

Multipart file upload that returns parsed JSON. This is the first file upload method on HttpClient — the Bundle's upload bypasses HttpClient and hits the httpx client directly (since it uses an `/app/` route). This one goes through the standard `/api/v1/` path.

### New CardResource Method

`upload_file(file_path) -> str`

Opens a local file, guesses MIME type, uploads via `post_file()`, returns the URL from the response's `link` field.

### API Details

- **Endpoint**: `POST /api/v1/attachments/upload`
- **Request**: multipart form, field name `file`, tuple of `(filename, bytes, mimetype)`
- **Response**: `{"attachmentId": "...", "link": "https://content.api.getguru.com/files/view/...", "filename": "...", "mimeType": "...", "size": ...}`
- **Not in public Swagger spec** — see ADR-006

## Scope

| Component | Change |
|-----------|--------|
| `HttpClient.post_file()` | New method for multipart uploads |
| `CardResource.upload_file()` | New method — upload file, return URL |
| Tests | HttpClient post_file + CardResource upload_file |

## Test Summary

6 new tests:
- **HttpClient.post_file** (2): sends multipart, raises on error
- **CardResource.upload_file** (4): returns URL, sends correct multipart POST, raises for missing file, accepts pathlib.Path

Total: 661 tests (655 → 661, +6)

## Quality Gates

```
ruff check   ✅ (zero errors)
mypy         ⏭ (segfaults in sandbox — verify on Mac)
pytest       ✅ 661 passed in 8.90s
```
