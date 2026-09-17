"""Documents in a workspace."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..datatypes import (
    DeleteWorkspaceDocuments,
    UpdateWorkspaceDocument,
    WorkspaceDeletedDocuments,
    WorkspaceDocument,
    WorkspaceDocumentPage,
)
from .base import Service, serialize

if TYPE_CHECKING:
    from ..pagination import AsyncPaginator


class Documents(Service):
    """Documents in a workspace."""

    async def upload_documents(
        self,
        workspace_id: str,
        file: Any,
    ) -> list[WorkspaceDocument]:
        """Upload documents.

        Args:
            workspace_id: The workspace id.
            file: The file to upload, as accepted by httpx: bytes, a file object, or a
            (filename, content, content_type) tuple.

        Returns:
            The response payload.

        """
        response = await self._request(
            "POST",
            f"/workspaces/{workspace_id}/documents",
            files={"file": file},
        )
        return [WorkspaceDocument.model_validate(item) for item in response.json()]

    def list_documents(
        self,
        workspace_id: str,
        *,
        formats: str | None = None,
        hash: str | None = None,
        modality: str | None = None,
        search: str | None = None,
        limit: int | None = None,
        include_count: bool | None = None,
    ) -> AsyncPaginator[WorkspaceDocumentPage, WorkspaceDocument]:
        """List documents.

        Args:
            workspace_id: The workspace id.
            formats: Filters the results.
            hash: Filters the results.
            modality: Filters the results.
            search: Filters the results.
            limit: Items per page, between 1 and 100.
            include_count: Whether to report the total count, which costs an extra
            query.

        Returns:
            A paginator over the workspace_documents.

        """
        return self._paginate(
            WorkspaceDocumentPage,
            f"/workspaces/{workspace_id}/documents",
            params={
                "formats": formats,
                "hash": hash,
                "modality": modality,
                "search": search,
                "limit": limit,
                "includeCount": include_count,
            },
        )

    async def get_document(
        self,
        workspace_id: str,
        document_id: str,
    ) -> WorkspaceDocument:
        """Get document metadata.

        Args:
            workspace_id: The workspace id.
            document_id: The document id.

        Returns:
            The response payload.

        """
        response = await self._request(
            "GET",
            f"/workspaces/{workspace_id}/documents/{document_id}",
        )
        return WorkspaceDocument.model_validate(response.json())

    async def download_document(self, workspace_id: str, document_id: str) -> bytes:
        """Download document.

        Args:
            workspace_id: The workspace id.
            document_id: The document id.

        Returns:
            The raw response body.

        """
        response = await self._request(
            "GET",
            f"/workspaces/{workspace_id}/documents/{document_id}/content",
        )
        return response.content

    async def update_document(
        self,
        workspace_id: str,
        document_id: str,
        body: UpdateWorkspaceDocument,
    ) -> WorkspaceDocument:
        """Update document.

        Args:
            workspace_id: The workspace id.
            document_id: The document id.
            body: The request payload.

        Returns:
            The response payload.

        """
        response = await self._request(
            "PATCH",
            f"/workspaces/{workspace_id}/documents/{document_id}",
            json=serialize(body),
        )
        return WorkspaceDocument.model_validate(response.json())

    async def delete_document(self, workspace_id: str, document_id: str) -> None:
        """Delete document.

        Args:
            workspace_id: The workspace id.
            document_id: The document id.

        """
        await self._request(
            "DELETE",
            f"/workspaces/{workspace_id}/documents/{document_id}",
        )

    async def delete_documents(
        self,
        workspace_id: str,
        body: DeleteWorkspaceDocuments,
    ) -> WorkspaceDeletedDocuments:
        """Delete documents.

        Args:
            workspace_id: The workspace id.
            body: The request payload.

        Returns:
            The response payload.

        """
        response = await self._request(
            "POST",
            f"/workspaces/{workspace_id}/documents/delete",
            json=serialize(body),
        )
        return WorkspaceDeletedDocuments.model_validate(response.json())
