"""API tokens belonging to the account."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..datatypes import (
    AccountApiToken,
    AccountApiTokenPage,
    AccountApiTokenWithJwt,
    CreateAccountApiToken,
    UpdateAccountApiToken,
)
from .base import Service, serialize

if TYPE_CHECKING:
    from ..pagination import AsyncPaginator


class ApiTokens(Service):
    """API tokens belonging to the account."""

    def list_api_tokens(
        self,
        *,
        limit: int | None = None,
        include_count: bool | None = None,
    ) -> AsyncPaginator[AccountApiTokenPage, AccountApiToken]:
        """List API tokens.

        Args:
            limit: Items per page, between 1 and 100.
            include_count: Whether to report the total count, which costs an extra
            query.

        Returns:
            A paginator over the account_api_tokens.

        """
        return self._paginate(
            AccountApiTokenPage,
            "/api-tokens",
            params={"limit": limit, "includeCount": include_count},
        )

    async def get_api_token(self, token_id: str) -> AccountApiToken:
        """Get API token.

        Args:
            token_id: The token id.

        Returns:
            The response payload.

        """
        response = await self._request("GET", f"/api-tokens/{token_id}")
        return AccountApiToken.model_validate(response.json())

    async def create_api_token(
        self,
        body: CreateAccountApiToken,
    ) -> AccountApiTokenWithJwt:
        """Create API token.

        Args:
            body: The request payload.

        Returns:
            The response payload.

        """
        response = await self._request("POST", "/api-tokens", json=serialize(body))
        return AccountApiTokenWithJwt.model_validate(response.json())

    async def update_api_token(
        self,
        token_id: str,
        body: UpdateAccountApiToken,
    ) -> AccountApiToken:
        """Update API token.

        Args:
            token_id: The token id.
            body: The request payload.

        Returns:
            The response payload.

        """
        response = await self._request(
            "PATCH",
            f"/api-tokens/{token_id}",
            json=serialize(body),
        )
        return AccountApiToken.model_validate(response.json())

    async def revoke_api_token(self, token_id: str) -> None:
        """Revoke API token.

        Args:
            token_id: The token id.

        """
        await self._request("DELETE", f"/api-tokens/{token_id}")
