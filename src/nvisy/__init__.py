"""Nvisy Python SDK.

An async client for the Nvisy document processing API:

    ```python
    import asyncio
    from nvisy import Nvisy


    async def main() -> None:
        async with Nvisy(api_token="your-api-token") as nvisy:
            async for workspace in nvisy.workspaces.list_workspaces():
                print(workspace.display_name)


    asyncio.run(main())
    ```
"""

__version__ = "0.2.0"

from .client import Nvisy
from .config import DEFAULT_BASE_URL, default_user_agent
from .errors import NvisyApiError, NvisyError
from .pagination import AsyncPaginator

__all__ = [
    "DEFAULT_BASE_URL",
    "AsyncPaginator",
    "Nvisy",
    "NvisyApiError",
    "NvisyError",
    "__version__",
    "default_user_agent",
]
