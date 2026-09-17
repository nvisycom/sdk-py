"""Tests for the client and its configuration."""

import httpx
import pytest

import nvisy

DEFAULT_BASE_URL = nvisy.DEFAULT_BASE_URL
Nvisy = nvisy.Nvisy
NvisyError = nvisy.NvisyError

from conftest import API_TOKEN


def ok(request: httpx.Request) -> httpx.Response:
    """Answer any request with an empty object.

    Args:
        request: The request being answered.

    Returns:
        An empty 200 response.
    """
    return httpx.Response(200, json={})


class TestVersion:
    """The package reports its version."""

    def test_is_a_semver_string(self):
        """The version is a dotted string."""
        assert isinstance(nvisy.__version__, str)
        assert len(nvisy.__version__.split(".")) >= 3

    def test_is_exported(self):
        """Everything named in __all__ can be imported."""
        for name in nvisy.__all__:
            assert hasattr(nvisy, name), name


class TestApiToken:
    """The API token is validated when the client is built."""

    def test_accepts_a_valid_token(self):
        """A conforming token is accepted."""
        assert Nvisy(api_token=API_TOKEN).base_url == DEFAULT_BASE_URL

    def test_accepts_dots(self):
        """A JWT-shaped token is accepted, since the API issues them."""
        assert Nvisy(api_token="header.payload.signature")

    def test_rejects_empty(self):
        """An empty token is rejected."""
        with pytest.raises(NvisyError, match="non-empty string"):
            Nvisy(api_token="")

    def test_rejects_whitespace(self):
        """A token of only whitespace is rejected."""
        with pytest.raises(NvisyError, match="non-empty string"):
            Nvisy(api_token="   ")

    def test_rejects_short(self):
        """A token below the minimum length is rejected."""
        with pytest.raises(NvisyError, match="at least 10 characters"):
            Nvisy(api_token="short")

    def test_rejects_invalid_characters(self):
        """A token with characters outside the allowed set is rejected."""
        with pytest.raises(NvisyError, match="invalid characters"):
            Nvisy(api_token="token with spaces")

    def test_strips_surrounding_whitespace(self, make_client, requests):
        """A padded token is sent trimmed."""
        client = make_client(ok, api_token=f"  {API_TOKEN}  ")
        assert client

    async def test_is_sent_as_a_bearer_token(self, make_client, requests):
        """The token authenticates every request."""
        async with make_client(ok) as client:
            await client.status.check_liveness()
        assert requests[0].headers["authorization"] == f"Bearer {API_TOKEN}"


class TestBaseUrl:
    """The base URL is validated and normalized."""

    def test_defaults_to_the_public_api(self):
        """Without one, requests go to the public API."""
        assert Nvisy(api_token=API_TOKEN).base_url == DEFAULT_BASE_URL

    def test_strips_a_trailing_slash(self):
        """A trailing slash is removed, so paths join predictably."""
        client = Nvisy(api_token=API_TOKEN, base_url="https://api.example.com/")
        assert client.base_url == "https://api.example.com"

    def test_rejects_a_non_http_scheme(self):
        """A non-HTTP URL is rejected."""
        with pytest.raises(NvisyError, match="HTTP or HTTPS"):
            Nvisy(api_token=API_TOKEN, base_url="ftp://api.example.com")

    def test_rejects_a_malformed_url(self):
        """A URL without a host is rejected."""
        with pytest.raises(NvisyError, match="valid HTTP/HTTPS URL"):
            Nvisy(api_token=API_TOKEN, base_url="not-a-url")


class TestHeaders:
    """Headers are merged over the defaults."""

    async def test_sends_a_default_user_agent(self, make_client, requests):
        """The SDK identifies itself by default."""
        async with make_client(ok) as client:
            await client.status.check_liveness()
        assert requests[0].headers["user-agent"].startswith("nvisy-sdk-python/")

    async def test_accepts_a_custom_user_agent(self, make_client, requests):
        """A caller can identify their own application."""
        async with make_client(ok, user_agent="MyApp/1.0") as client:
            await client.status.check_liveness()
        assert requests[0].headers["user-agent"] == "MyApp/1.0"

    async def test_sends_custom_headers(self, make_client, requests):
        """Extra headers reach the API."""
        async with make_client(ok, headers={"X-Custom": "value"}) as client:
            await client.status.check_liveness()
        assert requests[0].headers["x-custom"] == "value"

    async def test_custom_headers_win(self, make_client, requests):
        """A custom header overrides the default of the same name."""
        async with make_client(ok, headers={"Accept": "text/plain"}) as client:
            await client.status.check_liveness()
        assert requests[0].headers["accept"] == "text/plain"


class TestFromEnvironment:
    """The client can be configured from the environment."""

    def test_reads_the_token(self, monkeypatch):
        """The token comes from NVISY_API_TOKEN."""
        monkeypatch.setenv("NVISY_API_TOKEN", API_TOKEN)
        assert Nvisy.from_environment().base_url == DEFAULT_BASE_URL

    def test_reads_the_base_url(self, monkeypatch):
        """The base URL comes from NVISY_BASE_URL."""
        monkeypatch.setenv("NVISY_API_TOKEN", API_TOKEN)
        monkeypatch.setenv("NVISY_BASE_URL", "https://api.example.com")
        assert Nvisy.from_environment().base_url == "https://api.example.com"

    def test_requires_a_token(self, monkeypatch):
        """Without a token, building the client fails."""
        monkeypatch.delenv("NVISY_API_TOKEN", raising=False)
        with pytest.raises(NvisyError, match="NVISY_API_TOKEN"):
            Nvisy.from_environment()

    def test_overrides_win(self, monkeypatch):
        """An explicit argument beats the environment."""
        monkeypatch.setenv("NVISY_API_TOKEN", API_TOKEN)
        monkeypatch.setenv("NVISY_BASE_URL", "https://from-env.example.com")
        client = Nvisy.from_environment(base_url="https://explicit.example.com")
        assert client.base_url == "https://explicit.example.com"


class TestWithApiToken:
    """A client can be rebuilt with a different token."""

    def test_returns_a_new_client(self):
        """The original client is left alone."""
        client = Nvisy(api_token=API_TOKEN)
        other = client.with_api_token("another-token-5678")
        assert other is not client

    def test_preserves_other_settings(self):
        """Everything but the token carries over."""
        client = Nvisy(api_token=API_TOKEN, base_url="https://api.example.com")
        assert client.with_api_token("another-token-5678").base_url == (
            "https://api.example.com"
        )

    def test_validates_the_new_token(self):
        """An invalid replacement token is rejected."""
        client = Nvisy(api_token=API_TOKEN)
        with pytest.raises(NvisyError, match="at least 10 characters"):
            client.with_api_token("short")


class TestLifecycle:
    """The client manages its connections."""

    async def test_is_an_async_context_manager(self, make_client):
        """The client closes itself on leaving the block."""
        async with make_client(ok) as client:
            assert client.base_url == DEFAULT_BASE_URL

    async def test_can_be_closed_explicitly(self, make_client):
        """Closing without the context manager also works."""
        client = make_client(ok)
        await client.aclose()

    def test_repr_hides_the_token(self):
        """The representation never discloses the token."""
        assert API_TOKEN not in repr(Nvisy(api_token=API_TOKEN))

    def test_repr_names_the_base_url(self):
        """The representation says where requests go."""
        assert DEFAULT_BASE_URL in repr(Nvisy(api_token=API_TOKEN))


class TestServices:
    """Services hang off the client."""

    def test_exposes_services(self):
        """Each service is reachable by name."""
        client = Nvisy(api_token=API_TOKEN)
        assert client.status is not None
        assert client.workspaces is not None

    def test_exposes_the_http_client(self):
        """The underlying client is available as an escape hatch."""
        assert Nvisy(api_token=API_TOKEN).http is not None
