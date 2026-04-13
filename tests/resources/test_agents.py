"""Tests for guru_sdk.resources.agents — AgentResource (Knowledge Agents).

TDD tests covering the agent API surface:
- list() — list all agents (GET /assistants)
- get() — get by ID (GET /assistants/{id})
- resolve() — get by UUID or name (UUID → get, name → list + match)
- create() — create agent (POST /assistants)
- update() — update agent (PUT /assistants/{id})
- delete() — delete agent (DELETE /assistants/{id})
- list_groups() — list group access (GET /assistants/{id}/groups)
- add_group() — grant group access (POST /assistants/{id}/groups)
- update_group() — update group role (PUT /assistants/{id}/groups/{gid})
- remove_group() — revoke group access (DELETE /assistants/{id}/groups/{gid})
- Input validation
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from guru_sdk.errors import NotFoundError, ValidationError
from guru_sdk.models._generated import KnowledgeAgent, KnowledgeAgentAccess
from guru_sdk.resources.agents import AgentResource

if TYPE_CHECKING:
    from guru_sdk.http import HttpClient

# =============================================================================
# Test Data — realistic API response shapes
# =============================================================================

AGENT_UUID = "a1a1a1a1-a1a1-a1a1-a1a1-a1a1a1a1a1a1"
AGENT_UUID_2 = "b2b2b2b2-b2b2-b2b2-b2b2-b2b2b2b2b2b2"
GROUP_UUID = "c3c3c3c3-c3c3-c3c3-c3c3-c3c3c3c3c3c3"


def _agent_json(
    agent_id: str = AGENT_UUID,
    name: str = "Support Agent",
) -> dict:
    """Build a realistic KnowledgeAgent API response dict."""
    return {
        "id": agent_id,
        "name": name,
        "description": "Answers support questions",
        "imageUrl": "https://example.com/agent.png",
        "isDefault": False,
        "dateCreated": "2025-06-01T10:00:00.000+0000",
        "useAllSources": True,
        "tone": "professional",
        "answerPrompt": "Answer using only verified content.",
        "noAnswerMessage": "I could not find an answer.",
        "researchAllowed": True,
        "chatAllowed": True,
        "color": "#4A90D9",
        "webSearchMode": "DISABLED",
        "agentType": "DEEP_AGENT",
        "createdBy": {
            "email": "admin@example.com",
            "firstName": "Admin",
            "lastName": "User",
        },
    }


def _access_json(
    group_id: str = GROUP_UUID,
    group_name: str = "Engineering",
) -> dict:
    """Build a realistic KnowledgeAgentAccess API response dict."""
    return {
        "group": {
            "id": group_id,
            "name": group_name,
            "dateCreated": "2025-01-01T00:00:00.000+0000",
        },
        "role": "VIEWER",
        "objectRole": {
            "id": "11111111-1111-1111-1111-111111111111",
            "name": "Agent User",
            "permissions": ["AGENT_VIEW"],
        },
    }


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture()
def agents(http_client: HttpClient) -> AgentResource:
    """AgentResource wired to the mock HttpClient."""
    return AgentResource(http_client)


# =============================================================================
# list() — GET /assistants
# =============================================================================


class TestList:
    """List all Knowledge Agents."""

    def test_list_all(self, agents: AgentResource, httpx_mock) -> None:
        """List agents returns list of KnowledgeAgent objects."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/assistants",
            json=[
                _agent_json(AGENT_UUID, "Support Agent"),
                _agent_json(AGENT_UUID_2, "HR Agent"),
            ],
        )
        result = agents.list()
        assert len(result) == 2
        assert isinstance(result[0], KnowledgeAgent)
        assert result[0].name == "Support Agent"
        assert result[1].name == "HR Agent"

    def test_list_empty(self, agents: AgentResource, httpx_mock) -> None:
        """No agents returns empty list."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/assistants",
            json=[],
        )
        result = agents.list()
        assert result == []


# =============================================================================
# get() — GET /assistants/{id}
# =============================================================================


class TestGet:
    """Get an agent by ID."""

    def test_get_by_id(self, agents: AgentResource, httpx_mock) -> None:
        """Get an agent by UUID."""
        httpx_mock.add_response(
            url=f"https://api.getguru.com/api/v1/assistants/{AGENT_UUID}",
            json=_agent_json(),
        )
        result = agents.get(AGENT_UUID)
        assert isinstance(result, KnowledgeAgent)
        assert str(result.id) == AGENT_UUID
        assert result.name == "Support Agent"

    def test_validates_agent_id(self, agents: AgentResource) -> None:
        """Empty agent_id raises ValidationError."""
        with pytest.raises(ValidationError):
            agents.get("")

    def test_validates_control_chars(self, agents: AgentResource) -> None:
        """Control chars in agent_id are rejected."""
        with pytest.raises(ValidationError):
            agents.get("agent\x00id")


# =============================================================================
# resolve() — UUID → get, name → list + case-insensitive match
# =============================================================================


class TestResolve:
    """Resolve an agent by UUID or name."""

    def test_resolve_by_uuid(self, agents: AgentResource, httpx_mock) -> None:
        """UUID goes directly to get()."""
        httpx_mock.add_response(
            url=f"https://api.getguru.com/api/v1/assistants/{AGENT_UUID}",
            json=_agent_json(),
        )
        result = agents.resolve(AGENT_UUID)
        assert str(result.id) == AGENT_UUID

    def test_resolve_by_name(self, agents: AgentResource, httpx_mock) -> None:
        """Name does list + case-insensitive match."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/assistants",
            json=[
                _agent_json(AGENT_UUID, "Support Agent"),
                _agent_json(AGENT_UUID_2, "HR Agent"),
            ],
        )
        result = agents.resolve("support agent")
        assert str(result.id) == AGENT_UUID
        assert result.name == "Support Agent"

    def test_resolve_name_not_found(self, agents: AgentResource, httpx_mock) -> None:
        """Unknown name raises NotFoundError with available names."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/assistants",
            json=[_agent_json(AGENT_UUID, "Support Agent")],
        )
        with pytest.raises(NotFoundError, match="Support Agent"):
            agents.resolve("Nonexistent Agent")

    def test_resolve_validates_input(self, agents: AgentResource) -> None:
        """Empty input raises ValidationError."""
        with pytest.raises(ValidationError):
            agents.resolve("")


# =============================================================================
# create() — POST /assistants
# =============================================================================


class TestCreate:
    """Create a new agent."""

    def test_create_minimal(self, agents: AgentResource, httpx_mock) -> None:
        """Create with just a name."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/assistants",
            json=_agent_json(),
            status_code=201,
        )
        result = agents.create(name="Support Agent")
        assert isinstance(result, KnowledgeAgent)
        assert result.name == "Support Agent"

    def test_create_sends_body(self, agents: AgentResource, httpx_mock) -> None:
        """Create sends all provided fields."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/assistants",
            json=_agent_json(),
            status_code=201,
        )
        agents.create(
            name="Test Agent",
            description="A test agent",
            tone="friendly",
            answer_prompt="Be helpful.",
            no_answer_message="Sorry, no answer.",
            use_all_sources=True,
            research_allowed=True,
            chat_allowed=False,
            color="#FF0000",
        )
        request = httpx_mock.get_request()
        body = json.loads(request.content)
        assert body["name"] == "Test Agent"
        assert body["description"] == "A test agent"
        assert body["tone"] == "friendly"
        assert body["answerPrompt"] == "Be helpful."
        assert body["noAnswerMessage"] == "Sorry, no answer."
        assert body["useAllSources"] is True
        assert body["researchAllowed"] is True
        assert body["chatAllowed"] is False
        assert body["color"] == "#FF0000"

    def test_create_omits_none_fields(self, agents: AgentResource, httpx_mock) -> None:
        """None/default fields are not sent in the body."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/assistants",
            json=_agent_json(),
            status_code=201,
        )
        agents.create(name="Simple Agent")
        request = httpx_mock.get_request()
        body = json.loads(request.content)
        assert body == {"name": "Simple Agent"}

    def test_create_validates_name(self, agents: AgentResource) -> None:
        """Empty name raises ValidationError."""
        with pytest.raises(ValidationError):
            agents.create(name="")


# =============================================================================
# update() — PUT /assistants/{id}
# =============================================================================


class TestUpdate:
    """Update an existing agent."""

    def test_update(self, agents: AgentResource, httpx_mock) -> None:
        """Update returns updated KnowledgeAgent."""
        httpx_mock.add_response(
            url=f"https://api.getguru.com/api/v1/assistants/{AGENT_UUID}",
            json=_agent_json(name="Updated Agent"),
        )
        result = agents.update(AGENT_UUID, name="Updated Agent")
        assert isinstance(result, KnowledgeAgent)
        assert result.name == "Updated Agent"

    def test_update_sends_body(self, agents: AgentResource, httpx_mock) -> None:
        """Update sends only provided fields."""
        httpx_mock.add_response(
            url=f"https://api.getguru.com/api/v1/assistants/{AGENT_UUID}",
            json=_agent_json(),
        )
        agents.update(AGENT_UUID, name="New Name", tone="casual")
        request = httpx_mock.get_request()
        body = json.loads(request.content)
        assert body["name"] == "New Name"
        assert body["tone"] == "casual"
        assert "description" not in body

    def test_update_validates_agent_id(self, agents: AgentResource) -> None:
        """Empty agent_id raises ValidationError."""
        with pytest.raises(ValidationError):
            agents.update("", name="Test")


# =============================================================================
# delete() — DELETE /assistants/{id}
# =============================================================================


class TestDelete:
    """Delete an agent."""

    def test_delete(self, agents: AgentResource, httpx_mock) -> None:
        """Delete an agent by ID."""
        httpx_mock.add_response(
            url=f"https://api.getguru.com/api/v1/assistants/{AGENT_UUID}",
            method="DELETE",
            status_code=204,
        )
        agents.delete(AGENT_UUID)

    def test_validates_agent_id(self, agents: AgentResource) -> None:
        """Empty agent_id raises ValidationError."""
        with pytest.raises(ValidationError):
            agents.delete("")


# =============================================================================
# list_groups() — GET /assistants/{id}/groups
# =============================================================================


class TestListGroups:
    """List groups with access to an agent."""

    def test_list_groups(self, agents: AgentResource, httpx_mock) -> None:
        """Returns list of KnowledgeAgentAccess objects."""
        httpx_mock.add_response(
            url=f"https://api.getguru.com/api/v1/assistants/{AGENT_UUID}/groups",
            json=[_access_json(), _access_json("g2", "Product")],
        )
        result = agents.list_groups(AGENT_UUID)
        assert len(result) == 2
        assert isinstance(result[0], KnowledgeAgentAccess)
        assert result[0].group is not None
        assert result[0].group.name == "Engineering"

    def test_list_groups_empty(self, agents: AgentResource, httpx_mock) -> None:
        """No groups returns empty list."""
        httpx_mock.add_response(
            url=f"https://api.getguru.com/api/v1/assistants/{AGENT_UUID}/groups",
            json=[],
        )
        result = agents.list_groups(AGENT_UUID)
        assert result == []

    def test_validates_agent_id(self, agents: AgentResource) -> None:
        """Empty agent_id raises ValidationError."""
        with pytest.raises(ValidationError):
            agents.list_groups("")


# =============================================================================
# add_group() — POST /assistants/{id}/groups
# =============================================================================


class TestAddGroup:
    """Grant a group access to an agent."""

    def test_add_group(self, agents: AgentResource, httpx_mock) -> None:
        """Add group returns KnowledgeAgentAccess."""
        httpx_mock.add_response(
            url=f"https://api.getguru.com/api/v1/assistants/{AGENT_UUID}/groups",
            json=_access_json(),
        )
        result = agents.add_group(AGENT_UUID, GROUP_UUID)
        assert isinstance(result, KnowledgeAgentAccess)

    def test_add_group_with_role(self, agents: AgentResource, httpx_mock) -> None:
        """Add group sends role in body."""
        httpx_mock.add_response(
            url=f"https://api.getguru.com/api/v1/assistants/{AGENT_UUID}/groups",
            json=_access_json(),
        )
        agents.add_group(AGENT_UUID, GROUP_UUID, role="ADMIN")
        request = httpx_mock.get_request()
        body = json.loads(request.content)
        assert body["group"]["id"] == GROUP_UUID
        assert body["role"] == "ADMIN"

    def test_validates_agent_id(self, agents: AgentResource) -> None:
        """Empty agent_id raises ValidationError."""
        with pytest.raises(ValidationError):
            agents.add_group("", GROUP_UUID)

    def test_validates_group_id(self, agents: AgentResource) -> None:
        """Empty group_id raises ValidationError."""
        with pytest.raises(ValidationError):
            agents.add_group(AGENT_UUID, "")


# =============================================================================
# update_group() — PUT /assistants/{id}/groups/{gid}
# =============================================================================


class TestUpdateGroup:
    """Update a group's role on an agent."""

    def test_update_group(self, agents: AgentResource, httpx_mock) -> None:
        """Update group returns KnowledgeAgentAccess."""
        httpx_mock.add_response(
            url=f"https://api.getguru.com/api/v1/assistants/{AGENT_UUID}/groups/{GROUP_UUID}",
            json=_access_json(),
        )
        result = agents.update_group(AGENT_UUID, GROUP_UUID, role="ADMIN")
        assert isinstance(result, KnowledgeAgentAccess)

    def test_update_group_sends_body(self, agents: AgentResource, httpx_mock) -> None:
        """Update sends group + role in body."""
        httpx_mock.add_response(
            url=f"https://api.getguru.com/api/v1/assistants/{AGENT_UUID}/groups/{GROUP_UUID}",
            json=_access_json(),
        )
        agents.update_group(AGENT_UUID, GROUP_UUID, role="MEMBER")
        request = httpx_mock.get_request()
        body = json.loads(request.content)
        assert body["group"]["id"] == GROUP_UUID
        assert body["role"] == "MEMBER"

    def test_validates_agent_id(self, agents: AgentResource) -> None:
        """Empty agent_id raises ValidationError."""
        with pytest.raises(ValidationError):
            agents.update_group("", GROUP_UUID, role="MEMBER")


# =============================================================================
# remove_group() — DELETE /assistants/{id}/groups/{gid}
# =============================================================================


class TestRemoveGroup:
    """Revoke a group's access to an agent."""

    def test_remove_group(self, agents: AgentResource, httpx_mock) -> None:
        """Delete revokes group access."""
        httpx_mock.add_response(
            url=f"https://api.getguru.com/api/v1/assistants/{AGENT_UUID}/groups/{GROUP_UUID}",
            method="DELETE",
            status_code=204,
        )
        agents.remove_group(AGENT_UUID, GROUP_UUID)

    def test_validates_agent_id(self, agents: AgentResource) -> None:
        """Empty agent_id raises ValidationError."""
        with pytest.raises(ValidationError):
            agents.remove_group("", GROUP_UUID)

    def test_validates_group_id(self, agents: AgentResource) -> None:
        """Empty group_id raises ValidationError."""
        with pytest.raises(ValidationError):
            agents.remove_group(AGENT_UUID, "")
