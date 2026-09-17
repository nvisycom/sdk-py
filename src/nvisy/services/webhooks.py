"""Webhook endpoints registered for a workspace."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..datatypes import (
    CreateWorkspaceWebhook,
    TestWorkspaceWebhook,
    UpdateWorkspaceWebhook,
    WorkspaceWebhook,
    WorkspaceWebhookCreated,
    WorkspaceWebhookPage,
    WorkspaceWebhookResult,
)
from .base import Service, serialize

if TYPE_CHECKING:
    from ..pagination import AsyncPaginator


class Webhooks(Service):
    """Webhook endpoints registered for a workspace."""

    def list_webhooks(
        self,
        workspace_id: str,
        *,
        limit: int | None = None,
        include_count: bool | None = None,
    ) -> AsyncPaginator[WorkspaceWebhookPage, WorkspaceWebhook]:
        """List webhooks.

        Args:
            workspace_id: The workspace id.
            limit: Items per page, between 1 and 100.
            include_count: Whether to report the total count, which costs an extra
            query.

        Returns:
            A paginator over the workspace_webhooks.

        """
        return self._paginate(
            WorkspaceWebhookPage,
            f"/workspaces/{workspace_id}/webhooks",
            params={"limit": limit, "includeCount": include_count},
        )

    async def create_webhook(
        self,
        workspace_id: str,
        body: CreateWorkspaceWebhook,
    ) -> WorkspaceWebhookCreated:
        """Create webhook.

        Args:
            workspace_id: The workspace id.
            body: The request payload.

        Returns:
            The response payload.

        """
        response = await self._request(
            "POST",
            f"/workspaces/{workspace_id}/webhooks",
            json=serialize(body),
        )
        return WorkspaceWebhookCreated.model_validate(response.json())

    async def get_webhook(self, workspace_id: str, webhook_id: str) -> WorkspaceWebhook:
        """Get webhook.

        Args:
            workspace_id: The workspace id.
            webhook_id: The webhook id.

        Returns:
            The response payload.

        """
        response = await self._request(
            "GET",
            f"/workspaces/{workspace_id}/webhooks/{webhook_id}",
        )
        return WorkspaceWebhook.model_validate(response.json())

    async def update_webhook(
        self,
        workspace_id: str,
        webhook_id: str,
        body: UpdateWorkspaceWebhook,
    ) -> WorkspaceWebhook:
        """Update webhook.

        Args:
            workspace_id: The workspace id.
            webhook_id: The webhook id.
            body: The request payload.

        Returns:
            The response payload.

        """
        response = await self._request(
            "PATCH",
            f"/workspaces/{workspace_id}/webhooks/{webhook_id}",
            json=serialize(body),
        )
        return WorkspaceWebhook.model_validate(response.json())

    async def delete_webhook(self, workspace_id: str, webhook_id: str) -> None:
        """Delete webhook.

        Args:
            workspace_id: The workspace id.
            webhook_id: The webhook id.

        """
        await self._request(
            "DELETE",
            f"/workspaces/{workspace_id}/webhooks/{webhook_id}",
        )

    async def test_webhook(
        self,
        workspace_id: str,
        webhook_id: str,
        body: TestWorkspaceWebhook,
    ) -> WorkspaceWebhookResult:
        """Test webhook.

        Args:
            workspace_id: The workspace id.
            webhook_id: The webhook id.
            body: The request payload.

        Returns:
            The response payload.

        """
        response = await self._request(
            "POST",
            f"/workspaces/{workspace_id}/webhooks/{webhook_id}/test",
            json=serialize(body),
        )
        return WorkspaceWebhookResult.model_validate(response.json())
