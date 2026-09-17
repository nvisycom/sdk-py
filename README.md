# Nvisy Python SDK

[![PyPI version](https://img.shields.io/pypi/v/nvisy-sdk?color=000000&style=flat-square)](https://pypi.org/project/nvisy-sdk/)
[![build](https://img.shields.io/github/actions/workflow/status/nvisy/sdk-py/build.yml?branch=main&color=000000&style=flat-square)](https://github.com/nvisy/sdk-py/actions/workflows/build.yml)
[![python](https://img.shields.io/badge/Python-3.8+-000000?style=flat-square&logo=python&logoColor=white)](https://python.org/)
[![ruff](https://img.shields.io/badge/Ruff-000000?style=flat-square&logo=ruff&logoColor=white)](https://docs.astral.sh/ruff/)

Official Python SDK for the Nvisy document redaction platform.

## Features

- Modern Python 3.8+ support with full type hints
- Async/await and synchronous interfaces
- Flexible configuration via a config object or builder pattern
- Built-in environment variable support
- Automatic retry logic with smart error handling
- Individual module exports for optimal usage

## Installation

```bash
pip install nvisy-sdk
```

## Usage

### Direct Configuration

Create a client by passing configuration options directly to the constructor:

```python
from nvisy import Client

client = Client({
    "api_key": "your-api-key",  # Required: 10+ chars, alphanumeric with _ and -
    "base_url": "https://api.nvisy.com",  # Optional: API endpoint (default shown)
    "timeout": 30.0,  # Optional: 1.0-300.0 seconds (default: 30.0)
    "max_retries": 3,  # Optional: 0-5 attempts (default: 3)
    "user_agent": "MyApp/1.0.0",  # Optional: custom user agent
    "headers": {  # Optional: custom headers
        "X-Custom-Header": "value",
    },
})
```

### Builder Pattern

Use the fluent builder API for more readable configuration:

```python
from nvisy import Client

client = Client.builder() \
    .with_api_key("your-api-key") \
    .with_base_url("https://api.nvisy.com") \
    .with_timeout(60.0) \
    .with_max_retries(5) \
    .with_user_agent("MyApp/1.0.0") \
    .with_header("X-Custom-Header", "value") \
    .with_headers({"X-Another": "header"}) \
    .build()
```

### From Environment Variables

Load configuration from environment variables:

```python
from nvisy import Client, ClientBuilder

# Using builder pattern from environment (allows additional configuration)
client = ClientBuilder.from_environment() \
    .with_timeout(60.0) \
    .build()

# Or using Client directly
client = Client.from_environment()
```

Set these environment variables:

| Variable            | Description                      | Required |
| ------------------- | -------------------------------- | -------- |
| `NVISY_API_TOKEN`   | API key for authentication       | Yes      |
| `NVISY_BASE_URL`    | Custom API endpoint URL          | No       |
| `NVISY_MAX_TIMEOUT` | Request timeout in milliseconds  | No       |
| `NVISY_MAX_RETRIES` | Maximum number of retry attempts | No       |
| `NVISY_USER_AGENT`  | Custom user agent string         | No       |

### Async Usage

```python
import asyncio
from nvisy import Client

async def main():
    async with Client.from_environment() as client:
        # Get API status
        status = await client.get("status")
        print(f"API Status: {status}")
        
        # Create a document
        document = await client.post("documents", json={
            "name": "Example Document",
            "description": "Created via SDK"
        })
        print(f"Created document: {document}")

asyncio.run(main())
```

### Synchronous Usage

```python
from nvisy import Client

with Client.from_environment() as client:
    # Get API status
    status = client.get_sync("status")
    print(f"API Status: {status}")
    
    # List documents
    documents = client.get_sync("documents")
    print(f"Found {len(documents.get('data', []))} documents")
```

### Error Handling

```python
from nvisy import (
    Client,
    NvisyError,
    NvisyAPIError,
    NvisyAuthenticationError,
    NvisyRateLimitError,
    NvisyValidationError,
)

try:
    client = Client.from_environment()
    result = await client.get("documents/some-id")
except NvisyAuthenticationError:
    print("Invalid API credentials")
except NvisyRateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
except NvisyValidationError as e:
    print(f"Validation failed: {e.validation_errors}")
except NvisyAPIError as e:
    print(f"API error {e.status_code}: {e.message}")
    if e.request_id:
        print(f"Request ID: {e.request_id}")
except NvisyError as e:
    print(f"SDK error: {e}")
```

## Development

### Requirements

- Python 3.8 or higher
- uv (recommended) or pip
- ruff for linting and formatting

### Development Setup

```bash
git clone https://github.com/nvisy/sdk-py.git
cd sdk-py
make setup
```

### Scripts

- `make build` - Build the package for distribution
- `make dev` - Run development checks (format + lint + test)
- `make test` - Run test suite
- `make test-cov` - Run tests with coverage report
- `make test-watch` - Run tests in watch mode
- `make lint` - Check code style and quality
- `make format` - Format code with ruff
- `make check` - Run all linting, formatting, and type checks
- `make type-check` - Verify type hints with mypy
- `make clean` - Remove build artifacts

### Quality Checks

Before submitting changes:

```bash
make check    # Lint, format, and type check
make test     # Run test suite
make build    # Verify build works
```

## API Services

The SDK provides access to the following services:

- **Documents** - Document upload, management, and processing
- **Members** - Team member invitation and management
- **Integrations** - Third-party service integrations
- **Status** - API health and status monitoring

_Note: Service implementations are coming soon. Currently, use the base HTTP
methods (`get`, `post`, etc.) to interact with API endpoints._

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for release notes and version history.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## License

MIT License - see [LICENSE.txt](LICENSE.txt) for details.

## Support

- Documentation: [docs.nvisy.com](https://docs.nvisy.com)
- Issues: [GitHub Issues](https://github.com/nvisy/sdk-py/issues)
- Email: [support@nvisy.com](mailto:support@nvisy.com)
