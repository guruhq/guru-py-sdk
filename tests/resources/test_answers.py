"""Tests for guru_sdk.resources.answers — AnswerResource.

TDD tests covering the answer API surface:
- ask() — ask a question (POST /answers)
- ask_minimal() — ask a quick question (POST /answers/minimal)
- Input validation
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from guru_sdk.errors import ValidationError
from guru_sdk.models._generated import Answer
from guru_sdk.resources.answers import AnswerResource

if TYPE_CHECKING:
    from guru_sdk.http import HttpClient

# =============================================================================
# Test Data — realistic API response shapes
# =============================================================================

AGENT_UUID = "a1a1a1a1-a1a1-a1a1-a1a1-a1a1a1a1a1a1"


def _answer_json(
    question: str = "How do I reset my password?",
    answered: bool = True,
) -> dict:
    """Build a realistic Answer API response dict."""
    result: dict = {
        "answerId": "ans-1234",
        "answer": "Go to Settings > Security > Reset Password.",
        "question": question,
        "answered": answered,
        "answerDate": "2025-06-15T14:30:00.000+0000",
        "lastModified": "2025-06-15T14:30:00.000+0000",
        "status": "ANSWERED",
        "chatThreadId": "thread-5678",
        "sources": [
            {
                "id": "doc-1",
                "title": "Password Reset Guide",
                "documentType": "GURU",
            }
        ],
        "answerExplanation": {
            "searchTerms": ["reset", "password"],
            "explanation": "Found in the Password Reset Guide.",
        },
        "suggestedQuestions": {
            "questions": ["How do I enable 2FA?"],
        },
        "searchAssistant": {
            "id": AGENT_UUID,
            "name": "Support Agent",
        },
        "asker": {
            "email": "user@example.com",
            "firstName": "Test",
            "lastName": "User",
        },
    }
    return result


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture()
def answers(http_client: HttpClient) -> AnswerResource:
    """AnswerResource wired to the mock HttpClient."""
    return AnswerResource(http_client)


# =============================================================================
# ask() — POST /answers
# =============================================================================


class TestAsk:
    """Ask a question — full answer with sources and explanation."""

    def test_ask(self, answers: AnswerResource, httpx_mock) -> None:
        """Ask returns Answer object."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/answers",
            json=_answer_json(),
        )
        result = answers.ask("How do I reset my password?")
        assert isinstance(result, Answer)
        assert result.answer_id == "ans-1234"
        assert result.answered is True
        assert result.question == "How do I reset my password?"

    def test_ask_sends_body(self, answers: AnswerResource, httpx_mock) -> None:
        """Ask sends question in POST body."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/answers",
            json=_answer_json(),
        )
        answers.ask("What is our PTO policy?")
        request = httpx_mock.get_request()
        body = json.loads(request.content)
        assert body["question"] == "What is our PTO policy?"
        assert "agentId" not in body

    def test_ask_with_agent_id(self, answers: AnswerResource, httpx_mock) -> None:
        """Ask with agent_id sends agentId in body."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/answers",
            json=_answer_json(),
        )
        answers.ask("What is our PTO policy?", agent_id=AGENT_UUID)
        request = httpx_mock.get_request()
        body = json.loads(request.content)
        assert body["agentId"] == AGENT_UUID

    def test_ask_nested_fields(self, answers: AnswerResource, httpx_mock) -> None:
        """Answer parses nested sources and explanation."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/answers",
            json=_answer_json(),
        )
        result = answers.ask("Test?")
        assert result.sources is not None
        assert len(result.sources) == 1
        assert result.answer_explanation is not None
        assert result.search_assistant is not None
        assert result.search_assistant.name == "Support Agent"

    def test_ask_validates_empty_question(self, answers: AnswerResource) -> None:
        """Empty question raises ValidationError."""
        with pytest.raises(ValidationError):
            answers.ask("")

    def test_ask_validates_whitespace_question(self, answers: AnswerResource) -> None:
        """Whitespace-only question raises ValidationError."""
        with pytest.raises(ValidationError):
            answers.ask("   ")


# =============================================================================
# ask_minimal() — POST /answers/minimal
# =============================================================================


class TestAskMinimal:
    """Ask a quick question — lighter response."""

    def test_ask_minimal(self, answers: AnswerResource, httpx_mock) -> None:
        """Ask minimal returns Answer object."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/answers/minimal",
            json=_answer_json(),
        )
        result = answers.ask_minimal("Quick question?")
        assert isinstance(result, Answer)
        assert result.answer_id == "ans-1234"

    def test_ask_minimal_with_agent_id(self, answers: AnswerResource, httpx_mock) -> None:
        """Ask minimal with agent_id sends agentId in body."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/answers/minimal",
            json=_answer_json(),
        )
        answers.ask_minimal("Quick?", agent_id=AGENT_UUID)
        request = httpx_mock.get_request()
        body = json.loads(request.content)
        assert body["agentId"] == AGENT_UUID

    def test_ask_minimal_validates_empty(self, answers: AnswerResource) -> None:
        """Empty question raises ValidationError."""
        with pytest.raises(ValidationError):
            answers.ask_minimal("")
