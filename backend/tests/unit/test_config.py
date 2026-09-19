"""Test Configuration

Tests for application configuration and settings.
"""

from app.core.config import get_settings, Settings


def test_settings_loads():
    """Test that settings load correctly."""
    settings = get_settings()

    assert isinstance(settings, Settings)
    assert settings.PROJECT_NAME == "AAS PAAS"
    assert settings.VERSION == "0.1.0"
    assert settings.API_V1_PREFIX == "/api/v1"


def test_settings_cached():
    """Test that settings are cached (same instance returned)."""
    settings1 = get_settings()
    settings2 = get_settings()

    # Should be the same instance due to lru_cache
    assert settings1 is settings2


def test_allowed_origins_parsed():
    """Test that ALLOWED_ORIGINS string is parsed into list."""
    settings = get_settings()

    assert isinstance(settings.ALLOWED_ORIGINS, list)
    assert len(settings.ALLOWED_ORIGINS) > 0


def test_environment_properties():
    """Test environment property helpers."""
    settings = get_settings()

    # Should have is_production and is_development properties
    assert isinstance(settings.is_production, bool)
    assert isinstance(settings.is_development, bool)

    # One should be True, but not both
    assert settings.is_production != settings.is_development
