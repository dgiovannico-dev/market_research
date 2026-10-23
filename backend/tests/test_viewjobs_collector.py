"""ViewJobs AU collector — mocked MCP (no network)."""

from __future__ import annotations

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

from app.collectors.viewjobs import MCP_URL, ViewJobsCollector

SAMPLE_JOB = {
    "id": "abc-123",
    "title": "Python Developer",
    "employer": "Tech Co",
    "location": "Sydney, NSW",
    "work_type": "full-time",
    "pay": None,
    "posted_at": "2026-10-14T23:49:35.833Z",
    "url": "https://www.viewjobs.com.au/listing/abc-123?utm_source=other",
}


def _sse(jobs: list[dict]) -> str:
    payload = {
        "result": {
            "structuredContent": {
                "query": "python",
                "jobs": jobs,
            }
        }
    }
    return f"event: message\ndata: {json.dumps(payload)}\n\n"


def _mock_client(body: str = _sse([SAMPLE_JOB])):
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.text = body
    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_resp)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    return mock_client


def test_collect_maps_job():
    mock_client = _mock_client()
    with patch("app.collectors.viewjobs.httpx.AsyncClient", return_value=mock_client):
        result = asyncio.run(ViewJobsCollector().collect("python"))

    assert result.errors == []
    assert len(result.records) >= 1
    job = result.records[0]
    assert job.source_job_id == "abc-123"
    assert job.url.endswith("/listing/abc-123")
    assert job.company == "Tech Co"
    assert "Australia" in (job.location or "")
    assert job.raw.get("country") == "AU"
    mock_client.post.assert_awaited()
    call = mock_client.post.await_args
    assert call.args[0] == MCP_URL
    assert call.kwargs["json"]["params"]["name"] == "search_jobs"


def test_collect_blank_fails_closed():
    """Search-mode must not fan out inventing queries (ADR-007)."""
    from app.collectors.base import MISSING_QUERY

    result = asyncio.run(ViewJobsCollector().collect(None))
    assert result.records == []
    assert any(MISSING_QUERY in e for e in result.errors)


def test_registered():
    from app.collectors.registry import COLLECTOR_GEO, COLLECTORS

    assert "viewjobs" in COLLECTORS
    assert COLLECTORS["viewjobs"].collection_mode == "search"
    assert COLLECTOR_GEO["viewjobs"] == frozenset({"AU"})
