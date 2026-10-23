from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.collectors.bamboohr import MAX_PER_TENANT, BambooHRCollector, _location, _remote_hint


def test_bamboohr_constants():
    assert MAX_PER_TENANT == 40
    assert BambooHRCollector.source_key == "bamboohr"
    assert BambooHRCollector.collection_mode == "dump"


def test_helpers():
    assert _location({"location": {"city": "Austin", "state": "TX"}}) == "Austin, TX"
    assert _remote_hint({"isRemote": True}) is True
    assert _remote_hint({"locationType": "Hybrid"}) is None


@pytest.mark.asyncio
async def test_bamboohr_collect_maps_list_and_detail():
    list_payload = {
        "result": [
            {
                "id": 42,
                "jobOpeningName": "Platform Engineer",
                "departmentLabel": "Engineering",
                "employmentType": "Full-Time",
                "location": {"city": "Austin", "state": "TX"},
                "isRemote": False,
            }
        ]
    }
    detail_payload = {
        "result": {
            "jobOpening": {
                "description": "<p>Ship infra</p>",
                "jobOpeningShareUrl": "https://acme.bamboohr.com/careers/42",
                "datePosted": "2026-10-01T12:00:00Z",
                "compensation": "$120k–$150k",
                "location": {"city": "Austin", "state": "TX", "addressCountry": "US"},
                "isRemote": False,
            }
        }
    }

    async def _get(url, *args, **kwargs):
        resp = AsyncMock()
        resp.status_code = 200
        resp.raise_for_status = lambda: None
        if url.endswith("/list"):
            resp.json = lambda: list_payload
        else:
            resp.json = lambda: detail_payload
        return resp

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(side_effect=_get)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    with patch("app.collectors.bamboohr.get_settings") as mock_settings:
        mock_settings.return_value.bamboohr_companies = "acme"
        with patch("app.collectors.bamboohr.httpx.AsyncClient", return_value=mock_client):
            result = await BambooHRCollector().collect()
    assert len(result.records) == 1
    rec = result.records[0]
    assert rec.source_job_id == "acme:42"
    assert rec.salary_text and "120k" in rec.salary_text
    assert "Ship infra" in (rec.description or "")


@pytest.mark.asyncio
async def test_bamboohr_empty_companies():
    with patch("app.collectors.bamboohr.get_settings") as mock_settings:
        mock_settings.return_value.bamboohr_companies = ""
        result = await BambooHRCollector().collect()
    assert result.records == []
    assert len(result.errors) == 1
    assert "BAMBOOHR_COMPANIES empty" in result.errors[0]
    assert "ATS_TENANTS" in result.errors[0]


@pytest.mark.asyncio
async def test_bamboohr_redirect_treated_as_error():
    mock_resp = AsyncMock()
    mock_resp.status_code = 302
    mock_resp.headers = {"location": "https://www.bamboohr.com/"}
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_resp)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    with patch("app.collectors.bamboohr.get_settings") as mock_settings:
        mock_settings.return_value.bamboohr_companies = "fake"
        with patch("app.collectors.bamboohr.httpx.AsyncClient", return_value=mock_client):
            result = await BambooHRCollector().collect()
    assert result.records == []
    assert any("redirect" in e for e in result.errors)


@pytest.mark.asyncio
async def test_bamboohr_503_and_empty_list():
    async def _get(url, *args, **kwargs):
        resp = AsyncMock()
        if "blocked" in url:
            resp.status_code = 503
        else:
            resp.status_code = 200
            resp.raise_for_status = lambda: None
            resp.json = lambda: {"result": []}
        return resp

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(side_effect=_get)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    with patch("app.collectors.bamboohr.get_settings") as mock_settings:
        mock_settings.return_value.bamboohr_companies = "blocked,emptyco"
        with patch("app.collectors.bamboohr.httpx.AsyncClient", return_value=mock_client):
            result = await BambooHRCollector().collect()
    assert result.records == []
    assert any("503" in e and "egress" in e for e in result.errors)
    assert any("empty careers list" in e for e in result.errors)


@pytest.mark.asyncio
async def test_bamboohr_all_503_summary():
    mock_resp = AsyncMock()
    mock_resp.status_code = 503
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_resp)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    with patch("app.collectors.bamboohr.get_settings") as mock_settings:
        mock_settings.return_value.bamboohr_companies = "a,b"
        with patch("app.collectors.bamboohr.httpx.AsyncClient", return_value=mock_client):
            result = await BambooHRCollector().collect()
    assert result.records == []
    assert sum(1 for e in result.errors if e.startswith(("a:", "b:")) and "503" in e) == 2
    assert any(e.startswith("all slugs HTTP 503") for e in result.errors)
