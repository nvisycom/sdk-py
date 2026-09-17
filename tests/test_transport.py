"""Tests for how requests are put on the wire.

These cover the parts that are easy to get subtly wrong: which content type a
body earns, which token authenticates a cloned client, whether logging works
at all, and which error statuses are allowed to reach the caller.
"""

import logging

import httpx
import pytest

from nvisy import Nvisy, NvisyApiError, NvisyError
from nvisy.datatypes import CreateWorkspace

from conftest import API_TOKEN, workspace

HEALTH = {"status": "unhealthy", "timestamp": "2026-01-01T00:00:00Z", "checks": []}


def responds(status: int, **response):
    """Build a handler answering every request the same way.

    Args:
        status: The status code to answer with.
        **response: Passed to `httpx.Response`, such as `json`.

    Returns:
        A request handler.
    """

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status, **response)

    return handler


class TestContentType:
    """httpx decides the content type from the body it is given."""

    async def test_json_body(self, make_client, requests):
        """A JSON body is sent as JSON."""
        handler = responds(201, json=workspace(1, "alpha"))
        async with make_client(handler) as client:
            await client.workspaces.create_workspace(
                CreateWorkspace(handle="alpha", displayName="Alpha")
            )
        assert requests[0].headers["content-type"] == "application/json"

    async def test_no_body(self, make_client, requests):
        """A request without a body sends no content type."""
        async with make_client(responds(200, json=workspace(1, "alpha"))) as client:
            await client.workspaces.get_workspace("ws-1")
        assert "content-type" not in requests[0].headers

    async def test_multipart_body(self, make_client, requests):
        """An upload is multipart, with the boundary httpx generated.

        A blanket `Content-Type: application/json` on the client would leave
        the boundary off and the upload unparseable.
        """
        async with make_client(responds(200, json={})) as client:
            await client.workspaces.upload_avatar("ws-1", b"image-bytes")

        content_type = requests[0].headers["content-type"]
        assert content_type.startswith("multipart/form-data")
        assert "boundary=" in content_type

    async def test_caller_content_type_cannot_break_an_upload(self, requests):
        """A caller's Content-Type never labels a multipart body.

        httpx generates the multipart type and its boundary from the body, but
        a client-level header outranks that, so an upload would go out labelled
        as something it is not.
        """

        def recording(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            return httpx.Response(200, json={})

        client = Nvisy(
            api_token=API_TOKEN,
            headers={"Content-Type": "application/json", "X-Custom": "keep-me"},
            transport=httpx.MockTransport(recording),
        )
        async with client:
            await client.workspaces.upload_avatar("ws-1", b"image-bytes")

        assert requests[0].headers["content-type"].startswith("multipart/form-data")

    async def test_other_caller_headers_survive(self, requests):
        """Dropping Content-Type leaves the caller's other headers alone."""

        def recording(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            return httpx.Response(200, json={})

        client = Nvisy(
            api_token=API_TOKEN,
            headers={"Content-Type": "application/json", "X-Custom": "keep-me"},
            transport=httpx.MockTransport(recording),
        )
        async with client:
            await client.status.check_liveness()

        assert requests[0].headers["x-custom"] == "keep-me"
        assert requests[0].headers["authorization"] == f"Bearer {API_TOKEN}"

    async def test_multipart_body_is_encoded(self, make_client, requests):
        """The uploaded bytes reach the wire inside the multipart body."""
        async with make_client(responds(200, json={})) as client:
            await client.workspaces.upload_avatar("ws-1", b"image-bytes")
        assert b"image-bytes" in requests[0].read()


class TestAuthorization:
    """The token a client was built with is the one it sends."""

    async def test_sends_the_token(self, make_client, requests):
        """The configured token authenticates the request."""
        async with make_client(responds(200, json={})) as client:
            await client.status.check_liveness()
        assert requests[0].headers["authorization"] == f"Bearer {API_TOKEN}"

    async def test_replacement_token_wins(self, requests):
        """A cloned client authenticates with its new token.

        A caller may have passed `Authorization` among their custom headers;
        that must not outrank the token the clone was given, or the clone
        silently keeps using the old credential.
        """

        def recording(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            return httpx.Response(200, json={})

        client = Nvisy(
            api_token=API_TOKEN,
            headers={"Authorization": "Bearer stale-token-9999"},
            transport=httpx.MockTransport(recording),
        )
        async with client.with_api_token("replacement-token-5678") as clone:
            await clone.status.check_liveness()

        assert requests[0].headers["authorization"] == "Bearer replacement-token-5678"


class TestLogging:
    """Logging reports each request without breaking it."""

    async def test_requests_succeed(self, requests, caplog):
        """Turning logging on does not break the request.

        The duration cannot come from `response.elapsed`, which raises until
        the response has been read — and a response hook runs before that.
        """

        def recording(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            return httpx.Response(200, json={})

        client = Nvisy(
            api_token=API_TOKEN,
            with_logging=True,
            transport=httpx.MockTransport(recording),
        )
        with caplog.at_level(logging.DEBUG, logger="nvisy"):
            async with client:
                await client.status.check_liveness()

        assert requests, "the request was never sent"

    async def test_logs_the_response(self, caplog):
        """The response is logged with its status."""
        client = Nvisy(
            api_token=API_TOKEN,
            with_logging=True,
            transport=httpx.MockTransport(lambda r: httpx.Response(200, json={})),
        )
        with caplog.at_level(logging.DEBUG, logger="nvisy"):
            async with client:
                await client.status.check_liveness()

        assert any("200" in record.getMessage() for record in caplog.records)

    async def test_stays_quiet_by_default(self, make_client, caplog):
        """Nothing is logged unless logging was asked for."""
        with caplog.at_level(logging.DEBUG, logger="nvisy"):
            async with make_client(responds(200, json={})) as client:
                await client.status.check_liveness()

        assert not caplog.records


class TestAllowedStatuses:
    """Only the statuses a method names are allowed through."""

    async def test_health_returns_its_report(self, make_client):
        """A 503 from /health is the report, not a failure."""
        async with make_client(responds(503, json=HEALTH)) as client:
            assert (await client.status.check_health()).status == "unhealthy"

    async def test_readiness_returns_its_report(self, make_client):
        """A 503 from /health/ready is the report too."""
        async with make_client(responds(503, json=HEALTH)) as client:
            assert (await client.status.check_readiness()).status == "unhealthy"

    @pytest.mark.parametrize("status", [401, 403, 404, 500])
    async def test_other_statuses_still_raise(self, make_client, status):
        """Any other error on /health raises rather than failing to parse.

        Suppressing every status would hand a 401 body to the health model
        and surface a validation error instead of the real problem.
        """
        payload = {"name": "Unauthorized", "message": "bad token"}
        async with make_client(responds(status, json=payload)) as client:
            with pytest.raises(NvisyApiError) as caught:
                await client.status.check_health()
        assert caught.value.status_code == status

    async def test_liveness_raises(self, make_client):
        """The liveness probe allows nothing, so any error raises."""
        async with make_client(responds(503, json=HEALTH)) as client:
            with pytest.raises(NvisyApiError):
                await client.status.check_liveness()


class TestFromEnvironment:
    """The token may come from the environment or from an override."""

    def test_reads_a_supplied_mapping(self, monkeypatch):
        """A mapping passed in is read instead of the process environment."""
        monkeypatch.delenv("NVISY_API_TOKEN", raising=False)
        client = Nvisy.from_environment({"NVISY_API_TOKEN": "mapping-token-1234"})
        assert client.base_url

    def test_override_supplies_the_token(self, monkeypatch):
        """An override alone is enough, with nothing in the environment."""
        monkeypatch.delenv("NVISY_API_TOKEN", raising=False)
        client = Nvisy.from_environment(api_token="override-token-5678")
        assert client.base_url

    def test_reports_a_missing_token(self, monkeypatch):
        """With neither a variable nor an override, the token is reported."""
        monkeypatch.delenv("NVISY_API_TOKEN", raising=False)
        with pytest.raises(NvisyError, match="NVISY_API_TOKEN"):
            Nvisy.from_environment({})
