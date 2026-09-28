"""Unit tests for Application Configuration & Environment Variables."""

from pydantic import ValidationError
import pytest
from app.config import Settings, get_settings


@pytest.mark.unit
class TestConfig:
    """Test suite verifying environment variable loading, validation, and security."""

    def test_default_settings_load(self):
        """Verify default settings instantiation."""
        settings = Settings()
        assert settings.APP_NAME is not None
        assert settings.APP_ENV in {"development", "staging", "production", "testing"}
        assert 1 <= settings.PORT <= 65535
        assert settings.LOG_LEVEL in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        assert settings.LOG_FORMAT in {"json", "text"}

    def test_secret_key_masking(self):
        """Ensure secret keys are masked in string representations to prevent accidental leakage in logs."""
        secret_val = "super-secret-token-12345"
        settings = Settings(API_SECRET_KEY=secret_val)
        # SecretStr.__str__ and __repr__ must mask the value
        assert secret_val not in str(settings.API_SECRET_KEY)
        assert secret_val not in repr(settings.API_SECRET_KEY)
        assert settings.API_SECRET_KEY.get_secret_value() == secret_val

    def test_invalid_app_env_raises_validation_error(self):
        """Ensure invalid environment names are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            Settings(APP_ENV="invalid_env")
        assert "Invalid APP_ENV" in str(exc_info.value)

    def test_invalid_log_level_raises_validation_error(self):
        """Ensure invalid log levels are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            Settings(LOG_LEVEL="VERBOSE")
        assert "Invalid LOG_LEVEL" in str(exc_info.value)

    def test_invalid_log_format_raises_validation_error(self):
        """Ensure invalid log formats are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            Settings(LOG_FORMAT="xml")
        assert "Invalid LOG_FORMAT" in str(exc_info.value)

    def test_invalid_port_range(self):
        """Ensure port must be within standard TCP port range [1, 65535]."""
        with pytest.raises(ValidationError):
            Settings(PORT=0)
        with pytest.raises(ValidationError):
            Settings(PORT=70000)

    @pytest.mark.parametrize(
        "env_val,expected",
        [
            ("production", True),
            ("development", False),
            ("staging", False),
            ("testing", False),
        ],
    )
    def test_is_production_property(self, env_val: str, expected: bool):
        """Verify is_production property accurately detects production stage."""
        settings = Settings(APP_ENV=env_val)
        assert settings.is_production is expected

    def test_cors_origins_parsing(self):
        """Verify allowed origins parsing handles wildcard and explicit domains."""
        wildcard_settings = Settings(ALLOWED_ORIGINS="*")
        assert wildcard_settings.cors_origins_list == ["*"]

        custom_settings = Settings(ALLOWED_ORIGINS="https://app.example.com, https://admin.example.com")
        assert custom_settings.cors_origins_list == [
            "https://app.example.com",
            "https://admin.example.com",
        ]

    def test_get_settings_cache(self):
        """Ensure get_settings returns cached singleton instance."""
        s1 = get_settings()
        s2 = get_settings()
        assert s1 is s2
