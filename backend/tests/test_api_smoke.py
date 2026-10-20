import os

import pytest
from fastapi.testclient import TestClient

# Skip if no database available
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://fmi:fmi_dev_password_change_me@localhost:5432/fmi",
)
os.environ["DATABASE_URL"] = DATABASE_URL
os.environ["ENABLE_SCHEDULER"] = "false"

from app.main import app  # noqa: E402


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_health(client):
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_dashboard_and_quality(client):
    assert client.get("/api/v1/dashboard/summary").status_code == 200
    assert client.get("/api/v1/market/quality").status_code == 200
    assert client.get("/api/v1/market/rates").status_code == 200
    assert client.get("/api/v1/market/countries").status_code == 200
    assert client.get("/api/v1/market/skills/cooccurrence").status_code == 200


def test_profile_and_report(client):
    assert client.get("/api/v1/profile").status_code == 200
    assert client.get("/api/v1/profile/skill-gaps").status_code == 200
    assert client.get("/api/v1/reports/weekly").status_code == 200
    assert client.post("/api/v1/alerts/evaluate").status_code == 200


def test_llm_status_rules_mode(client):
    res = client.get("/api/v1/llm/status")
    assert res.status_code == 200
    body = res.json()
    assert body["configured_provider"] in {"none", "ollama", "vllm"}


def test_llm_evaluation_stub(client):
    res = client.post("/api/v1/llm/evaluation/run?limit=5")
    assert res.status_code == 200
    body = res.json()
    assert body["method"] == "rules_self_consistency"
    assert "overall_agreement" in body
