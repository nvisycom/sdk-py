"""Aggregate figures for a workspace."""

from __future__ import annotations

from ..datatypes import WorkspaceAnalytics, WorkspaceDetectionTimeSeries
from .base import Service


class Analytics(Service):
    """Aggregate figures for a workspace."""

    async def get_analytics(self, workspace_id: str) -> WorkspaceAnalytics:
        """Workspace analytics.

        Args:
            workspace_id: The workspace id.

        Returns:
            The response payload.

        """
        response = await self._request("GET", f"/workspaces/{workspace_id}/analytics")
        return WorkspaceAnalytics.model_validate(response.json())

    async def get_detection_time_series(
        self,
        workspace_id: str,
        *,
        from_: str | None = None,
        to: str | None = None,
    ) -> WorkspaceDetectionTimeSeries:
        """Workspace detection time series.

        Args:
            workspace_id: The workspace id.
            from_: Filters the results.
            to: Filters the results.

        Returns:
            The response payload.

        """
        response = await self._request(
            "GET",
            f"/workspaces/{workspace_id}/analytics/detections/timeseries",
            params={"from": from_, "to": to},
        )
        return WorkspaceDetectionTimeSeries.model_validate(response.json())
