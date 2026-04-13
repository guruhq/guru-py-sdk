"""Answer resource — AI-powered Q&A against the Guru knowledge base.

Ask questions and receive AI-generated answers with sources, explanations,
and suggested follow-up questions. Optionally target a specific Knowledge
Agent for domain-specific answers.

API surface mirrors guru-cli's AnswerResource.
"""

from __future__ import annotations

from typing import Any

from guru_sdk._compat import validate_free_text, validate_input
from guru_sdk.errors import ValidationError
from guru_sdk.models._generated import Answer
from guru_sdk.resources._base import BaseResource

# =============================================================================
# Public API — AnswerResource
# =============================================================================


class AnswerResource(BaseResource):
    """Guru Answers — AI-powered Q&A.

    Methods:
        ask()         — full answer with sources and explanation (POST /answers)
        ask_minimal() — lighter answer without extras (POST /answers/minimal)
    """

    def ask(
        self,
        question: str,
        *,
        agent_id: str | None = None,
    ) -> Answer:
        """Ask a question — returns full answer with sources and explanation.

        Args:
            question: The question to ask (natural language).
            agent_id: Target a specific Knowledge Agent by UUID.
        """
        validate_free_text(question, "question")
        if not question.strip():
            raise ValidationError("question must not be empty")
        if agent_id is not None:
            validate_input(agent_id, "agent_id")

        body: dict[str, Any] = {"question": question}
        if agent_id is not None:
            body["agentId"] = agent_id
        return self._http.post("/answers", body, Answer)

    def ask_minimal(
        self,
        question: str,
        *,
        agent_id: str | None = None,
    ) -> Answer:
        """Ask a question — returns minimal answer without explanations or sources.

        Args:
            question: The question to ask (natural language).
            agent_id: Target a specific Knowledge Agent by UUID.
        """
        validate_free_text(question, "question")
        if not question.strip():
            raise ValidationError("question must not be empty")
        if agent_id is not None:
            validate_input(agent_id, "agent_id")

        body: dict[str, Any] = {"question": question}
        if agent_id is not None:
            body["agentId"] = agent_id
        return self._http.post("/answers/minimal", body, Answer)
