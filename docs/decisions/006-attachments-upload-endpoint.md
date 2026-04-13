# ADR-006: Using the /attachments/upload Endpoint for File Uploads

## Context

Card content in Guru can reference uploaded files (images, PDFs, etc.) via URLs. The legacy py-sdk provides `upload_file()` which uploads a file and returns a URL that can be embedded in card HTML.

The endpoint is:

- `POST https://api.getguru.com/api/v1/attachments/upload` — multipart file upload
- Request: multipart form with field name `file` containing `(filename, file_bytes, mimetype)`
- Response: `{"attachmentId": "...", "link": "https://content.api.getguru.com/files/view/...", "filename": "...", "mimeType": "...", "size": ...}`

This endpoint is **not in the public Swagger spec** (`/api/v1/swagger.json`). However, it lives under `/api/v1/` (unlike the Bundle's `/app/` routes), uses the same auth, and has been stable in the legacy SDK for years.

## Decision

We will use the `/api/v1/attachments/upload` endpoint in `CardResource.upload_file()`. This is the same pattern as ADR-005 (contentupload) — a stable, functional endpoint that isn't in the public spec.

### Why

1. **No alternative exists**: There is no other way to programmatically upload files for use in card content.
2. **Stable and widely used**: The legacy py-sdk has used this endpoint since early versions. Customers depend on it for image uploads, PDF attachments, etc.
3. **Same auth, same base URL**: Unlike the Bundle's `/app/` routes, this endpoint lives at `/api/v1/` and behaves like any other API endpoint — just missing from the Swagger spec.
4. **Essential for content migration**: Without file upload, any migration that involves images or attachments would be incomplete.

## Consequences

- `CardResource.upload_file()` works as expected for customers migrating from the legacy py-sdk.
- The method's docstring notes that this endpoint is not in the public Swagger spec.
- If Guru adds this to the public spec, no code changes are needed — just remove the disclaimer.
