# Iteration 019 — Card Attachments — Learnings

## What Worked

1. **Small iteration, clean separation**: This was a focused iteration — one new HttpClient method (`post_file`) and one new CardResource method (`upload_file`). The two-layer architecture made it straightforward: transport concern (multipart upload) in HttpClient, business logic (file reading, MIME guessing, URL extraction) in CardResource.

2. **HttpClient.post_file as a reusable primitive**: Rather than doing the multipart upload directly in CardResource (like the Bundle does for its `/app/` upload), we added `post_file()` to HttpClient. This keeps the "all HTTP goes through HttpClient" contract intact and makes the method reusable if other endpoints need file uploads in the future.

3. **stdlib mimetypes module**: `mimetypes.guess_type()` handles MIME detection without any external dependency. Falls back to `application/octet-stream` for unknown extensions, which is safe for Guru's upload endpoint.

4. **Accepting both str and pathlib.Path**: The `upload_file(file_path: str | Path)` signature means callers can pass either type without conversion. Minor but eliminates friction.

## What We Learned

1. **Two non-public endpoints now documented**: With ADR-005 (contentupload) and ADR-006 (attachments/upload), we have a clear pattern for handling endpoints that work but aren't in the public Swagger spec. Both follow the same template: document why, note it in the docstring, and move on.

2. **Bundle bypasses HttpClient for uploads**: The Bundle's `upload()` method hits the httpx client directly (because `/app/` routes aren't relative to the API base URL). Card attachments go through HttpClient normally (because `/attachments/upload` IS under `/api/v1/`). This inconsistency is acceptable — different URL structures require different approaches.

## Patterns for Future Iterations

- **File upload follows the same pattern**: `post_file()` → multipart POST → parse JSON response. If Guru adds more upload endpoints, they can reuse this method.
- **ADR template for non-public endpoints**: Context (what it does), Decision (use it anyway), Why (no alternative, stable, customer dependency), Consequences (works, with caveat).
