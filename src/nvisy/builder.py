"""Builder module for fluent API configuration."""

import contextlib
import os
from typing import TYPE_CHECKING

from .config import ClientConfiguration
from .errors import ConfigError

if TYPE_CHECKING:
    from .client import Client


class ClientBuilder:
    """Builder for creating Nvisy client instances with fluent API.

    Provides a chainable interface for configuring client settings
    before building the final Client instance.
    """

    def __init__(self) -> None:
        """Initialize the builder with default values."""
        self._api_key: str | None = None
        self._base_url: str = "https://api.nvisy.com"
        self._timeout: float = 30.0
        self._max_retries: int = 3
        self._user_agent: str | None = None
        self._headers: dict[str, str] = {}
        self._debug: bool = False

    def with_api_key(self, api_key: str) -> "ClientBuilder":
        """Set the API key.

        Args:
            api_key: API key (must be 10+ chars, alphanumeric with _ and -)

        Returns:
            Self for method chaining
        """
        self._api_key = api_key
        return self

    def with_base_url(self, base_url: str) -> "ClientBuilder":
        """Set the base URL.

        Args:
            base_url: API base URL (must be valid HTTP/HTTPS URL)

        Returns:
            Self for method chaining
        """
        self._base_url = base_url
        return self

    def with_timeout(self, timeout: int | float) -> "ClientBuilder":
        """Set the request timeout.

        Args:
            timeout: Timeout in seconds (1-300)

        Returns:
            Self for method chaining
        """
        self._timeout = float(timeout)
        return self

    def with_max_retries(self, max_retries: int) -> "ClientBuilder":
        """Set the maximum retry attempts.

        Args:
            max_retries: Maximum retries (0-5)

        Returns:
            Self for method chaining
        """
        self._max_retries = max_retries
        return self

    def with_user_agent(self, user_agent: str) -> "ClientBuilder":
        """Set a custom user agent.

        Args:
            user_agent: Custom user agent string

        Returns:
            Self for method chaining
        """
        self._user_agent = user_agent
        return self

    def with_header(self, name: str, value: str) -> "ClientBuilder":
        """Add a single custom header.

        Args:
            name: Header name
            value: Header value

        Returns:
            Self for method chaining
        """
        self._headers[name] = value
        return self

    def with_headers(self, headers: dict[str, str]) -> "ClientBuilder":
        """Add multiple custom headers.

        Args:
            headers: Dictionary of headers to add

        Returns:
            Self for method chaining
        """
        self._headers.update(headers)
        return self

    def with_debug(self, debug: bool = True) -> "ClientBuilder":
        """Enable or disable debug mode.

        Args:
            debug: Whether to enable debug mode

        Returns:
            Self for method chaining
        """
        self._debug = debug
        return self

    @classmethod
    def from_environment(cls) -> "ClientBuilder":
        """Create a builder from environment variables.

        Reads configuration from these environment variables:
        - NVISY_API_TOKEN: API key
        - NVISY_BASE_URL: Base URL
        - NVISY_MAX_TIMEOUT: Timeout in milliseconds
        - NVISY_MAX_RETRIES: Maximum retries
        - NVISY_USER_AGENT: User agent
        - DEBUG: Enable debug mode

        Returns:
            Builder instance configured from environment

        Example:
            >>> builder = ClientBuilder.from_environment()
            >>> client = builder.with_timeout(60).build()
        """
        builder = cls()

        if api_token := os.getenv("NVISY_API_TOKEN"):
            builder = builder.with_api_key(api_token)

        if base_url := os.getenv("NVISY_BASE_URL"):
            builder = builder.with_base_url(base_url)

        if timeout_ms := os.getenv("NVISY_MAX_TIMEOUT"):
            with contextlib.suppress(ValueError, TypeError):
                timeout_seconds = float(timeout_ms) / 1000.0
                builder = builder.with_timeout(timeout_seconds)

        if max_retries := os.getenv("NVISY_MAX_RETRIES"):
            with contextlib.suppress(ValueError, TypeError):
                builder = builder.with_max_retries(int(max_retries))

        if user_agent := os.getenv("NVISY_USER_AGENT"):
            builder = builder.with_user_agent(user_agent)

        if os.getenv("DEBUG", "").lower() in ("true", "1", "yes"):
            builder = builder.with_debug(True)

        return builder

    def build(self) -> "Client":
        """Build the client instance.

        Returns:
            Configured Client instance

        Raises:
            ConfigError: If API key is not provided
        """
        if not self._api_key:
            raise ConfigError.missing_api_key()

        config = ClientConfiguration(
            api_key=self._api_key,
            base_url=self._base_url,
            timeout=self._timeout,
            max_retries=self._max_retries,
            user_agent=self._user_agent,
            headers=self._headers,
            debug=self._debug,
        )

        # Import here to avoid circular imports
        from .client import Client

        return Client(config)
