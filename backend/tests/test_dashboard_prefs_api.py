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


def test_dashboard_prefs_roundtrip(client):
    payload = {
        "prefs": {
            "view_mode": "trends_only",
            "period_days": 90,
            "focus_technologies": ["Java"],
            "focus_countries": ["DE"],
            "nav_hidden": ["/alerts"],
            "visible_widgets": [],
            "presets": {},
        }
    }
    put = client.put("/api/v1/profile/dashboard-prefs", json=payload)
    assert put.status_code == 200, put.text
    body = put.json()
    assert body["status"] == "saved"
    assert body["prefs"]["view_mode"] == "trends_only"
    assert body["prefs"]["period_days"] == 90

    get = client.get("/api/v1/profile/dashboard-prefs")
    assert get.status_code == 200
    got = get.json()
    assert got["prefs"]["view_mode"] == "trends_only"
    assert got["prefs"]["focus_technologies"] == ["Java"]


def test_gold_eval_endpoint(client):
    res = client.post("/api/v1/llm/evaluation/gold")
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["method"] == "gold_labels_rules"
    assert body["items_evaluated"] >= 5
