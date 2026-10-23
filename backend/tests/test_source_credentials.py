"""Encrypted source_credentials: crypto, resolve DB>env, ops API gate."""

from __future__ import annotations

import json

import pytest
from cryptography.fernet import Fernet
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings
from app.secrets.crypto import CredentialsCryptoError, decrypt_bytes, encrypt_bytes
from app.secrets.resolve import credential_bundle, credentials_source, has_required_credentials
from app.secrets.schema import CONNECTOR_SECRET_FIELDS
from app.secrets.store import delete_secrets, load_secrets, save_secrets
from app.storage.db import Base, get_db
from app.storage.models_core import SourceCredential


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


def test_fernet_roundtrip(master_key: str):
    token = encrypt_bytes(b'{"app_id":"x"}')
    assert decrypt_bytes(token) == b'{"app_id":"x"}'


def test_encrypt_fails_without_master_key(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("CREDENTIALS_MASTER_KEY", "")
    get_settings.cache_clear()
    with pytest.raises(CredentialsCryptoError):
        encrypt_bytes(b"x")
    get_settings.cache_clear()


def test_store_save_load_delete(db_session, master_key: str):
    save_secrets(db_session, "adzuna", {"app_id": "id1", "app_key": "key1"}, updated_by="test")
    loaded = load_secrets(db_session, "adzuna")
    assert loaded == {"app_id": "id1", "app_key": "key1"}
    assert delete_secrets(db_session, "adzuna") is True
    assert load_secrets(db_session, "adzuna") is None


def test_resolve_db_wins_over_env(db_session, master_key: str, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("ADZUNA_APP_ID", "env-id")
    monkeypatch.setenv("ADZUNA_APP_KEY", "env-key")
    get_settings.cache_clear()
    save_secrets(db_session, "adzuna", {"app_id": "db-id", "app_key": "db-key"})
    bundle = credential_bundle("adzuna", db=db_session)
    assert bundle == {"app_id": "db-id", "app_key": "db-key"}
    assert credentials_source("adzuna", db=db_session) == "db"
    assert has_required_credentials("adzuna", db=db_session) is True


def test_resolve_env_fallback(db_session, master_key: str, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("JOOBLE_API_KEY", "env-jooble")
    get_settings.cache_clear()
    assert credential_bundle("jooble", db=db_session) == {"api_key": "env-jooble"}
    assert credentials_source("jooble", db=db_session) == "env"


def test_resolve_none_when_empty(db_session, master_key: str, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("JOOBLE_API_KEY", "")
    get_settings.cache_clear()
    assert credential_bundle("jooble", db=db_session) == {}
    assert credentials_source("jooble", db=db_session) == "none"
    assert has_required_credentials("jooble", db=db_session) is False


def test_all_scaffolds_have_schema():
    from app.collectors.registry import CREDENTIALED_SCAFFOLDS

    for key in CREDENTIALED_SCAFFOLDS:
        assert key in CONNECTOR_SECRET_FIELDS, key


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


def test_ops_put_requires_token(api_client):
    res = api_client.put(
        "/api/v1/ops/connectors/adzuna/credentials",
        json={"fields": {"app_id": "a", "app_key": "b"}},
    )
    assert res.status_code == 401


def test_ops_put_get_delete_no_plaintext(api_client, db_session):
    secret = "super-secret-key-value-xyz"
    res = api_client.put(
        "/api/v1/ops/connectors/adzuna/credentials",
        json={"fields": {"app_id": "aid", "app_key": secret}, "ops_label": "test"},
        headers={"X-Ops-Token": "test-ops-token"},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["credentials_present"] is True
    assert body["credentials_source"] == "db"
    assert secret not in json.dumps(body)

    meta = api_client.get(
        "/api/v1/ops/connectors/adzuna/credential-fields",
        headers={"X-Ops-Token": "test-ops-token"},
    )
    assert meta.status_code == 200
    meta_body = meta.json()
    assert secret not in json.dumps(meta_body)
    assert meta_body["fields"]["app_key"]["set"] is True
    assert "value" not in meta_body["fields"]["app_key"]

    listed = api_client.get("/api/v1/ops/connectors")
    assert listed.status_code == 200
    assert secret not in listed.text
    adz = next(i for i in listed.json()["items"] if i["connector_key"] == "adzuna")
    assert adz["credentials_source"] == "db"

    deleted = api_client.delete(
        "/api/v1/ops/connectors/adzuna/credentials",
        headers={"X-Ops-Token": "test-ops-token"},
    )
    assert deleted.status_code == 200
    assert db_session.get(SourceCredential, "adzuna") is None
