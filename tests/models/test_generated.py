"""Tests for auto-generated Pydantic v2 models.

These tests validate that:
1. Generated models inherit from GuruModel (not raw BaseModel)
2. GuruModel behavior is inherited: extra="ignore", frozen=True, populate_by_name=True
3. Fields are snake_case with camelCase aliases for API compatibility
4. Core models can be instantiated from realistic API response shapes
5. Cross-references between models work (e.g., Card → User, Card → CollectionModel)
6. Enum fields validate correctly
7. Excluded schemas (Board, etc.) are not present
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from guru_sdk.models._base import GuruModel
from guru_sdk.models._generated import (
    Card,
    CollectionModel,
    Folder,
    KnowledgeAgent,
    NewCard,
    Page,
    Source,
    Tag,
    Team,
    User,
    UserGroup,
    WhoAmI,
)

# =============================================================================
# GuruModel Inheritance — all generated models must inherit from GuruModel
# =============================================================================


class TestGuruModelInheritance:
    """Verify generated models inherit from GuruModel, not raw BaseModel."""

    @pytest.mark.parametrize(
        "model_cls",
        [Card, Folder, CollectionModel, Tag, User, Team, UserGroup, KnowledgeAgent, Page, Source],
    )
    def test_inherits_from_guru_model(self, model_cls: type) -> None:
        assert issubclass(model_cls, GuruModel)

    @pytest.mark.parametrize(
        "model_cls",
        [Card, Folder, CollectionModel, Tag, User],
    )
    def test_extra_ignore(self, model_cls: type[GuruModel]) -> None:
        """extra='ignore' means unknown fields are silently dropped."""
        config = model_cls.model_config
        assert config.get("extra") == "ignore"

    @pytest.mark.parametrize(
        "model_cls",
        [Card, Folder, CollectionModel, Tag, User],
    )
    def test_frozen(self, model_cls: type[GuruModel]) -> None:
        """frozen=True means models are immutable."""
        config = model_cls.model_config
        assert config.get("frozen") is True


# =============================================================================
# Snake_case Field Naming — Pythonic access with camelCase API compat
# =============================================================================


class TestSnakeCaseFields:
    """Verify fields are snake_case with camelCase aliases."""

    def test_card_snake_case_access(self) -> None:
        """Card fields are accessed via snake_case names."""
        card = Card(content="<p>Hi</p>", preferredPhrase="Test")
        assert card.preferred_phrase == "Test"
        assert card.content == "<p>Hi</p>"

    def test_card_camel_case_creation(self) -> None:
        """Cards can be created with camelCase keys (API response compat)."""
        card = Card(
            content="<p>Hi</p>",
            preferredPhrase="Test",
            verificationState="TRUSTED",
            shareStatus="TEAM",
        )
        assert card.preferred_phrase == "Test"
        assert card.verification_state is not None
        assert card.verification_state.value == "TRUSTED"
        assert card.share_status is not None
        assert card.share_status.value == "TEAM"

    def test_nested_user_snake_case(self) -> None:
        """Nested objects also use snake_case."""
        card = Card(
            content="<p>Hi</p>",
            preferredPhrase="Test",
            owner={"firstName": "Jane", "lastName": "Doe", "email": "jane@example.com"},
        )
        assert card.owner is not None
        assert card.owner.first_name == "Jane"
        assert card.owner.last_name == "Doe"

    def test_folder_snake_case(self) -> None:
        """Folder fields use snake_case."""
        folder = Folder(title="Getting Started", numberOfFacts=12)
        assert folder.number_of_facts == 12

    def test_tag_snake_case(self) -> None:
        """Tag fields use snake_case."""
        tag = Tag(id="tag-1", value="onboarding", numberOfCards=42, categoryId="cat-1")
        assert tag.number_of_cards == 42
        assert tag.category_id == "cat-1"

    def test_model_dump_by_alias(self) -> None:
        """model_dump(by_alias=True) serializes back to camelCase for API calls."""
        card = Card(content="<p>Hi</p>", preferredPhrase="Test")
        data = card.model_dump(by_alias=True, exclude_none=True)
        assert "preferredPhrase" in data
        assert data["preferredPhrase"] == "Test"
        # snake_case key should NOT appear when serializing by alias
        assert "preferred_phrase" not in data


# =============================================================================
# Card Model — the most complex and important model
# =============================================================================


class TestCardModel:
    """Tests for the Card model."""

    def test_minimal_card(self) -> None:
        """Card can be created with just required fields."""
        card = Card(content="<p>Hello</p>", preferredPhrase="My Card")
        assert card.content == "<p>Hello</p>"
        assert card.preferred_phrase == "My Card"

    def test_card_with_all_core_fields(self) -> None:
        """Card can be created with a full API response shape."""
        data = {
            "id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
            "content": "<p>Content</p>",
            "preferredPhrase": "Test Card",
            "slug": "test-card-AbCdEf",
            "verificationState": "TRUSTED",
            "shareStatus": "TEAM",
            "archived": False,
            "version": 3,
            "commentCount": 5,
        }
        card = Card(**data)
        assert card.id == "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
        assert card.verification_state is not None
        assert card.verification_state.value == "TRUSTED"
        assert card.version == 3
        assert card.comment_count == 5

    def test_card_extra_fields_ignored(self) -> None:
        """Unknown API fields are silently dropped (forward compat)."""
        card = Card(
            content="<p>Hi</p>",
            preferredPhrase="Test",
            brandNewApiField="should be ignored",
            anotherNewField=42,
        )
        assert card.content == "<p>Hi</p>"
        assert not hasattr(card, "brand_new_api_field")

    def test_card_frozen(self) -> None:
        """Cards are immutable — mutations go through resource methods."""
        card = Card(content="<p>Hi</p>", preferredPhrase="Test")
        with pytest.raises(ValidationError):
            card.content = "new content"  # type: ignore[misc]

    def test_card_with_nested_collection(self) -> None:
        """Card can contain a nested CollectionModel."""
        card = Card(
            content="<p>Hi</p>",
            preferredPhrase="Test",
            collection={
                "id": "col-123",
                "name": "Engineering",
                "color": "#1A73E8",
            },
        )
        assert card.collection is not None
        assert card.collection.name == "Engineering"

    def test_card_with_tags(self) -> None:
        """Card can contain an array of Tag objects."""
        card = Card(
            content="<p>Hi</p>",
            preferredPhrase="Test",
            tags=[
                {"id": "tag-1", "value": "onboarding"},
                {"id": "tag-2", "value": "engineering"},
            ],
        )
        assert card.tags is not None
        assert len(card.tags) == 2
        assert card.tags[0].value == "onboarding"


# =============================================================================
# Folder Model
# =============================================================================


class TestFolderModel:
    def test_minimal_folder(self) -> None:
        folder = Folder()
        assert folder.id is None
        assert folder.title is None

    def test_folder_from_api_response(self) -> None:
        folder = Folder(
            id="folder-123",
            title="Getting Started",
            description="Onboarding docs",
            home=True,
            numberOfFacts=12,
        )
        assert folder.title == "Getting Started"
        assert folder.home is True
        assert folder.number_of_facts == 12


# =============================================================================
# Other Core Models
# =============================================================================


class TestCollectionModel:
    def test_basic_collection(self) -> None:
        col = CollectionModel(
            id="col-123",
            name="Engineering",
            description="Engineering knowledge base",
            color="#1A73E8",
        )
        assert col.name == "Engineering"
        assert col.color == "#1A73E8"


class TestTagModel:
    def test_basic_tag(self) -> None:
        tag = Tag(id="tag-1", value="onboarding", numberOfCards=42)
        assert tag.value == "onboarding"
        assert tag.number_of_cards == 42


class TestUserModel:
    def test_basic_user(self) -> None:
        user = User(
            firstName="Jane",
            lastName="Doe",
            email="jane@example.com",
        )
        assert user.first_name == "Jane"
        assert user.email == "jane@example.com"


class TestTeamModel:
    def test_basic_team(self) -> None:
        team = Team(id="team-123", name="Acme Corp")
        assert team.name == "Acme Corp"


class TestWhoAmI:
    def test_whoami(self) -> None:
        # WhoAmI has a required tokenType field
        me = WhoAmI(
            tokenType="API",
            user={"firstName": "Jane", "lastName": "Doe", "email": "jane@example.com"},
            team={"id": "team-123", "name": "Acme Corp"},
        )
        assert me.user is not None
        assert me.team is not None


class TestKnowledgeAgent:
    def test_basic_agent(self) -> None:
        # KnowledgeAgent.id is a UUID field in the Swagger spec
        agent = KnowledgeAgent(
            id="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
            name="Support Agent",
            description="Answers support questions",
        )
        assert agent.name == "Support Agent"


# =============================================================================
# Write Input Models
# =============================================================================


class TestNewCard:
    def test_new_card(self) -> None:
        nc = NewCard(content="<p>Hello</p>", preferredPhrase="New Card")
        assert nc.content == "<p>Hello</p>"
        assert nc.preferred_phrase == "New Card"


# =============================================================================
# Excluded Schemas — must NOT be present in generated output
# =============================================================================


class TestExcludedSchemas:
    """Verify that deprecated schemas were filtered out during generation."""

    @pytest.mark.parametrize(
        "class_name",
        [
            "Board",
            "BoardIdExpression",
            "BoardPermission",
            "BoardPermissions",
            "Framework",
            "Question",
        ],
    )
    def test_excluded_schema_not_importable(self, class_name: str) -> None:
        """Excluded schemas should not exist in the generated module."""
        import guru_sdk.models._generated as gen

        assert not hasattr(gen, class_name), f"{class_name} should have been excluded"
