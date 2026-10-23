"""Findwork.dev collector: fail-closed key, missing_query, mock success, 401."""
from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from app.collectors.base import MISSING_QUERY
from app.collectors.findwork import FindworkCollector
from app.core.config import get_settings


def _mock_client(resp: MagicMock) -> AsyncMock:
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=resp)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    return mock_client


def test_findwork_fails_closed_without_key(monkeypatch):
    monkeypatch.setenv("FINDWORK_API_KEY", "")
    get_settings.cache_clear()
    result = asyncio.run(FindworkCollector().collect("python"))
    assert result.records == []
    assert result.pages_scanned == 0
    assert any("FINDWORK_API_KEY is required" in e for e in result.errors)


def test_findwork_blank_query_missing_query():
    result = asyncio.run(FindworkCollector().collect(""))
    assert result.records == []
    assert result.pages_scanned == 0
    assert result.errors == [MISSING_QUERY]


def test_findwork_mock_success(monkeypatch):
    monkeypatch.setenv("FINDWORK_API_KEY", "test-token")
    monkeypatch.setenv("FINDWORK_LOCATION", "remote")
    get_settings.cache_clear()

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = {
        "count": 1,
        "next": None,
        "previous": None,
        "results": [
            {
                "id": 42,
                "title": "Python Engineer",
                "company_name": "Acme",
                "location": "Remote",
                "remote": True,
                "pub_date": "2026-03-01T12:00:00Z",
                "url": "https://findwork.dev/jobs/42/",
                "description": "Build APIs",
                "keywords": ["python", "django"],
            }
        ],
    }
    mock_client = _mock_client(mock_resp)

    with patch(
        "app.collectors.findwork.httpx.AsyncClient", return_value=mock_client
    ) as client_cls:
        result = asyncio.run(FindworkCollector().collect("python OR java"))

    assert result.errors == []
    assert len(result.records) == 1
    job = result.records[0]
    assert job.source_job_id == "42"
    assert job.title == "Python Engineer"
    assert job.company == "Acme"
    assert job.remote_hint is True
    assert "python" in job.tags
    init_kwargs = client_cls.call_args.kwargs
    assert init_kwargs.get("headers", {}).get("Authorization") == "Token test-token"
    params = mock_client.get.await_args.kwargs.get("params") or {}
    assert params.get("search") == "python"
    assert params.get("location") == "remote"
    assert params.get("page") == 1
    assert mock_client.get.await_args.args[0] == "https://findwork.dev/api/jobs/"


def test_findwork_401_auth_failed(monkeypatch):
    monkeypatch.setenv("FINDWORK_API_KEY", "bad-token")
    monkeypatch.setenv("FINDWORK_LOCATION", "")
    get_settings.cache_clear()

    mock_resp = MagicMock()
    mock_resp.status_code = 401
    mock_client = _mock_client(mock_resp)

    with patch("app.collectors.findwork.httpx.AsyncClient", return_value=mock_client):
        result = asyncio.run(FindworkCollector().collect("python"))

    assert result.records == []
    assert result.pages_scanned == 1
    assert any("Findwork auth failed HTTP 401" in e for e in result.errors)
