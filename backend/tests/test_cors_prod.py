import pytest
from pydantic import ValidationError

from app.core.config import Settings, assert_safe_prod_cors


@pytest.mark.parametrize("env", ["production", "prod", "PRODUCTION"])
def test_prod_rejects_wildcard_cors(env: str):
    with pytest.raises(ValueError, match="API_CORS_ORIGINS"):
        assert_safe_prod_cors(env, ["*"])


@pytest.mark.parametrize("env", ["production", "prod"])
def test_prod_rejects_empty_cors(env: str):
    with pytest.raises(ValueError, match="API_CORS_ORIGINS"):
        assert_safe_prod_cors(env, [])


def test_dev_allows_wildcard_and_empty():
    assert_safe_prod_cors("development", ["*"])
    assert_safe_prod_cors("dev", [])
    assert_safe_prod_cors("development", ["http://localhost:3000"])


def test_settings_fail_fast_on_prod_wildcard():
    with pytest.raises(ValidationError, match="API_CORS_ORIGINS"):
        Settings(app_env="production", api_cors_origins="*")


def test_settings_accept_prod_explicit_origins():
    s = Settings(
        app_env="production",
        api_cors_origins="https://app.example.com,https://www.example.com",
    )
    assert s.cors_origins_list == [
        "https://app.example.com",
        "https://www.example.com",
    ]
