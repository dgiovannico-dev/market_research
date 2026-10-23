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
    body = res.json()
    assert body["status"] == "ok"
    assert "methodology_version" in body


def test_livez_public(client):
    res = client.get("/livez")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert body["probe"] == "live"
    assert "database" not in body


def test_readyz_public(client):
    res = client.get("/readyz")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert body["database"] == "up"
    assert body["probe"] == "ready"


def test_healthz_is_ready_alias(client):
    """/healthz matches /readyz (readiness), not /livez."""
    hz = client.get("/healthz")
    rz = client.get("/readyz")
    assert hz.status_code == 200
    assert hz.status_code == rz.status_code
    assert hz.json() == rz.json()
    assert hz.json()["probe"] == "ready"
    assert hz.json() != client.get("/livez").json()


def test_authenticated_health_advertises_probes(client):
    body = client.get("/api/v1/health").json()
    assert body["public_live"] == "/livez"
    assert body["public_ready"] == "/readyz"
    assert body["public_ready_alias"] == "/healthz"


def test_dashboard_and_quality(client):
    summary = client.get("/api/v1/dashboard/summary")
    assert summary.status_code == 200
    # Hardening: SecurityHeadersMiddleware on real app responses.
    assert summary.headers["x-content-type-options"] == "nosniff"
    assert summary.headers["x-frame-options"] == "DENY"
    assert summary.headers["referrer-policy"] == "strict-origin-when-cross-origin"
    body = summary.json()
    assert "jobs_per_day" in body
    assert "kpis" in body
    series = body["jobs_per_day"]
    assert isinstance(series, list)
    for row in series:
        assert set(row) >= {"day", "jobs"}
        assert isinstance(row["day"], str)
        assert isinstance(row["jobs"], int)
    assert client.get("/api/v1/market/quality").status_code == 200
    assert client.get("/api/v1/market/rates").status_code == 200
    assert client.get("/api/v1/market/countries").status_code == 200
    assert client.get("/api/v1/market/countries", params={"for_map": "true"}).status_code == 200
    assert client.get("/api/v1/market/facets").status_code == 200
    assert client.get("/api/v1/market/languages").status_code == 200
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


def test_min_evidence_query_param(client):
    ok = client.get("/api/v1/market/rates", params={"min_evidence": "all"})
    assert ok.status_code == 200
    assert ok.json().get("min_evidence") == "all"

    bad = client.get("/api/v1/market/rates", params={"min_evidence": "gold"})
    assert bad.status_code == 400
    assert "min_evidence" in bad.json()["detail"].lower()
