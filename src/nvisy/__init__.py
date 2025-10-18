"""Nvisy Python SDK.

A Python SDK for interacting with the Nvisy API.
"""

__version__ = "0.1.0"

# Import main client and configuration classes
from .builder import ClientBuilder
from .client import Client
from .config import ClientConfiguration

# Import exceptions
from .exceptions import (
    NvisyAPIError,
    NvisyAuthenticationError,
    NvisyAuthorizationError,
    NvisyConfigurationError,
    NvisyConnectionError,
    NvisyError,
    NvisyNotFoundError,
    NvisyParsingError,
    NvisyRateLimitError,
    NvisyServerError,
    NvisyTimeoutError,
    NvisyValidationError,
)

__all__ = [
    "__version__",
    # Core classes
    "Client",
    "ClientBuilder",
    "ClientConfiguration",
    # Exceptions
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
]
