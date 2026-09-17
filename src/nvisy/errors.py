"""Error classes for the Nvisy SDK.

The hierarchy is deliberately flat:

- `NvisyError` — base class for every SDK error, and what a network failure or
  a misconfiguration is raised as.
- `NvisyApiError` — an error response from the API, carrying the HTTP status.

Catch `NvisyError` to handle anything the SDK raises; catch `NvisyApiError`
when the HTTP status or the API's error type matters.
"""

from __future__ import annotations


class NvisyError(Exception):
    """Base class for all Nvisy SDK errors.

    Raised directly for configuration problems and network failures — the
    cases where no HTTP response came back to describe what went wrong.
    """

    def __init__(self, message: str) -> None:
        """Initialize the error.

        Args:
            message: Human-readable error message.
        """
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        """Return the error message."""
        return self.message

    def __repr__(self) -> str:
        """Return a detailed representation of the error."""
        return f"{type(self).__name__}({self.message!r})"


class NvisyApiError(NvisyError):
    """An error response returned by the API.

    The API reports errors as a name identifying the kind of failure and a
    message safe to show an end user. Both are exposed here, alongside the
    HTTP status code.

    Note that `error_name` is the API's identifier (for example
    `"ValidationError"`), which is distinct from this class's own name.

    Example:
        ```python
        try:
            await nvisy.account.get_account()
        except NvisyApiError as error:
            print(error.status_code, error.error_name, error.message)
            if error.is_retryable():
                ...
        ```
    """

    def __init__(
        self,
        message: str,
        status_code: int,
        *,
        error_name: str,
        request_id: str | None = None,
    ) -> None:
        """Initialize the error.

        Args:
            message: Human-readable message from the API.
            status_code: HTTP status code of the response.
            error_name: The API's error type identifier.
            request_id: Correlation id, when the response carried one.
        """
        super().__init__(message)
        self.status_code = status_code
        self.error_name = error_name
        self.request_id = request_id

    @classmethod
    def from_response(
        cls,
        status_code: int,
        reason_phrase: str,
        payload: object = None,
        request_id: str | None = None,
    ) -> NvisyApiError:
        """Build an error from a response body.

        Falls back to the HTTP status line when the body is missing or is not
        the documented `{name, message}` shape — an error response is the
        least reliable thing to assume well-formed.

        Args:
            status_code: HTTP status code of the response.
            reason_phrase: HTTP reason phrase, used when the body says nothing.
            payload: Decoded response body, if it parsed as JSON.
            request_id: Correlation id, when the response carried one.

        Returns:
            The corresponding error.
        """
        fallback = f"HTTP {status_code}: {reason_phrase}".rstrip(": ")

        name = "ApiError"
        message = fallback
        if isinstance(payload, dict):
            raw_message = payload.get("message")
            if isinstance(raw_message, str) and raw_message:
                message = raw_message
            raw_name = payload.get("name")
            if isinstance(raw_name, str) and raw_name:
                name = raw_name

        return cls(
            message,
            status_code,
            error_name=name,
            request_id=request_id,
        )

    def is_client_error(self) -> bool:
        """Report whether the request itself was at fault.

        Returns:
            True for a 4xx status.
        """
        return 400 <= self.status_code < 500

    def is_server_error(self) -> bool:
        """Report whether the API failed to serve the request.

        Returns:
            True for a 5xx status.
        """
        return self.status_code >= 500

    def is_retryable(self) -> bool:
        """Report whether the request may succeed if sent again.

        The SDK never retries on its own; this only says when doing so is
        worthwhile.

        Returns:
            True for a server error, a request timeout, or rate limiting.
        """
        return self.is_server_error() or self.status_code in {408, 429}

    def __repr__(self) -> str:
        """Return a detailed representation of the error."""
        return (
            f"{type(self).__name__}({self.message!r}, "
            f"status_code={self.status_code}, error_name={self.error_name!r})"
        )


__all__ = ["NvisyApiError", "NvisyError"]
