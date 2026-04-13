# Iteration 015 — Publisher (Folder-Based Content Sync) — Learnings

## What Worked

1. **Frozen dataclass for CardChanges**: Using `@dataclass(frozen=True)` for `CardChanges` made it immutable and hashable — good for a value object that represents a snapshot of what changed. The `needs_publishing()` method on the dataclass is a clean way to encapsulate the "anything changed?" logic without spreading that check across callers.

2. **Abstract base class with optional hooks**: Making folder/collection hooks optional (empty methods with `# noqa: B027`) while keeping card hooks abstract was the right split. Most publisher implementations only care about cards — forcing subclasses to implement folder and collection hooks would be needless boilerplate. The `find_external_*` hooks follow the same optional pattern for pre-existing content discovery.

3. **Explicit save_metadata() over auto-save**: The legacy SDK auto-saved metadata on every change. Making it explicit gives callers control — useful for dry-run mode, batch operations, and testing. Callers call `save_metadata()` when they're ready, not after every card.

4. **Metadata as visited-set pattern**: Using a `_visited` set during publish runs, then diffing against metadata keys in `process_deletions()`, is a clean way to detect removed items without needing a separate "before" snapshot. The set is cleared at the start of each `publish_collection()` call.

5. **Timestamp comparison via .isoformat()**: Standardizing on `datetime.isoformat()` for both storage and comparison eliminated format mismatches between Pydantic's string representation and what we stored in metadata.

## What We Learned

1. **Pydantic models don't pre-load relationships**: The legacy SDK's Card objects had `.folders` and `.tags` properties that were pre-loaded. Our Pydantic models are pure data — folder and tag lists require separate API calls (`g.cards.list_folders()`, `g.cards.list_tags()`). The publisher bridges this by fetching them explicitly in `_compute_card_changes()`. This is more explicit but chattier.

2. **str() vs .isoformat() on datetimes**: `str(datetime_obj)` produces `"2026-04-13 12:00:00+00:00"` (space separator) while `.isoformat()` produces `"2026-04-13T12:00:00+00:00"` (T separator). The legacy API returns ISO format with T, so `.isoformat()` is the right choice for consistent comparison.

3. **ruff B027 for intentionally empty methods**: Empty methods in an ABC that aren't `@abstractmethod` trigger B027. This is correct — it's warning that subclasses might forget to override. For our optional hooks, the empty body IS the intended default. `# noqa: B027` is the right suppression, not making them abstract.

4. **Link rewriting is HTML string manipulation**: The `_rewrite_guru_links()` method uses `html.parser` to find cross-card links, then does string replacement to convert Guru URLs to external URLs via the `get_external_url()` hook. This keeps the BeautifulSoup dependency out while handling the common case of `<a href="https://app.getguru.com/card/...">` links.

## What We'd Do Differently

1. **Consider a Protocol instead of ABC**: A `Publisher` Protocol (PEP 544) would allow duck-typing instead of requiring inheritance. However, the ABC approach matches the legacy SDK and is more familiar to users porting existing publisher implementations. Worth revisiting if we see demand.

2. **Batch folder/tag fetching**: Currently `_compute_card_changes()` makes 2 extra API calls per card (list_folders + list_tags). A future optimization could batch these if the API supports it, or cache them during a publish run.

## Patterns for Future Iterations

- **Frozen dataclasses for change tracking**: `CardChanges` pattern works well — immutable, with a predicate method. Reuse this for any "what changed?" detection.
- **Visited-set deletion pattern**: Track what was seen during a walk, then diff against known state to find deletions. Cleaner than snapshot-compare.
- **Optional ABC hooks via empty methods**: Use `# noqa: B027` for hooks that have sensible defaults (no-op). Only make hooks `@abstractmethod` when subclasses MUST implement them.
- **pathlib for metadata persistence**: `Path.read_text()` / `Path.write_text()` is cleaner than open/read/write for simple JSON files.
