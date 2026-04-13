"""Tests for guru_sdk.contrib.workflows — convenience workflows.

TDD tests covering all six workflow functions:
- move_card_between_folders — remove from source + add to target
- batch_add_users_to_group — batch emails in groups of 100, retry failures
- add_user_to_groups — add one email to multiple groups
- remove_user_from_groups — remove one email from multiple groups
- make_collection_with_setup — create collection + add group access
- add_tag_with_auto_create — add tag to card, creating if not found
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from guru_sdk.errors import NotFoundError
from guru_sdk.models._generated import (
    CollectionModel,
    Folder,
    Tag,
    UserGroupAccess,
)

# =============================================================================
# Test Data
# =============================================================================

CARD_UUID = "c1c1c1c1-c1c1-c1c1-c1c1-c1c1c1c1c1c1"
FOLDER_SRC = "f1f1f1f1-f1f1-f1f1-f1f1-f1f1f1f1f1f1"
FOLDER_DST = "f2f2f2f2-f2f2-f2f2-f2f2-f2f2f2f2f2f2"
GROUP_UUID = "g1g1g1g1-g1g1-g1g1-g1g1-g1g1g1g1g1g1"
GROUP_UUID_2 = "g2g2g2g2-g2g2-g2g2-g2g2-g2g2g2g2g2g2"
GROUP_UUID_3 = "g3g3g3g3-g3g3-g3g3-g3g3-g3g3g3g3g3g3"
COLL_UUID = "d1d1d1d1-d1d1-d1d1-d1d1-d1d1d1d1d1d1"
TAG_UUID = "t1t1t1t1-t1t1-t1t1-t1t1-t1t1t1t1t1t1"
CAT_UUID = "e1e1e1e1-e1e1-e1e1-e1e1-e1e1e1e1e1e1"


def _make_guru_mock() -> MagicMock:
    """Create a mock Guru client with mock resource attributes."""
    g = MagicMock()
    # Set up resource attributes so they're accessible as g.cards, g.groups, etc.
    g.cards = MagicMock()
    g.groups = MagicMock()
    g.collections = MagicMock()
    g.tags = MagicMock()
    g.folders = MagicMock()
    return g


def _make_folder(folder_id: str = FOLDER_DST) -> Folder:
    """Build a minimal Folder model for return values."""
    return Folder.model_validate(
        {
            "id": folder_id,
            "title": "Target Folder",
            "slug": "target-folder-abc",
            "home": False,
        }
    )


def _make_collection(coll_id: str = COLL_UUID) -> CollectionModel:
    """Build a minimal CollectionModel for return values."""
    return CollectionModel.model_validate(
        {
            "id": coll_id,
            "name": "Engineering",
            "color": "#4A90D9",
        }
    )


def _make_tag(tag_id: str = TAG_UUID, value: str = "important") -> Tag:
    """Build a minimal Tag model for return values."""
    return Tag.model_validate(
        {
            "id": tag_id,
            "value": value,
        }
    )


def _make_group_access(
    group_id: str = GROUP_UUID,
    role: str = "COLL_ADMIN",
) -> UserGroupAccess:
    """Build a minimal UserGroupAccess for return values."""
    return UserGroupAccess.model_validate(
        {
            "groupId": group_id,
            "role": role,
        }
    )


# =============================================================================
# move_card_between_folders
# =============================================================================


class TestMoveCardBetweenFolders:
    """move_card_between_folders(g, card_id, source_folder_id, target_folder_id)."""

    def test_happy_path(self) -> None:
        """Remove card from source, add to target, return target folder."""
        from guru_sdk.contrib.workflows import move_card_between_folders

        g = _make_guru_mock()
        g.cards.remove_from_folder.return_value = None
        g.cards.add_to_folder.return_value = _make_folder(FOLDER_DST)

        result = move_card_between_folders(g, CARD_UUID, FOLDER_SRC, FOLDER_DST)

        g.cards.remove_from_folder.assert_called_once_with(CARD_UUID, FOLDER_SRC)
        g.cards.add_to_folder.assert_called_once_with(CARD_UUID, FOLDER_DST)
        assert result.id == FOLDER_DST

    def test_remove_failure_does_not_add(self) -> None:
        """If remove fails, don't attempt the add — let the exception propagate."""
        from guru_sdk.contrib.workflows import move_card_between_folders

        g = _make_guru_mock()
        g.cards.remove_from_folder.side_effect = NotFoundError("Card not in folder")

        with pytest.raises(NotFoundError, match="Card not in folder"):
            move_card_between_folders(g, CARD_UUID, FOLDER_SRC, FOLDER_DST)

        g.cards.add_to_folder.assert_not_called()

    def test_accepts_names_not_just_uuids(self) -> None:
        """Arguments are passed through to resource methods — names work too."""
        from guru_sdk.contrib.workflows import move_card_between_folders

        g = _make_guru_mock()
        g.cards.remove_from_folder.return_value = None
        g.cards.add_to_folder.return_value = _make_folder()

        move_card_between_folders(g, "my-card-slug", "Source Folder", "Target Folder")

        g.cards.remove_from_folder.assert_called_once_with("my-card-slug", "Source Folder")
        g.cards.add_to_folder.assert_called_once_with("my-card-slug", "Target Folder")


# =============================================================================
# batch_add_users_to_group
# =============================================================================


class TestBatchAddUsersToGroup:
    """batch_add_users_to_group(g, group_id, emails)."""

    def test_small_batch_single_call(self) -> None:
        """Fewer than 100 emails → single add_members call."""
        from guru_sdk.contrib.workflows import batch_add_users_to_group

        g = _make_guru_mock()
        g.groups.add_members.return_value = None

        emails = [f"user{i}@example.com" for i in range(10)]
        result = batch_add_users_to_group(g, GROUP_UUID, emails)

        g.groups.add_members.assert_called_once_with(
            GROUP_UUID, emails=emails
        )
        # All should be marked successful
        assert all(result[e] for e in emails)
        assert len(result) == 10

    def test_large_batch_splits_at_100(self) -> None:
        """250 emails → 3 batches (100 + 100 + 50)."""
        from guru_sdk.contrib.workflows import batch_add_users_to_group

        g = _make_guru_mock()
        g.groups.add_members.return_value = None

        emails = [f"user{i}@example.com" for i in range(250)]
        result = batch_add_users_to_group(g, GROUP_UUID, emails)

        assert g.groups.add_members.call_count == 3
        assert len(result) == 250
        assert all(result[e] for e in emails)

    def test_failed_batch_retries_with_smaller_size(self) -> None:
        """When a batch fails, retry its emails with a smaller batch size."""
        from guru_sdk.contrib.workflows import batch_add_users_to_group

        g = _make_guru_mock()
        emails = [f"user{i}@example.com" for i in range(5)]

        # First call fails, subsequent calls succeed
        call_count = 0

        def side_effect(group_id: str, *, emails: list[str]) -> None:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("API error — batch too large")

        g.groups.add_members.side_effect = side_effect

        result = batch_add_users_to_group(g, GROUP_UUID, emails)

        # First call failed for all 5, retries should happen with smaller batches
        assert g.groups.add_members.call_count > 1
        # The retried emails should succeed
        assert any(result[e] for e in emails)

    def test_empty_list_returns_empty_dict(self) -> None:
        """Empty email list → no API calls, empty result."""
        from guru_sdk.contrib.workflows import batch_add_users_to_group

        g = _make_guru_mock()
        result = batch_add_users_to_group(g, GROUP_UUID, [])

        g.groups.add_members.assert_not_called()
        assert result == {}

    def test_all_retries_exhausted(self) -> None:
        """When retries reach batch_size=1 and still fail, mark as failed."""
        from guru_sdk.contrib.workflows import batch_add_users_to_group

        g = _make_guru_mock()
        g.groups.add_members.side_effect = Exception("Permanent failure")

        emails = ["bad@example.com"]
        result = batch_add_users_to_group(g, GROUP_UUID, emails)

        assert result["bad@example.com"] is False


# =============================================================================
# add_user_to_groups
# =============================================================================


class TestAddUserToGroups:
    """add_user_to_groups(g, email, group_ids)."""

    def test_happy_path(self) -> None:
        """Add email to two groups — both succeed."""
        from guru_sdk.contrib.workflows import add_user_to_groups

        g = _make_guru_mock()
        g.groups.add_members.return_value = None

        result = add_user_to_groups(
            g, "alice@example.com", [GROUP_UUID, GROUP_UUID_2]
        )

        assert g.groups.add_members.call_count == 2
        assert result[GROUP_UUID] is True
        assert result[GROUP_UUID_2] is True

    def test_partial_failure(self) -> None:
        """One group add succeeds, the other fails."""
        from guru_sdk.contrib.workflows import add_user_to_groups

        g = _make_guru_mock()

        def side_effect(group_id: str, *, emails: list[str]) -> None:
            if group_id == GROUP_UUID_2:
                raise Exception("Group full")

        g.groups.add_members.side_effect = side_effect

        result = add_user_to_groups(
            g, "alice@example.com", [GROUP_UUID, GROUP_UUID_2]
        )

        assert result[GROUP_UUID] is True
        assert result[GROUP_UUID_2] is False

    def test_empty_groups_returns_empty(self) -> None:
        """Empty group list → no API calls, empty result."""
        from guru_sdk.contrib.workflows import add_user_to_groups

        g = _make_guru_mock()
        result = add_user_to_groups(g, "alice@example.com", [])

        g.groups.add_members.assert_not_called()
        assert result == {}

    def test_single_group(self) -> None:
        """Single group — result keyed by that group ID."""
        from guru_sdk.contrib.workflows import add_user_to_groups

        g = _make_guru_mock()
        g.groups.add_members.return_value = None

        result = add_user_to_groups(g, "alice@example.com", [GROUP_UUID])

        g.groups.add_members.assert_called_once_with(
            GROUP_UUID, emails=["alice@example.com"]
        )
        assert result == {GROUP_UUID: True}


# =============================================================================
# remove_user_from_groups
# =============================================================================


class TestRemoveUserFromGroups:
    """remove_user_from_groups(g, email, group_ids)."""

    def test_happy_path(self) -> None:
        """Remove email from two groups — both succeed."""
        from guru_sdk.contrib.workflows import remove_user_from_groups

        g = _make_guru_mock()
        g.groups.remove_member.return_value = None

        result = remove_user_from_groups(
            g, "alice@example.com", [GROUP_UUID, GROUP_UUID_2]
        )

        assert g.groups.remove_member.call_count == 2
        assert result[GROUP_UUID] is True
        assert result[GROUP_UUID_2] is True

    def test_partial_failure(self) -> None:
        """One removal succeeds, the other fails."""
        from guru_sdk.contrib.workflows import remove_user_from_groups

        g = _make_guru_mock()

        def side_effect(group_id: str, *, email: str) -> None:
            if group_id == GROUP_UUID_2:
                raise NotFoundError("Not a member")

        g.groups.remove_member.side_effect = side_effect

        result = remove_user_from_groups(
            g, "alice@example.com", [GROUP_UUID, GROUP_UUID_2]
        )

        assert result[GROUP_UUID] is True
        assert result[GROUP_UUID_2] is False

    def test_empty_groups_returns_empty(self) -> None:
        """Empty group list → no API calls."""
        from guru_sdk.contrib.workflows import remove_user_from_groups

        g = _make_guru_mock()
        result = remove_user_from_groups(g, "alice@example.com", [])

        g.groups.remove_member.assert_not_called()
        assert result == {}


# =============================================================================
# make_collection_with_setup
# =============================================================================


class TestMakeCollectionWithSetup:
    """make_collection_with_setup(g, name, group_id, role, ...)."""

    def test_happy_path(self) -> None:
        """Creates collection and adds group access."""
        from guru_sdk.contrib.workflows import make_collection_with_setup

        g = _make_guru_mock()
        coll = _make_collection()
        g.collections.create.return_value = coll
        g.collections.add_group.return_value = _make_group_access()

        result = make_collection_with_setup(
            g,
            name="Engineering",
            group_id=GROUP_UUID,
            role="COLL_ADMIN",
        )

        g.collections.create.assert_called_once_with(
            name="Engineering", description=None, color=None
        )
        g.collections.add_group.assert_called_once_with(
            COLL_UUID, GROUP_UUID, role="COLL_ADMIN"
        )
        assert result.id == COLL_UUID

    def test_with_optional_fields(self) -> None:
        """Passes description and color through to create."""
        from guru_sdk.contrib.workflows import make_collection_with_setup

        g = _make_guru_mock()
        coll = _make_collection()
        g.collections.create.return_value = coll
        g.collections.add_group.return_value = _make_group_access()

        make_collection_with_setup(
            g,
            name="Docs",
            group_id=GROUP_UUID,
            role="AUTHOR",
            description="Documentation collection",
            color="#FF5733",
        )

        g.collections.create.assert_called_once_with(
            name="Docs", description="Documentation collection", color="#FF5733"
        )

    def test_create_failure_does_not_add_group(self) -> None:
        """If collection creation fails, don't try to add the group."""
        from guru_sdk.contrib.workflows import make_collection_with_setup

        g = _make_guru_mock()
        g.collections.create.side_effect = Exception("Name taken")

        with pytest.raises(Exception, match="Name taken"):
            make_collection_with_setup(
                g, name="Duplicate", group_id=GROUP_UUID, role="COLL_ADMIN"
            )

        g.collections.add_group.assert_not_called()

    def test_no_group_id_skips_add_group(self) -> None:
        """If group_id is None, just create the collection without group setup."""
        from guru_sdk.contrib.workflows import make_collection_with_setup

        g = _make_guru_mock()
        coll = _make_collection()
        g.collections.create.return_value = coll

        result = make_collection_with_setup(
            g, name="Standalone", group_id=None, role="COLL_ADMIN"
        )

        g.collections.create.assert_called_once()
        g.collections.add_group.assert_not_called()
        assert result.id == COLL_UUID


# =============================================================================
# add_tag_with_auto_create
# =============================================================================


class TestAddTagWithAutoCreate:
    """add_tag_with_auto_create(g, card_id, tag_value, category_id)."""

    def test_tag_exists_adds_directly(self) -> None:
        """Tag found by name → use it directly, no creation."""
        from guru_sdk.contrib.workflows import add_tag_with_auto_create

        g = _make_guru_mock()
        existing_tag = _make_tag(TAG_UUID, "important")
        g.tags.get_tag.return_value = existing_tag
        g.cards.add_tag.return_value = [existing_tag]

        result = add_tag_with_auto_create(
            g, CARD_UUID, "important", CAT_UUID
        )

        g.tags.get_tag.assert_called_once_with("important")
        g.tags.create_tag.assert_not_called()
        g.cards.add_tag.assert_called_once_with(CARD_UUID, TAG_UUID)
        assert result.id == TAG_UUID

    def test_tag_not_found_creates_then_adds(self) -> None:
        """Tag not found → create it in category, then add to card."""
        from guru_sdk.contrib.workflows import add_tag_with_auto_create

        g = _make_guru_mock()
        g.tags.get_tag.side_effect = NotFoundError("No tag 'urgent'")
        new_tag = _make_tag(TAG_UUID, "urgent")
        g.tags.create_tag.return_value = new_tag
        g.cards.add_tag.return_value = [new_tag]

        result = add_tag_with_auto_create(
            g, CARD_UUID, "urgent", CAT_UUID
        )

        g.tags.get_tag.assert_called_once_with("urgent")
        g.tags.create_tag.assert_called_once_with(
            category_id=CAT_UUID, value="urgent"
        )
        g.cards.add_tag.assert_called_once_with(CARD_UUID, TAG_UUID)
        assert result.id == TAG_UUID

    def test_creation_failure_propagates(self) -> None:
        """If tag creation fails, the error propagates — no add_tag call."""
        from guru_sdk.contrib.workflows import add_tag_with_auto_create

        g = _make_guru_mock()
        g.tags.get_tag.side_effect = NotFoundError("Not found")
        g.tags.create_tag.side_effect = Exception("Category not found")

        with pytest.raises(Exception, match="Category not found"):
            add_tag_with_auto_create(g, CARD_UUID, "broken", CAT_UUID)

        g.cards.add_tag.assert_not_called()

    def test_returns_tag_object(self) -> None:
        """Always returns the Tag object (whether existing or newly created)."""
        from guru_sdk.contrib.workflows import add_tag_with_auto_create

        g = _make_guru_mock()
        tag = _make_tag(TAG_UUID, "review")
        g.tags.get_tag.return_value = tag
        g.cards.add_tag.return_value = [tag]

        result = add_tag_with_auto_create(g, CARD_UUID, "review", CAT_UUID)

        assert result.value == "review"
        assert result.id == TAG_UUID
