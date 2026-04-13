# ADR-005: Using the /app/contentupload Endpoint for Bundle Imports

## Context

The Bundle system generates a zip file containing YAML metadata and HTML content for bulk import into Guru. The legacy py-sdk uploads this zip via two endpoints:

- `POST https://api.getguru.com/app/contentupload?collectionId={id}` — one-time import (adds content to a collection)
- `POST https://api.getguru.com/app/contentsyncupload?collectionId={id}` — sync (replaces collection content)

Both are multipart file uploads. The import uses field name `contentFile`, the sync uses field name `file`.

These endpoints live under `/app/`, not `/api/v1/`. They do **not** appear in the public Swagger spec (`/api/v1/swagger.json`). However, they are documented in Guru's developer documentation and are the only mechanism for zip-based content import — there is no `/api/v1/` equivalent.

## Decision

We will use the `/app/contentupload` and `/app/contentsyncupload` endpoints in the Bundle implementation. This is a known deviation from our rule that all CLI/SDK commands must use the public API only.

### Why

1. **No alternative exists**: There is no public API endpoint for zip-based content import. The only way to do bulk import is through these `/app/` routes.
2. **Documented and stable**: These endpoints are documented in Guru's developer docs and have been stable for years. The legacy py-sdk has used them since the Bundle feature was first created.
3. **Customer dependency**: Existing py-sdk customers rely on Bundle for content migrations. Dropping upload support would make the port significantly less useful.
4. **Authentication works**: These endpoints accept the same basic auth (email + API token) as the `/api/v1/` endpoints.

### Mitigation

- The `upload()` method's docstring will note that this uses an `/app/` endpoint not in the public Swagger spec.
- If Guru adds a public API equivalent in the future, we will migrate to it.
- The Bundle's zip generation (the `zip()` method) is independently useful even without `upload()` — customers can upload manually through the Guru UI.

## Consequences

- Bundle upload works as expected for customers migrating from the legacy py-sdk.
- We accept the risk that `/app/` endpoints could change without notice, though historically they have been stable.
- The zip generation layer has no dependency on these endpoints — it's pure file I/O. Only `upload()` touches the non-public route.
