"""Manually defined models for internal API endpoints.

These models cover resources that are NOT in the Guru public Swagger spec
(pages, page drafts, page permissions, page draft collaborators). They are
used by the internal API endpoints documented in guru-cli's ADR-014.

Unlike _generated.py, these models are hand-written. They follow the same
conventions: GuruModel base class, snake_case fields with camelCase aliases,
all fields optional (API may omit any field).
"""

from __future__ import annotations

from typing import Annotated

from pydantic import AwareDatetime, Field

from guru_sdk.models._base import GuruModel
from guru_sdk.models._generated import Team, User

# =============================================================================
# Page Draft — response model for /pagedrafts endpoints
# =============================================================================


class PageDraft(GuruModel):
    """A page draft — an unpublished page edit.

    Similar to Page but includes page_id (link to the published page) and
    created_by (the user who created the draft). These fields are not on the
    generated Page model because page drafts are internal API only.
    """

    id: str | None = None
    page_id: Annotated[
        str | None, Field(alias="pageId", description="ID of the published page this draft is for")
    ] = None
    title: str | None = None
    json_content: Annotated[
        str | None, Field(alias="jsonContent", description="The JSON content of the page draft")
    ] = None
    hero_image: Annotated[
        str | None, Field(alias="heroImage", description="The hero image link")
    ] = None
    badge_emoji: Annotated[
        str | None, Field(alias="badgeEmoji", description="Emoji badge for the page draft")
    ] = None
    parent_page_id: Annotated[
        str | None, Field(alias="parentPageId", description="ID of the parent page")
    ] = None
    knowledge_agent_id: Annotated[
        str | None,
        Field(alias="knowledgeAgentId", description="ID of the default Knowledge Agent"),
    ] = None
    draft: bool | None = None
    editable: bool | None = None
    only_navigable: Annotated[
        bool | None,
        Field(alias="onlyNavigable", description="Navigation-only page (no content)"),
    ] = None
    date_created: Annotated[
        AwareDatetime | None, Field(alias="dateCreated")
    ] = None
    last_modified: Annotated[
        AwareDatetime | None, Field(alias="lastModified")
    ] = None
    last_modified_by: Annotated[
        User | None, Field(alias="lastModifiedBy")
    ] = None
    created_by: Annotated[
        User | None, Field(alias="createdBy")
    ] = None
    team: Team | None = None


# =============================================================================
# Page Permission — permission entry on a page
# =============================================================================


class PagePermission(GuruModel):
    """A permission entry on a page — user or user-group with a role.

    Returned by GET /pages/{id}/permissions. The type field indicates whether
    this permission is for an individual user or a user-group.
    """

    id: str | None = None
    type: str | None = None  # "user" or "user-group"
    permission_type: Annotated[
        str | None,
        Field(alias="permissionType", description="EDITOR or VIEWER"),
    ] = None
    # objectRole is a nested object in the API — keep as dict for flexibility
    object_role: Annotated[
        dict[str, str | None] | None,
        Field(alias="objectRole"),
    ] = None


# =============================================================================
# Page Draft Collaborator — collaborator on a page draft
# =============================================================================


class PageDraftCollaborator(GuruModel):
    """A collaborator on a page draft — user or user-group with a role.

    Returned by GET /pagedrafts/{id}/collaborators.
    """

    id: str | None = None
    type: str | None = None  # "user" or "user-group"
    object_role: Annotated[
        dict[str, str | None] | None,
        Field(alias="objectRole"),
    ] = None
    user: User | None = None
    group: Annotated[dict[str, str | None] | None, Field(None)] = None
