"""Basic tests for the Nvisy SDK."""

import os
from unittest.mock import patch

import pytest

import nvisy
from nvisy import (
    Client,
    ClientBuilder,
    ClientConfiguration,
    NvisyAPIError,
    NvisyAuthenticationError,
    NvisyConfigurationError,
)


def test_version():
    """Test that the version is accessible."""
    assert nvisy.__version__
    assert isinstance(nvisy.__version__, str)
    assert len(nvisy.__version__.split(".")) >= 3


def test_imports():
    """Test that basic imports work."""
    # Test that the module can be imported
    assert nvisy is not None

    # Test that main classes can be imported
    assert Client is not None
    assert ClientBuilder is not None
    assert ClientConfiguration is not None


class TestClientConfiguration:
    """Test ClientConfiguration class."""

    def test_valid_configuration(self):
        """Test creating a valid configuration."""
        config = ClientConfiguration(
            api_key="test-api-key-123456",
            base_url="https://api.nvisy.com",
            timeout=30.0,
            max_retries=3,
        )

        assert config.api_key == "test-api-key-123456"
        assert config.base_url == "https://api.nvisy.com"
        assert config.timeout == 30.0
        assert config.max_retries == 3

    def test_invalid_api_key(self):
        """Test validation of API key."""
        from pydantic import ValidationError

        with pytest.raises(
            ValidationError, match="String should have at least 10 characters"
        ):
            ClientConfiguration(api_key="short")

    def test_invalid_base_url(self):
        """Test validation of base URL."""
        with pytest.raises(ValueError, match="Base URL must be a valid HTTP/HTTPS URL"):
            ClientConfiguration(api_key="test-api-key-123456", base_url="not-a-url")

    def test_default_user_agent(self):
        """Test default user agent generation."""
        config = ClientConfiguration(api_key="test-api-key-123456")
        user_agent = config.get_effective_user_agent()
        assert "nvisy-sdk-python" in user_agent
        assert nvisy.__version__ in user_agent

    def test_custom_user_agent(self):
        """Test custom user agent."""
        config = ClientConfiguration(
            api_key="test-api-key-123456", user_agent="MyApp/1.0.0"
        )
        assert config.get_effective_user_agent() == "MyApp/1.0.0"

    def test_effective_headers(self):
        """Test header generation."""
        config = ClientConfiguration(
            api_key="test-api-key-123456", headers={"X-Custom": "value"}
        )
        headers = config.get_effective_headers()

        assert headers["Authorization"] == "Bearer test-api-key-123456"
        assert "User-Agent" in headers
        assert headers["Content-Type"] == "application/json"
        assert headers["Accept"] == "application/json"
        assert headers["X-Custom"] == "value"

    @patch.dict(
        os.environ,
        {
            "NVISY_API_TOKEN": "env-api-key-123456",
            "NVISY_BASE_URL": "https://api-staging.nvisy.com",
            "NVISY_MAX_TIMEOUT": "60000",
            "NVISY_MAX_RETRIES": "5",
            "NVISY_USER_AGENT": "EnvApp/2.0.0",
            "DEBUG": "true",
        },
    )
    def test_from_environment(self):
        """Test creating configuration from environment variables."""
        config = ClientConfiguration.from_environment()

        assert config.api_key == "env-api-key-123456"
        assert config.base_url == "https://api-staging.nvisy.com"
        assert config.timeout == 60.0  # Converted from milliseconds
        assert config.max_retries == 5
        assert config.user_agent == "EnvApp/2.0.0"
        assert config.debug is True

    def test_from_environment_missing_api_key(self):
        """Test error when API key is missing from environment."""
        with patch.dict(os.environ, {}, clear=True), pytest.raises(
            ValueError, match="API key is required"
        ):
            ClientConfiguration.from_environment()


class TestClientBuilder:
    """Test ClientBuilder class."""

    def test_basic_builder(self):
        """Test basic builder functionality."""
        builder = ClientBuilder()
        assert builder is not None

    def test_fluent_api(self):
        """Test fluent API chaining."""
        builder = (
            ClientBuilder()
            .with_api_key("test-api-key-123456")
            .with_base_url("https://api-test.nvisy.com")
            .with_timeout(60)
            .with_max_retries(5)
            .with_user_agent("TestApp/1.0.0")
            .with_header("X-Test", "value")
            .with_debug(True)
        )

        assert builder is not None
        # Builder should return itself for chaining
        assert isinstance(builder, ClientBuilder)

    def test_build_client(self):
        """Test building a client from builder."""
        client = ClientBuilder().with_api_key("test-api-key-123456").build()

        assert isinstance(client, Client)
        assert client.config.api_key == "test-api-key-123456"

    def test_build_without_api_key(self):
        """Test building without API key raises error."""
        builder = ClientBuilder()

        with pytest.raises(NvisyConfigurationError, match="API key is required"):
            builder.build()

    def test_multiple_headers(self):
        """Test adding multiple headers."""
        client = (
            ClientBuilder()
            .with_api_key("test-api-key-123456")
            .with_header("X-First", "value1")
            .with_headers({"X-Second": "value2", "X-Third": "value3"})
            .build()
        )

        headers = client.config.headers
        assert headers["X-First"] == "value1"
        assert headers["X-Second"] == "value2"
        assert headers["X-Third"] == "value3"

    @patch.dict(
        os.environ,
        {
            "NVISY_API_TOKEN": "env-api-key-123456",
            "NVISY_BASE_URL": "https://api-staging.nvisy.com",
        },
    )
    def test_from_environment_builder(self):
        """Test creating builder from environment."""
        builder = ClientBuilder.from_environment()
        client = builder.with_timeout(45).build()

        assert client.config.api_key == "env-api-key-123456"
        assert client.config.base_url == "https://api-staging.nvisy.com"
        assert client.config.timeout == 45.0  # Override from builder


class TestClient:
    """Test Client class."""

    def test_direct_configuration(self):
        """Test creating client with direct configuration."""
        config = ClientConfiguration(api_key="test-api-key-123456")
        client = Client(config)

        assert isinstance(client, Client)
        assert client.config.api_key == "test-api-key-123456"

    def test_dict_configuration(self):
        """Test creating client with dictionary configuration."""
        client = Client({"api_key": "test-api-key-123456"})

        assert isinstance(client, Client)
        assert client.config.api_key == "test-api-key-123456"

    def test_builder_class_method(self):
        """Test Client.builder() class method."""
        builder = Client.builder()
        assert isinstance(builder, ClientBuilder)

    @patch.dict(os.environ, {"NVISY_API_TOKEN": "env-api-key-123456"})
    def test_from_environment_class_method(self):
        """Test Client.from_environment() class method."""
        client = Client.from_environment()

        assert isinstance(client, Client)
        assert client.config.api_key == "env-api-key-123456"

    def test_context_manager(self):
        """Test client as context manager."""
        config = ClientConfiguration(api_key="test-api-key-123456")

        with Client(config) as client:
            assert isinstance(client, Client)

    def test_repr(self):
        """Test string representation of client."""
        config = ClientConfiguration(api_key="test-api-key-123456")
        client = Client(config)

        repr_str = repr(client)
        assert "Client(" in repr_str
        assert "https://api.nvisy.com" in repr_str
        assert "30" in repr_str  # timeout


class TestExceptions:
    """Test exception imports and basic functionality."""

    def test_exception_imports(self):
        """Test that exceptions can be imported."""
        from nvisy import (
            NvisyAPIError,
            NvisyAuthenticationError,
            NvisyConfigurationError,
            NvisyError,
        )

        assert issubclass(NvisyAPIError, NvisyError)
        assert issubclass(NvisyAuthenticationError, NvisyAPIError)
        assert issubclass(NvisyConfigurationError, NvisyError)

    def test_exception_hierarchy(self):
        """Test exception hierarchy works correctly."""
        try:
            raise NvisyAuthenticationError("Auth failed")
        except NvisyAPIError:
            # Should catch parent class
            pass
        except Exception:
            pytest.fail("Exception hierarchy not working correctly")


class TestModuleLevel:
    """Test module-level functionality."""

    def test_module_has_all_attribute(self):
        """Test that __all__ is defined."""
        assert hasattr(nvisy, "__all__")
        assert isinstance(nvisy.__all__, list)

        # Check that main exports are in __all__
        assert "Client" in nvisy.__all__
        assert "ClientBuilder" in nvisy.__all__
        assert "ClientConfiguration" in nvisy.__all__

    def test_version_format(self):
        """Test version follows semantic versioning."""
        version_parts = nvisy.__version__.split(".")
        assert len(version_parts) >= 3

        # Check that major, minor, patch are numeric
        for i in range(3):
            assert version_parts[i].isdigit(), f"Version part {i} should be numeric"

    def test_all_exports_importable(self):
        """Test that all items in __all__ can be imported."""
        for item in nvisy.__all__:
            if item != "__version__":  # Skip version string
                assert hasattr(nvisy, item), f"{item} not available in module"


@pytest.mark.asyncio
async def test_async_functionality():
    """Test that async functionality is available."""
    # This will be expanded when actual client methods are implemented
    config = ClientConfiguration(api_key="test-api-key-123456")
    client = Client(config)

    # Test context manager works
    async with client:
        assert isinstance(client, Client)
