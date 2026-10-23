"""Reed collector: RSS (free ACTIVE) vs optional JSON API when REED_API_KEY is set."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from app.collectors.reed import API_URL, RSS_URL, ReedCollector
from app.core.config import get_settings

RSS_FIXTURE = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
  <item>
    <title>Java Developer</title>
    <link>http://www.reed.co.uk/jobs/java-developer/12345</link>
    <guid>12345</guid>
    <description>Salary : £45,000 - £55,000</description>
  </item>
</channel></rss>""".encode()


def _mock_http_client(*, get_handler):
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(side_effect=get_handler)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    return mock_client


def test_reed_rss_mocked_without_api_key(monkeypatch):
    monkeypatch.setenv("REED_API_KEY", "")
    get_settings.cache_clear()

    async def fake_get(url, params=None):
        assert url == RSS_URL
        assert params == {"keywords": "java"}
        resp = MagicMock()
        resp.status_code = 200
        resp.raise_for_status = MagicMock()
        resp.content = RSS_FIXTURE
        return resp

    mock_client = _mock_http_client(get_handler=fake_get)
    with patch("app.collectors.reed.httpx.AsyncClient", return_value=mock_client):
        result = asyncio.run(ReedCollector().collect("java"))

    assert result.errors == []
    assert len(result.records) == 1
    job = result.records[0]
    assert job.source_job_id == "12345"
    assert job.url.startswith("https://www.reed.co.uk/")
    assert job.location == "UK"
    assert job.raw.get("mode") == "rss"
    assert job.salary_text is not None


def test_reed_rss_blank_query_no_keywords_param(monkeypatch):
    monkeypatch.setenv("REED_API_KEY", "")
    get_settings.cache_clear()

    async def fake_get(url, params=None):
        assert url == RSS_URL
        assert params is None
        resp = MagicMock()
        resp.status_code = 200
        resp.raise_for_status = MagicMock()
        resp.content = RSS_FIXTURE
        return resp

    mock_client = _mock_http_client(get_handler=fake_get)
    with patch("app.collectors.reed.httpx.AsyncClient", return_value=mock_client):
        result = asyncio.run(ReedCollector().collect(""))

    assert result.errors == []
    assert len(result.records) == 1


def test_reed_api_mocked_with_key(monkeypatch):
    monkeypatch.setenv("REED_API_KEY", "reed-test-key")
    get_settings.cache_clear()

    api_payload = {
        "results": [
            {
                "jobId": 4242,
                "jobTitle": "Senior Java Engineer",
                "employerName": "Acme Ltd",
                "locationName": "London",
                "county": "Greater London",
                "country": "UK",
                "jobUrl": "https://www.reed.co.uk/jobs/senior-java/4242",
                "jobDescription": "Build services",
                "date": "2026-01-15T12:00:00Z",
                "minimumSalary": 50000,
                "maximumSalary": 70000,
                "currency": "GBP",
                "contractType": "permanent",
            }
        ]
    }

    async def fake_get(url, params=None, auth=None, headers=None):
        assert url == API_URL
        assert auth == ("reed-test-key", "")
        assert params["keywords"] == "python developer"
        assert params["resultsToTake"] == 50
        resp = MagicMock()
        resp.status_code = 200
        resp.raise_for_status = MagicMock()
        resp.json.return_value = api_payload
        return resp

    mock_client = _mock_http_client(get_handler=fake_get)
    with patch("app.collectors.reed.httpx.AsyncClient", return_value=mock_client):
        result = asyncio.run(ReedCollector().collect("python developer"))

    assert result.errors == []
    assert len(result.records) == 1
    job = result.records[0]
    assert job.source_job_id == "4242"
    assert job.company == "Acme Ltd"
    assert job.job_type == "permanent"
    assert "50000" in (job.salary_text or "")
    assert job.raw.get("mode") == "api"
    assert "London" in (job.location or "")


def test_reed_api_missing_query_with_key(monkeypatch):
    monkeypatch.setenv("REED_API_KEY", "reed-test-key")
    get_settings.cache_clear()

    with patch("app.collectors.reed.httpx.AsyncClient") as client_cls:
        result = asyncio.run(ReedCollector().collect(""))
        client_cls.assert_not_called()

    assert result.records == []
    assert result.errors == ["missing_query"]


def test_reed_api_auth_failure(monkeypatch):
    monkeypatch.setenv("REED_API_KEY", "bad-key")
    get_settings.cache_clear()

    async def fake_get(url, params=None, auth=None, headers=None):  # noqa: ARG001
        resp = MagicMock()
        resp.status_code = 401
        return resp

    mock_client = _mock_http_client(get_handler=fake_get)
    with patch("app.collectors.reed.httpx.AsyncClient", return_value=mock_client):
        result = asyncio.run(ReedCollector().collect("java"))

    assert result.records == []
    assert any("auth failed" in e.lower() for e in result.errors)
