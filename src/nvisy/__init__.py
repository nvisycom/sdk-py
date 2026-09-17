"""Nvisy Python SDK.

A Python SDK for interacting with the Nvisy API.
"""

__version__ = "0.1.0"

# Import main client and configuration classes
from .builder import ClientBuilder
from .client import Client
from .config import ClientConfiguration

# Import errors
from .errors import ApiError, ClientError, ConfigError, ErrorResponse, NetworkError

__all__ = [
    "__version__",
    # Core classes
    "Client",
    "ClientBuilder",
    "ClientConfiguration",
    # Errors
    "ClientError",
    "ConfigError",
    "NetworkError",
    "ApiError",
    "ErrorResponse",
]
