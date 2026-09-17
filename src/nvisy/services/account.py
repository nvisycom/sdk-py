"""The authenticated account, its identities, and its avatar."""

from __future__ import annotations

from typing import Any

from ..datatypes import (
    Account as AccountData,
)
from ..datatypes import (
    AccountIdentities,
    OidcStartResponse,
    PublicAccount,
    SetPassword,
    UpdateAccount,
)
from .base import Service, serialize


class Account(Service):
    """The authenticated account, its identities, and its avatar."""

    async def get_account(self) -> AccountData:
        """Get own account.

        Returns:
            The response payload.

        """
        response = await self._request("GET", "/account")
        return AccountData.model_validate(response.json())

    async def update_account(self, body: UpdateAccount) -> AccountData:
        """Update account.

        Args:
            body: The request payload.

        Returns:
            The response payload.

        """
        response = await self._request("PATCH", "/account", json=serialize(body))
        return AccountData.model_validate(response.json())

    async def delete_account(self) -> None:
        """Delete account."""
        await self._request("DELETE", "/account")

    async def get_public_account(self, account_id: str) -> PublicAccount:
        """Get account by id.

        Args:
            account_id: The account id.

        Returns:
            The response payload.

        """
        response = await self._request("GET", f"/accounts/{account_id}")
        return PublicAccount.model_validate(response.json())

    async def upload_avatar(self, account_id: str, file: Any) -> AccountData:
        """Upload account avatar.

        Args:
            account_id: The account id.
            file: The file to upload, as accepted by httpx: bytes, a file object, or a
            (filename, content, content_type) tuple.

        Returns:
            The response payload.

        """
        response = await self._request(
            "PUT",
            f"/accounts/{account_id}/avatar",
            files={"file": file},
        )
        return AccountData.model_validate(response.json())

    async def delete_avatar(self, account_id: str) -> None:
        """Delete account avatar.

        Args:
            account_id: The account id.

        """
        await self._request("DELETE", f"/accounts/{account_id}/avatar")

    async def list_identities(self) -> AccountIdentities:
        """List sign-in methods.

        Returns:
            The response payload.

        """
        response = await self._request("GET", "/account/identities")
        return AccountIdentities.model_validate(response.json())

    async def set_password(self, body: SetPassword) -> None:
        """Set or change password.

        Args:
            body: The request payload.

        """
        await self._request("PUT", "/account/identities/password", json=serialize(body))

    async def remove_password(self) -> None:
        """Remove password."""
        await self._request("DELETE", "/account/identities/password")

    async def link_identity(
        self,
        provider: str,
        *,
        reauth_proof: str | None = None,
        redirect_uri: str | None = None,
    ) -> OidcStartResponse:
        """Link a provider.

        Args:
            provider: The provider.
            reauth_proof: Filters the results.
            redirect_uri: Filters the results.

        Returns:
            The response payload.

        """
        response = await self._request(
            "POST",
            f"/account/identities/{provider}",
            params={"reauthProof": reauth_proof, "redirectUri": redirect_uri},
        )
        return OidcStartResponse.model_validate(response.json())

    async def unlink_identity(self, provider: str) -> None:
        """Unlink a provider.

        Args:
            provider: The provider.

        """
        await self._request("DELETE", f"/account/identities/{provider}")

    async def reauth(
        self,
        provider: str,
        *,
        reauth_proof: str | None = None,
        redirect_uri: str | None = None,
    ) -> OidcStartResponse:
        """Start OIDC step-up re-authentication.

        Args:
            provider: The provider.
            reauth_proof: Filters the results.
            redirect_uri: Filters the results.

        Returns:
            The response payload.

        """
        response = await self._request(
            "GET",
            f"/auth/{provider}/reauth",
            params={"reauthProof": reauth_proof, "redirectUri": redirect_uri},
        )
        return OidcStartResponse.model_validate(response.json())
