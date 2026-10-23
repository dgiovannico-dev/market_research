"""Multi-country filter on dashboard/summary and market/rates."""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://fmi:fmi_dev_password_change_me@localhost:5432/fmi",
)
os.environ["ENABLE_SCHEDULER"] = "false"

from app.analytics.country_filter import parse_country_codes  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_parse_country_codes_csv_and_dedupe():
    assert parse_country_codes("it, CH, it, ALL, ") == ["IT", "CH"]
    assert parse_country_codes(None) == []
    assert parse_country_codes(["de", "DE", "fr"]) == ["DE", "FR"]


def _unique_jobs(body: dict) -> float:
    for kpi in body.get("kpis") or []:
        if kpi.get("metric_name") == "unique_jobs_observed":
            return float(kpi.get("metric_value") or 0)
    return 0.0


def test_summary_multi_country_scopes(client):
    unscoped = client.get("/api/v1/dashboard/summary", params={"days": 90})
    assert unscoped.status_code == 200, unscoped.text
    all_n = _unique_jobs(unscoped.json())
    assert all_n > 0

    scoped = client.get(
        "/api/v1/dashboard/summary",
        params={"days": 90, "country_code": "IT,CH"},
    )
    assert scoped.status_code == 200, scoped.text
    body = scoped.json()
    assert body.get("countries") == ["IT", "CH"]
    scoped_n = _unique_jobs(body)
    assert scoped_n <= all_n
    assert scoped_n > 0
    for row in body.get("top_countries") or []:
        assert row["country_code"] in {"IT", "CH"}


def test_rates_multi_country_and_invalid_ignored(client):
    res = client.get(
        "/api/v1/market/rates",
        params={"days": 180, "country_code": "IT,CH,ALL,,xx", "min_sample": 1},
    )
    assert res.status_code == 200, res.text
    body = res.json()
    # xx kept as literal code; ALL/empty dropped
    assert "IT" in (body.get("countries") or [])
    assert "CH" in (body.get("countries") or [])
    for item in body.get("items") or []:
        assert item["country_code"] in set(body["countries"])


def test_summary_lens_and_countries_and(client):
    market = client.get(
        "/api/v1/dashboard/summary",
        params={"days": 90, "lens": "market", "country_code": "IT"},
    )
    assert market.status_code == 200
    assert market.json().get("countries") == ["IT"]
    assert market.json().get("lens") == "market"
