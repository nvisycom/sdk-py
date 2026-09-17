"""Error classes for the Nvisy SDK."""

from typing import Any


class ErrorResponse:
    """Error response structure from server."""

    def __init__(self, name: str, message: str, context: str = "") -> None:
        """Initialize error response.

        Args:
            name: Error type/name
            message: Human-readable error message
            context: Additional error context
        """
        self.name = name
        self.message = message
        self.context = context

    def to_dict(self) -> dict[str, str]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "message": self.message,
            "context": self.context,
        }


class ClientError(Exception):
    """Base error class for all Nvisy SDK errors."""

    def __init__(self, message: str) -> None:
        """Initialize the error.

        Args:
            message: Human-readable error message
        """
        super().__init__(message)
        self.message = message

    def to_dict(self) -> dict[str, str]:
        """Convert error to dictionary representation."""
        return {
            "name": self.__class__.__name__,
            "message": self.message,
            "context": "",
        }

    def __str__(self) -> str:
        """Return string representation of the error."""
        return self.message

    def __repr__(self) -> str:
        """Return detailed representation of the error."""
        return f"{self.__class__.__name__}({self.message!r})"


class ConfigError(ClientError):
    """Configuration error - thrown when client configuration is invalid."""

    def __init__(
        self,
        message: str,
        *,
        field: str | None = None,
        reason: str | None = None,
    ) -> None:
        """Initialize configuration error.

        Args:
            message: Error message
            field: Field that caused the error (for validation errors)
            reason: Reason why the configuration is invalid
        """
        super().__init__(message)
        self.field = field
        self.reason = reason

    @classmethod
    def missing_api_key(cls) -> "ConfigError":
        """Create error for missing API key."""
        return cls(
            "API key is required",
            field="api_key",
            reason="API key must be provided in configuration",
        )

    @classmethod
    def invalid_field(cls, field: str, reason: str) -> "ConfigError":
        """Create error for invalid configuration field."""
        return cls(
            f"Invalid configuration for {field}: {reason}",
            field=field,
            reason=reason,
        )

    @classmethod
    def missing_field(cls, field: str) -> "ConfigError":
        """Create error for missing required field."""
        return cls(
            f"Missing required configuration field: {field}",
            field=field,
            reason="This field is required",
        )

    def to_dict(self) -> dict[str, str]:
        """Convert error to dictionary representation."""
        context = ""
        if self.field or self.reason:
            context = f"field: {self.field}, reason: {self.reason}"

        return {
            "name": self.__class__.__name__,
            "message": self.message,
            "context": context,
        }


class NetworkError(ClientError):
    """Network error - thrown when network requests fail."""

    def __init__(self, message: str, cause: Exception | None = None) -> None:
        """Initialize network error.

        Args:
            message: Error message
            cause: Original error that caused this network error
        """
        super().__init__(message)
        self.cause = cause

    @classmethod
    def connection(cls, message: str, cause: Exception | None = None) -> "NetworkError":
        """Create error for network/connection issues."""
        return cls(message, cause=cause)

    @classmethod
    def timeout(cls, timeout_ms: int) -> "NetworkError":
        """Create error for request timeout."""
        return cls(f"Request timed out after {timeout_ms}ms")

    @classmethod
    def aborted(cls) -> "NetworkError":
        """Create error for aborted request."""
        return cls("Request was aborted")

    @classmethod
    def dns_resolution(cls, hostname: str) -> "NetworkError":
        """Create error for DNS resolution failure."""
        return cls(f"Failed to resolve hostname: {hostname}")

    def to_dict(self) -> dict[str, str]:
        """Convert error to dictionary representation."""
        context = ""
        if self.cause:
            context = f"cause: {self.cause!s}"

        return {
            "name": self.__class__.__name__,
            "message": self.message,
            "context": context,
        }


class ApiError(ClientError):
    """API error - thrown when server responds with an error."""

    def __init__(
        self,
        message: str,
        status_code: int,
        *,
        error_response: ErrorResponse | None = None,
        request_id: str | None = None,
    ) -> None:
        """Initialize API error.

        Args:
            message: Error message
            status_code: HTTP status code
            error_response: Error response from server
            request_id: Request ID for debugging
        """
        super().__init__(message)
        self.status_code = status_code
        self.error_response = error_response
        self.request_id = request_id

    @classmethod
    def from_response(
        cls,
        status_code: int,
        status_text: str,
        error_data: dict[str, Any] | None = None,
        request_id: str | None = None,
    ) -> "ApiError":
        """Create error from HTTP response.

        Args:
            status_code: HTTP status code
            status_text: HTTP status text
            error_data: Error data from response
            request_id: Request ID for tracking
        """
        message = (
            error_data.get("message", f"HTTP {status_code}: {status_text}")
            if error_data
            else f"HTTP {status_code}: {status_text}"
        )

        error_response = None
        if error_data:
            error_response = ErrorResponse(
                name=error_data.get("name", "ApiError"),
                message=message,
                context=error_data.get("context", ""),
            )

        return cls(
            message,
            status_code,
            error_response=error_response,
            request_id=request_id,
        )

    @classmethod
    def rate_limited(
        cls,
        retry_after: int | None = None,
        request_id: str | None = None,
    ) -> "ApiError":
        """Create error for rate limiting.

        Args:
            retry_after: Seconds to wait before retrying
            request_id: Request ID for tracking
        """
        message = (
            f"Rate limited. Retry after {retry_after} seconds"
            if retry_after
            else "Rate limited"
        )

        error_response = ErrorResponse(
            name="RateLimitError",
            message=message,
            context=f"retryAfter: {retry_after}" if retry_after else "",
        )

        return cls(message, 429, error_response=error_response, request_id=request_id)

    def is_client_error(self) -> bool:
        """Check if error is a client error (4xx)."""
        return 400 <= self.status_code < 500

    def is_server_error(self) -> bool:
        """Check if error is a server error (5xx)."""
        return self.status_code >= 500

    def is_retryable(self) -> bool:
        """Check if error is retryable based on HTTP status."""
        return (
            self.status_code >= 500  # Server errors
            or self.status_code == 408  # Request timeout
            or self.status_code == 429  # Rate limited
        )

    def get_retry_delay(self) -> float | None:
        """Get retry delay in seconds (returns None if not retryable)."""
        if not self.is_retryable():
            return None

        # For rate limiting, check if we have retry-after info
        if (
            self.status_code == 429
            and self.error_response
            and self.error_response.context
        ):
            import re

            match = re.search(r"retryAfter: (\d+)", self.error_response.context)
            if match:
                return float(match.group(1))

        # Default delays based on error type
        if self.status_code >= 500:
            return 1.0  # 1 second for server errors

        return 1.0  # Default 1 second

    def to_dict(self) -> dict[str, str]:
        """Convert error to dictionary representation."""
        context_parts = [f"statusCode: {self.status_code}"]

        if self.request_id:
            context_parts.append(f"requestId: {self.request_id}")

        if self.error_response:
            import json

            context_parts.append(
                f"errorResponse: {json.dumps(self.error_response.to_dict())}"
            )

        return {
            "name": self.__class__.__name__,
            "message": self.message,
            "context": ", ".join(context_parts),
        }

    def __str__(self) -> str:
        """Return string representation of the error."""
        parts = [self.message, f"Status: {self.status_code}"]
        if self.request_id:
            parts.append(f"Request ID: {self.request_id}")
        return " | ".join(parts)


__all__ = [
    "ClientError",
    "ConfigError",
    "NetworkError",
    "ApiError",
    "ErrorResponse",
]
