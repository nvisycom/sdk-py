"""Members of a workspace."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..datatypes import UpdateWorkspaceMember, WorkspaceMember, WorkspaceMemberPage
from .base import Service, serialize

if TYPE_CHECKING:
    from ..pagination import AsyncPaginator


class Members(Service):
    """Members of a workspace."""

    def list_members(
        self,
        workspace_id: str,
        *,
        order: str | None = None,
        role: str | None = None,
        sort_by: str | None = None,
        limit: int | None = None,
        include_count: bool | None = None,
    ) -> AsyncPaginator[WorkspaceMemberPage, WorkspaceMember]:
        """List members.

        Args:
            workspace_id: The workspace id.
            order: Filters the results.
            role: Filters the results.
            sort_by: Filters the results.
            limit: Items per page, between 1 and 100.
            include_count: Whether to report the total count, which costs an extra
            query.

        Returns:
            A paginator over the workspace_members.

        """
        return self._paginate(
            WorkspaceMemberPage,
            f"/workspaces/{workspace_id}/members",
            params={
                "order": order,
                "role": role,
                "sortBy": sort_by,
                "limit": limit,
                "includeCount": include_count,
            },
        )

    async def get_member(self, workspace_id: str, account_id: str) -> WorkspaceMember:
        """Get member.

        Args:
            workspace_id: The workspace id.
            account_id: The account id.

        Returns:
            The response payload.

        """
        response = await self._request(
            "GET",
            f"/workspaces/{workspace_id}/members/{account_id}",
        )
        return WorkspaceMember.model_validate(response.json())

    async def update_member(
        self,
        workspace_id: str,
        account_id: str,
        body: UpdateWorkspaceMember,
    ) -> WorkspaceMember:
        """Update member role.

        Args:
            workspace_id: The workspace id.
            account_id: The account id.
            body: The request payload.

        Returns:
            The response payload.

        """
        response = await self._request(
            "PATCH",
            f"/workspaces/{workspace_id}/members/{account_id}",
            json=serialize(body),
        )
        return WorkspaceMember.model_validate(response.json())

    async def remove_member(self, workspace_id: str, account_id: str) -> None:
        """Remove member.

        Args:
            workspace_id: The workspace id.
            account_id: The account id.

        """
        await self._request(
            "DELETE",
            f"/workspaces/{workspace_id}/members/{account_id}",
        )

    async def leave_workspace(self, workspace_id: str) -> None:
        """Leave workspace.

        Args:
            workspace_id: The workspace id.

        """
        await self._request("POST", f"/workspaces/{workspace_id}/members/leave")
