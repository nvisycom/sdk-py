"""Shared test fixtures."""

import httpx
import pytest

from nvisy import Nvisy

#: A token that passes validation, for tests that need any valid one.
API_TOKEN = "test-token-1234"

#: An account reference, as the API embeds one in most resources.
ACCOUNT_REF = {
    "id": "550e8400-e29b-41d4-a716-4466554400aa",
    "username": "owner",
}


def workspace(suffix: int, handle: str) -> dict:
    """Build a workspace payload as the API would return it.

    Args:
        suffix: Digit distinguishing this workspace's id.
        handle: The workspace's handle.

    Returns:
        The payload, in the API's camelCase wire format.
    """
    return {
        "id": f"550e8400-e29b-41d4-a716-44665544000{suffix}",
        "handle": handle,
        "displayName": handle.title(),
        "memberRole": "owner",
        "createdBy": ACCOUNT_REF,
        "settings": {},
        "createdAt": "2026-01-01T00:00:00Z",
        "updatedAt": "2026-01-01T00:00:00Z",
    }


@pytest.fixture
def api_token() -> str:
    """A token that passes validation."""
    return API_TOKEN


@pytest.fixture
def requests() -> list[httpx.Request]:
    """Record of the requests a client issued."""
    return []


@pytest.fixture
def make_client(requests):
    """Build a client whose responses come from a handler.

    Args:
        requests: The list each issued request is recorded in.

    Returns:
        A factory taking a request handler and returning a client.
    """

    def factory(handler, **options) -> Nvisy:
        def recording(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            return handler(request)

        return Nvisy(
            api_token=options.pop("api_token", API_TOKEN),
            transport=httpx.MockTransport(recording),
            **options,
        )

    return factory
