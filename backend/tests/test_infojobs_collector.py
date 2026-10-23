"""InfoJobs collector: fail-closed credentials, search params, mocked collect."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from app.collectors.base import MISSING_QUERY
from app.collectors.infojobs import (
    InfoJobsCollector,
    SEARCH_URL,
    build_search_params,
)
from app.core.config import get_settings


def _mock_client(resp: MagicMock) -> AsyncMock:
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=resp)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    return mock_client


def test_build_search_params_keyword_and_pagination():
    params = build_search_params("java developer", page=2, max_results=30, country="italia")
    assert params["q"] == "java developer"
    assert params["page"] == 2
    assert params["maxResults"] == 30
    assert params["country"] == "italia"
    assert params["order"] == "relevancia-desc"


def test_infojobs_fails_closed_without_keys(monkeypatch):
    monkeypatch.setenv("INFOJOBS_CLIENT_ID", "")
    monkeypatch.setenv("INFOJOBS_CLIENT_SECRET", "")
    get_settings.cache_clear()
    result = asyncio.run(InfoJobsCollector().collect("developer"))
    assert result.records == []
    assert result.pages_scanned == 0
    assert any("INFOJOBS_CLIENT_ID" in e for e in result.errors)


def test_infojobs_blank_query_missing_query():
    result = asyncio.run(InfoJobsCollector().collect(""))
    assert result.records == []
    assert result.errors == [MISSING_QUERY]


def test_infojobs_mock_success(monkeypatch):
    monkeypatch.setenv("INFOJOBS_CLIENT_ID", "test-client-id")
    monkeypatch.setenv("INFOJOBS_CLIENT_SECRET", "test-client-secret")
    monkeypatch.setenv("INFOJOBS_COUNTRY", "italia")
    get_settings.cache_clear()

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = {
        "currentPage": 1,
        "totalPages": 1,
        "offers": [
            {
                "id": "abc123",
                "title": "Java Developer",
                "link": "https://www.infojobs.net/oferta-java",
                "city": "Milano",
                "province": {"id": 1, "value": "Milano"},
                "published": "2026-03-01T12:00:00Z",
                "author": {"name": "TechCo"},
                "contractType": {"value": "Indefinido"},
                "category": {"value": "Informática"},
                "requirementMin": "Java experience",
            }
        ],
    }
    mock_client = _mock_client(mock_resp)

    with patch(
        "app.collectors.infojobs.httpx.AsyncClient", return_value=mock_client
    ) as client_cls:
        result = asyncio.run(InfoJobsCollector().collect("java OR python"))

    assert result.errors == []
    assert len(result.records) == 1
    job = result.records[0]
    assert job.source_job_id == "abc123"
    assert job.title == "Java Developer"
    assert job.company == "TechCo"
    assert "Informática" in job.tags
    init_kwargs = client_cls.call_args.kwargs
    assert init_kwargs.get("auth") == ("test-client-id", "test-client-secret")
    assert mock_client.get.await_args.args[0] == SEARCH_URL
    params = mock_client.get.await_args.kwargs.get("params") or {}
    assert params.get("q") == "java"
    assert params.get("country") == "italia"
    assert params.get("page") == 1


def test_infojobs_401_auth_failed(monkeypatch):
    monkeypatch.setenv("INFOJOBS_CLIENT_ID", "bad-id")
    monkeypatch.setenv("INFOJOBS_CLIENT_SECRET", "bad-secret")
    get_settings.cache_clear()

    mock_resp = MagicMock()
    mock_resp.status_code = 401
    mock_client = _mock_client(mock_resp)

    with patch("app.collectors.infojobs.httpx.AsyncClient", return_value=mock_client):
        result = asyncio.run(InfoJobsCollector().collect("developer"))

    assert result.records == []
    assert result.pages_scanned == 1
    assert any("InfoJobs auth failed HTTP 401" in e for e in result.errors)
