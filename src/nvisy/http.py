"""HTTP transport for the Nvisy SDK.

Builds the `httpx.AsyncClient` every service shares. Error responses are
turned into exceptions by a response hook rather than by the services, so a
service method is just the request it makes.
"""

from __future__ import annotations

import json
import logging
import time
from typing import TYPE_CHECKING

import httpx

from .config import DEFAULT_BASE_URL, default_user_agent
from .errors import NvisyApiError, NvisyError

if TYPE_CHECKING:
    from collections.abc import Mapping

logger = logging.getLogger("nvisy")

#: Header carrying the correlation id, when the API sends one.
REQUEST_ID_HEADER = "x-request-id"

#: Request extension holding the error statuses whose body is meaningful and
#: should reach the caller as a response rather than an exception.
ALLOWED_STATUSES = "nvisy_allowed_statuses"

#: Request extension holding when the request was sent, for the logging hook.
START_TIME = "nvisy_start_time"


async def _raise_for_error(response: httpx.Response) -> None:
    """Raise `NvisyApiError` for any error response.

    Registered as an httpx response hook, so every request is covered without
    a service having to check. The body is read here only on failure, leaving
    successful streaming responses untouched.

    Args:
        response: The response to inspect.

    Raises:
        NvisyApiError: If the response carries a 4xx or 5xx status.
    """
    if not response.is_error:
        return
    allowed = response.request.extensions.get(ALLOWED_STATUSES)
    if allowed and response.status_code in allowed:
        await response.aread()
        return

    await response.aread()

    payload: object = None
    try:
        payload = response.json()
    except (json.JSONDecodeError, UnicodeDecodeError):
        # An error response is the least reliable thing to assume well-formed;
        # from_response falls back to the status line.
        payload = None

    raise NvisyApiError.from_response(
        response.status_code,
        response.reason_phrase,
        payload,
        response.headers.get(REQUEST_ID_HEADER),
    )


async def _log_request(request: httpx.Request) -> None:
    """Log an outgoing request and note when it started.

    Args:
        request: The request about to be sent.
    """
    request.extensions[START_TIME] = time.perf_counter()
    logger.debug("%s %s", request.method, request.url)


async def _log_response(response: httpx.Response) -> None:
    """Log a response and how long its request took.

    The duration is measured from the request hook rather than read from
    `response.elapsed`, which is only available once the response has been
    read or closed — and a hook runs before either.

    Args:
        response: The response received.
    """
    started = response.request.extensions.get(START_TIME)
    duration = (time.perf_counter() - started) * 1000 if started else 0.0
    logger.debug(
        "%s %s %s (%dms)",
        response.request.method,
        response.request.url.path,
        response.status_code,
        duration,
    )


def create_http_client(
    *,
    api_token: str,
    base_url: str = DEFAULT_BASE_URL,
    headers: Mapping[str, str] | None = None,
    user_agent: str | None = None,
    with_logging: bool = False,
    transport: httpx.AsyncBaseTransport | None = None,
) -> httpx.AsyncClient:
    """Build the HTTP client used for every request.

    Args:
        api_token: Token sent as a bearer credential.
        base_url: Base URL for the API.
        headers: Extra headers, merged over the defaults so a caller can
            override any of them.
        user_agent: Custom user agent; defaults to one naming the SDK.
        with_logging: Whether to log requests and responses at debug level.
        transport: Custom transport, chiefly for tests.

    Returns:
        A configured client.
    """
    # Content-Type is deliberately never set on the client, and a caller's is
    # dropped. httpx derives it from each body, which is the only way a
    # multipart upload gets its boundary; a client-level value outranks that
    # and would label every upload with a type its body does not have.
    default_headers = {
        "Accept": "application/json",
        "User-Agent": user_agent or default_user_agent(),
    }
    if headers:
        default_headers.update(
            {k: v for k, v in headers.items() if k.lower() != "content-type"}
        )

    # Applied last, so the token this client was built with is the one it
    # sends. A stale Authorization header carried over from another client
    # would otherwise silently outrank it.
    default_headers["Authorization"] = f"Bearer {api_token}"

    hooks: dict[str, list] = {"request": [], "response": [_raise_for_error]}
    if with_logging:
        hooks["request"].append(_log_request)
        # Logging runs before the error hook, so a failure is logged as well.
        hooks["response"].insert(0, _log_response)

    return httpx.AsyncClient(
        base_url=base_url,
        headers=default_headers,
        event_hooks=hooks,
        follow_redirects=True,
        transport=transport,
    )


def wrap_network_errors(error: httpx.HTTPError) -> NvisyError:
    """Convert a transport failure into an SDK error.

    Args:
        error: The underlying httpx error.

    Returns:
        The SDK error to raise in its place.
    """
    return NvisyError(str(error) or "An unknown network error occurred")


__all__ = [
    "REQUEST_ID_HEADER",
    "create_http_client",
    "wrap_network_errors",
]
