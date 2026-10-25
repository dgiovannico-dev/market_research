"""Admin LLM settings must never echo API keys."""

from __future__ import annotations

import json

import pytest
from cryptography.fernet import Fernet
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings
from app.storage.db import Base, get_db


@pytest.fixture()
def master_key(monkeypatch: pytest.MonkeyPatch) -> str:
    key = Fernet.generate_key().decode()
    monkeypatch.setenv("CREDENTIALS_MASTER_KEY", key)
    monkeypatch.setenv("OPS_API_TOKEN", "test-ops-token")
    get_settings.cache_clear()
    yield key
    get_settings.cache_clear()


@pytest.fixture()
def db_session(master_key: str):
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def api_client(db_session, master_key: str):
    from app.main import app

    def _override():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_llm_settings_put_get_masks_key(api_client):
    secret = "sk-live-never-echo-this-key-xyz"
    put = api_client.put(
        "/api/v1/ops/llm/settings",
        json={
            "provider": "openai_compatible",
            "base_url": "https://api.openai.com/v1",
            "model": "gpt-4o-mini",
            "api_key": secret,
            "enable_classify": True,
        },
        headers={"X-Ops-Token": "test-ops-token"},
    )
    assert put.status_code == 200, put.text
    body = put.json()
    assert secret not in json.dumps(body)
    assert body.get("api_key_set") is True
    assert "api_key" not in body

    got = api_client.get(
        "/api/v1/ops/llm/settings",
        headers={"X-Ops-Token": "test-ops-token"},
    )
    assert got.status_code == 200
    assert secret not in got.text
    assert got.json()["api_key_set"] is True
    assert got.json()["provider"] == "openai_compatible"


def test_llm_settings_requires_admin(api_client):
    res = api_client.get("/api/v1/ops/llm/settings")
    assert res.status_code == 401


def test_prompt_seed_and_activate(api_client):
    seed = api_client.post(
        "/api/v1/ops/llm/prompts/seed",
        headers={"X-Ops-Token": "test-ops-token"},
    )
    assert seed.status_code == 200
    listed = api_client.get(
        "/api/v1/ops/llm/prompts",
        headers={"X-Ops-Token": "test-ops-token"},
    )
    assert listed.status_code == 200
    items = listed.json()["items"]
    assert any(i["slug"] == "classify_job" for i in items)
    created = api_client.post(
        "/api/v1/ops/llm/prompts/classify_job/versions",
        json={
            "system_text": "Return JSON only v2.",
            "user_text": "TEXT:\n{{text}}",
            "notes": "test v2",
            "activate": True,
        },
        headers={"X-Ops-Token": "test-ops-token"},
    )
    assert created.status_code == 200, created.text
    assert created.json()["status"] == "active"
    assert created.json()["version"] >= 2
