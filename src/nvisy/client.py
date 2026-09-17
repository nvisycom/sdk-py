"""Main client class for the Nvisy SDK."""

import asyncio
import time
from typing import TYPE_CHECKING, Any
from urllib.parse import urljoin

import httpx

from .config import ClientConfiguration
from .errors import ApiError, NetworkError

if TYPE_CHECKING:
    from .builder import ClientBuilder


class Client:
    """Main client for the Nvisy API.

    Provides HTTP request functionality with automatic retries,
    error handling, and both async and sync interfaces.
    """

    def __init__(self, config: ClientConfiguration | dict[str, Any]) -> None:
        """Initialize the client.

        Args:
            config: Configuration object or dictionary
        """
        if isinstance(config, dict):
            self.config = ClientConfiguration(**config)
        else:
            self.config = config

        self._http_client: httpx.AsyncClient | None = None
        self._sync_http_client: httpx.Client | None = None

    @classmethod
    def builder(cls) -> "ClientBuilder":
        """Create a client builder for fluent configuration.

        Returns:
            New ClientBuilder instance
        """
        from .builder import ClientBuilder

        return ClientBuilder()

    @classmethod
    def from_environment(cls) -> "Client":
        """Create a client from environment variables.

        Returns:
            Client configured from environment variables
        """
        config = ClientConfiguration.from_environment()
        return cls(config)

    def _get_async_client(self) -> httpx.AsyncClient:
        """Get or create the async HTTP client."""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(
                base_url=self.config.base_url,
                headers=self.config.get_effective_headers(),
                timeout=httpx.Timeout(
                    connect=10.0, read=self.config.timeout, write=10.0, pool=5.0
                ),
                limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
                follow_redirects=True,
            )
        return self._http_client

    def _get_sync_client(self) -> httpx.Client:
        """Get or create the sync HTTP client."""
        if self._sync_http_client is None:
            self._sync_http_client = httpx.Client(
                base_url=self.config.base_url,
                headers=self.config.get_effective_headers(),
                timeout=httpx.Timeout(
                    connect=10.0, read=self.config.timeout, write=10.0, pool=5.0
                ),
                limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
                follow_redirects=True,
            )
        return self._sync_http_client

    async def request(  # noqa: PLR0912
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Make an async HTTP request with retry logic.

        Args:
            method: HTTP method
            path: API endpoint path
            params: Query parameters
            json: JSON request body
            data: Form data
            headers: Additional headers

        Returns:
            Response data

        Raises:
            ApiError: For API errors
            NetworkError: For network/connection errors
        """
        client = self._get_async_client()
        url = (
            path
            if path.startswith(("http://", "https://"))
            else urljoin(self.config.base_url + "/", path.lstrip("/"))
        )

        request_headers = {}
        if headers:
            request_headers.update(headers)

        attempt = 0
        last_exception: Exception | None = None

        while attempt <= self.config.max_retries:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json,
                    data=data,
                    headers=request_headers,
                )

                # Handle successful responses
                if 200 <= response.status_code < 300:
                    content_type = response.headers.get("content-type", "")
                    if content_type.startswith("application/json"):
                        return response.json()
                    return {"data": response.text}

                # Handle error responses
                try:
                    error_data = response.json()
                except Exception:
                    error_data = {"message": response.text or "Unknown error"}

                request_id = response.headers.get("x-request-id")
                raise ApiError.from_response(
                    response.status_code,
                    response.reason_phrase,
                    error_data,
                    request_id,
                )

            except httpx.TimeoutException as e:
                timeout_ms = int(self.config.timeout * 1000)
                last_exception = NetworkError.timeout(timeout_ms)
                last_exception.cause = e
            except httpx.ConnectError as e:
                last_exception = NetworkError.connection("Failed to connect to API", e)
            except httpx.HTTPError as e:
                last_exception = NetworkError.connection("HTTP error occurred", e)
            except ApiError:
                # Re-raise API errors immediately without retry
                raise

            attempt += 1
            if attempt <= self.config.max_retries and last_exception:
                # Simple exponential backoff
                await asyncio.sleep(min(2 ** (attempt - 1), 10))

        if last_exception:
            raise last_exception
        raise NetworkError.connection("Request failed after all retry attempts")

    def request_sync(  # noqa: PLR0912
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Make a sync HTTP request with retry logic.

        Args:
            method: HTTP method
            path: API endpoint path
            params: Query parameters
            json: JSON request body
            data: Form data
            headers: Additional headers

        Returns:
            Response data

        Raises:
            ApiError: For API errors
            NetworkError: For network/connection errors
        """
        client = self._get_sync_client()
        url = (
            path
            if path.startswith(("http://", "https://"))
            else urljoin(self.config.base_url + "/", path.lstrip("/"))
        )

        request_headers = {}
        if headers:
            request_headers.update(headers)

        attempt = 0
        last_exception: Exception | None = None

        while attempt <= self.config.max_retries:
            try:
                response = client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json,
                    data=data,
                    headers=request_headers,
                )

                # Handle successful responses
                if 200 <= response.status_code < 300:
                    content_type = response.headers.get("content-type", "")
                    if content_type.startswith("application/json"):
                        return response.json()
                    return {"data": response.text}

                # Handle error responses
                try:
                    error_data = response.json()
                except Exception:
                    error_data = {"message": response.text or "Unknown error"}

                request_id = response.headers.get("x-request-id")
                raise ApiError.from_response(
                    response.status_code,
                    response.reason_phrase,
                    error_data,
                    request_id,
                )

            except httpx.TimeoutException as e:
                timeout_ms = int(self.config.timeout * 1000)
                last_exception = NetworkError.timeout(timeout_ms)
                last_exception.cause = e
            except httpx.ConnectError as e:
                last_exception = NetworkError.connection("Failed to connect to API", e)
            except httpx.HTTPError as e:
                last_exception = NetworkError.connection("HTTP error occurred", e)
            except ApiError:
                # Re-raise API errors immediately without retry
                raise

            attempt += 1
            if attempt <= self.config.max_retries and last_exception:
                # Simple exponential backoff
                time.sleep(min(2 ** (attempt - 1), 10))

        if last_exception:
            raise last_exception
        raise NetworkError.connection("Request failed after all retry attempts")

    # Convenience methods for common HTTP verbs
    async def get(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Make a GET request."""
        return await self.request("GET", path, params=params, headers=headers)

    async def post(
        self,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Make a POST request."""
        return await self.request(
            "POST", path, json=json, data=data, params=params, headers=headers
        )

    async def put(
        self,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Make a PUT request."""
        return await self.request(
            "PUT", path, json=json, data=data, params=params, headers=headers
        )

    async def patch(
        self,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Make a PATCH request."""
        return await self.request(
            "PATCH", path, json=json, data=data, params=params, headers=headers
        )

    async def delete(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Make a DELETE request."""
        return await self.request("DELETE", path, params=params, headers=headers)

    # Sync versions
    def get_sync(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Make a sync GET request."""
        return self.request_sync("GET", path, params=params, headers=headers)

    def post_sync(
        self,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Make a sync POST request."""
        return self.request_sync(
            "POST", path, json=json, data=data, params=params, headers=headers
        )

    def put_sync(
        self,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Make a sync PUT request."""
        return self.request_sync(
            "PUT", path, json=json, data=data, params=params, headers=headers
        )

    def patch_sync(
        self,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Make a sync PATCH request."""
        return self.request_sync(
            "PATCH", path, json=json, data=data, params=params, headers=headers
        )

    def delete_sync(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Make a sync DELETE request."""
        return self.request_sync("DELETE", path, params=params, headers=headers)

    async def close(self) -> None:
        """Close the async HTTP client."""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

    def close_sync(self) -> None:
        """Close the sync HTTP client."""
        if self._sync_http_client:
            self._sync_http_client.close()
            self._sync_http_client = None

    async def __aenter__(self) -> "Client":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    def __enter__(self) -> "Client":
        """Sync context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Sync context manager exit."""
        self.close_sync()

    def __repr__(self) -> str:
        """Return a string representation of the client."""
        return (
            f"Client(base_url={self.config.base_url!r}, timeout={self.config.timeout})"
        )
