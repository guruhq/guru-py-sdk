"""Agent resource — CRUD + group access for Guru Knowledge Agents.

Knowledge Agents are AI-powered assistants configured with specific knowledge
sources, tone, and behavior. The API calls them "assistants" — the SDK uses
"agents" to match the Guru product terminology.

API surface mirrors guru-cli's AssistantResource.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from guru_sdk._compat import is_uuid, validate_free_text, validate_input
from guru_sdk.errors import NotFoundError
from guru_sdk.models._generated import KnowledgeAgent, KnowledgeAgentAccess
from guru_sdk.resources._base import BaseResource

if TYPE_CHECKING:
    import builtins

# =============================================================================
# Public API — AgentResource
# =============================================================================


class AgentResource(BaseResource):
    """Guru Knowledge Agents — CRUD, name resolution, group access.

    Methods:
        list()         — list all agents (GET /assistants)
        get()          — get by ID (GET /assistants/{id})
        resolve()      — get by UUID or name (UUID → get, name → list + match)
        create()       — create agent (POST /assistants)
        update()       — update agent (PUT /assistants/{id})
        delete()       — delete agent (DELETE /assistants/{id})
        list_groups()  — list group access (GET /assistants/{id}/groups)
        add_group()    — grant group access (POST /assistants/{id}/groups)
        update_group() — update group role (PUT /assistants/{id}/groups/{gid})
        remove_group() — revoke group access (DELETE /assistants/{id}/groups/{gid})
    """

    # -------------------------------------------------------------------------
    # Read
    # -------------------------------------------------------------------------

    def list(self) -> builtins.list[KnowledgeAgent]:
        """List all Knowledge Agents."""
        return self._http.get_list("/assistants", KnowledgeAgent)

    def get(self, agent_id: str) -> KnowledgeAgent:
        """Get an agent by ID.

        Args:
            agent_id: Agent UUID.
        """
        validate_input(agent_id, "agent_id")
        return self._http.get(f"/assistants/{agent_id}", KnowledgeAgent)

    def resolve(self, id_or_name: str) -> KnowledgeAgent:
        """Get an agent by UUID or name.

        UUIDs go directly to get(). Non-UUIDs do a list() + case-insensitive
        name match. Raises NotFoundError if no match, with available names.

        Args:
            id_or_name: Agent UUID or human-readable name.
        """
        validate_input(id_or_name, "agent ID or name")
        if is_uuid(id_or_name):
            return self.get(id_or_name)
        # Name resolution — list all and match case-insensitively
        all_agents = self.list()
        lower_name = id_or_name.lower()
        for agent in all_agents:
            if agent.name and agent.name.lower() == lower_name:
                return agent
        available = ", ".join(a.name for a in all_agents if a.name)
        raise NotFoundError(f'No agent found with name "{id_or_name}". Available: {available}')

    # -------------------------------------------------------------------------
    # Write
    # -------------------------------------------------------------------------

    def create(
        self,
        *,
        name: str,
        description: str | None = None,
        tone: str | None = None,
        answer_prompt: str | None = None,
        no_answer_message: str | None = None,
        use_all_sources: bool | None = None,
        research_allowed: bool | None = None,
        chat_allowed: bool | None = None,
        color: str | None = None,
        web_search_mode: str | None = None,
        agent_type: str | None = None,
        is_default: bool | None = None,
        allow_in_search_bar: bool | None = None,
        verification_agent_enabled: bool | None = None,
    ) -> KnowledgeAgent:
        """Create a new Knowledge Agent.

        Args:
            name: Agent name (required).
            description: Agent description.
            tone: Response tone (e.g. "professional", "friendly").
            answer_prompt: Custom system prompt for answers.
            no_answer_message: Message when no answer is found.
            use_all_sources: If True, agent uses all available sources.
            research_allowed: Allow research mode.
            chat_allowed: Allow chat mode.
            color: Agent color (hex string).
            web_search_mode: Web search behavior (e.g. "DISABLED").
            agent_type: Agent type (e.g. "STANDARD").
            is_default: Make this the default agent.
            allow_in_search_bar: Show agent in search bar.
            verification_agent_enabled: Enable verification agent.
        """
        validate_input(name, "name")
        if description is not None:
            validate_free_text(description, "description")
        if answer_prompt is not None:
            validate_free_text(answer_prompt, "answer_prompt")
        if no_answer_message is not None:
            validate_free_text(no_answer_message, "no_answer_message")

        body: dict[str, Any] = {"name": name}
        if description is not None:
            body["description"] = description
        if tone is not None:
            body["tone"] = tone
        if answer_prompt is not None:
            body["answerPrompt"] = answer_prompt
        if no_answer_message is not None:
            body["noAnswerMessage"] = no_answer_message
        if use_all_sources is not None:
            body["useAllSources"] = use_all_sources
        if research_allowed is not None:
            body["researchAllowed"] = research_allowed
        if chat_allowed is not None:
            body["chatAllowed"] = chat_allowed
        if color is not None:
            body["color"] = color
        if web_search_mode is not None:
            body["webSearchMode"] = web_search_mode
        if agent_type is not None:
            body["agentType"] = agent_type
        if is_default is not None:
            body["isDefault"] = is_default
        if allow_in_search_bar is not None:
            body["allowInSearchBar"] = allow_in_search_bar
        if verification_agent_enabled is not None:
            body["verificationAgentEnabled"] = verification_agent_enabled
        return self._http.post("/assistants", body, KnowledgeAgent)

    def update(
        self,
        agent_id: str,
        *,
        name: str | None = None,
        description: str | None = None,
        tone: str | None = None,
        answer_prompt: str | None = None,
        no_answer_message: str | None = None,
        use_all_sources: bool | None = None,
        research_allowed: bool | None = None,
        chat_allowed: bool | None = None,
        color: str | None = None,
        web_search_mode: str | None = None,
        agent_type: str | None = None,
        is_default: bool | None = None,
        allow_in_search_bar: bool | None = None,
        verification_agent_enabled: bool | None = None,
    ) -> KnowledgeAgent:
        """Update an agent. Only provided fields are changed.

        Args:
            agent_id: Agent UUID.
            name: New name.
            description: New description.
            tone: New tone.
            answer_prompt: New answer prompt.
            no_answer_message: New no-answer message.
            use_all_sources: Use all sources flag.
            research_allowed: Research mode flag.
            chat_allowed: Chat mode flag.
            color: New color.
            web_search_mode: Web search behavior.
            agent_type: Agent type.
            is_default: Default agent flag.
            allow_in_search_bar: Search bar visibility flag.
            verification_agent_enabled: Verification agent flag.
        """
        validate_input(agent_id, "agent_id")
        if name is not None:
            validate_input(name, "name")
        if description is not None:
            validate_free_text(description, "description")
        if answer_prompt is not None:
            validate_free_text(answer_prompt, "answer_prompt")
        if no_answer_message is not None:
            validate_free_text(no_answer_message, "no_answer_message")

        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description
        if tone is not None:
            body["tone"] = tone
        if answer_prompt is not None:
            body["answerPrompt"] = answer_prompt
        if no_answer_message is not None:
            body["noAnswerMessage"] = no_answer_message
        if use_all_sources is not None:
            body["useAllSources"] = use_all_sources
        if research_allowed is not None:
            body["researchAllowed"] = research_allowed
        if chat_allowed is not None:
            body["chatAllowed"] = chat_allowed
        if color is not None:
            body["color"] = color
        if web_search_mode is not None:
            body["webSearchMode"] = web_search_mode
        if agent_type is not None:
            body["agentType"] = agent_type
        if is_default is not None:
            body["isDefault"] = is_default
        if allow_in_search_bar is not None:
            body["allowInSearchBar"] = allow_in_search_bar
        if verification_agent_enabled is not None:
            body["verificationAgentEnabled"] = verification_agent_enabled
        return self._http.put(f"/assistants/{agent_id}", body, KnowledgeAgent)

    def delete(self, agent_id: str) -> None:
        """Delete an agent.

        Args:
            agent_id: Agent UUID.
        """
        validate_input(agent_id, "agent_id")
        self._http.delete(f"/assistants/{agent_id}")

    # -------------------------------------------------------------------------
    # Group Access
    # -------------------------------------------------------------------------

    def list_groups(self, agent_id: str) -> builtins.list[KnowledgeAgentAccess]:
        """List groups with access to an agent.

        Args:
            agent_id: Agent UUID.
        """
        validate_input(agent_id, "agent_id")
        return self._http.get_list(f"/assistants/{agent_id}/groups", KnowledgeAgentAccess)

    def add_group(
        self,
        agent_id: str,
        group_id: str,
        *,
        role: str | None = None,
    ) -> KnowledgeAgentAccess:
        """Grant a group access to an agent.

        Args:
            agent_id: Agent UUID.
            group_id: Group UUID.
            role: Optional role (e.g. "MEMBER", "ADMIN").
        """
        validate_input(agent_id, "agent_id")
        validate_input(group_id, "group_id")
        if role is not None:
            validate_input(role, "role")
        body: dict[str, Any] = {"group": {"id": group_id}}
        if role is not None:
            body["role"] = role
        return self._http.post(f"/assistants/{agent_id}/groups", body, KnowledgeAgentAccess)

    def update_group(
        self,
        agent_id: str,
        group_id: str,
        *,
        role: str,
    ) -> KnowledgeAgentAccess:
        """Update a group's role on an agent.

        Args:
            agent_id: Agent UUID.
            group_id: Group UUID.
            role: New role.
        """
        validate_input(agent_id, "agent_id")
        validate_input(group_id, "group_id")
        validate_input(role, "role")
        body: dict[str, Any] = {"group": {"id": group_id}, "role": role}
        return self._http.put(
            f"/assistants/{agent_id}/groups/{group_id}",
            body,
            KnowledgeAgentAccess,
        )

    def remove_group(self, agent_id: str, group_id: str) -> None:
        """Revoke a group's access to an agent.

        Args:
            agent_id: Agent UUID.
            group_id: Group UUID.
        """
        validate_input(agent_id, "agent_id")
        validate_input(group_id, "group_id")
        self._http.delete(f"/assistants/{agent_id}/groups/{group_id}")
