"""Tests for cursor pagination."""

import pytest
from pydantic import BaseModel

from nvisy.pagination import AsyncPaginator


class Item(BaseModel):
    """An item in a stub page."""

    slug: str


class StubPage(BaseModel):
    """A stub of the `*Page` shape every paginated endpoint returns."""

    items: list[Item]
    next_cursor: str | None = None
    total: int | None = None


def make_fetch(pages, calls):
    """Build a fetch coroutine serving `pages`, recording cursors in `calls`.

    Args:
        pages: Mapping of cursor to raw page payload.
        calls: List that each requested cursor is appended to.

    Returns:
        A coroutine function taking a cursor and returning a StubPage.
    """

    async def fetch(cursor):
        calls.append(cursor)
        return StubPage.model_validate(pages[cursor])

    return fetch


@pytest.fixture
def calls():
    """Record of the cursors requested."""
    return []


@pytest.fixture
def fetch(calls):
    """A fetch over three pages holding five items."""
    return make_fetch(
        {
            None: {
                "items": [{"slug": "w1"}, {"slug": "w2"}],
                "next_cursor": "c1",
                "total": 5,
            },
            "c1": {"items": [{"slug": "w3"}, {"slug": "w4"}], "next_cursor": "c2"},
            "c2": {"items": [{"slug": "w5"}]},
        },
        calls,
    )


class TestAwait:
    """Awaiting a paginator yields the first page."""

    async def test_returns_first_page(self, fetch):
        """Awaiting returns the page itself, not the items."""
        page = await AsyncPaginator(fetch)
        assert [item.slug for item in page.items] == ["w1", "w2"]

    async def test_exposes_total(self, fetch):
        """The page's total survives, since it is on the response."""
        page = await AsyncPaginator(fetch)
        assert page.total == 5

    async def test_fetches_one_page(self, fetch, calls):
        """Awaiting fetches only the first page."""
        await AsyncPaginator(fetch)
        assert calls == [None]


class TestIteration:
    """Iterating a paginator yields every item across pages."""

    async def test_yields_all_items(self, fetch):
        """Items from every page arrive in order."""
        items = [item.slug async for item in AsyncPaginator(fetch)]
        assert items == ["w1", "w2", "w3", "w4", "w5"]

    async def test_threads_cursors(self, fetch, calls):
        """Each request carries the previous page's cursor."""
        [item async for item in AsyncPaginator(fetch)]
        assert calls == [None, "c1", "c2"]

    async def test_stops_without_cursor(self, fetch, calls):
        """A page with no next cursor ends the iteration."""
        [item async for item in AsyncPaginator(fetch)]
        assert len(calls) == 3


class TestPages:
    """`pages()` walks whole pages rather than items."""

    async def test_yields_pages(self, fetch):
        """Each page arrives intact, with its own size."""
        sizes = [len(page.items) async for page in AsyncPaginator(fetch).pages()]
        assert sizes == [2, 2, 1]

    async def test_exposes_total(self, fetch):
        """The first page still carries its total."""
        pages = [page async for page in AsyncPaginator(fetch).pages()]
        assert pages[0].total == 5


class TestLaziness:
    """Nothing is requested until the caller asks for it."""

    async def test_construct_fetches_nothing(self, fetch, calls):
        """Building a paginator performs no request."""
        AsyncPaginator(fetch)
        assert calls == []

    async def test_break_stops_fetching(self, fetch, calls):
        """Abandoning iteration does not fetch the remaining pages."""
        async for _ in AsyncPaginator(fetch):
            break
        assert calls == [None]

    async def test_partial_iteration(self, fetch, calls):
        """Consuming into the second page fetches exactly two."""
        seen = []
        async for item in AsyncPaginator(fetch):
            seen.append(item.slug)
            if len(seen) == 3:
                break
        assert seen == ["w1", "w2", "w3"]
        assert calls == [None, "c1"]


class TestEdgeCases:
    """Degenerate pages behave sensibly."""

    async def test_single_page(self, calls):
        """A lone page without a cursor yields its items and stops."""
        fetch = make_fetch({None: {"items": [{"slug": "only"}]}}, calls)
        assert [item.slug async for item in AsyncPaginator(fetch)] == ["only"]
        assert calls == [None]

    async def test_empty_page(self, calls):
        """An empty page yields nothing."""
        fetch = make_fetch({None: {"items": []}}, calls)
        assert [item async for item in AsyncPaginator(fetch)] == []

    async def test_empty_cursor_stops(self, calls):
        """An empty-string cursor ends iteration rather than refetching."""
        fetch = make_fetch(
            {None: {"items": [{"slug": "a"}], "next_cursor": ""}},
            calls,
        )
        assert [item.slug async for item in AsyncPaginator(fetch)] == ["a"]
        assert calls == [None]

    async def test_reiterable(self, fetch):
        """A paginator can be iterated more than once."""
        paginator = AsyncPaginator(fetch)
        first = [item.slug async for item in paginator]
        second = [item.slug async for item in paginator]
        assert first == second
