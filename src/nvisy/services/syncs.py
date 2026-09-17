"""Synchronization runs for a workspace's connections."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..datatypes import WorkspaceConnectionSync, WorkspaceConnectionSyncPage
from .base import Service

if TYPE_CHECKING:
    from ..pagination import AsyncPaginator


class Syncs(Service):
    """Synchronization runs for a workspace's connections."""

    def list_workspace_syncs(
        self,
        workspace_id: str,
        *,
        provider: str | None = None,
        status: str | None = None,
        limit: int | None = None,
        include_count: bool | None = None,
    ) -> AsyncPaginator[WorkspaceConnectionSyncPage, WorkspaceConnectionSync]:
        """List workspace syncs.

        Args:
            workspace_id: The workspace id.
            provider: Filters the results.
            status: Filters the results.
            limit: Items per page, between 1 and 100.
            include_count: Whether to report the total count, which costs an extra
            query.

        Returns:
            A paginator over the workspace_connection_syncs.

        """
        return self._paginate(
            WorkspaceConnectionSyncPage,
            f"/workspaces/{workspace_id}/syncs",
            params={
                "provider": provider,
                "status": status,
                "limit": limit,
                "includeCount": include_count,
            },
        )

    async def start_sync(
        self,
        workspace_id: str,
        connection_id: str,
    ) -> WorkspaceConnectionSync:
        """Sync connection.

        Args:
            workspace_id: The workspace id.
            connection_id: The connection id.

        Returns:
            The response payload.

        """
        response = await self._request(
            "POST",
            f"/workspaces/{workspace_id}/connections/{connection_id}/sync",
        )
        return WorkspaceConnectionSync.model_validate(response.json())

    def list_syncs(
        self,
        workspace_id: str,
        connection_id: str,
        *,
        limit: int | None = None,
        include_count: bool | None = None,
    ) -> AsyncPaginator[WorkspaceConnectionSyncPage, WorkspaceConnectionSync]:
        """List connection syncs.

        Args:
            workspace_id: The workspace id.
            connection_id: The connection id.
            limit: Items per page, between 1 and 100.
            include_count: Whether to report the total count, which costs an extra
            query.

        Returns:
            A paginator over the workspace_connection_syncs.

        """
        return self._paginate(
            WorkspaceConnectionSyncPage,
            f"/workspaces/{workspace_id}/connections/{connection_id}/syncs",
            params={"limit": limit, "includeCount": include_count},
        )

    async def get_sync(
        self,
        workspace_id: str,
        connection_id: str,
        sync_id: str,
    ) -> WorkspaceConnectionSync:
        """Get connection sync.

        Args:
            workspace_id: The workspace id.
            connection_id: The connection id.
            sync_id: The sync id.

        Returns:
            The response payload.

        """
        response = await self._request(
            "GET",
            f"/workspaces/{workspace_id}/connections/{connection_id}/syncs/{sync_id}",
        )
        return WorkspaceConnectionSync.model_validate(response.json())

    async def cancel_sync(
        self,
        workspace_id: str,
        connection_id: str,
        sync_id: str,
    ) -> WorkspaceConnectionSync:
        """Cancel connection sync.

        Args:
            workspace_id: The workspace id.
            connection_id: The connection id.
            sync_id: The sync id.

        Returns:
            The response payload.

        """
        response = await self._request(
            "POST",
            f"/workspaces/{workspace_id}/connections/{connection_id}/syncs/{sync_id}/cancel",
        )
        return WorkspaceConnectionSync.model_validate(response.json())
