"""Configuration for the Nvisy SDK."""

from __future__ import annotations

import os
import re
from urllib.parse import urlparse

from .errors import NvisyError

#: Default base URL for the Nvisy API.
DEFAULT_BASE_URL = "https://api.nvisy.com"

#: Environment variable holding the API token.
ENV_API_TOKEN = "NVISY_API_TOKEN"

#: Environment variable holding a custom base URL.
ENV_BASE_URL = "NVISY_BASE_URL"

#: Environment variable holding a custom user agent.
ENV_USER_AGENT = "NVISY_USER_AGENT"

_TOKEN_PATTERN = re.compile(r"^[a-zA-Z0-9_.-]+$")
_TOKEN_MIN_LENGTH = 10


def default_user_agent() -> str:
    """Build the user agent sent when the caller does not supply one.

    Returns:
        A user agent identifying the SDK and its version.
    """
    from . import __version__

    return f"nvisy-sdk-python/{__version__}"


def validate_api_token(api_token: str) -> str:
    """Validate an API token.

    Args:
        api_token: The token to validate.

    Returns:
        The token, stripped of surrounding whitespace.

    Raises:
        NvisyError: If the token is empty, too short, or malformed.
    """
    if not isinstance(api_token, str) or not api_token.strip():
        raise NvisyError("API token must be a non-empty string")

    token = api_token.strip()
    if len(token) < _TOKEN_MIN_LENGTH:
        raise NvisyError(f"API token must be at least {_TOKEN_MIN_LENGTH} characters")
    if not _TOKEN_PATTERN.match(token):
        raise NvisyError("API token contains invalid characters")

    return token


def validate_base_url(base_url: str) -> str:
    """Validate a base URL.

    Args:
        base_url: The URL to validate.

    Returns:
        The URL without a trailing slash.

    Raises:
        NvisyError: If the URL is not a valid HTTP or HTTPS URL.
    """
    parsed = urlparse(base_url)
    if not parsed.scheme or not parsed.netloc:
        raise NvisyError("Base URL must be a valid HTTP/HTTPS URL")
    if parsed.scheme not in ("http", "https"):
        raise NvisyError("Base URL must use HTTP or HTTPS protocol")

    return base_url.rstrip("/")


def api_token_from_environment() -> str:
    """Read the API token from the environment.

    Returns:
        The token held in `NVISY_API_TOKEN`.

    Raises:
        NvisyError: If the variable is unset or empty.
    """
    api_token = os.getenv(ENV_API_TOKEN)
    if not api_token:
        raise NvisyError(
            f"API token is required. Set the {ENV_API_TOKEN} environment variable."
        )

    return api_token


__all__ = [
    "DEFAULT_BASE_URL",
    "ENV_API_TOKEN",
    "ENV_BASE_URL",
    "ENV_USER_AGENT",
    "api_token_from_environment",
    "default_user_agent",
    "validate_api_token",
    "validate_base_url",
]
