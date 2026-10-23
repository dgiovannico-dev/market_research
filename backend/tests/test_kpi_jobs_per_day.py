"""KPI summary contract: jobs_per_day on dashboard summary (Executive sparkline)."""

import os

import pytest
from fastapi.testclient import TestClient

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


def test_summary_kpis_include_jobs_per_day(client):
    res = client.get("/api/v1/dashboard/summary")
    assert res.status_code == 200
    body = res.json()
    assert isinstance(body.get("kpis"), list)
    series = body["jobs_per_day"]
    assert isinstance(series, list)
    for row in series:
        assert "day" in row and "jobs" in row
