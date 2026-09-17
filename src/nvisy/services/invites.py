"""Invitations to join a workspace."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..datatypes import (
    CreateWorkspaceInvite,
    GenerateWorkspaceInviteCode,
    InvitePreview,
    ReplyWorkspaceInvite,
    WorkspaceInvite,
    WorkspaceInviteCode,
    WorkspaceInvitePage,
    WorkspaceInviteSent,
)
from .base import Service, serialize

if TYPE_CHECKING:
    from ..pagination import AsyncPaginator


class Invites(Service):
    """Invitations to join a workspace."""

    def list_invites(
        self,
        workspace_id: str,
        *,
        order: str | None = None,
        role: str | None = None,
        sort_by: str | None = None,
        limit: int | None = None,
        include_count: bool | None = None,
    ) -> AsyncPaginator[WorkspaceInvitePage, WorkspaceInvite]:
        """List invitations.

        Args:
            workspace_id: The workspace id.
            order: Filters the results.
            role: Filters the results.
            sort_by: Filters the results.
            limit: Items per page, between 1 and 100.
            include_count: Whether to report the total count, which costs an extra
            query.

        Returns:
            A paginator over the workspace_invites.

        """
        return self._paginate(
            WorkspaceInvitePage,
            f"/workspaces/{workspace_id}/invites",
            params={
                "order": order,
                "role": role,
                "sortBy": sort_by,
                "limit": limit,
                "includeCount": include_count,
            },
        )

    async def send_invite(
        self,
        workspace_id: str,
        body: CreateWorkspaceInvite,
    ) -> WorkspaceInviteSent:
        """Send invitation.

        Args:
            workspace_id: The workspace id.
            body: The request payload.

        Returns:
            The response payload.

        """
        response = await self._request(
            "POST",
            f"/workspaces/{workspace_id}/invites",
            json=serialize(body),
        )
        return WorkspaceInviteSent.model_validate(response.json())

    async def cancel_invite(self, workspace_id: str, invite_id: str) -> None:
        """Cancel invitation.

        Args:
            workspace_id: The workspace id.
            invite_id: The invite id.

        """
        await self._request("DELETE", f"/workspaces/{workspace_id}/invites/{invite_id}")

    async def reply_to_invite(
        self,
        workspace_id: str,
        invite_id: str,
        body: ReplyWorkspaceInvite,
    ) -> None:
        """Reply to invitation.

        Args:
            workspace_id: The workspace id.
            invite_id: The invite id.
            body: The request payload.

        """
        await self._request(
            "POST",
            f"/workspaces/{workspace_id}/invites/{invite_id}",
            json=serialize(body),
        )

    async def generate_invite_code(
        self,
        workspace_id: str,
        body: GenerateWorkspaceInviteCode,
    ) -> WorkspaceInviteCode:
        """Generate invite code.

        Args:
            workspace_id: The workspace id.
            body: The request payload.

        Returns:
            The response payload.

        """
        response = await self._request(
            "POST",
            f"/workspaces/{workspace_id}/invites/code",
            json=serialize(body),
        )
        return WorkspaceInviteCode.model_validate(response.json())

    async def reply_to_invite_code(
        self,
        invite_code: str,
        body: ReplyWorkspaceInvite,
    ) -> None:
        """Reply to invite code.

        Args:
            invite_code: The invite code.
            body: The request payload.

        """
        await self._request(
            "POST",
            f"/invites/code/{invite_code}",
            json=serialize(body),
        )

    async def preview_invite(self, invite_code: str) -> InvitePreview:
        """Preview invite.

        Args:
            invite_code: The invite code.

        Returns:
            The response payload.

        """
        response = await self._request("GET", f"/invites/code/{invite_code}")
        return InvitePreview.model_validate(response.json())
