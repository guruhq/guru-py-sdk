"""Source resource — read-only operations on Guru sources (external connectors).

Sources represent external data connectors (Confluence, Jira, Slack, etc.)
that sync content into Guru. This resource provides read access to source
metadata, object type definitions, and grouped connection views.

API surface mirrors guru-cli's SourceResource (read operations). Facet
discovery (facet_values, facet_hierarchy) is deferred — those endpoints
are not in the public Swagger spec and their response models aren't generated.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from guru_sdk._compat import validate_input

if TYPE_CHECKING:
    import builtins
from guru_sdk.models._generated import (
    GroupedSourceConnection,
    ObjectType,
    Source,
)
from guru_sdk.resources._base import BaseResource

# =============================================================================
# Public API — SourceResource
# =============================================================================


class SourceResource(BaseResource):
    """Guru Sources — read-only access to external data connectors.

    Methods:
        list()              — list all sources (GET /sources)
        get()               — get a source by ID (GET /sources/{sourceId})
        object_types()      — list object types (GET /sources/{sourceId}/objecttypes)
        connections()       — list grouped connections (GET /sources/groups)
        get_connection()    — get a grouped connection (GET /sources/groups/{groupId})
    """

    # -------------------------------------------------------------------------
    # Source CRUD (read-only)
    # -------------------------------------------------------------------------

    def list(self) -> list[Source]:
        """List all sources.

        Returns all external data connectors configured for this team.
        """
        return self._http.get_list("/sources", Source)

    def get(self, source_id: str) -> Source:
        """Get a source by ID.

        Args:
            source_id: Source UUID.
        """
        validate_input(source_id, "source_id")
        return self._http.get(f"/sources/{source_id}", Source)

    # -------------------------------------------------------------------------
    # Object Types — discover the schema of a source's data
    # -------------------------------------------------------------------------

    def object_types(self, source_id: str) -> builtins.list[ObjectType]:
        """List object types and their facet definitions for a source.

        Object types describe the kinds of records a source syncs (e.g., a
        Confluence source has "Pages" and "Spaces" object types, each with
        their own facets and fields).

        Args:
            source_id: Source UUID.
        """
        validate_input(source_id, "source_id")
        return self._http.get_list(f"/sources/{source_id}/objecttypes", ObjectType)

    # -------------------------------------------------------------------------
    # Grouped Connections — aggregate view of source connections
    # -------------------------------------------------------------------------

    def connections(self) -> builtins.list[GroupedSourceConnection]:
        """List grouped source connections.

        Returns connections grouped by source definition (e.g., all Confluence
        connections together, all Jira connections together).
        """
        return self._http.get_list("/sources/groups", GroupedSourceConnection)

    def get_connection(self, group_id: str) -> GroupedSourceConnection:
        """Get a single grouped source connection with its sources.

        Args:
            group_id: Connection group UUID.
        """
        validate_input(group_id, "group_id")
        return self._http.get(f"/sources/groups/{group_id}", GroupedSourceConnection)
