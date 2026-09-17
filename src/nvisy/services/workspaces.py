"""Workspace management."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..datatypes import (
    CreateWorkspace,
    UpdateWorkspace,
    UpdateWorkspaceNotificationSettings,
    Workspace,
    WorkspaceNotificationSettings,
    WorkspacePage,
)
from .base import Service, serialize

if TYPE_CHECKING:
    from ..pagination import AsyncPaginator


class Workspaces(Service):
    """Workspaces, their notification settings, and their avatars."""

    def list_workspaces(
        self,
        *,
        limit: int | None = None,
        include_count: bool | None = None,
    ) -> AsyncPaginator[WorkspacePage, Workspace]:
        """List the workspaces the account belongs to.

        Args:
            limit: Items per page, between 1 and 100.
            include_count: Whether to report the total count, which costs an
                extra query.

        Returns:
            A paginator over the workspaces.
        """
        return self._paginate(
            WorkspacePage,
            "/workspaces",
            params={"limit": limit, "includeCount": include_count},
        )

    async def get_workspace(self, workspace_id: str) -> Workspace:
        """Get a workspace.

        Args:
            workspace_id: The workspace's id.

        Returns:
            The workspace.
        """
        response = await self._request("GET", f"/workspaces/{workspace_id}")
        return Workspace.model_validate(response.json())

    async def create_workspace(self, workspace: CreateWorkspace) -> Workspace:
        """Create a workspace.

        Args:
            workspace: The workspace to create.

        Returns:
            The created workspace.
        """
        response = await self._request("POST", "/workspaces", json=serialize(workspace))
        return Workspace.model_validate(response.json())

    async def update_workspace(
        self, workspace_id: str, updates: UpdateWorkspace
    ) -> Workspace:
        """Update a workspace.

        Args:
            workspace_id: The workspace's id.
            updates: The fields to change.

        Returns:
            The updated workspace.
        """
        response = await self._request(
            "PATCH", f"/workspaces/{workspace_id}", json=serialize(updates)
        )
        return Workspace.model_validate(response.json())

    async def delete_workspace(self, workspace_id: str) -> None:
        """Delete a workspace.

        Args:
            workspace_id: The workspace's id.
        """
        await self._request("DELETE", f"/workspaces/{workspace_id}")

    async def get_notification_settings(
        self, workspace_id: str
    ) -> WorkspaceNotificationSettings:
        """Get a workspace's notification settings.

        Args:
            workspace_id: The workspace's id.

        Returns:
            The notification settings.
        """
        response = await self._request(
            "GET", f"/workspaces/{workspace_id}/notifications"
        )
        return WorkspaceNotificationSettings.model_validate(response.json())

    async def update_notification_settings(
        self,
        workspace_id: str,
        settings: UpdateWorkspaceNotificationSettings,
    ) -> WorkspaceNotificationSettings:
        """Update a workspace's notification settings.

        Args:
            workspace_id: The workspace's id.
            settings: The settings to change.

        Returns:
            The updated notification settings.
        """
        response = await self._request(
            "PATCH",
            f"/workspaces/{workspace_id}/notifications",
            json=serialize(settings),
        )
        return WorkspaceNotificationSettings.model_validate(response.json())

    async def upload_avatar(self, workspace_id: str, avatar: Any) -> None:
        """Set a workspace's avatar.

        Args:
            workspace_id: The workspace's id.
            avatar: The image to upload, as accepted by httpx: bytes, a file
                object, or a (filename, content, content_type) tuple.
        """
        await self._request(
            "PUT",
            f"/workspaces/{workspace_id}/avatar",
            files={"avatar": avatar},
        )

    async def delete_avatar(self, workspace_id: str) -> None:
        """Remove a workspace's avatar.

        Args:
            workspace_id: The workspace's id.
        """
        await self._request("DELETE", f"/workspaces/{workspace_id}/avatar")
