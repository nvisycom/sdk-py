# Nvisy Python SDK

[![PyPI version](https://img.shields.io/pypi/v/nvisy-sdk?color=000000&style=flat-square)](https://pypi.org/project/nvisy-sdk/)
[![build](https://img.shields.io/github/actions/workflow/status/nvisycom/sdk-py/build.yml?branch=main&color=000000&style=flat-square)](https://github.com/nvisycom/sdk-py/actions/workflows/build.yml)
[![python](https://img.shields.io/badge/Python-3.11+-000000?style=flat-square&logo=python&logoColor=white)](https://python.org/)
[![ruff](https://img.shields.io/badge/Ruff-000000?style=flat-square&logo=ruff&logoColor=white)](https://docs.astral.sh/ruff/)

Official Python SDK for the Nvisy document processing platform.

Nvisy combines deterministic patterns, named-entity recognition, computer
vision, and LLM classification into auditable, policy-driven redaction
pipelines.

## Installation

```bash
pip install nvisy-sdk
```

Requires Python 3.11 or newer.

## Quick start

```python
import asyncio

from nvisy import Nvisy


async def main() -> None:
    async with Nvisy(api_token="your-api-token") as nvisy:
        async for workspace in nvisy.workspaces.list_workspaces():
            print(workspace.display_name)


asyncio.run(main())
```

The client is asynchronous, so it runs inside an event loop. Using it as a
context manager closes its connections when you are done.

## Configuration

```python
nvisy = Nvisy(
    api_token="your-api-token",
    base_url="https://api.nvisy.com",
    headers={"X-Custom-Header": "value"},
    user_agent="MyApp/1.0.0",
    with_logging=False,
)
```

Only `api_token` is required. Custom headers are merged over the defaults, so
any of them can be overridden.

To read the configuration from the environment instead:

```python
nvisy = Nvisy.from_environment()
```

| Variable           | Description                | Required |
| ------------------ | -------------------------- | -------- |
| `NVISY_API_TOKEN`  | API token for the account  | Yes      |
| `NVISY_BASE_URL`   | Custom API endpoint        | No       |
| `NVISY_USER_AGENT` | Custom user agent string   | No       |

Arguments passed to `from_environment` take precedence over the environment.

## Services

Resources hang off the client as namespaces:

```python
account = await nvisy.account.get_account()
workspace = await nvisy.workspaces.get_workspace(workspace_id)
document = await nvisy.documents.get_document(workspace_id, document_id)
```

| Namespace                                                         | Covers                                            |
| ----------------------------------------------------------------- | ------------------------------------------------- |
| `account`, `auth`, `api_tokens`, `notifications`                  | The signed-in account and its credentials         |
| `workspaces`, `members`, `invites`, `activities`, `analytics`     | Workspaces and who belongs to them                |
| `documents`, `pipelines`, `policies`, `detections`, `redactions`  | Processing documents and what was found in them   |
| `reviews`                                                         | Human review of detections                        |
| `connections`, `syncs`, `providers`, `webhooks`                   | External systems                                  |
| `capabilities`, `status`                                          | What the deployment supports, and whether it is up |

## Pagination

List methods return a paginator. Await it for a single page, or iterate it to
walk every item, fetching pages as they are needed:

```python
# One page.
page = await nvisy.workspaces.list_workspaces(limit=50)
print(page.items, page.total)

# Every item, across pages.
async for workspace in nvisy.workspaces.list_workspaces():
    print(workspace.display_name)

# Whole pages, when the per-page total matters.
async for page in nvisy.workspaces.list_workspaces().pages():
    print(len(page.items))
```

Nothing is requested until you await or iterate, and abandoning the iteration
fetches no further pages. Pass `include_count=True` to populate `page.total`,
which costs an extra query.

## Error handling

```python
from nvisy import Nvisy, NvisyApiError, NvisyError

try:
    workspace = await nvisy.workspaces.get_workspace(workspace_id)
except NvisyApiError as error:
    # The API answered with a 4xx or 5xx.
    print(error.status_code, error.error_name, error.message)
    if error.is_retryable():
        ...
except NvisyError as error:
    # A configuration problem or a network failure.
    print(error)
```

`NvisyApiError` carries the HTTP `status_code`, the API's own `error_name`
(such as `"NotFoundError"`), the `message`, and a `request_id` when the
response included one. It classifies itself through `is_client_error()`,
`is_server_error()`, and `is_retryable()`.

The SDK does not retry on its own; `is_retryable()` reports when doing so is
worthwhile, leaving the policy to you.

## Typed models

Requests and responses are Pydantic models generated from the API's OpenAPI
specification. Fields are snake_case in Python and serialized to the API's
camelCase on the wire:

```python
from nvisy.datatypes import CreateWorkspace

workspace = await nvisy.workspaces.create_workspace(
    CreateWorkspace(handle="research", displayName="Research")
)
print(workspace.display_name)
```

## Development

```bash
git clone https://github.com/nvisycom/sdk-py.git
cd sdk-py
make setup
```

| Command             | Does                                            |
| ------------------- | ----------------------------------------------- |
| `make check`        | Format, lint, and type check                    |
| `make test`         | Run the test suite                              |
| `make test-cov`     | Run the tests with a coverage report            |
| `make build`        | Build the package                               |
| `make generate`     | Regenerate the datatypes from the OpenAPI spec  |
| `make clean`        | Remove build artifacts                          |

Run `make check && make test` before submitting a change.

The models in `src/nvisy/datatypes.py` are generated; the service classes that
use them are written by hand, because the specification declares no
`operationId`s to derive method names from.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for release notes and version history.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## License

MIT License - see [LICENSE.txt](LICENSE.txt) for details.

## Support

- Documentation: [docs.nvisy.com](https://docs.nvisy.com)
- Issues: [GitHub Issues](https://github.com/nvisycom/sdk-py/issues)
- Email: [support@nvisy.com](mailto:support@nvisy.com)
