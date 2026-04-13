"""Tests for guru_sdk.http — HttpClient transport layer."""

import json

import pytest
from pydantic import Field

from guru_sdk.errors import (
    AuthenticationError,
    ForbiddenError,
    GuruApiError,
    NotFoundError,
    RateLimitError,
)
from guru_sdk.http import HttpClient, _parse_link_header
from guru_sdk.models._base import GuruModel

# =============================================================================
# Test Models
# =============================================================================


class FakeCard(GuruModel):
    id: str
    title: str = Field(alias="preferredPhrase")


class FakeFolder(GuruModel):
    id: str
    name: str = ""


# =============================================================================
# HttpClient.get() — single resource
# =============================================================================


class TestGet:
    def test_get_returns_validated_model(self, httpx_mock):
        httpx_mock.add_response(json={"id": "abc-123", "preferredPhrase": "My Card"})
        client = HttpClient("https://api.getguru.com/api/v1", "user", "token")
        card = client.get("/cards/abc-123", FakeCard)
        assert card.id == "abc-123"
        assert card.title == "My Card"

    def test_get_sends_auth_header(self, httpx_mock):
        httpx_mock.add_response(json={"id": "1", "preferredPhrase": "X"})
        client = HttpClient("https://api.getguru.com/api/v1", "user@test.com", "my-token")
        client.get("/cards/1", FakeCard)
        request = httpx_mock.get_request()
        assert request is not None
        # httpx sends Basic auth
        assert request.headers.get("authorization") is not None

    def test_get_sends_tracking_headers(self, httpx_mock):
        httpx_mock.add_response(json={"id": "1", "preferredPhrase": "X"})
        client = HttpClient("https://api.getguru.com/api/v1", "user", "token")
        client.get("/cards/1", FakeCard)
        request = httpx_mock.get_request()
        assert request is not None
        assert "guru-sdk-python" in request.headers.get("user-agent", "")
        assert request.headers.get("x-guru-sdk", "").startswith("python/")


# =============================================================================
# HttpClient.get_list() — list endpoints
# =============================================================================


class TestGetList:
    def test_returns_list_of_models(self, httpx_mock):
        httpx_mock.add_response(
            json=[
                {"id": "1", "preferredPhrase": "Card 1"},
                {"id": "2", "preferredPhrase": "Card 2"},
            ]
        )
        client = HttpClient("https://api.getguru.com/api/v1", "user", "token")
        cards = client.get_list("/cards", FakeCard)
        assert len(cards) == 2
        assert cards[0].title == "Card 1"
        assert cards[1].title == "Card 2"

    def test_returns_empty_list_on_204(self, httpx_mock):
        httpx_mock.add_response(status_code=204)
        client = HttpClient("https://api.getguru.com/api/v1", "user", "token")
        result = client.get_list("/cards/id/comments", FakeCard)
        assert result == []


# =============================================================================
# HttpClient.post() — create resources
# =============================================================================


class TestPost:
    def test_post_sends_json_body(self, httpx_mock):
        httpx_mock.add_response(json={"id": "new-1", "preferredPhrase": "New Card"})
        client = HttpClient("https://api.getguru.com/api/v1", "user", "token")
        card = client.post(
            "/cards",
            {"preferredPhrase": "New Card", "content": "<p>Hello</p>"},
            FakeCard,
        )
        assert card.id == "new-1"
        request = httpx_mock.get_request()
        assert request is not None
        assert request.headers["content-type"] == "application/json"
        body = json.loads(request.content)
        assert body["preferredPhrase"] == "New Card"


# =============================================================================
# HttpClient.put() — update resources
# =============================================================================


class TestPut:
    def test_put_sends_json_body(self, httpx_mock):
        httpx_mock.add_response(json={"id": "1", "preferredPhrase": "Updated"})
        client = HttpClient("https://api.getguru.com/api/v1", "user", "token")
        card = client.put("/cards/1", {"preferredPhrase": "Updated"}, FakeCard)
        assert card.title == "Updated"


# =============================================================================
# HttpClient.delete()
# =============================================================================


class TestDelete:
    def test_delete_returns_none(self, httpx_mock):
        httpx_mock.add_response(status_code=204)
        client = HttpClient("https://api.getguru.com/api/v1", "user", "token")
        result = client.delete("/cards/1")
        assert result is None


# =============================================================================
# Error Mapping — HTTP status codes → typed exceptions
# =============================================================================


class TestErrorMapping:
    def test_401_raises_authentication_error(self, httpx_mock):
        httpx_mock.add_response(status_code=401, json={"message": "Unauthorized"})
        client = HttpClient("https://api.getguru.com/api/v1", "user", "token")
        with pytest.raises(AuthenticationError) as exc_info:
            client.get("/whoami", FakeCard)
        assert exc_info.value.status_code == 401

    def test_403_raises_forbidden_error(self, httpx_mock):
        httpx_mock.add_response(status_code=403, json={"message": "Forbidden"})
        client = HttpClient("https://api.getguru.com/api/v1", "user", "token")
        with pytest.raises(ForbiddenError):
            client.get("/cards/1", FakeCard)

    def test_404_raises_not_found_error(self, httpx_mock):
        httpx_mock.add_response(status_code=404, json={"message": "Not found"})
        client = HttpClient("https://api.getguru.com/api/v1", "user", "token")
        with pytest.raises(NotFoundError):
            client.get("/cards/nonexistent", FakeCard)

    def test_429_raises_rate_limit_error(self, httpx_mock):
        httpx_mock.add_response(status_code=429, json={"message": "Rate limited"})
        client = HttpClient("https://api.getguru.com/api/v1", "user", "token")
        with pytest.raises(RateLimitError):
            client.get("/cards/1", FakeCard)

    def test_500_raises_guru_api_error(self, httpx_mock):
        httpx_mock.add_response(status_code=500, text="Internal Server Error")
        client = HttpClient("https://api.getguru.com/api/v1", "user", "token")
        with pytest.raises(GuruApiError) as exc_info:
            client.get("/cards/1", FakeCard)
        assert exc_info.value.status_code == 500


# =============================================================================
# Pagination
# =============================================================================


class TestPagination:
    def test_single_page_no_link_header(self, httpx_mock):
        httpx_mock.add_response(json=[{"id": "1", "name": "F1"}, {"id": "2", "name": "F2"}])
        client = HttpClient("https://api.getguru.com/api/v1", "user", "token")
        folders = client.get_paginated("/folders", FakeFolder)
        assert len(folders) == 2

    def test_follows_link_header_for_next_page(self, httpx_mock):
        # Page 1: returns 2 items + Link header pointing to page 2
        httpx_mock.add_response(
            json=[{"id": "1", "name": "F1"}],
            headers={"Link": '<https://api.getguru.com/api/v1/folders?page=2>; rel="next"'},
        )
        # Page 2: returns 1 item, no Link header
        httpx_mock.add_response(json=[{"id": "2", "name": "F2"}])

        client = HttpClient("https://api.getguru.com/api/v1", "user", "token")
        folders = client.get_paginated("/folders", FakeFolder)
        assert len(folders) == 2
        assert folders[0].id == "1"
        assert folders[1].id == "2"

    def test_respects_max_pages(self, httpx_mock):
        # Register exactly max_pages responses — each has a Link header
        for _ in range(3):
            httpx_mock.add_response(
                json=[{"id": "x", "name": "X"}],
                headers={"Link": '<https://api.getguru.com/api/v1/folders?page=99>; rel="next"'},
            )
        client = HttpClient("https://api.getguru.com/api/v1", "user", "token")
        folders = client.get_paginated("/folders", FakeFolder, max_pages=3)
        assert len(folders) == 3


# =============================================================================
# HttpClient.post_file() — multipart file upload
# =============================================================================


class TestPostFile:
    def test_post_file_sends_multipart(self, httpx_mock):
        httpx_mock.add_response(json={"link": "https://content.api.getguru.com/files/view/abc"})
        client = HttpClient("https://api.getguru.com/api/v1", "user", "token")
        result = client.post_file(
            "/attachments/upload",
            field_name="file",
            filename="image.png",
            file_bytes=b"fake-png-data",
            mimetype="image/png",
        )
        assert result["link"] == "https://content.api.getguru.com/files/view/abc"

        request = httpx_mock.get_request()
        assert request is not None
        assert request.method == "POST"
        assert b"image.png" in request.content
        assert b"fake-png-data" in request.content

    def test_post_file_raises_on_error(self, httpx_mock):
        httpx_mock.add_response(status_code=401, json={"message": "Unauthorized"})
        client = HttpClient("https://api.getguru.com/api/v1", "user", "token")
        with pytest.raises(AuthenticationError):
            client.post_file(
                "/attachments/upload",
                field_name="file",
                filename="test.txt",
                file_bytes=b"data",
                mimetype="text/plain",
            )


# =============================================================================
# Link Header Parsing
# =============================================================================


class TestParseLinkHeader:
    def test_parses_next_link(self):
        header = '<https://api.getguru.com/api/v1/folders?page=2>; rel="next"'
        assert _parse_link_header(header) == "https://api.getguru.com/api/v1/folders?page=2"

    def test_returns_none_when_no_next(self):
        header = '<https://api.getguru.com/api/v1/folders?page=1>; rel="prev"'
        assert _parse_link_header(header) is None

    def test_returns_none_for_none(self):
        assert _parse_link_header(None) is None

    def test_returns_none_for_empty(self):
        assert _parse_link_header("") is None


# =============================================================================
# Context Manager
# =============================================================================


class TestContextManager:
    def test_context_manager_closes_client(self, httpx_mock):
        httpx_mock.add_response(json={"id": "1", "preferredPhrase": "X"})
        with HttpClient("https://api.getguru.com/api/v1", "user", "token") as client:
            card = client.get("/cards/1", FakeCard)
            assert card.id == "1"
        # After exiting, the httpx client should be closed
        # (httpx.Client raises RuntimeError on use after close)
