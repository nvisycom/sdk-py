"""Configuration module for the Nvisy SDK."""

import contextlib
import os
import re
from typing import Any, Dict, Optional
from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator


class ClientConfiguration(BaseModel):
    """Configuration model for the Nvisy client.

    Handles all client settings including authentication, network configuration,
    and request parameters with proper validation.
    """

    api_key: str = Field(..., min_length=10, description="API key for authentication")
    base_url: str = Field(
        default="https://api.nvisy.com", description="Base URL for the Nvisy API"
    )
    timeout: float = Field(
        default=30.0, ge=1.0, le=300.0, description="Request timeout in seconds (1-300)"
    )
    max_retries: int = Field(
        default=3, ge=0, le=5, description="Maximum number of retry attempts (0-5)"
    )
    user_agent: Optional[str] = Field(
        default=None, description="Custom user agent string"
    )
    headers: Dict[str, str] = Field(
        default_factory=dict, description="Additional headers to send with requests"
    )
    debug: bool = Field(default=False, description="Enable debug mode")

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """Validate API key format."""
        if not re.match(r"^[a-zA-Z0-9_-]{10,}$", v):
            raise ValueError(
                "API key must be at least 10 characters and contain only "
                "alphanumeric characters, underscores, and hyphens"
            )
        return v

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, v: str) -> str:
        """Validate base URL format."""
        parsed = urlparse(v)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("Base URL must be a valid HTTP/HTTPS URL")
        if parsed.scheme not in ("http", "https"):
            raise ValueError("Base URL must use HTTP or HTTPS protocol")
        return v.rstrip("/")

    @field_validator("user_agent")
    @classmethod
    def validate_user_agent(cls, v: Optional[str]) -> Optional[str]:
        """Validate user agent string."""
        if v is not None and len(v.strip()) == 0:
            return None
        return v

    def get_default_user_agent(self) -> str:
        """Get the default user agent string."""
        from . import __version__

        return f"nvisy-sdk-python/{__version__}"

    def get_effective_user_agent(self) -> str:
        """Get the effective user agent (custom or default)."""
        return self.user_agent or self.get_default_user_agent()

    def get_effective_headers(self) -> Dict[str, str]:
        """Get the effective headers including authentication and user agent."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": self.get_effective_user_agent(),
            "Content-Type": "application/json",
            "Accept": "application/json",
            **self.headers,
        }
        return headers

    @classmethod
    def from_environment(cls) -> "ClientConfiguration":
        """Create configuration from environment variables.

        Reads configuration from these environment variables:
        - NVISY_API_TOKEN: API key (required)
        - NVISY_BASE_URL: Base URL
        - NVISY_MAX_TIMEOUT: Timeout in milliseconds
        - NVISY_MAX_RETRIES: Maximum retries
        - NVISY_USER_AGENT: User agent
        - DEBUG: Enable debug mode

        Returns:
            ClientConfiguration instance

        Raises:
            ValueError: If required environment variables are missing
        """
        api_key = os.getenv("NVISY_API_TOKEN")
        if not api_key:
            raise ValueError(
                "API key is required. Set NVISY_API_TOKEN environment variable."
            )

        config_dict: Dict[str, Any] = {"api_key": api_key}

        if base_url := os.getenv("NVISY_BASE_URL"):
            config_dict["base_url"] = base_url

        if timeout_ms := os.getenv("NVISY_MAX_TIMEOUT"):
            with contextlib.suppress(ValueError, TypeError):
                timeout_seconds = float(timeout_ms) / 1000.0
                config_dict["timeout"] = timeout_seconds

        if max_retries := os.getenv("NVISY_MAX_RETRIES"):
            with contextlib.suppress(ValueError, TypeError):
                config_dict["max_retries"] = int(max_retries)

        if user_agent := os.getenv("NVISY_USER_AGENT"):
            config_dict["user_agent"] = user_agent

        if os.getenv("DEBUG", "").lower() in ("true", "1", "yes"):
            config_dict["debug"] = True

        return cls(**config_dict)
