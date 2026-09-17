"""API status and health checks."""

from __future__ import annotations

from ..datatypes import Health
from .base import Service


class Status(Service):
    """Health and readiness of the API and its dependencies."""

    async def check_health(self) -> Health:
        """Report the health of the server and its dependencies.

        Returns:
            The health report, whether the server is healthy, degraded, or
            unhealthy.
        """
        response = await self._request("GET", "/health", allow_statuses={503})
        return Health.model_validate(response.json())

    async def check_liveness(self) -> None:
        """Check that the process is running, probing no dependencies.

        Raises:
            NvisyApiError: If the process is not live.
        """
        await self._request("GET", "/health/live")

    async def check_readiness(self) -> Health:
        """Report health from a short-lived cache, safe to poll frequently.

        Returns:
            The health report.
        """
        response = await self._request("GET", "/health/ready", allow_statuses={503})
        return Health.model_validate(response.json())
