"""Connections to external file services and object stores."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..datatypes import (
    CreateWorkspaceConnection,
    ExportWorkspaceFiles,
    ImportWorkspaceFiles,
    OAuthStartResponse,
    StartFileServiceOAuth,
    UpdateWorkspaceConnection,
    WorkspaceConnection,
    WorkspaceConnectionPage,
    WorkspaceConnectionSync,
    WorkspaceConnectionVerification,
    WorkspacePickerToken,
    WorkspacePickerTokenRequest,
)
from .base import Service, serialize

if TYPE_CHECKING:
    from ..pagination import AsyncPaginator


class Connections(Service):
    """Connections to external file services and object stores."""

    def list_connections(
        self,
        workspace_id: str,
        *,
        provider: str | None = None,
        limit: int | None = None,
        include_count: bool | None = None,
    ) -> AsyncPaginator[WorkspaceConnectionPage, WorkspaceConnection]:
        """List connections.

        Args:
            workspace_id: The workspace id.
            provider: Filters the results.
            limit: Items per page, between 1 and 100.
            include_count: Whether to report the total count, which costs an extra
            query.

        Returns:
            A paginator over the workspace_connections.

        """
        return self._paginate(
            WorkspaceConnectionPage,
            f"/workspaces/{workspace_id}/connections",
            params={
                "provider": provider,
                "limit": limit,
                "includeCount": include_count,
            },
        )

    async def create_connection(
        self,
        workspace_id: str,
        body: CreateWorkspaceConnection,
    ) -> WorkspaceConnection:
        """Create connection.

        Args:
            workspace_id: The workspace id.
            body: The request payload.

        Returns:
            The response payload.

        """
        response = await self._request(
            "POST",
            f"/workspaces/{workspace_id}/connections",
            json=serialize(body),
        )
        return WorkspaceConnection.model_validate(response.json())

    async def get_connection(
        self,
        workspace_id: str,
        connection_id: str,
    ) -> WorkspaceConnection:
        """Get connection.

        Args:
            workspace_id: The workspace id.
            connection_id: The connection id.

        Returns:
            The response payload.

        """
        response = await self._request(
            "GET",
            f"/workspaces/{workspace_id}/connections/{connection_id}",
        )
        return WorkspaceConnection.model_validate(response.json())

    async def update_connection(
        self,
        workspace_id: str,
        connection_id: str,
        body: UpdateWorkspaceConnection,
    ) -> WorkspaceConnection:
        """Update connection.

        Args:
            workspace_id: The workspace id.
            connection_id: The connection id.
            body: The request payload.

        Returns:
            The response payload.

        """
        response = await self._request(
            "PATCH",
            f"/workspaces/{workspace_id}/connections/{connection_id}",
            json=serialize(body),
        )
        return WorkspaceConnection.model_validate(response.json())

    async def delete_connection(self, workspace_id: str, connection_id: str) -> None:
        """Delete connection.

        Args:
            workspace_id: The workspace id.
            connection_id: The connection id.

        """
        await self._request(
            "DELETE",
            f"/workspaces/{workspace_id}/connections/{connection_id}",
        )

    async def verify_connection(
        self,
        workspace_id: str,
        connection_id: str,
    ) -> WorkspaceConnectionVerification:
        """Verify connection.

        Args:
            workspace_id: The workspace id.
            connection_id: The connection id.

        Returns:
            The response payload.

        """
        response = await self._request(
            "POST",
            f"/workspaces/{workspace_id}/connections/{connection_id}/verify",
        )
        return WorkspaceConnectionVerification.model_validate(response.json())

    async def start_file_service_o_auth(
        self,
        workspace_id: str,
        provider: str,
        body: StartFileServiceOAuth,
    ) -> OAuthStartResponse:
        """Start cloud file OAuth.

        Args:
            workspace_id: The workspace id.
            provider: The provider.
            body: The request payload.

        Returns:
            The response payload.

        """
        response = await self._request(
            "POST",
            f"/workspaces/{workspace_id}/connections/oauth/{provider}/start",
            json=serialize(body),
        )
        return OAuthStartResponse.model_validate(response.json())

    async def import_files(
        self,
        workspace_id: str,
        connection_id: str,
        body: ImportWorkspaceFiles,
    ) -> WorkspaceConnectionSync:
        """Import selected files.

        Args:
            workspace_id: The workspace id.
            connection_id: The connection id.
            body: The request payload.

        Returns:
            The response payload.

        """
        response = await self._request(
            "POST",
            f"/workspaces/{workspace_id}/connections/{connection_id}/import",
            json=serialize(body),
        )
        return WorkspaceConnectionSync.model_validate(response.json())

    async def export_files(
        self,
        workspace_id: str,
        connection_id: str,
        body: ExportWorkspaceFiles,
    ) -> WorkspaceConnectionSync:
        """Export files to connection.

        Args:
            workspace_id: The workspace id.
            connection_id: The connection id.
            body: The request payload.

        Returns:
            The response payload.

        """
        response = await self._request(
            "POST",
            f"/workspaces/{workspace_id}/connections/{connection_id}/export",
            json=serialize(body),
        )
        return WorkspaceConnectionSync.model_validate(response.json())

    async def get_picker_token(
        self,
        workspace_id: str,
        connection_id: str,
        body: WorkspacePickerTokenRequest,
    ) -> WorkspacePickerToken:
        """Mint picker token.

        Args:
            workspace_id: The workspace id.
            connection_id: The connection id.
            body: The request payload.

        Returns:
            The response payload.

        """
        response = await self._request(
            "POST",
            f"/workspaces/{workspace_id}/connections/{connection_id}/picker-token",
            json=serialize(body),
        )
        return WorkspacePickerToken.model_validate(response.json())
