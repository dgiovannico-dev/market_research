"""Dev Global Jobs collector — mocked API (no network)."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from app.collectors.devglobaljobs import API_URL, DevGlobalJobsCollector

SAMPLE = {
    "meta": {"total": 1, "limit": 50, "offset": 0, "hasMore": False},
    "jobs": [
        {
            "id": 42,
            "title": "Security Engineer",
            "organization": "Stripe",
            "location": "Luxembourg",
            "country": "LU",
            "category": "technology",
            "skillCategory": "technology",
            "jobType": "Full-time",
            "salary": None,
            "descriptionExcerpt": "Build secure systems.",
            "postedAt": "2026-10-19T15:41:23.796Z",
            "url": "https://devglobaljobs.com/jobs/detail/42",
        }
    ],
}


def _mock_client(body: dict = SAMPLE):
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json = MagicMock(return_value=body)
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_resp)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    return mock_client


def test_collect_maps_job():
    mock_client = _mock_client()
    with (
        patch(
            "app.collectors.devglobaljobs.get_settings",
            return_value=MagicMock(devglobaljobs_countries="lu"),
        ),
        patch(
            "app.collectors.devglobaljobs.httpx.AsyncClient", return_value=mock_client
        ),
    ):
        result = asyncio.run(DevGlobalJobsCollector().collect())

    assert result.errors == []
    assert len(result.records) == 1
    job = result.records[0]
    assert job.source_job_id == "42"
    assert job.url.endswith("/42")
    assert job.title == "Security Engineer"
    assert job.company == "Stripe"
    assert "technology" in job.tags
    assert job.raw.get("attribution") == "Dev Global Jobs"
    assert job.raw.get("country_code") == "LU"
    assert job.raw.get("country") == "LU"
    mock_client.get.assert_awaited()
    call = mock_client.get.await_args
    assert call.args[0] == API_URL
    assert call.kwargs["params"]["country"] == "lu"


def test_request_iso_wins_over_payload_country_name():
    """BG request must tag ISO2 even when API returns a non-ISO country label."""
    body = {
        "meta": {"total": 1, "limit": 50, "offset": 0, "hasMore": False},
        "jobs": [
            {
                **SAMPLE["jobs"][0],
                "id": 99,
                "country": "Bulgaria",
                "location": "Sofia",
                "url": "https://devglobaljobs.com/jobs/detail/99",
            }
        ],
    }
    mock_client = _mock_client(body)
    with (
        patch(
            "app.collectors.devglobaljobs.get_settings",
            return_value=MagicMock(devglobaljobs_countries="bg"),
        ),
        patch(
            "app.collectors.devglobaljobs.httpx.AsyncClient", return_value=mock_client
        ),
    ):
        result = asyncio.run(DevGlobalJobsCollector().collect())

    assert len(result.records) == 1
    assert result.records[0].raw.get("country_code") == "BG"
    assert result.records[0].raw.get("country") == "BG"
    assert result.records[0].raw.get("api_country") == "Bulgaria"


def test_collect_passes_search_query():
    mock_client = _mock_client()
    with (
        patch(
            "app.collectors.devglobaljobs.get_settings",
            return_value=MagicMock(devglobaljobs_countries="bg"),
        ),
        patch(
            "app.collectors.devglobaljobs.httpx.AsyncClient", return_value=mock_client
        ),
    ):
        result = asyncio.run(DevGlobalJobsCollector().collect("python OR java"))

    assert len(result.records) == 1
    params = mock_client.get.await_args.kwargs["params"]
    assert params["search"] == "python"
    assert params["country"] == "bg"


def test_registered():
    from app.collectors.registry import COLLECTORS, COLLECTOR_GEO

    assert "devglobaljobs" in COLLECTORS
    assert COLLECTORS["devglobaljobs"].collection_mode == "dump"
    assert "LU" in COLLECTOR_GEO["devglobaljobs"]
    assert "BG" in COLLECTOR_GEO["devglobaljobs"]
