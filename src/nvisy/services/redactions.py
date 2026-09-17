"""Redactions produced in a workspace."""

from __future__ import annotations

from ..datatypes import Audit
from .base import Service


class Redactions(Service):
    """Redactions produced in a workspace."""

    async def get_review(self, workspace_id: str, redaction_id: str) -> Audit:
        """Get redaction review.

        Args:
            workspace_id: The workspace id.
            redaction_id: The redaction id.

        Returns:
            The response payload.

        """
        response = await self._request(
            "GET",
            f"/workspaces/{workspace_id}/redactions/{redaction_id}/review",
        )
        return Audit.model_validate(response.json())
