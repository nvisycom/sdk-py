"""Detection runs and the redactions made from them."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..datatypes import (
    ArtifactSet,
    Audit,
    CreateAdhocWorkspaceDetection,
    CreateWorkspaceDetection,
    RedactWorkspaceDetection,
    WorkspaceDetection,
    WorkspaceDetectionPage,
    WorkspaceRedactionResult,
    WorkspaceRedactionResultPage,
)
from .base import Service, serialize

if TYPE_CHECKING:
    from ..pagination import AsyncPaginator


class Detections(Service):
    """Detection runs and the redactions made from them."""

    def list_detections(
        self,
        workspace_id: str,
        *,
        document_id: str | None = None,
        pipeline_id: str | None = None,
        status: str | None = None,
        trigger_type: str | None = None,
        triggered_by: str | None = None,
        limit: int | None = None,
        include_count: bool | None = None,
    ) -> AsyncPaginator[WorkspaceDetectionPage, WorkspaceDetection]:
        """List workspace detections.

        Args:
            workspace_id: The workspace id.
            document_id: Filters the results.
            pipeline_id: Filters the results.
            status: Filters the results.
            trigger_type: Filters the results.
            triggered_by: Filters the results.
            limit: Items per page, between 1 and 100.
            include_count: Whether to report the total count, which costs an extra
            query.

        Returns:
            A paginator over the workspace_detections.

        """
        return self._paginate(
            WorkspaceDetectionPage,
            f"/workspaces/{workspace_id}/pipelines/detections",
            params={
                "documentId": document_id,
                "pipelineId": pipeline_id,
                "status": status,
                "triggerType": trigger_type,
                "triggeredBy": triggered_by,
                "limit": limit,
                "includeCount": include_count,
            },
        )

    def list_pipeline_detections(
        self,
        workspace_id: str,
        pipeline_id: str,
        *,
        document_id: str | None = None,
        status: str | None = None,
        trigger_type: str | None = None,
        triggered_by: str | None = None,
        limit: int | None = None,
        include_count: bool | None = None,
    ) -> AsyncPaginator[WorkspaceDetectionPage, WorkspaceDetection]:
        """List pipeline detections.

        Args:
            workspace_id: The workspace id.
            pipeline_id: The pipeline id.
            document_id: Filters the results.
            status: Filters the results.
            trigger_type: Filters the results.
            triggered_by: Filters the results.
            limit: Items per page, between 1 and 100.
            include_count: Whether to report the total count, which costs an extra
            query.

        Returns:
            A paginator over the workspace_detections.

        """
        return self._paginate(
            WorkspaceDetectionPage,
            f"/workspaces/{workspace_id}/pipelines/{pipeline_id}/detections",
            params={
                "documentId": document_id,
                "status": status,
                "triggerType": trigger_type,
                "triggeredBy": triggered_by,
                "limit": limit,
                "includeCount": include_count,
            },
        )

    async def create_detection(
        self,
        workspace_id: str,
        pipeline_id: str,
        body: CreateWorkspaceDetection,
    ) -> WorkspaceDetection:
        """Start a detection.

        Args:
            workspace_id: The workspace id.
            pipeline_id: The pipeline id.
            body: The request payload.

        Returns:
            The response payload.

        """
        response = await self._request(
            "POST",
            f"/workspaces/{workspace_id}/pipelines/{pipeline_id}/detections",
            json=serialize(body),
        )
        return WorkspaceDetection.model_validate(response.json())

    async def create_adhoc_detection(
        self,
        workspace_id: str,
        body: CreateAdhocWorkspaceDetection,
    ) -> WorkspaceDetection:
        """Start an ad-hoc detection.

        Args:
            workspace_id: The workspace id.
            body: The request payload.

        Returns:
            The response payload.

        """
        response = await self._request(
            "POST",
            f"/workspaces/{workspace_id}/detections",
            json=serialize(body),
        )
        return WorkspaceDetection.model_validate(response.json())

    async def get_detection(
        self,
        workspace_id: str,
        detection_id: str,
    ) -> WorkspaceDetection:
        """Get detection.

        Args:
            workspace_id: The workspace id.
            detection_id: The detection id.

        Returns:
            The response payload.

        """
        response = await self._request(
            "GET",
            f"/workspaces/{workspace_id}/detections/{detection_id}",
        )
        return WorkspaceDetection.model_validate(response.json())

    async def get_analysis(self, workspace_id: str, detection_id: str) -> Audit:
        """Get detection findings.

        Args:
            workspace_id: The workspace id.
            detection_id: The detection id.

        Returns:
            The response payload.

        """
        response = await self._request(
            "GET",
            f"/workspaces/{workspace_id}/detections/{detection_id}/analysis",
        )
        return Audit.model_validate(response.json())

    async def get_intermediates(
        self,
        workspace_id: str,
        detection_id: str,
    ) -> ArtifactSet:
        """Get detection intermediates.

        Args:
            workspace_id: The workspace id.
            detection_id: The detection id.

        Returns:
            The response payload.

        """
        response = await self._request(
            "GET",
            f"/workspaces/{workspace_id}/detections/{detection_id}/intermediates",
        )
        return ArtifactSet.model_validate(response.json())

    async def download_audit(
        self,
        workspace_id: str,
        detection_id: str,
        *,
        format_: str | None = None,
    ) -> bytes:
        """Download detection audit.

        Args:
            workspace_id: The workspace id.
            detection_id: The detection id.
            format_: Filters the results.

        Returns:
            The raw response body.

        """
        response = await self._request(
            "GET",
            f"/workspaces/{workspace_id}/detections/{detection_id}/audit",
            params={"format": format_},
        )
        return response.content

    def list_redactions(
        self,
        workspace_id: str,
        detection_id: str,
        *,
        limit: int | None = None,
        include_count: bool | None = None,
    ) -> AsyncPaginator[WorkspaceRedactionResultPage, WorkspaceRedactionResult]:
        """List detection redactions.

        Args:
            workspace_id: The workspace id.
            detection_id: The detection id.
            limit: Items per page, between 1 and 100.
            include_count: Whether to report the total count, which costs an extra
            query.

        Returns:
            A paginator over the workspace_redaction_results.

        """
        return self._paginate(
            WorkspaceRedactionResultPage,
            f"/workspaces/{workspace_id}/detections/{detection_id}/redactions",
            params={"limit": limit, "includeCount": include_count},
        )

    async def create_redaction(
        self,
        workspace_id: str,
        detection_id: str,
        body: RedactWorkspaceDetection,
    ) -> WorkspaceRedactionResult:
        """Redact a detection.

        Args:
            workspace_id: The workspace id.
            detection_id: The detection id.
            body: The request payload.

        Returns:
            The response payload.

        """
        response = await self._request(
            "POST",
            f"/workspaces/{workspace_id}/detections/{detection_id}/redactions",
            json=serialize(body),
        )
        return WorkspaceRedactionResult.model_validate(response.json())
