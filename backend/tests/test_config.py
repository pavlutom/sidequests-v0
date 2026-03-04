import pytest
from config import settings
from datetime import datetime
import zoneinfo
import os

def test_config_timezone_respected(monkeypatch):
    from config import Settings
    
    # Test with New York time
    monkeypatch.setenv("TIMEZONE", "America/New_York")
    ny_settings = Settings()
    assert ny_settings.timezone == "America/New_York"
    assert ny_settings.tz.key == "America/New_York"
    
    # Test with Tokyo time
    monkeypatch.setenv("TIMEZONE", "Asia/Tokyo")
    tokyo_settings = Settings()
    assert tokyo_settings.timezone == "Asia/Tokyo"
    assert tokyo_settings.tz.key == "Asia/Tokyo"

def test_database_url_construction(monkeypatch):
    from config import Settings
    # Clear DATABASE_URL from env to ensure we test construction
    monkeypatch.delenv("DATABASE_URL", raising=False)
    
    # Set other env vars
    monkeypatch.setenv("POSTGRES_USER", "uv_user")
    monkeypatch.setenv("POSTGRES_PASSWORD", "uv_password")
    monkeypatch.setenv("DATABASE_HOST", "uv_host")
    monkeypatch.setenv("DATABASE_PORT", "5432")
    monkeypatch.setenv("POSTGRES_DB", "uv_db")
        
    s = Settings()
    expected = "postgresql+psycopg://uv_user:uv_password@uv_host:5432/uv_db"
    assert s.database_url == expected

def test_database_url_override(monkeypatch):
    from config import Settings
    # Test that DATABASE_URL in env overrides construction
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    s = Settings()
    assert s.database_url == "sqlite:///:memory:"
