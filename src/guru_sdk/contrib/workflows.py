"""Convenience workflows — multi-step operations composed from resource calls.

These functions are not methods on the Guru client. They live in contrib/
to keep the core SDK lean. Each function takes a Guru client as its first
argument and composes multiple resource calls into a single logical operation.

Usage::

    from guru_sdk import Guru
    from guru_sdk.contrib.workflows import move_card_between_folders

    g = Guru()
    move_card_between_folders(g, card_id, src_folder, dst_folder)
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from guru_sdk.errors import NotFoundError

if TYPE_CHECKING:
    from guru_sdk.client import Guru
    from guru_sdk.models._generated import CollectionModel, Folder, Tag

# =============================================================================
# Card Workflows
# =============================================================================


def move_card_between_folders(
    g: Guru,
    card_id: str,
    source_folder_id: str,
    target_folder_id: str,
) -> Folder:
    """Remove a card from one folder and add it to another.

    This is a two-step operation: remove from source, then add to target.
    If the remove fails, the add is not attempted. Arguments are passed
    through to the underlying resource methods, so names work as well as UUIDs.

    Args:
        g: Guru client instance.
        card_id: Card UUID or slug.
        source_folder_id: Source folder UUID or slug.
        target_folder_id: Target folder UUID or slug.

    Returns:
        The target Folder object (from the add_to_folder response).

    Raises:
        NotFoundError: If the card or either folder is not found.
    """
    # Remove first — if this fails, we don't want to add to the target
    g.cards.remove_from_folder(card_id, source_folder_id)
    return g.cards.add_to_folder(card_id, target_folder_id)


# =============================================================================
# Tag Workflows
# =============================================================================


def add_tag_with_auto_create(
    g: Guru,
    card_id: str,
    tag_value: str,
    category_id: str,
) -> Tag:
    """Add a tag to a card, creating the tag first if it doesn't exist.

    Looks up the tag by name. If not found, creates it in the specified
    category, then adds it to the card.

    Args:
        g: Guru client instance.
        card_id: Card UUID or slug.
        tag_value: Tag display value (e.g., "important").
        category_id: Tag category UUID — used only if the tag needs to be created.

    Returns:
        The Tag object (existing or newly created).
    """
    # Try to find the tag by name
    try:
        tag = g.tags.get_tag(tag_value)
    except NotFoundError:
        # Tag doesn't exist — create it in the specified category
        tag = g.tags.create_tag(category_id=category_id, value=tag_value)

    # Add the tag to the card — tag.id is guaranteed non-None after get or create
    if tag.id is None:
        msg = f"Tag '{tag_value}' has no ID after lookup/creation."
        raise NotFoundError(msg)
    g.cards.add_tag(card_id, tag.id)
    return tag


# =============================================================================
# Group & Member Workflows
# =============================================================================


def batch_add_users_to_group(
    g: Guru,
    group_id: str,
    emails: list[str],
) -> dict[str, bool]:
    """Add many users to a single group, batching in groups of 100.

    Mirrors the legacy py-sdk behavior: sends emails in batches of up to 100.
    When a batch fails, retries with progressively smaller batch sizes until
    batch_size reaches 1. Failed emails at batch_size=1 are marked as failed.

    Args:
        g: Guru client instance.
        group_id: Group UUID or name.
        emails: List of email addresses to add.

    Returns:
        Dict mapping each email to True (success) or False (failure).
    """
    if not emails:
        return {}

    results: dict[str, bool] = {}
    batch_size = 100
    # Work on a mutable copy so we can retry failed batches
    remaining = list(emails)

    while remaining:
        failed_emails: list[str] = []

        # Process remaining emails in chunks of batch_size
        for i in range(0, len(remaining), batch_size):
            batch = remaining[i : i + batch_size]
            try:
                g.groups.add_members(group_id, emails=batch)
                # Whole batch succeeded
                for email in batch:
                    results[email] = True
            except Exception:
                # Whole batch failed — collect for retry
                failed_emails.extend(batch)
                for email in batch:
                    results[email] = False

        # If nothing failed, we're done
        if not failed_emails:
            break

        # If we were already at batch_size=1 and still failing, give up
        if batch_size == 1:
            break

        # Reduce batch size for retry — same halving strategy as legacy py-sdk
        if batch_size >= len(failed_emails):
            batch_size = max(len(failed_emails) // 5, 1)
        else:
            batch_size = max(batch_size // 2, 1)

        # Reset results for failed emails — they'll get a fresh chance
        for email in failed_emails:
            results[email] = False

        remaining = failed_emails

    return results


def add_user_to_groups(
    g: Guru,
    email: str,
    group_ids: list[str],
) -> dict[str, bool]:
    """Add a single user to multiple groups.

    Makes one add_members call per group. Failures are captured in the
    result dict — they don't stop processing of remaining groups.

    Args:
        g: Guru client instance.
        email: Email address of the user to add.
        group_ids: List of group UUIDs or names.

    Returns:
        Dict mapping each group_id to True (success) or False (failure).
    """
    results: dict[str, bool] = {}

    for group_id in group_ids:
        try:
            g.groups.add_members(group_id, emails=[email])
            results[group_id] = True
        except Exception:
            results[group_id] = False

    return results


def remove_user_from_groups(
    g: Guru,
    email: str,
    group_ids: list[str],
) -> dict[str, bool]:
    """Remove a single user from multiple groups.

    Makes one remove_member call per group. Failures are captured in the
    result dict — they don't stop processing of remaining groups.

    Args:
        g: Guru client instance.
        email: Email address of the user to remove.
        group_ids: List of group UUIDs or names.

    Returns:
        Dict mapping each group_id to True (success) or False (failure).
    """
    results: dict[str, bool] = {}

    for group_id in group_ids:
        try:
            g.groups.remove_member(group_id, email=email)
            results[group_id] = True
        except Exception:
            results[group_id] = False

    return results


# =============================================================================
# Collection Workflows
# =============================================================================


def make_collection_with_setup(
    g: Guru,
    *,
    name: str,
    group_id: str | None,
    role: str,
    description: str | None = None,
    color: str | None = None,
) -> CollectionModel:
    """Create a collection and optionally add a group with a specific role.

    A common two-step operation: create the collection, then grant a group
    access to it. If group_id is None, only the collection is created.

    Args:
        g: Guru client instance.
        name: Collection name.
        group_id: Group UUID to add as initial accessor, or None to skip.
        role: Role for the group (e.g., "COLL_ADMIN", "AUTHOR", "MEMBER").
        description: Optional collection description.
        color: Optional hex color (e.g., "#4A90D9").

    Returns:
        The newly created CollectionModel.
    """
    collection = g.collections.create(
        name=name, description=description, color=color
    )

    # Add group access if a group was specified
    if group_id is not None:
        if collection.id is None:
            msg = f"Collection '{name}' has no ID after creation."
            raise NotFoundError(msg)
        g.collections.add_group(collection.id, group_id, role=role)

    return collection


# =============================================================================
# Folder Hierarchy Workflows
# =============================================================================


def dump_folder_hierarchy(
    g: Guru,
    collection_id: str,
    *,
    path: str | None = None,
    output_dir: str | None = None,
) -> str:
    """Recursively walk a collection's folder tree and write it to CSV.

    Each row represents a folder, with columns showing the parent chain
    (e.g., ["Engineering", "Onboarding", "Week 1"]). Cards are skipped —
    only folders appear in the output.

    Args:
        g: Guru client instance.
        collection_id: Collection UUID or name.
        path: Explicit output file path. If None, auto-generates from
              the home folder title.
        output_dir: Directory for auto-generated filenames. Defaults to
                    current working directory. Ignored if path is set.

    Returns:
        The path to the created CSV file.
    """
    # Get the home folder for the collection
    home = g.collections.home_folder(collection_id)

    # Determine output path
    if path is None:
        title = home.title or "collection"
        filename = f"{title}_folder_hierarchy.csv"
        if output_dir:
            import os

            path = os.path.join(output_dir, filename)
        else:
            path = filename

    # Write the CSV by recursively walking the folder tree
    with open(path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
        _walk_folder_items(g, home.id or "", writer, parent_chain=[])

    return path


def _walk_folder_items(
    g: Guru,
    folder_id: str,
    writer: Any,  # csv.writer returns _csv._writer which isn't a public type
    parent_chain: list[str],
) -> None:
    """Recursively walk folder items, writing folder paths to CSV.

    For each sub-folder found in items(), writes its parent chain to CSV
    and recurses into it. Cards are skipped.
    """
    from guru_sdk.models._generated import Type9

    items = g.folders.items(folder_id)

    for item in items:
        # Only process folders, skip cards
        if item.type != Type9.folder:
            continue

        # item.id is the actual folder UUID; item.item_id is the placement UUID
        sub_folder_id = item.id
        if sub_folder_id is None:
            continue

        sub_folder = g.folders.get(sub_folder_id)
        title = sub_folder.title or sub_folder_id

        # Build the chain and write to CSV
        current_chain = [*parent_chain, title]
        writer.writerow(current_chain)

        # Recurse into sub-folder
        _walk_folder_items(g, sub_folder_id, writer, current_chain)


# =============================================================================
# Bulk Content Edits
# =============================================================================


@dataclass(frozen=True)
class CardReplaceResult:
    """Per-card outcome from :func:`replace_text_in_collection_cards`.

    Attributes:
        card_id: The card's UUID.
        title: The card's preferred phrase (display title), if known.
        status: One of ``"updated"``, ``"unchanged"``, ``"would_update"``
            (dry-run hit), or ``"failed"``.
        error: Error message when ``status == "failed"``, otherwise None.
    """

    card_id: str
    title: str
    status: str
    error: str | None = None


def replace_text_in_collection_cards(
    g: Guru,
    collection_id: str,
    old_text: str,
    new_text: str,
    *,
    dry_run: bool = False,
    case_sensitive: bool = True,
    keep_verification: bool = True,
) -> list[CardReplaceResult]:
    """Replace a text string in every card in a collection.

    Walks the collection's folder hierarchy starting at the home folder and,
    for each card it finds, replaces all occurrences of ``old_text`` with
    ``new_text``. Cards that don't contain the text are reported as
    ``"unchanged"`` and not patched. Errors fetching or patching an individual
    card are captured in the returned list — they don't stop the walk.

    Replacement is delegated to :func:`guru_sdk.contrib.content.replace_text`,
    which operates on the raw HTML string (matches in both visible text and
    attribute values).

    Updates use :meth:`Guru.cards.patch`, which preserves verification state
    by default (``keep_verification=True``). Pass ``keep_verification=False``
    to trigger re-verification for every modified card.

    Args:
        g: Guru client instance.
        collection_id: Collection UUID or name.
        old_text: Text to find. Must be non-empty.
        new_text: Replacement text.
        dry_run: If True, walk the collection and report ``"would_update"``
            for cards containing the text, but issue no PATCH calls.
        case_sensitive: If False, match regardless of case.
        keep_verification: Forwarded to :meth:`Guru.cards.patch`.

    Returns:
        A :class:`CardReplaceResult` per card visited (cards that appear in
        multiple folders are visited only once).

    Raises:
        ValueError: If ``old_text`` is empty.
        NotFoundError: If the collection has no home folder / does not exist.
    """
    if not old_text:
        msg = "old_text must not be empty"
        raise ValueError(msg)

    home = g.collections.home_folder(collection_id)

    results: list[CardReplaceResult] = []
    visited: set[str] = set()
    _replace_text_walk(
        g,
        home.id or "",
        old_text=old_text,
        new_text=new_text,
        dry_run=dry_run,
        case_sensitive=case_sensitive,
        keep_verification=keep_verification,
        results=results,
        visited=visited,
    )
    return results


def _replace_text_walk(
    g: Guru,
    folder_id: str,
    *,
    old_text: str,
    new_text: str,
    dry_run: bool,
    case_sensitive: bool,
    keep_verification: bool,
    results: list[CardReplaceResult],
    visited: set[str],
) -> None:
    """Recursively walk a folder, processing each card it finds."""
    from guru_sdk.contrib.content import replace_text
    from guru_sdk.models._generated import Type9

    items = g.folders.items(folder_id)

    for item in items:
        item_id = item.id
        if item_id is None:
            continue

        if item.type == Type9.folder:
            _replace_text_walk(
                g,
                item_id,
                old_text=old_text,
                new_text=new_text,
                dry_run=dry_run,
                case_sensitive=case_sensitive,
                keep_verification=keep_verification,
                results=results,
                visited=visited,
            )
            continue

        if item.type != Type9.card:
            continue

        # Cards can appear in multiple folders — only process each once.
        if item_id in visited:
            continue
        visited.add(item_id)

        try:
            card = g.cards.get(item_id)
            content = card.content or ""
            modified_content, changed = replace_text(
                content,
                old_text,
                new_text,
                case_sensitive=case_sensitive,
            )
            title = card.preferred_phrase or ""

            if not changed:
                results.append(
                    CardReplaceResult(
                        card_id=item_id, title=title, status="unchanged"
                    )
                )
                continue

            if dry_run:
                results.append(
                    CardReplaceResult(
                        card_id=item_id, title=title, status="would_update"
                    )
                )
                continue

            g.cards.patch(
                item_id,
                content=modified_content,
                keep_verification=keep_verification,
            )
            results.append(
                CardReplaceResult(card_id=item_id, title=title, status="updated")
            )
        except Exception as exc:
            results.append(
                CardReplaceResult(
                    card_id=item_id,
                    title="",
                    status="failed",
                    error=str(exc),
                )
            )
