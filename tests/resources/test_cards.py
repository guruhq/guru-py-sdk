"""Tests for guru_sdk.resources.cards — CardResource.

Comprehensive TDD tests covering the full card API surface:
- CRUD (get, create, update, remove)
- Verification (verify, unverify, list_unverified)
- Tags (list_tags, add_tag, remove_tag)
- Comments (list_comments, add_comment, delete_comment, reply, delete_reply, resolve, unresolve)
- Folders (list_folders, add_to_folder, remove_from_folder)
- Collaborators (list_collaborators, add_collaborator, remove_collaborator)
- Verifiers (list_verifiers)
- Name resolution (accept card ID or title)
- Input validation
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from guru_sdk.errors import NotFoundError, ValidationError
from guru_sdk.models import (
    Card,
    CardCollaborator,
    CardComment,
    CardCommentReply,
    CardCommentResult,
    Folder,
    Tag,
)
from guru_sdk.resources.cards import CardResource

if TYPE_CHECKING:
    from guru_sdk.http import HttpClient

# =============================================================================
# Test Data — realistic API response shapes
# =============================================================================

CARD_UUID = "11111111-1111-1111-1111-111111111111"
CARD_UUID_2 = "22222222-2222-2222-2222-222222222222"
FOLDER_UUID = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
TAG_UUID = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
COMMENT_UUID = "cccccccc-cccc-cccc-cccc-cccccccccccc"
REPLY_UUID = "dddddddd-dddd-dddd-dddd-dddddddddddd"
COLLECTION_UUID = "eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee"
USER_EMAIL = "author@example.com"


def _card_json(
    card_id: str = CARD_UUID,
    title: str = "Getting Started Guide",
    content: str = "<p>Hello world</p>",
) -> dict:
    """Build a realistic Card API response dict."""
    return {
        "id": card_id,
        "preferredPhrase": title,
        "content": content,
        "shareStatus": "TEAM",
        "verificationState": "TRUSTED",
        "owner": {"id": "user-1", "email": USER_EMAIL, "firstName": "Test", "lastName": "Author"},
        "collection": {"id": COLLECTION_UUID, "name": "Engineering"},
        "dateCreated": "2025-01-15T10:00:00.000+0000",
        "lastModified": "2025-06-01T14:30:00.000+0000",
    }


def _folder_json(folder_id: str = FOLDER_UUID, title: str = "Onboarding") -> dict:
    """Build a realistic Folder API response dict."""
    return {
        "id": folder_id,
        "title": title,
        "collection": {"id": COLLECTION_UUID, "name": "Engineering"},
    }


def _tag_json(tag_id: str = TAG_UUID, value: str = "important") -> dict:
    """Build a realistic Tag API response dict."""
    return {
        "id": tag_id,
        "value": value,
        "categoryId": "cat-1",
        "categoryName": "Priority",
    }


def _comment_json(
    comment_id: str = COMMENT_UUID,
    content: str = "Looks good!",
    status: str = "OPEN",
) -> dict:
    """Build a realistic CardComment API response dict."""
    return {
        "id": comment_id,
        "content": content,
        "status": status,
        "totalReplies": 0,
        "owner": {"id": "user-1", "email": USER_EMAIL, "firstName": "Test", "lastName": "Author"},
        "dateCreated": "2025-06-01T14:30:00.000+0000",
        "lastModified": "2025-06-01T14:30:00.000+0000",
    }


def _reply_json(reply_id: str = REPLY_UUID, content: str = "Thanks!") -> dict:
    """Build a realistic CardCommentReply API response dict."""
    return {
        "id": reply_id,
        "content": content,
        "owner": {"id": "user-1", "email": USER_EMAIL, "firstName": "Test", "lastName": "Author"},
        "dateCreated": "2025-06-02T09:00:00.000+0000",
        "lastModified": "2025-06-02T09:00:00.000+0000",
    }


def _card_comment_result_json(
    comment_id: str = COMMENT_UUID,
    content: str = "Looks good!",
    status: str = "OPEN",
    card_id: str = CARD_UUID,
    card_title: str = "Getting Started Guide",
) -> dict:
    """Build a realistic CardCommentResult API response dict.

    Returned by the team-wide GET /comments endpoint (bulk_get_comments) —
    unlike CardComment (per-card /cards/{id}/comments), the comment fields are
    flat at the top level and the card identity is nested under `card`.
    """
    return {
        "id": comment_id,
        "content": content,
        "status": status,
        "totalReplies": 1,
        "replies": [_reply_json()],
        "owner": {"id": "user-1", "email": USER_EMAIL, "firstName": "Test", "lastName": "Author"},
        "dateCreated": "2025-06-01T14:30:00.000+0000",
        "lastModified": "2025-06-01T14:30:00.000+0000",
        "card": {
            "id": card_id,
            "preferredPhrase": card_title,
            "slug": "getting-started-guide",
        },
    }


def _collaborator_json(collab_id: str = "user-2") -> dict:
    """Build a realistic CardCollaborator API response dict."""
    return {
        "id": collab_id,
        "type": "user",
        "dateCreated": "2025-06-01T12:00:00.000+0000",
    }


# =============================================================================
# Fixture — CardResource wired to pytest-httpx mock transport
# =============================================================================


@pytest.fixture()
def cards(http_client: HttpClient) -> CardResource:
    """CardResource backed by a mock HTTP transport."""
    return CardResource(http_client)


# =============================================================================
# CardResource.get() — GET /cards/{id}
# =============================================================================


class TestGet:
    """Get a single card by ID."""

    def test_get_by_uuid(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_card_json())
        card = cards.get(CARD_UUID)
        assert isinstance(card, Card)
        assert card.id == CARD_UUID
        assert card.preferred_phrase == "Getting Started Guide"

    def test_get_sends_correct_path(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_card_json())
        cards.get(CARD_UUID)
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.path == f"/api/v1/cards/{CARD_UUID}"

    def test_get_by_title_resolves(self, cards: CardResource, httpx_mock) -> None:
        """Non-UUID input triggers name resolution: list all cards, match by title."""
        # First call: list cards for name resolution
        httpx_mock.add_response(json=[_card_json()])
        # Second call: get the resolved card
        httpx_mock.add_response(json=_card_json())
        card = cards.get("Getting Started Guide")
        assert card.id == CARD_UUID

    def test_get_by_title_case_insensitive(self, cards: CardResource, httpx_mock) -> None:
        """Name resolution is case-insensitive."""
        httpx_mock.add_response(json=[_card_json()])
        httpx_mock.add_response(json=_card_json())
        card = cards.get("getting started guide")
        assert card.id == CARD_UUID

    def test_get_by_title_not_found(self, cards: CardResource, httpx_mock) -> None:
        """Name resolution raises NotFoundError when no card matches."""
        httpx_mock.add_response(json=[_card_json()])
        with pytest.raises(NotFoundError):
            cards.get("Nonexistent Card")

    def test_get_validates_input(self, cards: CardResource) -> None:
        """Input validation rejects control characters."""
        with pytest.raises(ValidationError):
            cards.get("card\x00id")


# =============================================================================
# CardResource.create() — POST /cards/extended
# =============================================================================


class TestCreate:
    """Create a new card."""

    def test_create_returns_card(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_card_json())
        card = cards.create(
            title="Getting Started Guide",
            content="<p>Hello world</p>",
            collection_id=COLLECTION_UUID,
        )
        assert isinstance(card, Card)
        assert card.preferred_phrase == "Getting Started Guide"

    def test_create_sends_correct_body(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_card_json())
        cards.create(
            title="Getting Started Guide",
            content="<p>Hello world</p>",
            collection_id=COLLECTION_UUID,
        )
        request = httpx_mock.get_request()
        assert request is not None
        body = json.loads(request.content)
        assert body["preferredPhrase"] == "Getting Started Guide"
        assert body["content"] == "<p>Hello world</p>"
        assert body["collection"]["id"] == COLLECTION_UUID
        # Default share status
        assert body["shareStatus"] == "TEAM"

    def test_create_sends_to_extended_endpoint(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_card_json())
        cards.create(title="X", content="Y", collection_id=COLLECTION_UUID)
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.path == "/api/v1/cards/extended"
        assert request.method == "POST"

    def test_create_validates_title(self, cards: CardResource) -> None:
        with pytest.raises(ValidationError):
            cards.create(title="Bad\x00Title", content="ok", collection_id=COLLECTION_UUID)

    def test_create_validates_collection_id(self, cards: CardResource) -> None:
        with pytest.raises(ValidationError):
            cards.create(title="Good Title", content="ok", collection_id="../escape")

    def test_create_with_custom_share_status(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_card_json())
        cards.create(
            title="X",
            content="Y",
            collection_id=COLLECTION_UUID,
            share_status="PRIVATE",
        )
        request = httpx_mock.get_request()
        assert request is not None
        body = json.loads(request.content)
        assert body["shareStatus"] == "PRIVATE"


# =============================================================================
# CardResource.update() — PUT /cards/{id}/extended
# =============================================================================


class TestUpdate:
    """Update an existing card."""

    def test_update_returns_card(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_card_json(title="Updated Title"))
        card = cards.update(CARD_UUID, title="Updated Title")
        assert card.preferred_phrase == "Updated Title"

    def test_update_sends_correct_path(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_card_json())
        cards.update(CARD_UUID, content="<p>New content</p>")
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.path == f"/api/v1/cards/{CARD_UUID}/extended"
        assert request.method == "PUT"

    def test_update_sends_only_provided_fields(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_card_json())
        cards.update(CARD_UUID, content="<p>New content</p>")
        request = httpx_mock.get_request()
        assert request is not None
        body = json.loads(request.content)
        assert body["content"] == "<p>New content</p>"
        # title (preferredPhrase) not in body since it wasn't provided
        assert "preferredPhrase" not in body

    def test_update_validates_card_id(self, cards: CardResource) -> None:
        with pytest.raises(ValidationError):
            cards.update("card?id=1", title="X")


# =============================================================================
# CardResource.remove() — DELETE /cards/{id}
# =============================================================================


class TestRemove:
    """Delete a card."""

    def test_remove_sends_delete(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(status_code=204)
        cards.remove(CARD_UUID)
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.path == f"/api/v1/cards/{CARD_UUID}"
        assert request.method == "DELETE"

    def test_remove_validates_card_id(self, cards: CardResource) -> None:
        with pytest.raises(ValidationError):
            cards.remove("../etc/passwd")


# =============================================================================
# CardResource.verify() — PUT /cards/{id}/verify
# =============================================================================


class TestVerify:
    """Mark a card as verified (trusted)."""

    def test_verify_returns_card(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_card_json())
        card = cards.verify(CARD_UUID)
        assert isinstance(card, Card)

    def test_verify_sends_correct_request(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_card_json())
        cards.verify(CARD_UUID)
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.path == f"/api/v1/cards/{CARD_UUID}/verify"
        assert request.method == "PUT"

    def test_verify_validates_card_id(self, cards: CardResource) -> None:
        with pytest.raises(ValidationError):
            cards.verify("bad%20id")


# =============================================================================
# CardResource.unverify() — POST /cards/{id}/unverify
# =============================================================================


class TestUnverify:
    """Mark a card as unverified."""

    def test_unverify_sends_correct_request(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(status_code=204)
        cards.unverify(CARD_UUID)
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.path == f"/api/v1/cards/{CARD_UUID}/unverify"
        assert request.method == "POST"


# =============================================================================
# CardResource.list_unverified() — GET /cards/verificationmgr
# =============================================================================


class TestListUnverified:
    """List cards needing verification."""

    def test_list_unverified_returns_cards(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(json=[_card_json(), _card_json(card_id=CARD_UUID_2)])
        result = cards.list_unverified()
        assert len(result) == 2
        assert all(isinstance(c, Card) for c in result)

    def test_list_unverified_sends_correct_path(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(json=[])
        cards.list_unverified()
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.path == "/api/v1/cards/verificationmgr"


# =============================================================================
# CardResource.list_tags() — GET /cards/{id}/tags
# =============================================================================


class TestListTags:
    """List tags on a card."""

    def test_list_tags_returns_tags(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(json=[_tag_json()])
        result = cards.list_tags(CARD_UUID)
        assert len(result) == 1
        assert isinstance(result[0], Tag)
        assert result[0].value == "important"

    def test_list_tags_empty(self, cards: CardResource, httpx_mock) -> None:
        """204 No Content is treated as empty list."""
        httpx_mock.add_response(status_code=204)
        result = cards.list_tags(CARD_UUID)
        assert result == []


# =============================================================================
# CardResource.add_tag() — PUT /cards/{id}/tags/{tagId}
# =============================================================================


class TestAddTag:
    """Add a tag to a card."""

    def test_add_tag_returns_tags(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(json=[_tag_json()])
        result = cards.add_tag(CARD_UUID, TAG_UUID)
        assert len(result) == 1
        assert isinstance(result[0], Tag)

    def test_add_tag_sends_correct_request(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(json=[_tag_json()])
        cards.add_tag(CARD_UUID, TAG_UUID)
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.path == f"/api/v1/cards/{CARD_UUID}/tags/{TAG_UUID}"
        assert request.method == "PUT"

    def test_add_tag_validates_both_ids(self, cards: CardResource) -> None:
        with pytest.raises(ValidationError):
            cards.add_tag("bad\x00id", TAG_UUID)
        with pytest.raises(ValidationError):
            cards.add_tag(CARD_UUID, "bad?id")


# =============================================================================
# CardResource.remove_tag() — DELETE /cards/{id}/tags/{tagId}
# =============================================================================


class TestRemoveTag:
    """Remove a tag from a card."""

    def test_remove_tag_sends_delete(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(status_code=204)
        cards.remove_tag(CARD_UUID, TAG_UUID)
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.path == f"/api/v1/cards/{CARD_UUID}/tags/{TAG_UUID}"
        assert request.method == "DELETE"


# =============================================================================
# CardResource.list_comments() — GET /cards/{id}/comments
# =============================================================================


class TestListComments:
    """List comments on a card."""

    def test_list_comments_returns_comments(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(json=[_comment_json()])
        result = cards.list_comments(CARD_UUID)
        assert len(result) == 1
        assert isinstance(result[0], CardComment)
        assert result[0].content == "Looks good!"

    def test_list_comments_empty(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(status_code=204)
        result = cards.list_comments(CARD_UUID)
        assert result == []


# =============================================================================
# CardResource.add_comment() — POST /cards/{id}/comments
# =============================================================================


class TestAddComment:
    """Add a comment to a card."""

    def test_add_comment_returns_comment(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_comment_json())
        result = cards.add_comment(CARD_UUID, "Looks good!")
        assert isinstance(result, CardComment)
        assert result.content == "Looks good!"

    def test_add_comment_sends_correct_body(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_comment_json())
        cards.add_comment(CARD_UUID, "Looks good!")
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.path == f"/api/v1/cards/{CARD_UUID}/comments"
        body = json.loads(request.content)
        assert body["content"] == "Looks good!"

    def test_add_comment_uses_free_text_validation(self, cards: CardResource, httpx_mock) -> None:
        """Comments use free-text validation — question marks are allowed."""
        httpx_mock.add_response(json=_comment_json(content="Is this right?"))
        # Should NOT raise — question marks are fine in comments
        result = cards.add_comment(CARD_UUID, "Is this right?")
        assert result.content == "Is this right?"

    def test_add_comment_rejects_control_chars(self, cards: CardResource) -> None:
        """Even free-text validation rejects control characters."""
        with pytest.raises(ValidationError):
            cards.add_comment(CARD_UUID, "bad\x00comment")


# =============================================================================
# CardResource.delete_comment() — DELETE /cards/{id}/comments/{commentId}
# =============================================================================


class TestDeleteComment:
    """Delete a comment from a card."""

    def test_delete_comment_sends_delete(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(status_code=204)
        cards.delete_comment(CARD_UUID, COMMENT_UUID)
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.path == f"/api/v1/cards/{CARD_UUID}/comments/{COMMENT_UUID}"
        assert request.method == "DELETE"


# =============================================================================
# CardResource.reply_comment() — POST /cards/{id}/comments/{commentId}/replies
# =============================================================================


class TestReplyComment:
    """Reply to a comment on a card."""

    def test_reply_returns_reply(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_reply_json())
        result = cards.reply_comment(CARD_UUID, COMMENT_UUID, "Thanks!")
        assert isinstance(result, CardCommentReply)
        assert result.content == "Thanks!"

    def test_reply_sends_correct_body(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_reply_json())
        cards.reply_comment(CARD_UUID, COMMENT_UUID, "Thanks!")
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.path == (f"/api/v1/cards/{CARD_UUID}/comments/{COMMENT_UUID}/replies")
        body = json.loads(request.content)
        assert body["content"] == "Thanks!"


# =============================================================================
# CardResource.delete_reply() — DELETE /cards/{id}/comments/{commentId}/replies/{replyId}
# =============================================================================


class TestDeleteReply:
    """Delete a reply from a comment."""

    def test_delete_reply_sends_delete(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(status_code=204)
        cards.delete_reply(CARD_UUID, COMMENT_UUID, REPLY_UUID)
        request = httpx_mock.get_request()
        assert request is not None
        expected = f"/api/v1/cards/{CARD_UUID}/comments/{COMMENT_UUID}/replies/{REPLY_UUID}"
        assert request.url.path == expected
        assert request.method == "DELETE"


# =============================================================================
# CardResource.resolve_comment() — PUT /cards/{id}/comments/{commentId}/resolve
# =============================================================================


class TestResolveComment:
    """Resolve a comment on a card."""

    def test_resolve_sends_put(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(status_code=204)
        cards.resolve_comment(CARD_UUID, COMMENT_UUID)
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.path == (f"/api/v1/cards/{CARD_UUID}/comments/{COMMENT_UUID}/resolve")
        assert request.method == "PUT"


# =============================================================================
# CardResource.unresolve_comment() — PUT /cards/{id}/comments/{commentId}/unresolve
# =============================================================================


class TestUnresolveComment:
    """Unresolve a comment on a card."""

    def test_unresolve_sends_put(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(status_code=204)
        cards.unresolve_comment(CARD_UUID, COMMENT_UUID)
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.path == (f"/api/v1/cards/{CARD_UUID}/comments/{COMMENT_UUID}/unresolve")
        assert request.method == "PUT"


# =============================================================================
# CardResource.list_folders() — GET /cards/{id}/folders
# =============================================================================


class TestListFolders:
    """List folders a card belongs to."""

    def test_list_folders_returns_folders(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(json=[_folder_json()])
        result = cards.list_folders(CARD_UUID)
        assert len(result) == 1
        assert isinstance(result[0], Folder)

    def test_list_folders_empty(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(status_code=204)
        result = cards.list_folders(CARD_UUID)
        assert result == []


# =============================================================================
# CardResource.add_to_folder() — POST /cards/{id}/folders
# =============================================================================


class TestAddToFolder:
    """Add a card to a folder."""

    def test_add_to_folder_sends_correct_body(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_folder_json())
        cards.add_to_folder(CARD_UUID, FOLDER_UUID)
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.path == f"/api/v1/cards/{CARD_UUID}/folders"
        assert request.method == "POST"
        body = json.loads(request.content)
        assert body["id"] == FOLDER_UUID

    def test_add_to_folder_returns_folder(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_folder_json())
        result = cards.add_to_folder(CARD_UUID, FOLDER_UUID)
        assert isinstance(result, Folder)

    def test_add_to_folder_validates_ids(self, cards: CardResource) -> None:
        with pytest.raises(ValidationError):
            cards.add_to_folder("bad?card", FOLDER_UUID)
        with pytest.raises(ValidationError):
            cards.add_to_folder(CARD_UUID, "bad%20folder")


# =============================================================================
# CardResource.remove_from_folder() — DELETE /cards/{id}/folders/{folderId}
# =============================================================================


class TestRemoveFromFolder:
    """Remove a card from a folder."""

    def test_remove_from_folder_sends_delete(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(status_code=204)
        cards.remove_from_folder(CARD_UUID, FOLDER_UUID)
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.path == f"/api/v1/cards/{CARD_UUID}/folders/{FOLDER_UUID}"
        assert request.method == "DELETE"


# =============================================================================
# CardResource.list_collaborators() — GET /cards/{id}/collaborators
# =============================================================================


class TestListCollaborators:
    """List collaborators on a card."""

    def test_list_collaborators_returns_list(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(json=[_collaborator_json()])
        result = cards.list_collaborators(CARD_UUID)
        assert len(result) == 1
        assert isinstance(result[0], CardCollaborator)

    def test_list_collaborators_empty(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(status_code=204)
        result = cards.list_collaborators(CARD_UUID)
        assert result == []


# =============================================================================
# CardResource.add_collaborator() — POST /cards/{id}/collaborators
# =============================================================================


class TestAddCollaborator:
    """Add a collaborator to a card."""

    def test_add_collaborator_sends_correct_body(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(json=[_collaborator_json()])
        cards.add_collaborator(CARD_UUID, "collab@example.com")
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.path == f"/api/v1/cards/{CARD_UUID}/collaborators"
        assert request.method == "POST"
        body = json.loads(request.content)
        # API expects an array of collaborator objects
        assert isinstance(body, list)
        assert body[0]["type"] == "user"
        assert body[0]["user"]["email"] == "collab@example.com"

    def test_add_collaborator_returns_list(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(json=[_collaborator_json()])
        result = cards.add_collaborator(CARD_UUID, "collab@example.com")
        assert len(result) == 1
        assert isinstance(result[0], CardCollaborator)


# =============================================================================
# CardResource.remove_collaborator() — DELETE /cards/{id}/collaborators/{email}
# =============================================================================


class TestRemoveCollaborator:
    """Remove a collaborator from a card."""

    def test_remove_collaborator_sends_delete(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(status_code=204)
        cards.remove_collaborator(CARD_UUID, "collab@example.com")
        request = httpx_mock.get_request()
        assert request is not None
        # Email must be URL-encoded in the path
        assert "/collaborators/collab%40example.com" in str(request.url)
        assert request.method == "DELETE"


# =============================================================================
# CardResource.list_verifiers() — GET /cards/{id}/verifiers
# =============================================================================


class TestListVerifiers:
    """List verifiers assigned to a card."""

    def test_list_verifiers_returns_list(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(
            json=[
                {"id": "v1", "type": "user", "dateCreated": "2025-01-01T00:00:00.000+0000"},
            ]
        )
        result = cards.list_verifiers(CARD_UUID)
        assert len(result) == 1

    def test_list_verifiers_empty(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(status_code=204)
        result = cards.list_verifiers(CARD_UUID)
        assert result == []

    def test_list_verifiers_sends_correct_path(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(json=[])
        cards.list_verifiers(CARD_UUID)
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.path == f"/api/v1/cards/{CARD_UUID}/verifiers"


# =============================================================================
# Name Resolution — resolve card title to UUID
# =============================================================================


class TestNameResolution:
    """Name resolution: when a non-UUID string is passed, resolve by listing cards."""

    def test_resolve_matches_exact_title(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(
            json=[
                _card_json(card_id=CARD_UUID, title="Getting Started Guide"),
                _card_json(card_id=CARD_UUID_2, title="Advanced Topics"),
            ]
        )
        httpx_mock.add_response(json=_card_json())
        card = cards.get("Getting Started Guide")
        assert card.id == CARD_UUID

    def test_resolve_is_case_insensitive(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(json=[_card_json()])
        httpx_mock.add_response(json=_card_json())
        card = cards.get("GETTING STARTED GUIDE")
        assert card.id == CARD_UUID

    def test_resolve_raises_not_found_for_no_match(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(json=[_card_json()])
        with pytest.raises(NotFoundError):
            cards.get("No Such Card")

    def test_uuid_skips_resolution(self, cards: CardResource, httpx_mock) -> None:
        """UUIDs go directly to the API — no name resolution needed."""
        httpx_mock.add_response(json=_card_json())
        cards.get(CARD_UUID)
        # Only one request was made (no list call)
        requests = httpx_mock.get_requests()
        assert len(requests) == 1
        assert f"/cards/{CARD_UUID}" in str(requests[0].url)


# =============================================================================
# Input Validation — defense against hallucinated inputs
# =============================================================================


class TestInputValidation:
    """Input validation rejects hallucinated patterns across all methods."""

    def test_control_chars_rejected(self, cards: CardResource) -> None:
        with pytest.raises(ValidationError):
            cards.get("card\x07id")

    def test_path_traversal_rejected(self, cards: CardResource) -> None:
        with pytest.raises(ValidationError):
            cards.get("../../../etc/passwd")

    def test_query_fragment_rejected(self, cards: CardResource) -> None:
        with pytest.raises(ValidationError):
            cards.get("card?admin=true")

    def test_percent_encoding_rejected(self, cards: CardResource) -> None:
        with pytest.raises(ValidationError):
            cards.get("card%2Fid")

    def test_remove_validates(self, cards: CardResource) -> None:
        with pytest.raises(ValidationError):
            cards.remove("bad\x00id")

    def test_verify_validates(self, cards: CardResource) -> None:
        with pytest.raises(ValidationError):
            cards.verify("../traversal")

    def test_list_tags_validates(self, cards: CardResource) -> None:
        with pytest.raises(ValidationError):
            cards.list_tags("card#fragment")

    def test_add_comment_validates_card_id(self, cards: CardResource) -> None:
        with pytest.raises(ValidationError):
            cards.add_comment("card%2F", "good comment")


# =============================================================================
# CardResource.patch() — PATCH /cards/{id}?keepVerificationState={bool}
# =============================================================================


class TestPatch:
    """Patch card content/title with optional verification preservation."""

    def test_patch_returns_card(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_card_json(title="Patched Title"))
        card = cards.patch(CARD_UUID, title="Patched Title")
        assert isinstance(card, Card)
        assert card.preferred_phrase == "Patched Title"

    def test_patch_sends_correct_request(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_card_json())
        cards.patch(CARD_UUID, content="<p>New</p>")
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.path == f"/api/v1/cards/{CARD_UUID}"
        assert request.method == "PATCH"
        body = json.loads(request.content)
        assert body["content"] == "<p>New</p>"

    def test_patch_keep_verification_default_true(self, cards: CardResource, httpx_mock) -> None:
        """By default, keepVerificationState is True (preserve verification)."""
        httpx_mock.add_response(json=_card_json())
        cards.patch(CARD_UUID, content="<p>X</p>")
        request = httpx_mock.get_request()
        assert request is not None
        assert "keepVerificationState=true" in str(request.url)

    def test_patch_keep_verification_false(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_card_json())
        cards.patch(CARD_UUID, content="<p>X</p>", keep_verification=False)
        request = httpx_mock.get_request()
        assert request is not None
        assert "keepVerificationState=false" in str(request.url)

    def test_patch_sends_only_provided_fields(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_card_json())
        cards.patch(CARD_UUID, title="New Title")
        request = httpx_mock.get_request()
        assert request is not None
        body = json.loads(request.content)
        assert body["preferredPhrase"] == "New Title"
        assert "content" not in body

    def test_patch_validates_card_id(self, cards: CardResource) -> None:
        with pytest.raises(ValidationError):
            cards.patch("bad?id", title="X")


# =============================================================================
# CardResource.archive() — DELETE /cards/{id} (same endpoint as remove)
# =============================================================================


class TestArchive:
    """Archive a card (soft delete — can be restored)."""

    def test_archive_sends_delete(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(status_code=204)
        cards.archive(CARD_UUID)
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.path == f"/api/v1/cards/{CARD_UUID}"
        assert request.method == "DELETE"


# =============================================================================
# CardResource.restore() — POST /cards/bulkop
# =============================================================================


class TestRestore:
    """Restore an archived card."""

    def test_restore_sends_correct_body(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(status_code=200, json={})
        cards.restore(CARD_UUID)
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.path == "/api/v1/cards/bulkop"
        assert request.method == "POST"
        body = json.loads(request.content)
        assert body["action"]["type"] == "restore-archived-card"
        assert body["items"]["type"] == "id"
        assert CARD_UUID in body["items"]["cardIds"]

    def test_restore_validates_card_id(self, cards: CardResource) -> None:
        with pytest.raises(ValidationError):
            cards.restore("bad\x00id")


# =============================================================================
# CardResource.get_version() — GET /cards/{id}/versions/{version}
# =============================================================================


class TestGetVersion:
    """Retrieve a historical version of a card."""

    def test_get_version_returns_card(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_card_json())
        card = cards.get_version(CARD_UUID, 3)
        assert isinstance(card, Card)

    def test_get_version_sends_correct_path(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_card_json())
        cards.get_version(CARD_UUID, 5)
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.path == f"/api/v1/cards/{CARD_UUID}/versions/5"

    def test_get_version_validates_card_id(self, cards: CardResource) -> None:
        with pytest.raises(ValidationError):
            cards.get_version("../bad", 1)


# =============================================================================
# CardResource.update_comment() — PUT /cards/{id}/comments/{commentId}
# =============================================================================


class TestUpdateComment:
    """Update an existing comment's content."""

    def test_update_comment_returns_comment(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_comment_json(content="Updated text"))
        result = cards.update_comment(CARD_UUID, COMMENT_UUID, "Updated text")
        assert isinstance(result, CardComment)
        assert result.content == "Updated text"

    def test_update_comment_sends_correct_body(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_comment_json())
        cards.update_comment(CARD_UUID, COMMENT_UUID, "New content")
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.path == f"/api/v1/cards/{CARD_UUID}/comments/{COMMENT_UUID}"
        assert request.method == "PUT"
        body = json.loads(request.content)
        assert body["content"] == "New content"

    def test_update_comment_validates_inputs(self, cards: CardResource) -> None:
        with pytest.raises(ValidationError):
            cards.update_comment(CARD_UUID, "bad?id", "text")
        with pytest.raises(ValidationError):
            cards.update_comment(CARD_UUID, COMMENT_UUID, "bad\x00text")


# =============================================================================
# CardResource.list_comments() with status filter
# =============================================================================


class TestListCommentsWithStatus:
    """List comments filtered by status (OPEN or RESOLVED)."""

    def test_list_comments_with_open_filter(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(json=[_comment_json(status="OPEN")])
        result = cards.list_comments(CARD_UUID, status="OPEN")
        assert len(result) == 1

    def test_list_comments_with_resolved_filter(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(json=[_comment_json(status="RESOLVED")])
        result = cards.list_comments(CARD_UUID, status="RESOLVED")
        assert len(result) == 1

    def test_list_comments_status_in_query_params(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(json=[])
        cards.list_comments(CARD_UUID, status="OPEN")
        request = httpx_mock.get_request()
        assert request is not None
        assert "status=OPEN" in str(request.url)

    def test_list_comments_no_status_no_param(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(json=[])
        cards.list_comments(CARD_UUID)
        request = httpx_mock.get_request()
        assert request is not None
        assert "status" not in str(request.url)


# =============================================================================
# CardResource.bulk_get_comments() — GET /comments (team-wide, not per-card)
# =============================================================================


class TestBulkGetComments:
    """Bulk-retrieve card comment threads team-wide via GET /comments."""

    def test_sends_all_filters_as_query_params(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(json=[])
        cards.bulk_get_comments(
            status="OPEN",
            active_after="2026-01-01",
            active_before="2026-02-01",
        )
        request = httpx_mock.get_request()
        assert request is not None
        assert "status=OPEN" in str(request.url)
        assert "activeAfter=2026-01-01" in str(request.url)
        assert "activeBefore=2026-02-01" in str(request.url)

    def test_accepts_full_iso_8601_timestamps(self, cards: CardResource, httpx_mock) -> None:
        # Full ISO 8601 timestamps carry characters a bare date does not:
        # `T`, `:`, `.`, a `+` offset, and a `Z` suffix. All must pass
        # validation and survive URL encoding intact.
        httpx_mock.add_response(json=[])
        cards.bulk_get_comments(
            active_after="2026-01-01T00:00:00.000+0000",
            active_before="2026-02-01T23:59:59Z",
        )
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.params["activeAfter"] == "2026-01-01T00:00:00.000+0000"
        assert request.url.params["activeBefore"] == "2026-02-01T23:59:59Z"
        # The offset's `+` must be percent-encoded on the wire — sent
        # literally, the server would decode it as a space.
        assert "activeAfter=2026-01-01T00%3A00%3A00.000%2B0000" in str(request.url)

    def test_rejects_pre_encoded_iso_8601_timestamp(self, cards: CardResource) -> None:
        # An already-URL-encoded timestamp would be double-encoded on the
        # wire; validation catches it before any request is made.
        with pytest.raises(ValidationError):
            cards.bulk_get_comments(active_after="2026-01-01T00%3A00%3A00%2B0000")

    def test_no_filters_sends_no_query_params(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(json=[])
        cards.bulk_get_comments()
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.query == b""

    def test_path_is_team_wide_not_nested_under_card(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(json=[])
        cards.bulk_get_comments()
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.path == "/api/v1/comments"

    def test_deserializes_into_card_comment_result_with_nested_card(
        self, cards: CardResource, httpx_mock
    ) -> None:
        httpx_mock.add_response(json=[_card_comment_result_json()])
        result = cards.bulk_get_comments()
        assert len(result) == 1
        comment = result[0]
        assert isinstance(comment, CardCommentResult)
        # Comment fields live at the top level, not nested under `.comment`.
        assert comment.content == "Looks good!"
        assert comment.status.value == "OPEN"
        assert comment.total_replies == 1
        assert len(comment.replies) == 1
        assert comment.replies[0].content == "Thanks!"
        # Card identity is nested under `.card` as a CardReference.
        assert comment.card is not None
        assert comment.card.id == CARD_UUID
        assert comment.card.preferred_phrase == "Getting Started Guide"
        assert comment.card.slug == "getting-started-guide"

    def test_paginates_across_link_header_pages(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(
            json=[_card_comment_result_json(comment_id=COMMENT_UUID)],
            headers={"Link": '<https://api.getguru.com/api/v1/comments?page=2>; rel="next"'},
        )
        httpx_mock.add_response(json=[_card_comment_result_json(comment_id=REPLY_UUID)])

        result = cards.bulk_get_comments()

        assert len(result) == 2
        assert {c.id for c in result} == {COMMENT_UUID, REPLY_UUID}

    def test_reports_complete_when_all_pages_fetched(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(json=[_card_comment_result_json()])
        result = cards.bulk_get_comments()
        assert result.complete is True

    def test_reports_incomplete_when_truncated_by_max_pages(
        self, cards: CardResource, httpx_mock
    ) -> None:
        # More pages remain (Link header present) but max_pages caps the walk.
        httpx_mock.add_response(
            json=[_card_comment_result_json()],
            headers={"Link": '<https://api.getguru.com/api/v1/comments?page=2>; rel="next"'},
        )
        result = cards.bulk_get_comments(max_pages=1)
        assert result.complete is False


# =============================================================================
# CardResource.favorite() / unfavorite()
# =============================================================================


class TestFavorite:
    """Favorite and unfavorite a card."""

    def test_unfavorite_sends_delete(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(status_code=204)
        cards.unfavorite(CARD_UUID)
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.path == f"/api/v1/cards/{CARD_UUID}/favorite"
        assert request.method == "DELETE"


# =============================================================================
# CardResource.download_pdf() — GET /cards/{id}/pdf
# =============================================================================


class TestDownloadPdf:
    """Download a card as PDF."""

    def test_download_pdf_returns_bytes(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(content=b"%PDF-1.4 fake pdf content")
        result = cards.download_pdf(CARD_UUID)
        assert isinstance(result, bytes)
        assert b"PDF" in result

    def test_download_pdf_sends_correct_path(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(content=b"%PDF-1.4")
        cards.download_pdf(CARD_UUID)
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.path == f"/api/v1/cards/{CARD_UUID}/pdf"


# =============================================================================
# CardResource.move_to_collection() — POST /cards/bulkop
# =============================================================================


class TestMoveToCollection:
    """Move a card to a different collection."""

    def test_move_sends_correct_body(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(status_code=200, json={})
        cards.move_to_collection(CARD_UUID, COLLECTION_UUID)
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.path == "/api/v1/cards/bulkop"
        body = json.loads(request.content)
        assert body["action"]["type"] == "move-card"
        assert body["action"]["collectionId"] == COLLECTION_UUID
        assert CARD_UUID in body["items"]["cardIds"]

    def test_move_validates_inputs(self, cards: CardResource) -> None:
        with pytest.raises(ValidationError):
            cards.move_to_collection("bad?id", COLLECTION_UUID)
        with pytest.raises(ValidationError):
            cards.move_to_collection(CARD_UUID, "../bad")


# =============================================================================
# CardResource.get_bulk() — POST /cards/bulk
# =============================================================================


class TestGetBulk:
    """Retrieve multiple cards in a single request."""

    def test_get_bulk_returns_cards(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(
            json=[_card_json(), _card_json(card_id=CARD_UUID_2, title="Second")]
        )
        result = cards.get_bulk([CARD_UUID, CARD_UUID_2])
        assert len(result) == 2
        assert all(isinstance(c, Card) for c in result)

    def test_get_bulk_sends_correct_body(self, cards: CardResource, httpx_mock) -> None:
        httpx_mock.add_response(json=[_card_json()])
        cards.get_bulk([CARD_UUID])
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.path == "/api/v1/cards/bulk"
        assert request.method == "POST"
        body = json.loads(request.content)
        assert CARD_UUID in body

    def test_get_bulk_validates_ids(self, cards: CardResource) -> None:
        with pytest.raises(ValidationError):
            cards.get_bulk(["bad?id"])


# =============================================================================
# CardResource.upload_file() — POST /attachments/upload
# =============================================================================


class TestUploadFile:
    """Upload a file attachment and get back a URL for embedding in card content."""

    def test_upload_file_returns_url(self, cards: CardResource, httpx_mock, tmp_path) -> None:
        attachment_response = {
            "attachmentId": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
            "link": "https://content.api.getguru.com/files/view/aaaaaaaa",
            "filename": "diagram.png",
            "mimeType": "image/png",
            "size": 12345,
        }
        httpx_mock.add_response(json=attachment_response)

        # Create a temp file to upload
        test_file = tmp_path / "diagram.png"
        test_file.write_bytes(b"fake-png-data")

        url = cards.upload_file(str(test_file))

        assert url == "https://content.api.getguru.com/files/view/aaaaaaaa"

    def test_upload_file_sends_multipart_post(
        self, cards: CardResource, httpx_mock, tmp_path
    ) -> None:
        httpx_mock.add_response(
            json={
                "attachmentId": "abc",
                "link": "https://content.api.getguru.com/files/view/abc",
                "filename": "notes.pdf",
                "mimeType": "application/pdf",
                "size": 999,
            }
        )

        test_file = tmp_path / "notes.pdf"
        test_file.write_bytes(b"%PDF-1.4 fake")

        cards.upload_file(str(test_file))

        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.path == "/api/v1/attachments/upload"
        assert request.method == "POST"
        # Multipart body should contain the filename and content
        assert b"notes.pdf" in request.content
        assert b"%PDF-1.4 fake" in request.content

    def test_upload_file_raises_for_missing_file(self, cards: CardResource) -> None:
        with pytest.raises(FileNotFoundError):
            cards.upload_file("/nonexistent/path/file.png")

    def test_upload_file_with_pathlib(self, cards: CardResource, httpx_mock, tmp_path) -> None:
        """Accepts pathlib.Path as well as str."""
        httpx_mock.add_response(
            json={
                "attachmentId": "xyz",
                "link": "https://content.api.getguru.com/files/view/xyz",
                "filename": "photo.jpg",
                "mimeType": "image/jpeg",
                "size": 500,
            }
        )

        test_file = tmp_path / "photo.jpg"
        test_file.write_bytes(b"fake-jpeg")

        url = cards.upload_file(test_file)
        assert url == "https://content.api.getguru.com/files/view/xyz"
