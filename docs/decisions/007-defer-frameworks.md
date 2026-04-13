# ADR-007: Defer Frameworks Resource

## Context

The backlog (iteration 021) planned a `FrameworkResource` with three methods: `list`, `get`, and `import_framework`. Frameworks are collection templates — importing one creates a new collection pre-populated with a folder/card structure.

Investigation revealed:

1. The `/frameworks` and `/frameworks/import/{id}` endpoints are **not in the public Swagger spec**.
2. The **guru-cli has no frameworks support** — no commands, no resource module, no references.
3. Only the legacy py-sdk implements these endpoints (`get_frameworks`, `get_framework`, `import_framework`).

## Decision

Defer the Frameworks resource. Do not implement it in the current SDK.

### Why

- **Not in public spec, not in CLI**: This is the only resource that would exist in the SDK but not the CLI, and without public API backing. The attachment upload (ADR-006) and content upload (ADR-005) are different — those are essential operations with no alternative. Frameworks have low usage and collections can be created through the normal `collections.create()` API.
- **Low customer demand**: Framework import is primarily a UI convenience (the "create collection from template" flow). Programmatic usage is rare.
- **Can be revisited**: If Guru adds frameworks to the public spec or the CLI, we can add the resource in a future iteration.

## Consequences

- Iteration 021 is removed from the active backlog.
- Customers who need framework import can use the legacy py-sdk or call the endpoint directly via httpx.
- The SDK's resource coverage remains aligned with the CLI and the public API spec.
