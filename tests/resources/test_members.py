"""Tests for guru_sdk.resources.members — MemberResource.

TDD tests covering the member API surface:
- List (with search parameter)
- Get by email
- Invite (core, with optional group/message)
- Remove
- Input validation
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING
from urllib.parse import unquote

import pytest

from guru_sdk.errors import ValidationError
from guru_sdk.models._generated import TeamUser
from guru_sdk.resources.members import MemberResource

if TYPE_CHECKING:
    from guru_sdk.http import HttpClient

# =============================================================================
# Test Data — realistic API response shapes
# =============================================================================

GROUP_UUID = "gggggggg-gggg-gggg-gggg-gggggggggggg"


def _member_json(email: str = "alice@example.com") -> dict:
    """Build a realistic TeamUser API response dict."""
    return {
        "id": "member-1",
        "dateCreated": "2025-01-01T00:00:00.000+0000",
        "user": {
            "email": email,
            "firstName": "Alice",
            "lastName": "Smith",
            "status": "ACTIVE",
        },
    }


# =============================================================================
# Fixture
# =============================================================================


@pytest.fixture()
def members(http_client: HttpClient) -> MemberResource:
    """MemberResource backed by a mock HTTP transport."""
    return MemberResource(http_client)


# =============================================================================
# MemberResource.list() — GET /members
# =============================================================================


class TestList:
    """List all team members."""

    def test_list_returns_members(self, members: MemberResource, httpx_mock) -> None:
        httpx_mock.add_response(json=[_member_json()])
        result = members.list()
        assert len(result) == 1
        assert isinstance(result[0], TeamUser)
        assert result[0].user.email == "alice@example.com"

    def test_list_sends_correct_path(self, members: MemberResource, httpx_mock) -> None:
        httpx_mock.add_response(json=[])
        members.list()
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.path == "/api/v1/members"

    def test_list_with_search(self, members: MemberResource, httpx_mock) -> None:
        httpx_mock.add_response(json=[_member_json()])
        members.list(search="alice")
        request = httpx_mock.get_request()
        assert request is not None
        assert "search=alice" in str(request.url)

    def test_list_empty_returns_empty(self, members: MemberResource, httpx_mock) -> None:
        httpx_mock.add_response(json=[])
        result = members.list()
        assert result == []


# =============================================================================
# MemberResource.get() — GET /members/{email}
# =============================================================================


class TestGet:
    """Get a single member by email."""

    def test_get_returns_member(self, members: MemberResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_member_json())
        result = members.get("alice@example.com")
        assert isinstance(result, TeamUser)
        assert result.user.email == "alice@example.com"

    def test_get_sends_correct_path(self, members: MemberResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_member_json())
        members.get("alice@example.com")
        request = httpx_mock.get_request()
        assert request is not None
        # Email should be percent-encoded in the URL path (@ → %40)
        path = unquote(request.url.path)
        assert path == "/api/v1/members/alice@example.com"

    def test_get_validates_input(self, members: MemberResource) -> None:
        with pytest.raises(ValidationError):
            members.get("bad\x00email")


# =============================================================================
# MemberResource.invite() — POST /members/invite
# =============================================================================


class TestInvite:
    """Invite a new member to the team."""

    def test_invite_sends_correct_body(self, members: MemberResource, httpx_mock) -> None:
        httpx_mock.add_response(status_code=204)
        members.invite(email="bob@example.com")
        request = httpx_mock.get_request()
        assert request is not None
        assert request.method == "POST"
        assert request.url.path == "/api/v1/members/invite"
        body = json.loads(request.content)
        assert body["emails"] == "bob@example.com"
        assert body["teamMemberType"] == "CORE"

    def test_invite_with_type(self, members: MemberResource, httpx_mock) -> None:
        httpx_mock.add_response(status_code=204)
        members.invite(email="bob@example.com", member_type="LIGHT")
        request = httpx_mock.get_request()
        assert request is not None
        body = json.loads(request.content)
        assert body["teamMemberType"] == "LIGHT"

    def test_invite_with_message(self, members: MemberResource, httpx_mock) -> None:
        httpx_mock.add_response(status_code=204)
        members.invite(email="bob@example.com", message="Welcome!")
        request = httpx_mock.get_request()
        assert request is not None
        body = json.loads(request.content)
        assert body["customMessage"] == "Welcome!"

    def test_invite_validates_email(self, members: MemberResource) -> None:
        with pytest.raises(ValidationError):
            members.invite(email="bad\x00email")


# =============================================================================
# MemberResource.remove() — DELETE /members/{email}
# =============================================================================


class TestRemove:
    """Remove a member from the team."""

    def test_remove_sends_correct_request(self, members: MemberResource, httpx_mock) -> None:
        httpx_mock.add_response(status_code=204)
        members.remove("alice@example.com")
        request = httpx_mock.get_request()
        assert request is not None
        assert request.method == "DELETE"
        path = unquote(request.url.path)
        assert path == "/api/v1/members/alice@example.com"

    def test_remove_validates_input(self, members: MemberResource) -> None:
        with pytest.raises(ValidationError):
            members.remove("bad\x00email")
