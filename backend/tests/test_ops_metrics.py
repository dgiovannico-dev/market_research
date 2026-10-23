import os

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://fmi:fmi_dev_password_change_me@localhost:5432/fmi",
)
os.environ["ENABLE_SCHEDULER"] = "false"

from app.main import app  # noqa: E402


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_ops_metrics(client):
    res = client.get("/api/v1/ops/metrics")
    assert res.status_code == 200
    body = res.json()
    assert body["evidence_kind"] == "observed"
    assert "jobs_canonical" in body
    assert "sources_enabled" in body
    assert "collection_runs_total" in body
    crawler = body["crawler"]
    assert "discovery_intents_enabled" in crawler
    assert "focus_intents_enabled" in crawler
    assert isinstance(crawler["discovery_intents_enabled"], int)
    assert isinstance(crawler["focus_intents_enabled"], int)
    assert "last_tick" in crawler
    if crawler["last_tick"] is not None:
        tick = crawler["last_tick"]
        assert "status" in tick
        assert "idempotent" in tick
        assert isinstance(tick["idempotent"], bool)
        assert "skips" in tick
        assert isinstance(tick["skips"], dict)
        assert "dump_ran" in tick or "calls" in tick


def test_ops_connectors(client):
    res = client.get("/api/v1/ops/connectors")
    assert res.status_code == 200
    body = res.json()
    assert body["evidence_kind"] == "config_observed"
    keys = {i["connector_key"] for i in body["items"]}
    assert "adzuna" in keys
    assert "bundesagentur" in keys
    assert "findwork" in keys
    assert "france_travail" in keys
    assert "jooble" in keys
    assert "careerjet" in keys
    assert "usajobs" in keys
    assert "infojobs" in keys
    for item in body["items"]:
        assert "credentials_present" in item
        assert isinstance(item["credentials_present"], bool)
    # Free ACTIVE connectors are separate from credentialed scaffolds.
    assert "active_free" in body
    free_keys = {i["connector_key"] for i in body["active_free"]}
    assert "tecnoempleo" in free_keys
    assert "le_forem" in free_keys
    assert "mpsv" in free_keys
    assert free_keys.isdisjoint(keys)
    for item in body["active_free"]:
        assert item["kind"] == "free_active"
        assert item["verification_status"] == "ACTIVE"
        assert "last_run_at" in item
        assert "last_success_at" in item
