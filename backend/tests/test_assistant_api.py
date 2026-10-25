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


def test_assistant_propose_dashboard(client):
    res = client.post(
        "/api/v1/assistant/propose",
        json={"prompt": "trend java 90 days trends-only", "kind": "dashboard"},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["kind"] == "dashboard"
    assert body["validation"]["ok"] is True
    assert body["spec"]["period_days"] == 90
    assert body["spec"]["view_mode"] == "trends_only"


def test_assistant_propose_report_materialize(client):
    res = client.post(
        "/api/v1/assistant/propose",
        json={"prompt": "weekly rates report", "kind": "report", "materialize": True},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["kind"] == "report"
    assert body["materialized"]["ok"] is True
    narrative = body["materialized"]["narrative"].lower()
    assert "eur" not in narrative or "undeclared" in narrative or "insufficient" in narrative


def test_assistant_report_pdf(client):
    res = client.post(
        "/api/v1/assistant/report-pdf",
        json={"prompt": "weekly rates report", "locale": "en"},
    )
    assert res.status_code == 200, res.text
    assert res.headers.get("content-type", "").startswith("application/pdf")
    assert res.content[:4] == b"%PDF"
    assert "filename=" in (res.headers.get("content-disposition") or "")


def test_assistant_accepts_locale(client):
    """Optional locale en|it must validate (not 422) and echo in meta."""
    propose = client.post(
        "/api/v1/assistant/propose",
        json={
            "prompt": "trend java 90 days trends-only",
            "kind": "dashboard",
            "locale": "it",
        },
    )
    assert propose.status_code == 200, propose.text
    assert propose.json()["meta"]["locale"] == "it"
    assert propose.json()["meta"]["narrative_locale"] == "en"

    brief = client.post(
        "/api/v1/assistant/brief",
        json={
            "brief_type": "rising_cooling",
            "lens": "market",
            "locale": "it",
            "country_code": "IT,CH",
        },
    )
    assert brief.status_code == 200, brief.text
    assert brief.json()["meta"]["locale"] == "it"
    assert brief.json()["meta"]["narrative_locale"] == "it"
    assert brief.json()["brief"].get("countries") in (None, ["IT", "CH"])
    narr = brief.json()["brief"].get("narrative") or ""
    assert "n=" in narr
    assert "Lens=" not in narr

    brief_default = client.post(
        "/api/v1/assistant/brief",
        json={"brief_type": "rising_cooling", "lens": "market"},
    )
    assert brief_default.status_code == 200, brief_default.text
    assert brief_default.json()["meta"]["locale"] == "en"
    assert brief_default.json()["meta"]["narrative_locale"] == "en"

    bad = client.post(
        "/api/v1/assistant/brief",
        json={"brief_type": "rising_cooling", "lens": "market", "locale": "fr"},
    )
    assert bad.status_code == 422
