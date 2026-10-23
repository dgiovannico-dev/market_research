"""DevITJobs collector: host fan-out, query terms, stratification, dedupe."""
from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from app.collectors.base import MISSING_QUERY
from app.collectors.devitjobs import (
    DEFAULT_HOSTS,
    MAX_HOSTS,
    MAX_PER_CATEGORY,
    DevITJobsCollector,
    _query_terms,
    _resolve_hosts,
    _select_items,
    _should_fan_out,
)


def _item(
    job_id: str,
    *,
    name: str = "Engineer",
    tech: str = "Python",
    company: str = "Acme",
    active: str = "2026-10-01T00:00:00Z",
    paused: bool = False,
    technologies: list[str] | None = None,
) -> dict:
    return {
        "_id": job_id,
        "jobUrl": f"Job-{job_id}",
        "name": name,
        "company": company,
        "techCategory": tech,
        "technologies": technologies or [tech],
        "filterTags": technologies or [tech],
        "isPaused": paused,
        "activeFrom": active,
        "cityCategory": "London",
        "workplace": "remote",
        "remoteType": "full",
        "jobType": "Full-Time",
        "annualSalaryFrom": 50000,
        "annualSalaryTo": 60000,
    }


def _mock_client(side_effect):
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(side_effect=side_effect)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    return mock_client


def _resp(payload):
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = payload
    return mock_resp


def test_resolve_hosts_fills_eu_defaults():
    hosts = _resolve_hosts("uk,com")
    assert hosts[0] == "uk"
    assert hosts[1] == "com"
    assert "nl" in hosts
    assert "fr" in hosts
    assert len(hosts) == MAX_HOSTS
    assert set(hosts).issubset(set(DEFAULT_HOSTS) | {"uk", "com"})


def test_resolve_hosts_respects_max():
    hosts = _resolve_hosts("uk,com,nl,fr,pl")
    assert hosts == ["uk", "com", "nl", "fr"]
    assert len(hosts) == MAX_HOSTS


def test_resolve_hosts_empty_uses_defaults():
    assert _resolve_hosts("")[:2] == ["uk", "com"]


def test_should_fan_out_generic_and_tech():
    assert _should_fan_out("it") is True
    assert _should_fan_out("java") is True
    assert _should_fan_out("software engineer") is True
    assert _should_fan_out("nurse london") is False


def test_query_terms_blank_means_dump():
    assert _query_terms(None) == []
    assert _query_terms("  ") == []


def test_query_terms_fan_out_for_tech():
    terms = _query_terms("java")
    assert terms[0] == "java"
    assert len(terms) >= 2
    assert len(terms) <= 4


def test_query_terms_or_split():
    terms = _query_terms("python OR golang")
    assert terms == ["python", "golang"]


def test_select_items_stratifies_categories():
    payload = []
    for i in range(40):
        payload.append(_item(f"d{i}", tech="DevOps", name=f"DevOps {i}"))
    for i in range(40):
        payload.append(_item(f"p{i}", tech="Python", name=f"Python {i}"))
    # Cap-bound window: stratification applies before remainder fill.
    picked = _select_items(payload, terms=[], limit=40)
    cats = {x["techCategory"] for x in picked}
    assert "DevOps" in cats and "Python" in cats
    assert sum(1 for x in picked if x["techCategory"] == "DevOps") <= MAX_PER_CATEGORY
    assert sum(1 for x in picked if x["techCategory"] == "Python") <= MAX_PER_CATEGORY
    assert len(picked) == 40


def test_select_items_filters_query_and_paused():
    payload = [
        _item("1", name="Java Developer", tech="Java"),
        _item("2", name="Nurse", tech="Support"),
        _item("3", name="Java Lead", tech="Java", paused=True),
    ]
    picked = _select_items(payload, terms=["java"], limit=10)
    assert [x["_id"] for x in picked] == ["1"]


def test_dump_mode_with_query_none():
    by_host = {
        "https://devitjobs.uk/api/jobsLight": [_item("uk1", tech="Java")],
        "https://devitjobs.com/api/jobsLight": [_item("com1", tech="Python")],
        "https://devitjobs.nl/api/jobsLight": [_item("nl1", tech="Data")],
        "https://devitjobs.fr/api/jobsLight": [_item("fr1", tech="Java")],
    }

    def side_effect(url, **_kwargs):
        return _resp(by_host.get(url, []))

    mock_client = _mock_client(side_effect)
    with patch("app.collectors.devitjobs.httpx.AsyncClient", return_value=mock_client):
        with patch("app.collectors.devitjobs.get_settings") as gs:
            gs.return_value.devitjobs_hosts = "uk,com"
            result = asyncio.run(DevITJobsCollector().collect(None))

    assert MISSING_QUERY not in result.errors
    assert result.errors == []
    assert result.pages_scanned == MAX_HOSTS
    assert len(result.records) == 4
    urls = {r.url for r in result.records}
    assert any("devitjobs.uk" in u for u in urls)
    assert any("devitjobs.nl" in u for u in urls)
    assert any("devitjobs.fr" in u for u in urls)


def test_dedupe_across_hosts_by_id():
    shared = _item("same", name="Shared Role", tech="Java")

    def side_effect(url, **_kwargs):
        if "devitjobs.uk" in url:
            return _resp([shared, _item("uk-only")])
        if "devitjobs.com" in url:
            return _resp([shared, _item("com-only")])
        return _resp([])

    mock_client = _mock_client(side_effect)
    with patch("app.collectors.devitjobs.httpx.AsyncClient", return_value=mock_client):
        with patch("app.collectors.devitjobs.get_settings") as gs:
            gs.return_value.devitjobs_hosts = "uk,com"
            result = asyncio.run(DevITJobsCollector().collect(None))

    ids = [r.source_job_id for r in result.records]
    assert ids.count("uk:same") == 1
    assert "com:same" not in ids
    assert "uk:uk-only" in ids
    assert "com:com-only" in ids


def test_query_filters_client_side():
    def side_effect(url, **_kwargs):
        if "devitjobs.uk" in url:
            return _resp(
                [
                    _item("1", name="Senior Java Engineer", tech="Java"),
                    _item("2", name="Payroll Clerk", tech="Business"),
                ]
            )
        return _resp([])

    mock_client = _mock_client(side_effect)
    with patch("app.collectors.devitjobs.httpx.AsyncClient", return_value=mock_client):
        with patch("app.collectors.devitjobs.get_settings") as gs:
            gs.return_value.devitjobs_hosts = "uk"
            # Force single host only
            with patch("app.collectors.devitjobs._resolve_hosts", return_value=["uk"]):
                result = asyncio.run(DevITJobsCollector().collect("java"))

    assert len(result.records) == 1
    assert "Java" in result.records[0].title


def test_host_error_continues():
    def side_effect(url, **_kwargs):
        if "devitjobs.uk" in url:
            raise RuntimeError("boom")
        if "devitjobs.com" in url:
            return _resp([_item("ok")])
        return _resp([])

    mock_client = _mock_client(side_effect)
    with patch("app.collectors.devitjobs.httpx.AsyncClient", return_value=mock_client):
        with patch("app.collectors.devitjobs.get_settings") as gs:
            gs.return_value.devitjobs_hosts = "uk,com"
            with patch(
                "app.collectors.devitjobs._resolve_hosts",
                return_value=["uk", "com"],
            ):
                result = asyncio.run(DevITJobsCollector().collect(None))

    assert any("uk:" in e for e in result.errors)
    assert len(result.records) == 1
    assert result.records[0].source_job_id == "com:ok"


def test_salary_currency_by_host():
    def side_effect(url, **_kwargs):
        if "devitjobs.fr" in url:
            return _resp([_item("fr1")])
        return _resp([])

    mock_client = _mock_client(side_effect)
    with patch("app.collectors.devitjobs.httpx.AsyncClient", return_value=mock_client):
        with patch("app.collectors.devitjobs.get_settings") as gs:
            gs.return_value.devitjobs_hosts = "fr"
            with patch("app.collectors.devitjobs._resolve_hosts", return_value=["fr"]):
                result = asyncio.run(DevITJobsCollector().collect(None))

    assert result.records[0].salary_text == "50000-60000 EUR/year"
