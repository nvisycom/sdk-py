"""Session and desktop-token operations for the signed-in account."""

from __future__ import annotations

from ..datatypes import AccountDesktopToken, DesktopTokenRequest
from .base import Service, serialize


class Auth(Service):
    """Session and desktop-token operations for the signed-in account."""

    async def logout_account(self) -> None:
        """Logout."""
        await self._request("POST", "/auth/logout")

    async def mint_desktop_token(
        self,
        body: DesktopTokenRequest,
    ) -> AccountDesktopToken:
        """Mint a desktop app token.

        Args:
            body: The request payload.

        Returns:
            The response payload.

        """
        response = await self._request(
            "POST",
            "/auth/desktop/token",
            json=serialize(body),
        )
        return AccountDesktopToken.model_validate(response.json())
