"""Inference providers configured for a workspace."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..datatypes import (
    CreateWorkspaceProvider,
    UpdateWorkspaceProvider,
    WorkspaceConnectionVerification,
    WorkspaceProvider,
    WorkspaceProviderPage,
)
from .base import Service, serialize

if TYPE_CHECKING:
    from ..pagination import AsyncPaginator


class Providers(Service):
    """Inference providers configured for a workspace."""

    def list_providers(
        self,
        workspace_id: str,
        *,
        provider: str | None = None,
        limit: int | None = None,
        include_count: bool | None = None,
    ) -> AsyncPaginator[WorkspaceProviderPage, WorkspaceProvider]:
        """List providers.

        Args:
            workspace_id: The workspace id.
            provider: Filters the results.
            limit: Items per page, between 1 and 100.
            include_count: Whether to report the total count, which costs an extra
            query.

        Returns:
            A paginator over the workspace_providers.

        """
        return self._paginate(
            WorkspaceProviderPage,
            f"/workspaces/{workspace_id}/providers",
            params={
                "provider": provider,
                "limit": limit,
                "includeCount": include_count,
            },
        )

    async def create_provider(
        self,
        workspace_id: str,
        body: CreateWorkspaceProvider,
    ) -> WorkspaceProvider:
        """Create provider.

        Args:
            workspace_id: The workspace id.
            body: The request payload.

        Returns:
            The response payload.

        """
        response = await self._request(
            "POST",
            f"/workspaces/{workspace_id}/providers",
            json=serialize(body),
        )
        return WorkspaceProvider.model_validate(response.json())

    async def get_provider(
        self,
        workspace_id: str,
        provider_id: str,
    ) -> WorkspaceProvider:
        """Get provider.

        Args:
            workspace_id: The workspace id.
            provider_id: The provider id.

        Returns:
            The response payload.

        """
        response = await self._request(
            "GET",
            f"/workspaces/{workspace_id}/providers/{provider_id}",
        )
        return WorkspaceProvider.model_validate(response.json())

    async def update_provider(
        self,
        workspace_id: str,
        provider_id: str,
        body: UpdateWorkspaceProvider,
    ) -> WorkspaceProvider:
        """Update provider.

        Args:
            workspace_id: The workspace id.
            provider_id: The provider id.
            body: The request payload.

        Returns:
            The response payload.

        """
        response = await self._request(
            "PATCH",
            f"/workspaces/{workspace_id}/providers/{provider_id}",
            json=serialize(body),
        )
        return WorkspaceProvider.model_validate(response.json())

    async def delete_provider(self, workspace_id: str, provider_id: str) -> None:
        """Delete provider.

        Args:
            workspace_id: The workspace id.
            provider_id: The provider id.

        """
        await self._request(
            "DELETE",
            f"/workspaces/{workspace_id}/providers/{provider_id}",
        )

    async def verify_provider(
        self,
        workspace_id: str,
        provider_id: str,
    ) -> WorkspaceConnectionVerification:
        """Verify provider.

        Args:
            workspace_id: The workspace id.
            provider_id: The provider id.

        Returns:
            The response payload.

        """
        response = await self._request(
            "POST",
            f"/workspaces/{workspace_id}/providers/{provider_id}/verify",
        )
        return WorkspaceConnectionVerification.model_validate(response.json())
