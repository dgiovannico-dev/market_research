"""findmethatdamjob.nl collector — mocked API (no network)."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from app.collectors.base import MISSING_QUERY
from app.collectors.findmethatdamjob import (
    JOBS_URL,
    NL_LOCATION,
    FindMeThatDamJobCollector,
)

SAMPLE = [
    {
        "id": "abc123",
        "slug": "acme-senior-python-abc123",
        "title": "Senior Python Engineer",
        "apply_url": "https://example.com/careers/python",
        "location": "Amsterdam",
        "company_name": "Acme BV",
        "first_seen_at": "2026-10-20T10:00:00Z",
        "gist": "Backend role with Django.",
        "facts": {
            "seniority": "senior",
            "work_mode": "hybrid",
            "skills": ["Python", "Django"],
        },
    },
    {
        "id": "skip-me",
        "title": "No URL",
        "apply_url": "",
    },
]


def _mock_client(body: list = SAMPLE):
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json = MagicMock(return_value=body)
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_resp)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    return mock_client


def test_blank_query_fails_closed():
    result = asyncio.run(FindMeThatDamJobCollector().collect(None))
    assert result.records == []
    assert any(MISSING_QUERY in e for e in result.errors)


def test_collect_maps_job():
    mock_client = _mock_client()
    with patch(
        "app.collectors.findmethatdamjob.httpx.AsyncClient", return_value=mock_client
    ):
        result = asyncio.run(FindMeThatDamJobCollector().collect("python"))

    assert result.errors == []
    assert len(result.records) == 1
    job = result.records[0]
    assert job.source_job_id == "abc123"
    assert job.url == "https://example.com/careers/python"
    assert job.title == "Senior Python Engineer"
    assert job.company == "Acme BV"
    assert job.remote_hint == "hybrid"
    assert "Python" in job.tags
    mock_client.get.assert_awaited_once()
    call = mock_client.get.await_args
    assert call.args[0] == JOBS_URL
    assert call.kwargs["params"] == {"location": NL_LOCATION}


def test_collect_query_filter():
    mock_client = _mock_client()
    with patch(
        "app.collectors.findmethatdamjob.httpx.AsyncClient", return_value=mock_client
    ):
        result = asyncio.run(FindMeThatDamJobCollector().collect("java"))

    assert result.records == []
    # Zero client-side hits is not an API error (avoids poisoning source.last_error).
    assert result.errors == []


def test_collect_focus_label_token_match():
    """Focus labels like 'cloud architect freelance' match on significant tokens."""
    body = [
        {
            "id": "c1",
            "title": "Cloud Platform Lead",
            "apply_url": "https://example.com/cloud",
            "company_name": "Dam BV",
            "location": "Amsterdam",
            "first_seen_at": "2026-10-20T10:00:00Z",
            "gist": "AWS and Kubernetes.",
            "facts": {"skills": ["AWS", "Cloud"]},
        }
    ]
    mock_client = _mock_client(body)
    with patch(
        "app.collectors.findmethatdamjob.httpx.AsyncClient", return_value=mock_client
    ):
        result = asyncio.run(
            FindMeThatDamJobCollector().collect("cloud architect freelance")
        )

    assert len(result.records) == 1
    assert result.records[0].source_job_id == "c1"
    assert result.errors == []


def test_collect_http_error():
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(side_effect=RuntimeError("timeout"))
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    with patch(
        "app.collectors.findmethatdamjob.httpx.AsyncClient", return_value=mock_client
    ):
        result = asyncio.run(FindMeThatDamJobCollector().collect("python"))

    assert result.records == []
    assert result.errors == ["timeout"]
