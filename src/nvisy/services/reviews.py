"""Document reviews, their assignees, timeline, and comments."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..datatypes import (
    CreateWorkspaceComment,
    CreateWorkspaceReview,
    RenameWorkspaceReview,
    UpdateWorkspaceComment,
    WorkspaceComment,
    WorkspaceReview,
    WorkspaceReviewEntry,
    WorkspaceReviewEntryPage,
    WorkspaceReviewEvent,
    WorkspaceReviewEventPage,
    WorkspaceReviewPage,
)
from .base import Service, serialize

if TYPE_CHECKING:
    from ..pagination import AsyncPaginator


class Reviews(Service):
    """Document reviews, their assignees, timeline, and comments."""

    async def list_for_document(
        self,
        workspace_id: str,
        document_id: str,
    ) -> list[WorkspaceReview]:
        """List a document's reviews.

        Args:
            workspace_id: The workspace id.
            document_id: The document id.

        Returns:
            The response payload.

        """
        response = await self._request(
            "GET",
            f"/workspaces/{workspace_id}/documents/{document_id}/reviews",
        )
        return [WorkspaceReview.model_validate(item) for item in response.json()]

    async def create_for_document(
        self,
        workspace_id: str,
        document_id: str,
        body: CreateWorkspaceReview,
    ) -> WorkspaceReview:
        """Open a review.

        Args:
            workspace_id: The workspace id.
            document_id: The document id.
            body: The request payload.

        Returns:
            The response payload.

        """
        response = await self._request(
            "POST",
            f"/workspaces/{workspace_id}/documents/{document_id}/reviews",
            json=serialize(body),
        )
        return WorkspaceReview.model_validate(response.json())

    def list_reviews(
        self,
        workspace_id: str,
        *,
        assignee: str | None = None,
        author: str | None = None,
        document_id: str | None = None,
        review_status: str | None = None,
        limit: int | None = None,
        include_count: bool | None = None,
    ) -> AsyncPaginator[WorkspaceReviewPage, WorkspaceReview]:
        """List reviews.

        Args:
            workspace_id: The workspace id.
            assignee: Filters the results.
            author: Filters the results.
            document_id: Filters the results.
            review_status: Filters the results.
            limit: Items per page, between 1 and 100.
            include_count: Whether to report the total count, which costs an extra
            query.

        Returns:
            A paginator over the workspace_reviews.

        """
        return self._paginate(
            WorkspaceReviewPage,
            f"/workspaces/{workspace_id}/reviews",
            params={
                "assignee": assignee,
                "author": author,
                "documentId": document_id,
                "reviewStatus": review_status,
                "limit": limit,
                "includeCount": include_count,
            },
        )

    async def get_review(self, workspace_id: str, review_id: str) -> WorkspaceReview:
        """Get a review.

        Args:
            workspace_id: The workspace id.
            review_id: The review id.

        Returns:
            The response payload.

        """
        response = await self._request(
            "GET",
            f"/workspaces/{workspace_id}/reviews/{review_id}",
        )
        return WorkspaceReview.model_validate(response.json())

    async def update_review(
        self,
        workspace_id: str,
        review_id: str,
        body: RenameWorkspaceReview,
    ) -> WorkspaceReview:
        """Rename a review.

        Args:
            workspace_id: The workspace id.
            review_id: The review id.
            body: The request payload.

        Returns:
            The response payload.

        """
        response = await self._request(
            "PATCH",
            f"/workspaces/{workspace_id}/reviews/{review_id}",
            json=serialize(body),
        )
        return WorkspaceReview.model_validate(response.json())

    async def delete_review(self, workspace_id: str, review_id: str) -> None:
        """Delete a review.

        Args:
            workspace_id: The workspace id.
            review_id: The review id.

        """
        await self._request("DELETE", f"/workspaces/{workspace_id}/reviews/{review_id}")

    async def assign_reviewer(
        self,
        workspace_id: str,
        review_id: str,
        account_id: str,
    ) -> WorkspaceReview:
        """Assign a reviewer.

        Args:
            workspace_id: The workspace id.
            review_id: The review id.
            account_id: The account id.

        Returns:
            The response payload.

        """
        response = await self._request(
            "POST",
            f"/workspaces/{workspace_id}/reviews/{review_id}/assignees/{account_id}",
        )
        return WorkspaceReview.model_validate(response.json())

    async def unassign_reviewer(
        self,
        workspace_id: str,
        review_id: str,
        account_id: str,
    ) -> WorkspaceReview:
        """Unassign a reviewer.

        Args:
            workspace_id: The workspace id.
            review_id: The review id.
            account_id: The account id.

        Returns:
            The response payload.

        """
        response = await self._request(
            "DELETE",
            f"/workspaces/{workspace_id}/reviews/{review_id}/assignees/{account_id}",
        )
        return WorkspaceReview.model_validate(response.json())

    async def verify_review(self, workspace_id: str, review_id: str) -> WorkspaceReview:
        """Verify a review.

        Args:
            workspace_id: The workspace id.
            review_id: The review id.

        Returns:
            The response payload.

        """
        response = await self._request(
            "POST",
            f"/workspaces/{workspace_id}/reviews/{review_id}/verify",
        )
        return WorkspaceReview.model_validate(response.json())

    async def reopen_review(self, workspace_id: str, review_id: str) -> WorkspaceReview:
        """Reopen a review.

        Args:
            workspace_id: The workspace id.
            review_id: The review id.

        Returns:
            The response payload.

        """
        response = await self._request(
            "POST",
            f"/workspaces/{workspace_id}/reviews/{review_id}/reopen",
        )
        return WorkspaceReview.model_validate(response.json())

    def get_timeline(
        self,
        workspace_id: str,
        review_id: str,
        *,
        limit: int | None = None,
        include_count: bool | None = None,
    ) -> AsyncPaginator[WorkspaceReviewEntryPage, WorkspaceReviewEntry]:
        """List a review's timeline.

        Args:
            workspace_id: The workspace id.
            review_id: The review id.
            limit: Items per page, between 1 and 100.
            include_count: Whether to report the total count, which costs an extra
            query.

        Returns:
            A paginator over the workspace_review_entrys.

        """
        return self._paginate(
            WorkspaceReviewEntryPage,
            f"/workspaces/{workspace_id}/reviews/{review_id}/timeline",
            params={"limit": limit, "includeCount": include_count},
        )

    def get_events(
        self,
        workspace_id: str,
        review_id: str,
        *,
        limit: int | None = None,
        include_count: bool | None = None,
    ) -> AsyncPaginator[WorkspaceReviewEventPage, WorkspaceReviewEvent]:
        """List a review's events.

        Args:
            workspace_id: The workspace id.
            review_id: The review id.
            limit: Items per page, between 1 and 100.
            include_count: Whether to report the total count, which costs an extra
            query.

        Returns:
            A paginator over the workspace_review_events.

        """
        return self._paginate(
            WorkspaceReviewEventPage,
            f"/workspaces/{workspace_id}/reviews/{review_id}/events",
            params={"limit": limit, "includeCount": include_count},
        )

    async def add_comment(
        self,
        workspace_id: str,
        review_id: str,
        body: CreateWorkspaceComment,
    ) -> WorkspaceComment:
        """Post a comment.

        Args:
            workspace_id: The workspace id.
            review_id: The review id.
            body: The request payload.

        Returns:
            The response payload.

        """
        response = await self._request(
            "POST",
            f"/workspaces/{workspace_id}/reviews/{review_id}/comments",
            json=serialize(body),
        )
        return WorkspaceComment.model_validate(response.json())

    async def update_comment(
        self,
        workspace_id: str,
        comment_id: str,
        body: UpdateWorkspaceComment,
    ) -> WorkspaceComment:
        """Edit a comment.

        Args:
            workspace_id: The workspace id.
            comment_id: The comment id.
            body: The request payload.

        Returns:
            The response payload.

        """
        response = await self._request(
            "PATCH",
            f"/workspaces/{workspace_id}/comments/{comment_id}",
            json=serialize(body),
        )
        return WorkspaceComment.model_validate(response.json())

    async def delete_comment(self, workspace_id: str, comment_id: str) -> None:
        """Delete a comment.

        Args:
            workspace_id: The workspace id.
            comment_id: The comment id.

        """
        await self._request(
            "DELETE",
            f"/workspaces/{workspace_id}/comments/{comment_id}",
        )

    async def link_detection(
        self,
        workspace_id: str,
        review_id: str,
        detection_id: str,
    ) -> WorkspaceReview:
        """Reference a detection from a review.

        Args:
            workspace_id: The workspace id.
            review_id: The review id.
            detection_id: The detection id.

        Returns:
            The response payload.

        """
        response = await self._request(
            "POST",
            f"/workspaces/{workspace_id}/reviews/{review_id}/detections/{detection_id}",
        )
        return WorkspaceReview.model_validate(response.json())

    async def link_redaction(
        self,
        workspace_id: str,
        review_id: str,
        redaction_id: str,
    ) -> WorkspaceReview:
        """Reference a redaction from a review.

        Args:
            workspace_id: The workspace id.
            review_id: The review id.
            redaction_id: The redaction id.

        Returns:
            The response payload.

        """
        response = await self._request(
            "POST",
            f"/workspaces/{workspace_id}/reviews/{review_id}/redactions/{redaction_id}",
        )
        return WorkspaceReview.model_validate(response.json())
