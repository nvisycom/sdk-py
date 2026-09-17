"""Redaction policies in a workspace."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..datatypes import (
    CreateWorkspacePolicy,
    UpdateWorkspacePolicy,
    WorkspacePolicy,
    WorkspacePolicySummary,
    WorkspacePolicySummaryPage,
)
from .base import Service, serialize

if TYPE_CHECKING:
    from ..pagination import AsyncPaginator


class Policies(Service):
    """Redaction policies in a workspace."""

    def list_policies(
        self,
        workspace_id: str,
        *,
        kind: str | None = None,
        limit: int | None = None,
        include_count: bool | None = None,
    ) -> AsyncPaginator[WorkspacePolicySummaryPage, WorkspacePolicySummary]:
        """List policies.

        Args:
            workspace_id: The workspace id.
            kind: Filters the results.
            limit: Items per page, between 1 and 100.
            include_count: Whether to report the total count, which costs an extra
            query.

        Returns:
            A paginator over the workspace_policy_summarys.

        """
        return self._paginate(
            WorkspacePolicySummaryPage,
            f"/workspaces/{workspace_id}/policies",
            params={
                "kind": kind,
                "limit": limit,
                "includeCount": include_count,
            },
        )

    async def create_policy(
        self,
        workspace_id: str,
        body: CreateWorkspacePolicy,
    ) -> WorkspacePolicy:
        """Create policy.

        Args:
            workspace_id: The workspace id.
            body: The request payload.

        Returns:
            The response payload.

        """
        response = await self._request(
            "POST",
            f"/workspaces/{workspace_id}/policies",
            json=serialize(body),
        )
        return WorkspacePolicy.model_validate(response.json())

    async def get_policy(self, workspace_id: str, policy_id: str) -> WorkspacePolicy:
        """Get policy.

        Args:
            workspace_id: The workspace id.
            policy_id: The policy id.

        Returns:
            The response payload.

        """
        response = await self._request(
            "GET",
            f"/workspaces/{workspace_id}/policies/{policy_id}",
        )
        return WorkspacePolicy.model_validate(response.json())

    async def update_policy(
        self,
        workspace_id: str,
        policy_id: str,
        body: UpdateWorkspacePolicy,
    ) -> WorkspacePolicy:
        """Update policy.

        Args:
            workspace_id: The workspace id.
            policy_id: The policy id.
            body: The request payload.

        Returns:
            The response payload.

        """
        response = await self._request(
            "PATCH",
            f"/workspaces/{workspace_id}/policies/{policy_id}",
            json=serialize(body),
        )
        return WorkspacePolicy.model_validate(response.json())

    async def delete_policy(self, workspace_id: str, policy_id: str) -> None:
        """Delete policy.

        Args:
            workspace_id: The workspace id.
            policy_id: The policy id.

        """
        await self._request(
            "DELETE",
            f"/workspaces/{workspace_id}/policies/{policy_id}",
        )
