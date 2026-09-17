"""Cursor pagination helpers for the Nvisy SDK.

The API paginates with an opaque cursor: a response carries the items of one
page and, when more exist, a `nextCursor` to pass as the next request's
`after`. Every paginated endpoint returns that same shape, so one helper
serves them all.

`AsyncPaginator` wraps that loop. It is returned by every `list_*` method, and
can be used three ways:

    # Iterate every item, fetching pages as needed.
    async for workspace in nvisy.workspaces.list_workspaces():
        print(workspace.display_name)

    # Or take a single page, when that is all you need.
    page = await nvisy.workspaces.list_workspaces()

    # Or walk whole pages, to see each response's `total`.
    async for page in nvisy.workspaces.list_workspaces().pages():
        print(len(page.items), page.total)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, Protocol, TypeVar

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Awaitable, Callable, Sequence

ItemT = TypeVar("ItemT")
ItemT_co = TypeVar("ItemT_co", covariant=True)


class Page(Protocol[ItemT_co]):
    """Structural type of a paginated response.

    Every `*Page` model generated from the specification matches this: the
    page's items, plus a cursor that is present only when more items exist.
    """

    @property
    def items(self) -> Sequence[ItemT_co]:
        """Items in this page."""

    @property
    def next_cursor(self) -> str | None:
        """Cursor for the next page, or `None` on the last page."""


PageT = TypeVar("PageT", bound=Page[Any])


class AsyncPaginator(Generic[PageT, ItemT]):
    """An awaitable, async-iterable view over a cursor-paginated endpoint.

    Awaiting yields the first page. Iterating yields every item across pages,
    fetching each page only as the previous one is exhausted. Nothing is
    requested until you await or iterate.
    """

    def __init__(
        self,
        fetch: Callable[[str | None], Awaitable[PageT]],
    ) -> None:
        """Initialize the paginator.

        Args:
            fetch: Coroutine taking a cursor (`None` for the first page) and
                returning one page.
        """
        self._fetch = fetch

    def __await__(self) -> Any:
        """Await the first page.

        Returns:
            Generator yielding the first page of results.
        """
        return self._fetch(None).__await__()

    async def __aiter__(self) -> AsyncIterator[ItemT]:
        """Iterate every item, fetching pages as they are needed.

        Yields:
            Each item, in order, across all pages.
        """
        async for page in self.pages():
            for item in page.items:
                yield item

    async def pages(self) -> AsyncIterator[PageT]:
        """Iterate whole pages rather than individual items.

        Use this when a response's `total` matters, or to control how much is
        held in memory at once.

        Yields:
            Each page, in order.
        """
        cursor: str | None = None
        while True:
            page = await self._fetch(cursor)
            yield page

            cursor = page.next_cursor
            if not cursor:
                return
