"""What the deployment can do: labels, recognizers, connectors."""

from __future__ import annotations

from ..datatypes import (
    AuthCapabilities,
    ConnectorCapabilities,
    LabelCatalog,
    RecognizerCatalog,
)
from .base import Service


class Capabilities(Service):
    """What the deployment can do: labels, recognizers, connectors."""

    async def list_labels(self) -> LabelCatalog:
        """List labels.

        Returns:
            The response payload.

        """
        response = await self._request("GET", "/capabilities/labels")
        return LabelCatalog.model_validate(response.json())

    async def list_recognizers(self) -> RecognizerCatalog:
        """List recognizers.

        Returns:
            The response payload.

        """
        response = await self._request("GET", "/capabilities/recognizers")
        return RecognizerCatalog.model_validate(response.json())

    async def list_connectors(self) -> ConnectorCapabilities:
        """List connectors.

        Returns:
            The response payload.

        """
        response = await self._request("GET", "/capabilities/connectors")
        return ConnectorCapabilities.model_validate(response.json())

    async def get_auth_capabilities(self) -> AuthCapabilities:
        """List sign-in methods.

        Returns:
            The response payload.

        """
        response = await self._request("GET", "/capabilities/auth")
        return AuthCapabilities.model_validate(response.json())
