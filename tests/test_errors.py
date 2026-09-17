"""Tests for error handling."""

import httpx
import pytest

from nvisy import NvisyApiError, NvisyError


def failing(status: int, **response) -> object:
    """Build a handler answering every request with one error.

    Args:
        status: The status code to answer with.
        **response: Passed to `httpx.Response`, such as `json` or `text`.

    Returns:
        A request handler.
    """

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status, **response)

    return handler


class TestHierarchy:
    """The error classes form a flat hierarchy."""

    def test_api_error_is_an_sdk_error(self):
        """Catching NvisyError catches API errors too."""
        assert issubclass(NvisyApiError, NvisyError)

    def test_sdk_error_is_an_exception(self):
        """The base error is a plain exception."""
        assert issubclass(NvisyError, Exception)

    def test_message_is_the_string_form(self):
        """Printing an error shows its message."""
        assert str(NvisyError("something went wrong")) == "something went wrong"


class TestApiErrors:
    """Error responses become typed errors."""

    async def test_raises_on_client_error(self, make_client):
        """A 4xx raises."""
        handler = failing(404, json={"name": "NotFoundError", "message": "No such"})
        async with make_client(handler) as client:
            with pytest.raises(NvisyApiError) as caught:
                await client.workspaces.get_workspace("missing")
        assert caught.value.status_code == 404

    async def test_carries_the_api_error_name(self, make_client):
        """The API's error type is exposed separately from the class name."""
        handler = failing(404, json={"name": "NotFoundError", "message": "No such"})
        async with make_client(handler) as client:
            with pytest.raises(NvisyApiError) as caught:
                await client.workspaces.get_workspace("missing")
        assert caught.value.error_name == "NotFoundError"
        assert type(caught.value).__name__ == "NvisyApiError"

    async def test_carries_the_api_message(self, make_client):
        """The API's message reaches the caller."""
        handler = failing(422, json={"name": "ValidationError", "message": "Bad input"})
        async with make_client(handler) as client:
            with pytest.raises(NvisyApiError, match="Bad input"):
                await client.workspaces.get_workspace("any")

    async def test_captures_the_request_id(self, make_client):
        """A correlation id is kept for support requests."""
        handler = failing(
            500,
            json={"name": "InternalError", "message": "Boom"},
            headers={"x-request-id": "req-123"},
        )
        async with make_client(handler) as client:
            with pytest.raises(NvisyApiError) as caught:
                await client.workspaces.get_workspace("any")
        assert caught.value.request_id == "req-123"

    async def test_raises_on_server_error(self, make_client):
        """A 5xx raises."""
        handler = failing(500, json={"name": "InternalError", "message": "Boom"})
        async with make_client(handler) as client:
            with pytest.raises(NvisyApiError):
                await client.workspaces.get_workspace("any")


class TestMalformedErrors:
    """An error response is never assumed well-formed."""

    async def test_falls_back_on_html(self, make_client):
        """An HTML error page still produces a typed error."""
        async with make_client(failing(502, text="<html>Bad Gateway</html>")) as client:
            with pytest.raises(NvisyApiError) as caught:
                await client.workspaces.get_workspace("any")
        assert caught.value.status_code == 502
        assert "502" in caught.value.message

    async def test_falls_back_on_empty_body(self, make_client):
        """An empty error body still produces a typed error."""
        async with make_client(failing(401)) as client:
            with pytest.raises(NvisyApiError) as caught:
                await client.workspaces.get_workspace("any")
        assert caught.value.status_code == 401

    async def test_falls_back_on_partial_json(self, make_client):
        """A body missing the error name still produces a typed error."""
        async with make_client(failing(400, json={"message": "Just a message"})) as c:
            with pytest.raises(NvisyApiError) as caught:
                await c.workspaces.get_workspace("any")
        assert caught.value.message == "Just a message"
        assert caught.value.error_name == "ApiError"


class TestClassification:
    """Errors classify themselves for the caller."""

    def test_client_error(self):
        """A 4xx is a client error."""
        error = NvisyApiError("m", 404, error_name="NotFoundError")
        assert error.is_client_error()
        assert not error.is_server_error()

    def test_server_error(self):
        """A 5xx is a server error."""
        error = NvisyApiError("m", 500, error_name="InternalError")
        assert error.is_server_error()
        assert not error.is_client_error()

    @pytest.mark.parametrize("status", [500, 502, 503, 408, 429])
    def test_retryable(self, status):
        """Server errors, timeouts, and rate limits are worth retrying."""
        assert NvisyApiError("m", status, error_name="E").is_retryable()

    @pytest.mark.parametrize("status", [400, 401, 403, 404, 422])
    def test_not_retryable(self, status):
        """Ordinary client errors are not worth retrying."""
        assert not NvisyApiError("m", status, error_name="E").is_retryable()


class TestNetworkFailures:
    """Transport failures surface as SDK errors."""

    async def test_wraps_a_connection_failure(self, make_client):
        """A connection failure is raised as an SDK error."""

        def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.ConnectError("connection refused")

        async with make_client(handler) as client:
            with pytest.raises(NvisyError, match="connection refused"):
                await client.workspaces.get_workspace("any")

    async def test_keeps_the_underlying_cause(self, make_client):
        """The httpx error is chained, so the detail is not lost."""

        def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.ConnectTimeout("timed out")

        async with make_client(handler) as client:
            with pytest.raises(NvisyError) as caught:
                await client.workspaces.get_workspace("any")
        assert isinstance(caught.value.__cause__, httpx.ConnectTimeout)

    async def test_network_failure_is_not_an_api_error(self, make_client):
        """A transport failure is not mistaken for an API response."""

        def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.ConnectError("connection refused")

        async with make_client(handler) as client:
            with pytest.raises(NvisyError) as caught:
                await client.workspaces.get_workspace("any")
        assert not isinstance(caught.value, NvisyApiError)
