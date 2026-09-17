"""Notifications for the authenticated account."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..datatypes import (
    AccountMarkedReadStatus,
    AccountNotification,
    AccountNotificationPage,
    AccountUnreadStatus,
)
from .base import Service

if TYPE_CHECKING:
    from ..pagination import AsyncPaginator


class Notifications(Service):
    """Notifications for the authenticated account."""

    def list_notifications(
        self,
        *,
        limit: int | None = None,
        include_count: bool | None = None,
    ) -> AsyncPaginator[AccountNotificationPage, AccountNotification]:
        """List notifications.

        Args:
            limit: Items per page, between 1 and 100.
            include_count: Whether to report the total count, which costs an extra
            query.

        Returns:
            A paginator over the account_notifications.

        """
        return self._paginate(
            AccountNotificationPage,
            "/notifications",
            params={"limit": limit, "includeCount": include_count},
        )

    async def get_unread_notifications_status(self) -> AccountUnreadStatus:
        """Get unread notifications count.

        Returns:
            The response payload.

        """
        response = await self._request("GET", "/notifications/unread")
        return AccountUnreadStatus.model_validate(response.json())

    async def mark_all_read(self) -> AccountMarkedReadStatus:
        """Mark all notifications as read.

        Returns:
            The response payload.

        """
        response = await self._request("POST", "/notifications/read")
        return AccountMarkedReadStatus.model_validate(response.json())

    async def mark_read(self, notification_id: str) -> None:
        """Mark notification as read.

        Args:
            notification_id: The notification id.

        """
        await self._request("POST", f"/notifications/{notification_id}/read")
