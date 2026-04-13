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

from typing import TYPE_CHECKING

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
