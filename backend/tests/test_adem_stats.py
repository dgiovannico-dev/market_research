"""ADEM LU skills open-data summary (reference stats, not job KPIs)."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app
from app.stats.adem import summarize_csv

FIXTURE = Path(__file__).parent / "fixtures" / "adem_skills_sample.csv"


def test_summarize_csv_fixture():
    out = summarize_csv(FIXTURE, top_skills=10)
    assert out["provider"] == "adem"
    assert out["country"] == "LU"
    assert out["distinct_vacancies"] == 4
    assert out["rows_empty_skill"] == 1
    skills = {row["skill"]: row["count"] for row in out["top_skills_by_row_count"]}
    assert skills["Python"] == 2
    assert skills["Docker"] == 1
    assert "2026-03" in out["vacancies_by_month"]


def test_summarize_csv_nace_filter():
    out = summarize_csv(FIXTURE, nace_prefix="J", top_skills=10)
    assert out["distinct_vacancies"] == 2
    assert out["rows_skipped_nace"] >= 1
    skills = {row["skill"] for row in out["top_skills_by_row_count"]}
    assert "Python" in skills
    assert "Accounting" not in skills


def test_adem_endpoint_not_configured(monkeypatch):
    monkeypatch.setenv("ADEM_CSV_PATH", "")
    get_settings.cache_clear()
    with TestClient(app) as client:
        r = client.get("/api/v1/stats/adem/skills-summary")
    get_settings.cache_clear()
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "not_configured"
    assert body["provider"] == "adem"


def test_adem_endpoint_with_fixture(monkeypatch):
    monkeypatch.setenv("ADEM_CSV_PATH", str(FIXTURE))
    get_settings.cache_clear()
    with TestClient(app) as client:
        r = client.get(
            "/api/v1/stats/adem/skills-summary",
            params={"nace_prefix": "J", "top_skills": 5},
        )
    get_settings.cache_clear()
    assert r.status_code == 200
    body = r.json()
    assert body["source"] == "adem_lu_skills_opendata"
    assert body["distinct_vacancies"] == 2
    assert body["evidence_kind"] == "official_statistics_reference"
