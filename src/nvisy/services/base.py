"""Shared base for the service classes."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar, cast

import httpx
from pydantic import BaseModel

from ..http import ALLOWED_STATUSES, wrap_network_errors
from ..pagination import AsyncPaginator, Page

if TYPE_CHECKING:
    from collections.abc import Collection, Mapping

PageT = TypeVar("PageT", bound=Page[Any])
ModelT = TypeVar("ModelT", bound=BaseModel)


class Service:
    """Base class holding the HTTP client a service issues requests through."""

    def __init__(self, http: httpx.AsyncClient) -> None:
        """Initialize the service.

        Args:
            http: The client to issue requests through.
        """
        self._http = http

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        json: Any = None,
        files: Any = None,
        allow_statuses: Collection[int] | None = None,
    ) -> httpx.Response:
        """Issue a request, letting the response hook raise on failure.

        Args:
            method: HTTP method.
            path: Request path, relative to the base URL.
            params: Query parameters; keys with a `None` value are dropped.
            json: JSON body to send.
            files: Multipart payload to send.
            allow_statuses: Error statuses whose body should be returned
                rather than raised. The health endpoints pass `{503}`, since
                they describe an unhealthy server in the body of one; every
                other status still raises.

        Returns:
            The response.
        """
        request: dict[str, Any] = {}
        if allow_statuses:
            request["extensions"] = {ALLOWED_STATUSES: frozenset(allow_statuses)}
        if params is not None:
            request["params"] = _clean_params(params)
        if json is not None:
            request["json"] = json
        if files is not None:
            request["files"] = files

        try:
            return await self._http.request(method, path, **request)
        except httpx.HTTPError as error:
            # A transport failure never reaches the response hook, so it is
            # wrapped here instead.
            raise wrap_network_errors(error) from error

    def _paginate(
        self,
        model: type[ModelT],
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
    ) -> AsyncPaginator[PageT, Any]:
        """Build a paginator over a cursor-paginated endpoint.

        Args:
            model: The page model the endpoint returns.
            path: Request path, relative to the base URL.
            params: Query parameters, sent alongside the cursor.

        Returns:
            A paginator that can be awaited for one page or iterated for all.
        """
        base = dict(params or {})

        async def fetch(cursor: str | None) -> PageT:
            query = dict(base)
            if cursor is not None:
                query["after"] = cursor
            response = await self._request("GET", path, params=query)
            # Every generated `*Page` model satisfies the Page protocol, which
            # the BaseModel bound cannot express on its own.
            return cast("PageT", model.model_validate(response.json()))

        return AsyncPaginator(fetch)


def serialize(body: Any) -> Any:
    """Render a request body for the wire.

    The generated models are snake_case with camelCase aliases, so a body must
    be dumped by alias or the API will not recognize its fields.

    Args:
        body: A model, or a value already shaped for the wire.

    Returns:
        The value to send as JSON.
    """
    if isinstance(body, BaseModel):
        return body.model_dump(mode="json", by_alias=True, exclude_none=True)

    return body


def _clean_params(params: Mapping[str, Any]) -> dict[str, Any]:
    """Drop unset query parameters and render the rest for the wire.

    Args:
        params: Raw query parameters.

    Returns:
        Parameters with `None` values removed and booleans lowercased.
    """
    cleaned: dict[str, Any] = {}
    for key, value in params.items():
        if value is None:
            continue
        cleaned[key] = "true" if value is True else "false" if value is False else value

    return cleaned


__all__ = ["Service", "serialize"]
