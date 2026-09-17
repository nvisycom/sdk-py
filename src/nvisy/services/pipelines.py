"""Processing pipelines in a workspace."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..datatypes import (
    CreateWorkspacePipeline,
    UpdateWorkspacePipeline,
    WorkspacePipeline,
    WorkspacePipelineSummary,
    WorkspacePipelineSummaryPage,
)
from .base import Service, serialize

if TYPE_CHECKING:
    from ..pagination import AsyncPaginator


class Pipelines(Service):
    """Processing pipelines in a workspace."""

    def list_pipelines(
        self,
        workspace_id: str,
        *,
        search: str | None = None,
        status: str | None = None,
        limit: int | None = None,
        include_count: bool | None = None,
    ) -> AsyncPaginator[WorkspacePipelineSummaryPage, WorkspacePipelineSummary]:
        """List pipelines.

        Args:
            workspace_id: The workspace id.
            search: Filters the results.
            status: Filters the results.
            limit: Items per page, between 1 and 100.
            include_count: Whether to report the total count, which costs an extra
            query.

        Returns:
            A paginator over the workspace_pipeline_summarys.

        """
        return self._paginate(
            WorkspacePipelineSummaryPage,
            f"/workspaces/{workspace_id}/pipelines",
            params={
                "search": search,
                "status": status,
                "limit": limit,
                "includeCount": include_count,
            },
        )

    async def create_pipeline(
        self,
        workspace_id: str,
        body: CreateWorkspacePipeline,
    ) -> WorkspacePipeline:
        """Create pipeline.

        Args:
            workspace_id: The workspace id.
            body: The request payload.

        Returns:
            The response payload.

        """
        response = await self._request(
            "POST",
            f"/workspaces/{workspace_id}/pipelines",
            json=serialize(body),
        )
        return WorkspacePipeline.model_validate(response.json())

    async def get_pipeline(
        self,
        workspace_id: str,
        pipeline_id: str,
    ) -> WorkspacePipeline:
        """Get pipeline.

        Args:
            workspace_id: The workspace id.
            pipeline_id: The pipeline id.

        Returns:
            The response payload.

        """
        response = await self._request(
            "GET",
            f"/workspaces/{workspace_id}/pipelines/{pipeline_id}",
        )
        return WorkspacePipeline.model_validate(response.json())

    async def update_pipeline(
        self,
        workspace_id: str,
        pipeline_id: str,
        body: UpdateWorkspacePipeline,
    ) -> WorkspacePipeline:
        """Update pipeline.

        Args:
            workspace_id: The workspace id.
            pipeline_id: The pipeline id.
            body: The request payload.

        Returns:
            The response payload.

        """
        response = await self._request(
            "PATCH",
            f"/workspaces/{workspace_id}/pipelines/{pipeline_id}",
            json=serialize(body),
        )
        return WorkspacePipeline.model_validate(response.json())

    async def delete_pipeline(self, workspace_id: str, pipeline_id: str) -> None:
        """Delete pipeline.

        Args:
            workspace_id: The workspace id.
            pipeline_id: The pipeline id.

        """
        await self._request(
            "DELETE",
            f"/workspaces/{workspace_id}/pipelines/{pipeline_id}",
        )
