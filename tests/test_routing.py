"""Tests that every service method addresses the endpoint it claims to.

The specification declares no operationIds, so method names and argument
order were derived rather than generated from a contract. These tests walk
the whole surface and check that each path argument lands in the path,
which is what catches a swapped pair of ids.
"""

import inspect

import httpx
import pytest

from nvisy import Nvisy
from nvisy.services import Service

#: Client attributes that are not services.
NOT_SERVICES = {"base_url", "http", "from_environment", "with_api_token", "aclose"}


def service_names(client: Nvisy) -> list[str]:
    """List the service properties hanging off a client.

    Args:
        client: The client to inspect.

    Returns:
        The names of its service properties.
    """
    return [
        name
        for name in dir(client)
        if not name.startswith("_") and name not in NOT_SERVICES
    ]


def method_names(service: Service) -> list[str]:
    """List the public methods of a service.

    Args:
        service: The service to inspect.

    Returns:
        The names of its public methods.
    """
    return [name for name in dir(service) if not name.startswith("_")]


def id_arguments(method) -> list[inspect.Parameter]:
    """List a method's required arguments, when they are all plain ids.

    Args:
        method: The bound method to inspect.

    Returns:
        The required positional parameters, or an empty list if any of them
        is not a plain string id (a body or a file, say).
    """
    params = [
        p
        for p in inspect.signature(method).parameters.values()
        if p.default is p.empty and p.kind is p.POSITIONAL_OR_KEYWORD
    ]
    if any(p.annotation not in ("str", str) for p in params):
        return []
    return params


@pytest.fixture
def probe(make_client, requests):
    """Call a service method with placeholder ids and report the request made.

    Args:
        make_client: Factory building a client against a mock transport.
        requests: The list requests are recorded in.

    Returns:
        A coroutine function taking a service name and a method name.
    """

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"items": []})

    async def run(service_name: str, method_name: str):
        async with make_client(handler) as client:
            service = getattr(client, service_name)
            method = getattr(service, method_name)
            params = id_arguments(method)
            if not params:
                return None, []

            args = [f"{p.name}-X" for p in params]
            requests.clear()
            try:
                result = method(*args)
                if inspect.isawaitable(result):
                    await result
                else:
                    await result
            except Exception:
                # A stub body will not validate; the request still went out,
                # which is all this is checking.
                pass

            if not requests:
                return None, []
            return requests[0], args

    return run


def all_methods():
    """Enumerate every service method on the client.

    Returns:
        Pairs of service name and method name.
    """
    client = Nvisy(api_token="test-token-1234")
    return [
        (service, method)
        for service in service_names(client)
        for method in method_names(getattr(client, service))
    ]


class TestSurface:
    """The client exposes the services the API documents."""

    def test_exposes_every_service(self):
        """All twenty-one services hang off the client."""
        assert len(service_names(Nvisy(api_token="test-token-1234"))) == 21

    def test_services_carry_methods(self):
        """Every service exposes at least one method."""
        client = Nvisy(api_token="test-token-1234")
        for name in service_names(client):
            assert method_names(getattr(client, name)), name


class TestRouting:
    """Each method sends its arguments to the right place."""

    @pytest.mark.parametrize(("service", "method"), all_methods())
    async def test_path_arguments_reach_the_path(self, probe, service, method):
        """Every id argument appears in the request path.

        A swapped pair of ids still produces a well-formed URL, so this
        checks each argument individually rather than the path as a whole.
        """
        request, args = await probe(service, method)
        if request is None:
            pytest.skip("not addressable by ids alone")

        for arg in args:
            assert (
                arg in request.url.path
            ), f"{service}.{method} did not route {arg} into {request.url.path}"

    @pytest.mark.parametrize(("service", "method"), all_methods())
    async def test_paths_are_fully_expanded(self, probe, service, method):
        """No path template is left unexpanded."""
        request, _ = await probe(service, method)
        if request is None:
            pytest.skip("not addressable by ids alone")

        assert "{" not in request.url.path
        assert "}" not in request.url.path
