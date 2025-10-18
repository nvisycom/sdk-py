"""Exception classes for the Nvisy SDK."""

from typing import Any, Dict, Optional, Union


class NvisyError(Exception):
    """Base exception class for all Nvisy SDK errors."""

    def __init__(
        self,
        message: str,
        *,
        details: Optional[Dict[str, Any]] = None,
        error_code: Optional[str] = None,
    ) -> None:
        """Initialize the exception.

        Args:
            message: Human-readable error message
            details: Additional error details
            error_code: Specific error code if available
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.error_code = error_code

    def __str__(self) -> str:
        """Return a string representation of the error."""
        parts = [self.message]
        if self.error_code:
            parts.append(f"Error Code: {self.error_code}")
        if self.details:
            parts.append(f"Details: {self.details}")
        return " | ".join(parts)

    def __repr__(self) -> str:
        """Return a detailed representation of the error."""
        return (
            f"{self.__class__.__name__}("
            f"message={self.message!r}, "
            f"error_code={self.error_code!r}, "
            f"details={self.details!r})"
        )


class NvisyAPIError(NvisyError):
    """Exception raised for API-related errors."""

    def __init__(
        self,
        message: str,
        *,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the API exception.

        Args:
            message: Human-readable error message
            status_code: HTTP status code
            response_data: Raw response data from the API
            request_id: Request ID for tracking
            **kwargs: Additional arguments passed to parent
        """
        super().__init__(message, **kwargs)
        self.status_code = status_code
        self.response_data = response_data or {}
        self.request_id = request_id

    def __str__(self) -> str:
        """Return a string representation of the API error."""
        parts = [self.message]
        if self.status_code:
            parts.append(f"Status: {self.status_code}")
        if self.request_id:
            parts.append(f"Request ID: {self.request_id}")
        if self.error_code:
            parts.append(f"Error Code: {self.error_code}")
        return " | ".join(parts)


class NvisyAuthenticationError(NvisyAPIError):
    """Exception raised for authentication failures."""

    def __init__(self, message: str = "Authentication failed", **kwargs: Any) -> None:
        super().__init__(message, status_code=401, **kwargs)


class NvisyAuthorizationError(NvisyAPIError):
    """Exception raised for authorization failures."""

    def __init__(self, message: str = "Authorization failed", **kwargs: Any) -> None:
        super().__init__(message, status_code=403, **kwargs)


class NvisyNotFoundError(NvisyAPIError):
    """Exception raised when a resource is not found."""

    def __init__(self, message: str = "Resource not found", **kwargs: Any) -> None:
        super().__init__(message, status_code=404, **kwargs)


class NvisyValidationError(NvisyAPIError):
    """Exception raised for validation errors."""

    def __init__(
        self,
        message: str = "Validation failed",
        *,
        validation_errors: Optional[list[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, status_code=422, **kwargs)
        self.validation_errors = validation_errors or []

    def __str__(self) -> str:
        """Return a string representation including validation errors."""
        base_str = super().__str__()
        if self.validation_errors:
            errors_str = ", ".join(
                f"{err.get('field', 'unknown')}: {err.get('message', 'invalid')}"
                for err in self.validation_errors
            )
            return f"{base_str} | Validation Errors: {errors_str}"
        return base_str


class NvisyRateLimitError(NvisyAPIError):
    """Exception raised when rate limits are exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        *,
        retry_after: Optional[Union[int, float]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, status_code=429, **kwargs)
        self.retry_after = retry_after

    def __str__(self) -> str:
        """Return a string representation including retry information."""
        base_str = super().__str__()
        if self.retry_after:
            return f"{base_str} | Retry After: {self.retry_after}s"
        return base_str


class NvisyServerError(NvisyAPIError):
    """Exception raised for server-side errors."""

    def __init__(self, message: str = "Internal server error", **kwargs: Any) -> None:
        super().__init__(message, status_code=500, **kwargs)


class NvisyTimeoutError(NvisyError):
    """Exception raised when requests timeout."""

    def __init__(
        self,
        message: str = "Request timed out",
        *,
        timeout_duration: Optional[Union[int, float]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.timeout_duration = timeout_duration

    def __str__(self) -> str:
        """Return a string representation including timeout duration."""
        base_str = super().__str__()
        if self.timeout_duration:
            return f"{base_str} | Timeout: {self.timeout_duration}s"
        return base_str


class NvisyConnectionError(NvisyError):
    """Exception raised for connection-related errors."""

    pass


class NvisyConfigurationError(NvisyError):
    """Exception raised for configuration-related errors."""

    pass


class NvisyParsingError(NvisyError):
    """Exception raised when response parsing fails."""

    def __init__(
        self,
        message: str = "Failed to parse response",
        *,
        raw_response: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.raw_response = raw_response


# Convenience function to create API errors from HTTP responses
def create_api_error_from_response(  # noqa: PLR0911
    response_status: int,
    response_data: Dict[str, Any],
    request_id: Optional[str] = None,
) -> NvisyError:
    """Create an appropriate API exception from an HTTP response.

    Args:
        response_status: HTTP status code
        response_data: Response data from the API
        request_id: Request ID for tracking

    Returns:
        Appropriate NvisyAPIError subclass instance
    """
    message = response_data.get("message", "API request failed")
    error_code = response_data.get("error_code")
    details = response_data.get("details")

    # Create the appropriate exception based on status code
    if response_status == 401:
        return NvisyAuthenticationError(
            message,
            response_data=response_data,
            request_id=request_id,
            error_code=error_code,
            details=details,
        )
    elif response_status == 403:
        return NvisyAuthorizationError(
            message,
            response_data=response_data,
            request_id=request_id,
            error_code=error_code,
            details=details,
        )
    elif response_status == 404:
        return NvisyNotFoundError(
            message,
            response_data=response_data,
            request_id=request_id,
            error_code=error_code,
            details=details,
        )
    elif response_status == 422:
        validation_errors = response_data.get("errors", [])
        return NvisyValidationError(
            message,
            validation_errors=validation_errors,
            response_data=response_data,
            request_id=request_id,
            error_code=error_code,
            details=details,
        )
    elif response_status == 429:
        retry_after = response_data.get("retry_after")
        return NvisyRateLimitError(
            message,
            retry_after=retry_after,
            response_data=response_data,
            request_id=request_id,
            error_code=error_code,
            details=details,
        )
    elif response_status >= 500:
        return NvisyServerError(
            message,
            status_code=response_status,
            response_data=response_data,
            request_id=request_id,
            error_code=error_code,
            details=details,
        )
    else:
        return NvisyAPIError(
            message,
            status_code=response_status,
            response_data=response_data,
            request_id=request_id,
            error_code=error_code,
            details=details,
        )


__all__ = [
    "NvisyError",
    "NvisyAPIError",
    "NvisyAuthenticationError",
    "NvisyAuthorizationError",
    "NvisyNotFoundError",
    "NvisyValidationError",
    "NvisyRateLimitError",
    "NvisyServerError",
    "NvisyTimeoutError",
    "NvisyConnectionError",
    "NvisyConfigurationError",
    "NvisyParsingError",
    "create_api_error_from_response",
]
