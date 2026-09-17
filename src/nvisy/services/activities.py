"""A workspace's activity log."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..datatypes import WorkspaceActivity, WorkspaceActivityPage
from .base import Service

if TYPE_CHECKING:
    from ..pagination import AsyncPaginator


class Activities(Service):
    """A workspace's activity log."""

    def list_activities(
        self,
        workspace_id: str,
        *,
        actor: str | None = None,
        type_: str | None = None,
        from_: str | None = None,
        to: str | None = None,
        limit: int | None = None,
        include_count: bool | None = None,
    ) -> AsyncPaginator[WorkspaceActivityPage, WorkspaceActivity]:
        """List workspace activities.

        Args:
            workspace_id: The workspace id.
            actor: Filters the results.
            type_: Filters the results.
            from_: Filters the results.
            to: Filters the results.
            limit: Items per page, between 1 and 100.
            include_count: Whether to report the total count, which costs an extra
            query.

        Returns:
            A paginator over the workspace_activitys.

        """
        return self._paginate(
            WorkspaceActivityPage,
            f"/workspaces/{workspace_id}/activities",
            params={
                "actor": actor,
                "type": type_,
                "from": from_,
                "to": to,
                "limit": limit,
                "includeCount": include_count,
            },
        )

    async def export_activities(
        self,
        workspace_id: str,
        *,
        actor: str | None = None,
        type_: str | None = None,
        from_: str | None = None,
        to: str | None = None,
        format_: str | None = None,
    ) -> bytes:
        """Export workspace activities.

        Args:
            workspace_id: The workspace id.
            actor: Filters the results.
            type_: Filters the results.
            from_: Filters the results.
            to: Filters the results.
            format_: Filters the results.

        Returns:
            The raw response body.

        """
        response = await self._request(
            "GET",
            f"/workspaces/{workspace_id}/activities/export",
            params={
                "actor": actor,
                "type": type_,
                "from": from_,
                "to": to,
                "format": format_,
            },
        )
        return response.content
