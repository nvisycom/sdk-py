# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-09-17

A rewrite. The SDK is now a typed, asynchronous client covering the whole API,
shaped like the TypeScript SDK so the two read alike.

### Added

- `Nvisy`, an async client authenticating with an API token.
- 21 service namespaces covering 127 methods across the API's 91 endpoints:
  `account`, `activities`, `analytics`, `api_tokens`, `auth`, `capabilities`,
  `connections`, `detections`, `documents`, `invites`, `members`,
  `notifications`, `pipelines`, `policies`, `providers`, `redactions`,
  `reviews`, `status`, `syncs`, `webhooks`, and `workspaces`.
- `nvisy.datatypes`, 586 Pydantic models generated from the OpenAPI
  specification. Fields are snake_case in Python and camelCase on the wire.
- `AsyncPaginator`, returned by every list method. Await it for one page,
  iterate it for every item, or call `pages()` to walk whole pages. Nothing is
  requested until awaited or iterated.
- `Nvisy.from_environment()` and `Nvisy.with_api_token()`.
- `make generate` / `make generate-local`, which regenerate the datatypes from
  the API's specification.

### Changed

- **Breaking:** `Client` is now `Nvisy`, and `api_key` is now `api_token`.
- **Breaking:** the client is asynchronous only. Every sync method is gone,
  including `request_sync`, the `*_sync` helpers, and `__enter__`/`__exit__`.
  Existing `with Client(...)` code fails at runtime, not at import.
- **Breaking:** `ClientError`, `ConfigError` and `NetworkError` collapse into
  `NvisyError`; `ApiError` becomes `NvisyApiError`. The API's error type is
  exposed as `error_name`, leaving `__class__.__name__` intact.
- **Breaking:** `ClientConfiguration` is gone. Configuration is validated by
  plain functions, so an invalid token raises `NvisyError` rather than a
  Pydantic `ValidationError`.
- Errors are raised from a single response hook rather than checked per call.
  A malformed error body — HTML from a proxy, an empty 401 — falls back to the
  status line instead of failing while reporting a failure.
- Transport failures are raised as `NvisyError` with the underlying `httpx`
  error chained as `__cause__`.
- Requires Python 3.11 or newer, up from 3.8.

### Fixed

- The API token pattern now allows `.`, which the API's own desktop tokens
  contain and the previous pattern wrongly rejected.
- `/health` and `/health/ready` answer 503 with a health report; that report is
  now returned rather than raised, since it is the very thing being asked for.

### Removed

- **Breaking:** `ClientBuilder` and `Client.builder()`. Keyword arguments
  already read the way the builder was meant to.
- **Breaking:** retries and timeouts, matching the TypeScript SDK. The SDK
  never retries on its own; `NvisyApiError.is_retryable()` reports when doing
  so is worthwhile, leaving the policy to the caller. The `NVISY_MAX_TIMEOUT`
  and `NVISY_MAX_RETRIES` environment variables are no longer read.
- **Breaking:** the generic `get`/`post`/`put`/`patch`/`delete` helpers. Use a
  service method, or `nvisy.http` for anything they do not cover.
- The `DEBUG` environment variable, replaced by the `with_logging` argument.

## [0.1.0] - 2024-12-19

### Added

- Initial release of the Nvisy Python SDK
- `Client` class for interacting with the Nvisy document redaction API
- `ClientBuilder` class for fluent configuration building with method chaining
- `ClientConfiguration` class for configuration management and validation
- Comprehensive error handling with `NvisyError` hierarchy and specialized
  exceptions
- Configuration management with environment variable support
- Full type hints and mypy compatibility for type safety
- Both async and sync HTTP request methods
- Automatic retry logic with exponential backoff for failed requests
- Context manager support for proper resource cleanup
- Custom header support with validation
- User agent customization and automatic generation
- Request timeout configuration with validation (1-300 seconds)
- Retry attempt configuration (0-5 attempts)
- Base URL validation for HTTP/HTTPS endpoints
- API key validation (minimum 10 characters, alphanumeric with _ and -)

### Features

- Fluent API for client configuration using builder pattern
- Built-in validation for all configuration options
- Comprehensive test coverage with over 70 test cases
- Modern Python 3.8+ support with async/await
- Environment variable configuration support
- HTTP client built on httpx for reliable networking
- Pydantic models for configuration validation

### Configuration

- Support for `NVISY_API_TOKEN` environment variable for API authentication
- Support for `NVISY_BASE_URL` for custom API endpoints
- Support for `NVISY_MAX_TIMEOUT` for request timeout in milliseconds
- Support for `NVISY_MAX_RETRIES` for maximum retry attempts
- Support for `NVISY_USER_AGENT` for custom user agent strings
- Support for `DEBUG` flag for development debugging

### Error Handling

- Structured error responses with detailed error information
- HTTP status code classification with appropriate exception types
- Network error handling for timeouts, DNS resolution, and connection issues
- Configuration validation with detailed error messages
- Request ID tracking for API error correlation
- Retry-after support for rate limiting scenarios

### Development

- Complete development workflow with Makefile
- Code formatting with ruff
- Type checking with mypy
- Testing with pytest and async support
- Pre-commit hooks for code quality
- Comprehensive documentation and examples

[Unreleased]: https://github.com/nvisycom/sdk-py/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/nvisycom/sdk-py/releases/tag/v0.2.0
[0.1.0]: https://github.com/nvisycom/sdk-py/releases/tag/v0.1.0
