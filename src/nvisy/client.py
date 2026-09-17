"""The Nvisy client."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from .config import (
    DEFAULT_BASE_URL,
    ENV_API_TOKEN,
    ENV_BASE_URL,
    ENV_USER_AGENT,
    validate_api_token,
    validate_base_url,
)
from .errors import NvisyError
from .http import create_http_client
from .services import (
    Account,
    Activities,
    Analytics,
    ApiTokens,
    Auth,
    Capabilities,
    Connections,
    Detections,
    Documents,
    Invites,
    Members,
    Notifications,
    Pipelines,
    Policies,
    Providers,
    Redactions,
    Reviews,
    Status,
    Syncs,
    Webhooks,
    Workspaces,
)

if TYPE_CHECKING:
    from collections.abc import Mapping
    from types import TracebackType

    import httpx


class Nvisy:
    """Client for the Nvisy document processing API.

    Authenticates with an API token. Every request is issued asynchronously,
    so the client is used inside an event loop, ideally as a context manager
    so its connections are closed when you are done:

        ```python
        async with Nvisy(api_token="...") as nvisy:
            account = await nvisy.account.get_account()
        ```
    """

    def __init__(
        self,
        *,
        api_token: str,
        base_url: str = DEFAULT_BASE_URL,
        headers: Mapping[str, str] | None = None,
        user_agent: str | None = None,
        with_logging: bool = False,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        """Initialize the client.

        Args:
            api_token: Token to authenticate with.
            base_url: Base URL for the API.
            headers: Extra headers sent with every request, merged over the
                defaults so any of them can be overridden. `Content-Type` is
                the exception: httpx derives it from each body, which is what
                gives a multipart upload its boundary.
            user_agent: Custom user agent; defaults to one naming the SDK.
            with_logging: Whether to log requests and responses to the `nvisy`
                logger at debug level.
            transport: Custom transport, chiefly for tests.

        Raises:
            NvisyError: If the token or the base URL is invalid.
        """
        self._api_token = validate_api_token(api_token)
        self._base_url = validate_base_url(base_url)
        self._headers = dict(headers or {})
        self._user_agent = user_agent
        self._with_logging = with_logging
        self._transport = transport

        self._http = create_http_client(
            api_token=self._api_token,
            base_url=self._base_url,
            headers=self._headers,
            user_agent=self._user_agent,
            with_logging=with_logging,
            transport=transport,
        )

    @classmethod
    def from_environment(
        cls,
        environ: Mapping[str, str] | os._Environ[str] | None = None,
        **overrides: object,
    ) -> Nvisy:
        """Build a client from environment variables.

        Reads `NVISY_API_TOKEN` (required), `NVISY_BASE_URL`, and
        `NVISY_USER_AGENT`.

        Args:
            environ: Environment to read; defaults to the process environment.
            **overrides: Arguments passed to the constructor, taking
                precedence over the environment.

        Returns:
            The configured client.

        Raises:
            NvisyError: If no API token is set.
        """
        env = os.environ if environ is None else environ

        settings: dict[str, object] = {}
        if api_token := env.get(ENV_API_TOKEN):
            settings["api_token"] = api_token
        if base_url := env.get(ENV_BASE_URL):
            settings["base_url"] = base_url
        if user_agent := env.get(ENV_USER_AGENT):
            settings["user_agent"] = user_agent

        # Overrides win, so the token may arrive from either side; only report
        # it missing once neither has supplied one.
        settings.update(overrides)
        if not settings.get("api_token"):
            raise NvisyError(
                f"API token is required. Set the {ENV_API_TOKEN} environment variable."
            )

        return cls(**settings)  # type: ignore[arg-type]

    def with_api_token(self, api_token: str) -> Nvisy:
        """Build a client like this one but authenticating with another token.

        This client is left as it is.

        Args:
            api_token: The token the new client should use.

        Returns:
            The new client.

        Raises:
            NvisyError: If the token is invalid.
        """
        return type(self)(
            api_token=api_token,
            base_url=self._base_url,
            headers=self._headers,
            user_agent=self._user_agent,
            with_logging=self._with_logging,
            transport=self._transport,
        )

    @property
    def base_url(self) -> str:
        """The base URL requests are sent to."""
        return self._base_url

    @property
    def http(self) -> httpx.AsyncClient:
        """The underlying HTTP client, for endpoints the services do not cover."""
        return self._http

    @property
    def account(self) -> Account:
        """The authenticated account, its identities, and its avatar."""
        return Account(self._http)

    @property
    def activities(self) -> Activities:
        """A workspace's activity log."""
        return Activities(self._http)

    @property
    def analytics(self) -> Analytics:
        """Aggregate figures for a workspace."""
        return Analytics(self._http)

    @property
    def api_tokens(self) -> ApiTokens:
        """API tokens belonging to the account."""
        return ApiTokens(self._http)

    @property
    def auth(self) -> Auth:
        """Session and desktop-token operations."""
        return Auth(self._http)

    @property
    def capabilities(self) -> Capabilities:
        """What the deployment can do: labels, recognizers, connectors."""
        return Capabilities(self._http)

    @property
    def connections(self) -> Connections:
        """Connections to external file services and object stores."""
        return Connections(self._http)

    @property
    def detections(self) -> Detections:
        """Detection runs and the redactions made from them."""
        return Detections(self._http)

    @property
    def documents(self) -> Documents:
        """Documents in a workspace."""
        return Documents(self._http)

    @property
    def invites(self) -> Invites:
        """Invitations to join a workspace."""
        return Invites(self._http)

    @property
    def members(self) -> Members:
        """Members of a workspace."""
        return Members(self._http)

    @property
    def notifications(self) -> Notifications:
        """Notifications for the authenticated account."""
        return Notifications(self._http)

    @property
    def pipelines(self) -> Pipelines:
        """Processing pipelines in a workspace."""
        return Pipelines(self._http)

    @property
    def policies(self) -> Policies:
        """Redaction policies in a workspace."""
        return Policies(self._http)

    @property
    def providers(self) -> Providers:
        """Inference providers configured for a workspace."""
        return Providers(self._http)

    @property
    def redactions(self) -> Redactions:
        """Redactions produced in a workspace."""
        return Redactions(self._http)

    @property
    def reviews(self) -> Reviews:
        """Document reviews, assignees, and comments."""
        return Reviews(self._http)

    @property
    def status(self) -> Status:
        """API status and health checks."""
        return Status(self._http)

    @property
    def syncs(self) -> Syncs:
        """Synchronization runs for a workspace's connections."""
        return Syncs(self._http)

    @property
    def webhooks(self) -> Webhooks:
        """Webhook endpoints registered for a workspace."""
        return Webhooks(self._http)

    @property
    def workspaces(self) -> Workspaces:
        """Workspace management."""
        return Workspaces(self._http)

    async def aclose(self) -> None:
        """Close the underlying connections."""
        await self._http.aclose()

    async def __aenter__(self) -> Nvisy:
        """Enter the context manager.

        Returns:
            This client.
        """
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Close the client on leaving the context manager."""
        await self.aclose()

    def __repr__(self) -> str:
        """Return a representation of the client, without its token."""
        return f"{type(self).__name__}(base_url={self._base_url!r})"


__all__ = ["Nvisy"]
