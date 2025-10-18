# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changed

### Fixed

### Removed

## [0.1.0] - 2024-12-19

### Added

- Initial release of the Nvisy Python SDK
- `Client` class for interacting with the Nvisy document redaction API
- `ClientBuilder` class for fluent configuration building with method chaining
- `ClientConfiguration` class for configuration management and validation
- Comprehensive error handling with `NvisyError` hierarchy and specialized exceptions
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

[Unreleased]: https://github.com/nvisy/sdk-py/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/nvisy/sdk-py/releases/tag/v0.1.0