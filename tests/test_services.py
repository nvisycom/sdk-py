"""Tests for the service layer."""

import httpx

from nvisy.datatypes import CreateWorkspace

from conftest import workspace


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


class TestRequests:
    """Services issue the requests their methods describe."""

    async def test_get_uses_the_resource_path(self, make_client, requests):
        """A read addresses the resource by id."""
        handler = responds(200, json=workspace(1, "alpha"))
        async with make_client(handler) as client:
            await client.workspaces.get_workspace("ws-1")
        assert requests[0].url.path == "/workspaces/ws-1"
        assert requests[0].method == "GET"

    async def test_delete_uses_the_resource_path(self, make_client, requests):
        """A delete addresses the resource by id."""
        handler = responds(204)
        async with make_client(handler) as client:
            await client.workspaces.delete_workspace("ws-1")
        assert requests[0].method == "DELETE"
        assert requests[0].url.path == "/workspaces/ws-1"

    async def test_parses_the_response(self, make_client):
        """A response becomes a typed model."""
        handler = responds(200, json=workspace(1, "alpha"))
        async with make_client(handler) as client:
            result = await client.workspaces.get_workspace("ws-1")
        assert result.display_name == "Alpha"


class TestBodies:
    """Request bodies are serialized for the wire."""

    async def test_sends_camel_case(self, make_client, requests):
        """Model fields are sent under their API names."""
        handler = responds(201, json=workspace(1, "alpha"))
        async with make_client(handler) as client:
            await client.workspaces.create_workspace(
                CreateWorkspace(handle="alpha", displayName="Alpha")
            )
        assert b"displayName" in requests[0].read()

    async def test_omits_unset_fields(self, make_client, requests):
        """Fields the caller left unset are not sent."""
        handler = responds(201, json=workspace(1, "alpha"))
        async with make_client(handler) as client:
            await client.workspaces.create_workspace(
                CreateWorkspace(handle="alpha", displayName="Alpha")
            )
        assert b"description" not in requests[0].read()


class TestQueryParameters:
    """Query parameters are cleaned before they are sent."""

    async def test_drops_unset_parameters(self, make_client, requests):
        """A parameter the caller omitted is not sent."""
        handler = responds(200, json={"items": []})
        async with make_client(handler) as client:
            await client.workspaces.list_workspaces()
        assert "limit" not in requests[0].url.params

    async def test_sends_given_parameters(self, make_client, requests):
        """A parameter the caller set is sent."""
        handler = responds(200, json={"items": []})
        async with make_client(handler) as client:
            await client.workspaces.list_workspaces(limit=50)
        assert requests[0].url.params["limit"] == "50"

    async def test_renders_booleans_lowercase(self, make_client, requests):
        """A boolean is sent as the API expects it."""
        handler = responds(200, json={"items": []})
        async with make_client(handler) as client:
            await client.workspaces.list_workspaces(include_count=True)
        assert requests[0].url.params["includeCount"] == "true"


class TestPagination:
    """List methods return a paginator over the endpoint."""

    def pages(self):
        """Build a handler serving two pages.

        Returns:
            A request handler.
        """

        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.params.get("after") is None:
                return httpx.Response(
                    200,
                    json={
                        "items": [workspace(1, "alpha")],
                        "nextCursor": "c1",
                        "total": 2,
                    },
                )
            return httpx.Response(200, json={"items": [workspace(2, "beta")]})

        return handler

    async def test_await_yields_one_page(self, make_client, requests):
        """Awaiting a list method fetches a single page."""
        async with make_client(self.pages()) as client:
            page = await client.workspaces.list_workspaces()
        assert [w.display_name for w in page.items] == ["Alpha"]
        assert len(requests) == 1

    async def test_await_exposes_the_total(self, make_client):
        """The page's total is available when requested."""
        async with make_client(self.pages()) as client:
            page = await client.workspaces.list_workspaces()
        assert page.total == 2

    async def test_iteration_spans_pages(self, make_client, requests):
        """Iterating a list method walks every page."""
        async with make_client(self.pages()) as client:
            names = [w.display_name async for w in client.workspaces.list_workspaces()]
        assert names == ["Alpha", "Beta"]
        assert len(requests) == 2

    async def test_iteration_threads_the_cursor(self, make_client, requests):
        """Each page after the first carries the previous cursor."""
        async with make_client(self.pages()) as client:
            [w async for w in client.workspaces.list_workspaces()]
        assert requests[1].url.params["after"] == "c1"


class TestHealth:
    """The health endpoints report status rather than failing."""

    async def test_unhealthy_does_not_raise(self, make_client):
        """A 503 from /health is parsed, since it describes the server."""
        payload = {
            "status": "unhealthy",
            "timestamp": "2026-01-01T00:00:00Z",
            "checks": [],
        }
        handler = responds(503, json=payload)
        async with make_client(handler) as client:
            assert (await client.status.check_health()).status == "unhealthy"

    async def test_readiness_reports_unhealthy(self, make_client):
        """A 503 from /health/ready is parsed too."""
        payload = {
            "status": "degraded",
            "timestamp": "2026-01-01T00:00:00Z",
            "checks": [],
        }
        handler = responds(503, json=payload)
        async with make_client(handler) as client:
            assert (await client.status.check_readiness()).status == "degraded"
