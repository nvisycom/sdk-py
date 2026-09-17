# nvisy-sdk

[![PyPI](https://img.shields.io/pypi/v/nvisy-sdk?style=flat-square)](https://pypi.org/project/nvisy-sdk/)
[![Build](https://img.shields.io/github/actions/workflow/status/nvisycom/sdk-py/build.yml?branch=main&label=build%20%26%20test&style=flat-square)](https://github.com/nvisycom/sdk-py/actions/workflows/build.yml)

Python client for the [Nvisy](https://nvisy.com/) multimodal redaction platform.

Nvisy detects and removes sensitive information across documents, images, and audio.
It combines deterministic patterns, NER, computer vision, and LLM-driven classification
into auditable, policy-driven pipelines built for regulated industries such as
healthcare, legal, government, and financial services.

## Installation

```bash
pip install nvisy-sdk
```

## Quick Start

```python
from nvisy import Nvisy


async def main() -> None:
    async with Nvisy(api_token="your-api-token") as client:
        account = await client.account.get_account()
        workspaces = await client.workspaces.list_workspaces()
```

The client accepts additional options:

```python
client = Nvisy(
    api_token="your-api-token",  # Required
    base_url="https://api.nvisy.com",  # Optional
    user_agent="MyApp/1.0.0",  # Optional
    with_logging=True,  # Optional
    headers={  # Optional
        "X-Custom-Header": "value",
    },
    transport=custom_transport,  # Optional, defaults to the httpx transport
)
```

Configuration can also come from the environment, through
`Nvisy.from_environment()`, which reads `NVISY_API_TOKEN`, `NVISY_BASE_URL`,
and `NVISY_USER_AGENT`.

## Features

- Python 3.11+, asynchronous throughout
- Fully typed, with Pydantic models generated from the API specification
- Cursor pagination that yields either a page or every item
- Debug logging for development

## Deployment

The fastest way to get started is with [Nvisy Cloud](https://nvisy.com).

To run locally, see the [nvisycom/server](https://github.com/nvisycom/server) (self-hosted backend) and [nvisycom/studio](https://github.com/nvisycom/studio) (web and desktop app) repositories.

If you only need redaction and not the full platform, [nvisycom/elide](https://github.com/nvisycom/elide) is a standalone framework for building PII detection and removal pipelines over multimodal documents.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and contribution guidelines.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for release notes and version history.

## License

MIT License, see [LICENSE](LICENSE)

## Support

- **Documentation**: [docs.nvisy.com](https://docs.nvisy.com)
- **Issues**: [github.com/nvisycom/sdk-py/issues](https://github.com/nvisycom/sdk-py/issues)
- **Email**: [support@nvisy.com](mailto:support@nvisy.com)
