"""Tests for guru_sdk.contrib.workflows — convenience workflows.

TDD tests covering all workflow functions:
- move_card_between_folders — remove from source + add to target
- batch_add_users_to_group — batch emails in groups of 100, retry failures
- add_user_to_groups — add one email to multiple groups
- remove_user_from_groups — remove one email from multiple groups
- make_collection_with_setup — create collection + add group access
- add_tag_with_auto_create — add tag to card, creating if not found
- dump_folder_hierarchy — recursive folder tree → CSV
"""

from __future__ import annotations

import csv
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from guru_sdk.errors import NotFoundError
from guru_sdk.models._generated import (
    Card,
    CollectionModel,
    Folder,
    FolderItem,
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


# =============================================================================
# dump_folder_hierarchy
# =============================================================================

HOME_FOLDER_UUID = "h1h1h1h1-h1h1-h1h1-h1h1-h1h1h1h1h1h1"
SUB_FOLDER_UUID_1 = "s1s1s1s1-s1s1-s1s1-s1s1-s1s1s1s1s1s1"
SUB_FOLDER_UUID_2 = "s2s2s2s2-s2s2-s2s2-s2s2-s2s2s2s2s2s2"
SUB_SUB_FOLDER_UUID = "s3s3s3s3-s3s3-s3s3-s3s3-s3s3s3s3s3s3"


def _make_folder_item(item_id: str, entry_type: str = "folder") -> FolderItem:
    """Build a FolderItem (folder or card) for mocking items() responses.

    id = actual folder/card UUID (used by folders.get / cards.get)
    itemId = placement UUID (Guru's internal position reference — NOT used for lookups)
    These must be distinct so tests catch id vs item_id misuse (see SC-152729).
    """
    return FolderItem.model_validate(
        {"id": item_id, "itemId": f"placement-{item_id}", "type": entry_type}
    )


def _make_folder_obj(folder_id: str, title: str) -> Folder:
    """Build a Folder model for mocking get() responses."""
    return Folder.model_validate(
        {"id": folder_id, "title": title, "slug": f"slug-{folder_id}", "home": False}
    )


class TestDumpFolderHierarchy:
    """dump_folder_hierarchy(g, collection_id, path)."""

    def test_flat_folders(self, tmp_path: Path) -> None:
        """Collection with two top-level folders, no nesting."""
        from guru_sdk.contrib.workflows import dump_folder_hierarchy

        g = _make_guru_mock()
        home = _make_folder_obj(HOME_FOLDER_UUID, "Engineering Home")
        g.collections.home_folder.return_value = home

        # Home folder has two sub-folders and one card (card should be skipped)
        g.folders.items.side_effect = [
            # Home folder items
            [
                _make_folder_item(SUB_FOLDER_UUID_1, "folder"),
                _make_folder_item(SUB_FOLDER_UUID_2, "folder"),
                _make_folder_item("card-uuid-123", "card"),
            ],
            # Sub-folder 1 items (empty)
            [],
            # Sub-folder 2 items (empty)
            [],
        ]

        def get_side_effect(folder_id: str) -> Folder:
            if folder_id == SUB_FOLDER_UUID_1:
                return _make_folder_obj(SUB_FOLDER_UUID_1, "Getting Started")
            if folder_id == SUB_FOLDER_UUID_2:
                return _make_folder_obj(SUB_FOLDER_UUID_2, "API Reference")
            raise NotFoundError(f"Unknown folder {folder_id}")

        g.folders.get.side_effect = get_side_effect

        csv_path = tmp_path / "hierarchy.csv"
        dump_folder_hierarchy(g, COLL_UUID, path=str(csv_path))

        # Read and verify CSV
        with open(csv_path, newline="", encoding="utf-8") as f:
            rows = list(csv.reader(f))

        assert len(rows) == 2
        assert rows[0] == ["Getting Started"]
        assert rows[1] == ["API Reference"]

    def test_nested_folders(self, tmp_path: Path) -> None:
        """Collection with nested folder structure (3 levels)."""
        from guru_sdk.contrib.workflows import dump_folder_hierarchy

        g = _make_guru_mock()
        home = _make_folder_obj(HOME_FOLDER_UUID, "Docs Home")
        g.collections.home_folder.return_value = home

        g.folders.items.side_effect = [
            # Home → one sub-folder
            [_make_folder_item(SUB_FOLDER_UUID_1, "folder")],
            # Sub-folder 1 → one nested sub-folder
            [_make_folder_item(SUB_SUB_FOLDER_UUID, "folder")],
            # Sub-sub-folder → empty
            [],
        ]

        def get_side_effect(folder_id: str) -> Folder:
            if folder_id == SUB_FOLDER_UUID_1:
                return _make_folder_obj(SUB_FOLDER_UUID_1, "Guides")
            if folder_id == SUB_SUB_FOLDER_UUID:
                return _make_folder_obj(SUB_SUB_FOLDER_UUID, "Advanced")
            raise NotFoundError(f"Unknown folder {folder_id}")

        g.folders.get.side_effect = get_side_effect

        csv_path = tmp_path / "nested.csv"
        dump_folder_hierarchy(g, COLL_UUID, path=str(csv_path))

        with open(csv_path, newline="", encoding="utf-8") as f:
            rows = list(csv.reader(f))

        assert len(rows) == 2
        assert rows[0] == ["Guides"]
        assert rows[1] == ["Guides", "Advanced"]

    def test_empty_collection(self, tmp_path: Path) -> None:
        """Collection with no sub-folders → empty CSV."""
        from guru_sdk.contrib.workflows import dump_folder_hierarchy

        g = _make_guru_mock()
        home = _make_folder_obj(HOME_FOLDER_UUID, "Empty Collection")
        g.collections.home_folder.return_value = home
        g.folders.items.return_value = []

        csv_path = tmp_path / "empty.csv"
        dump_folder_hierarchy(g, COLL_UUID, path=str(csv_path))

        with open(csv_path, newline="", encoding="utf-8") as f:
            rows = list(csv.reader(f))

        assert rows == []

    def test_default_path_uses_collection_title(self, tmp_path: Path) -> None:
        """When no path is given, uses <collection_title>_folder_hierarchy.csv."""
        from guru_sdk.contrib.workflows import dump_folder_hierarchy

        g = _make_guru_mock()
        home = _make_folder_obj(HOME_FOLDER_UUID, "Engineering")
        g.collections.home_folder.return_value = home
        g.folders.items.return_value = []

        # Use tmp_path as working directory by providing output_dir
        result_path = dump_folder_hierarchy(
            g, COLL_UUID, output_dir=str(tmp_path)
        )

        assert result_path.endswith("Engineering_folder_hierarchy.csv")
        assert Path(result_path).exists()

    def test_returns_file_path(self, tmp_path: Path) -> None:
        """Function returns the path to the created CSV file."""
        from guru_sdk.contrib.workflows import dump_folder_hierarchy

        g = _make_guru_mock()
        home = _make_folder_obj(HOME_FOLDER_UUID, "My Collection")
        g.collections.home_folder.return_value = home
        g.folders.items.return_value = []

        csv_path = tmp_path / "output.csv"
        result = dump_folder_hierarchy(g, COLL_UUID, path=str(csv_path))

        assert result == str(csv_path)

    def test_cards_are_skipped(self, tmp_path: Path) -> None:
        """Only folders are walked — cards in items() are ignored."""
        from guru_sdk.contrib.workflows import dump_folder_hierarchy

        g = _make_guru_mock()
        home = _make_folder_obj(HOME_FOLDER_UUID, "Mixed")
        g.collections.home_folder.return_value = home

        # Home has only cards, no folders
        g.folders.items.return_value = [
            _make_folder_item("card-1", "card"),
            _make_folder_item("card-2", "card"),
        ]

        csv_path = tmp_path / "cards_only.csv"
        dump_folder_hierarchy(g, COLL_UUID, path=str(csv_path))

        with open(csv_path, newline="", encoding="utf-8") as f:
            rows = list(csv.reader(f))

        # No folders → no rows
        assert rows == []

    def test_uses_item_id_not_item_id_placement(self, tmp_path: Path) -> None:
        """Regression: folders.get must use item.id (folder UUID), not item.item_id (placement UUID).

        See SC-152729 — same bug class as publisher.py. The _make_folder_item fixture
        uses distinct values for id vs itemId so this test catches the wrong field.
        """
        from guru_sdk.contrib.workflows import dump_folder_hierarchy

        g = _make_guru_mock()
        home = _make_folder_obj(HOME_FOLDER_UUID, "Regression Home")
        g.collections.home_folder.return_value = home

        folder_item = _make_folder_item(SUB_FOLDER_UUID_1, "folder")
        # Verify fixture uses distinct values
        assert folder_item.id == SUB_FOLDER_UUID_1
        assert folder_item.item_id == f"placement-{SUB_FOLDER_UUID_1}"

        g.folders.items.side_effect = [
            [folder_item],
            [],  # sub-folder is empty
        ]
        g.folders.get.return_value = _make_folder_obj(SUB_FOLDER_UUID_1, "Test Folder")

        csv_path = tmp_path / "regression.csv"
        dump_folder_hierarchy(g, COLL_UUID, path=str(csv_path))

        # folders.get must be called with the actual folder UUID, not the placement UUID
        g.folders.get.assert_called_with(SUB_FOLDER_UUID_1)


# =============================================================================
# replace_text_in_collection_cards
# =============================================================================

CARD_UUID_1 = "ca111111-1111-1111-1111-111111111111"
CARD_UUID_2 = "ca222222-2222-2222-2222-222222222222"
CARD_UUID_3 = "ca333333-3333-3333-3333-333333333333"


def _make_card(
    card_id: str,
    *,
    content: str,
    title: str = "Test Card",
) -> Card:
    """Build a minimal Card for cards.get() responses."""
    return Card.model_validate(
        {
            "id": card_id,
            "preferredPhrase": title,
            "content": content,
        }
    )


class TestReplaceTextInCollectionCards:
    """replace_text_in_collection_cards(g, collection_id, old_text, new_text, ...)."""

    def test_updates_cards_containing_text(self) -> None:
        """Cards containing old_text get patched with new content."""
        from guru_sdk.contrib.workflows import replace_text_in_collection_cards

        g = _make_guru_mock()
        home = _make_folder_obj(HOME_FOLDER_UUID, "Home")
        g.collections.home_folder.return_value = home

        # Home folder has two cards
        g.folders.items.return_value = [
            _make_folder_item(CARD_UUID_1, "card"),
            _make_folder_item(CARD_UUID_2, "card"),
        ]

        cards_by_id = {
            CARD_UUID_1: _make_card(
                CARD_UUID_1, content="<p>Welcome to Acme Corp!</p>", title="Welcome"
            ),
            CARD_UUID_2: _make_card(
                CARD_UUID_2, content="<p>Acme Corp rocks.</p>", title="About"
            ),
        }
        g.cards.get.side_effect = lambda cid: cards_by_id[cid]
        g.cards.patch.return_value = None

        results = replace_text_in_collection_cards(
            g, COLL_UUID, "Acme Corp", "Acme Inc."
        )

        assert g.cards.patch.call_count == 2
        # patch should pass new content and keep_verification by default
        for call in g.cards.patch.call_args_list:
            _args, kwargs = call
            assert "Acme Inc." in kwargs["content"]
            assert "Acme Corp" not in kwargs["content"]
            assert kwargs.get("keep_verification") is True

        statuses = sorted(r.status for r in results)
        assert statuses == ["updated", "updated"]

    def test_skips_cards_without_text(self) -> None:
        """Cards that don't contain old_text are reported as unchanged and not patched."""
        from guru_sdk.contrib.workflows import replace_text_in_collection_cards

        g = _make_guru_mock()
        home = _make_folder_obj(HOME_FOLDER_UUID, "Home")
        g.collections.home_folder.return_value = home

        g.folders.items.return_value = [
            _make_folder_item(CARD_UUID_1, "card"),
            _make_folder_item(CARD_UUID_2, "card"),
        ]

        cards_by_id = {
            CARD_UUID_1: _make_card(CARD_UUID_1, content="<p>Has Acme Corp here.</p>"),
            CARD_UUID_2: _make_card(CARD_UUID_2, content="<p>Nothing to see.</p>"),
        }
        g.cards.get.side_effect = lambda cid: cards_by_id[cid]

        results = replace_text_in_collection_cards(
            g, COLL_UUID, "Acme Corp", "Acme Inc."
        )

        # Only CARD_UUID_1 gets patched
        g.cards.patch.assert_called_once()
        called_card_id = g.cards.patch.call_args.args[0]
        assert called_card_id == CARD_UUID_1

        statuses = {r.card_id: r.status for r in results}
        assert statuses[CARD_UUID_1] == "updated"
        assert statuses[CARD_UUID_2] == "unchanged"

    def test_walks_nested_folders(self) -> None:
        """Recursively descends into sub-folders to find cards."""
        from guru_sdk.contrib.workflows import replace_text_in_collection_cards

        g = _make_guru_mock()
        home = _make_folder_obj(HOME_FOLDER_UUID, "Home")
        g.collections.home_folder.return_value = home

        # Home contains a sub-folder and one card
        # Sub-folder contains another card
        g.folders.items.side_effect = [
            [
                _make_folder_item(SUB_FOLDER_UUID_1, "folder"),
                _make_folder_item(CARD_UUID_1, "card"),
            ],
            [_make_folder_item(CARD_UUID_2, "card")],
        ]

        cards_by_id = {
            CARD_UUID_1: _make_card(CARD_UUID_1, content="<p>Foo bar.</p>"),
            CARD_UUID_2: _make_card(CARD_UUID_2, content="<p>Foo baz.</p>"),
        }
        g.cards.get.side_effect = lambda cid: cards_by_id[cid]

        results = replace_text_in_collection_cards(
            g, COLL_UUID, "Foo", "Bar"
        )

        assert {r.card_id for r in results} == {CARD_UUID_1, CARD_UUID_2}
        assert all(r.status == "updated" for r in results)
        assert g.cards.patch.call_count == 2

    def test_dry_run_does_not_patch(self) -> None:
        """dry_run=True records what *would* change but skips the patch call."""
        from guru_sdk.contrib.workflows import replace_text_in_collection_cards

        g = _make_guru_mock()
        home = _make_folder_obj(HOME_FOLDER_UUID, "Home")
        g.collections.home_folder.return_value = home

        g.folders.items.return_value = [
            _make_folder_item(CARD_UUID_1, "card"),
        ]
        g.cards.get.return_value = _make_card(
            CARD_UUID_1, content="<p>old text here</p>"
        )

        results = replace_text_in_collection_cards(
            g, COLL_UUID, "old", "new", dry_run=True
        )

        g.cards.patch.assert_not_called()
        assert len(results) == 1
        assert results[0].status == "would_update"

    def test_case_insensitive_match(self) -> None:
        """case_sensitive=False matches regardless of case."""
        from guru_sdk.contrib.workflows import replace_text_in_collection_cards

        g = _make_guru_mock()
        home = _make_folder_obj(HOME_FOLDER_UUID, "Home")
        g.collections.home_folder.return_value = home

        g.folders.items.return_value = [
            _make_folder_item(CARD_UUID_1, "card"),
        ]
        g.cards.get.return_value = _make_card(
            CARD_UUID_1, content="<p>GURU and guru and Guru</p>"
        )

        results = replace_text_in_collection_cards(
            g, COLL_UUID, "guru", "Acme", case_sensitive=False
        )

        assert results[0].status == "updated"
        patched_content = g.cards.patch.call_args.kwargs["content"]
        assert patched_content.count("Acme") == 3

    def test_failed_card_is_recorded(self) -> None:
        """Errors fetching or patching a card are captured and walking continues."""
        from guru_sdk.contrib.workflows import replace_text_in_collection_cards

        g = _make_guru_mock()
        home = _make_folder_obj(HOME_FOLDER_UUID, "Home")
        g.collections.home_folder.return_value = home

        g.folders.items.return_value = [
            _make_folder_item(CARD_UUID_1, "card"),
            _make_folder_item(CARD_UUID_2, "card"),
        ]

        def get_side_effect(cid: str) -> Card:
            if cid == CARD_UUID_1:
                raise NotFoundError("Card vanished")
            return _make_card(CARD_UUID_2, content="<p>old</p>")

        g.cards.get.side_effect = get_side_effect

        results = replace_text_in_collection_cards(
            g, COLL_UUID, "old", "new"
        )

        statuses = {r.card_id: r.status for r in results}
        assert statuses[CARD_UUID_1] == "failed"
        assert statuses[CARD_UUID_2] == "updated"
        # The second card still got patched
        g.cards.patch.assert_called_once()

    def test_duplicate_card_only_processed_once(self) -> None:
        """A card appearing in multiple folders is only updated once."""
        from guru_sdk.contrib.workflows import replace_text_in_collection_cards

        g = _make_guru_mock()
        home = _make_folder_obj(HOME_FOLDER_UUID, "Home")
        g.collections.home_folder.return_value = home

        # Home contains one sub-folder + the same card
        # Sub-folder contains the same card again
        g.folders.items.side_effect = [
            [
                _make_folder_item(SUB_FOLDER_UUID_1, "folder"),
                _make_folder_item(CARD_UUID_1, "card"),
            ],
            [_make_folder_item(CARD_UUID_1, "card")],
        ]
        g.cards.get.return_value = _make_card(
            CARD_UUID_1, content="<p>old text</p>"
        )

        results = replace_text_in_collection_cards(
            g, COLL_UUID, "old", "new"
        )

        # Card is processed once, patched once
        assert sum(1 for r in results if r.card_id == CARD_UUID_1) == 1
        g.cards.patch.assert_called_once()

    def test_empty_old_text_raises(self) -> None:
        """Empty old_text is rejected (would otherwise be a pathological no-op)."""
        from guru_sdk.contrib.workflows import replace_text_in_collection_cards

        g = _make_guru_mock()

        with pytest.raises(ValueError, match="old_text"):
            replace_text_in_collection_cards(g, COLL_UUID, "", "anything")

    def test_uses_card_id_not_placement_id(self) -> None:
        """Regression: cards.get must use item.id (card UUID), not item.item_id (placement UUID)."""
        from guru_sdk.contrib.workflows import replace_text_in_collection_cards

        g = _make_guru_mock()
        home = _make_folder_obj(HOME_FOLDER_UUID, "Home")
        g.collections.home_folder.return_value = home

        card_item = _make_folder_item(CARD_UUID_1, "card")
        # Verify fixture has distinct id vs itemId
        assert card_item.id == CARD_UUID_1
        assert card_item.item_id == f"placement-{CARD_UUID_1}"

        g.folders.items.return_value = [card_item]
        g.cards.get.return_value = _make_card(
            CARD_UUID_1, content="<p>old</p>"
        )

        replace_text_in_collection_cards(g, COLL_UUID, "old", "new")

        # cards.get must be called with the actual card UUID
        g.cards.get.assert_called_with(CARD_UUID_1)
        # patch must also be called with the card UUID
        assert g.cards.patch.call_args.args[0] == CARD_UUID_1
