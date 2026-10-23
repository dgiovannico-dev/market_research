"""okemprego collector — mocked API (no network)."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from app.collectors.okemprego import API_URL, OkEmpregoCollector

SAMPLE = {
    "data": [
        {
            "id": "job-1",
            "slug": "senior-python-developer",
            "url": "https://www.okemprego.com/pt/empregos/senior-python-developer",
            "title": "Senior Python Developer",
            "description": "Build APIs with FastAPI.",
            "company": "Devoteam",
            "country": "PT",
            "category": "it-data",
            "remote": "hybrid",
            "hoursType": "full-time",
            "experienceLevel": "senior",
            "skills": ["Python", "FastAPI"],
            "city": "Lisboa",
            "postedAt": "2026-10-20T22:03:33.124Z",
            "salary": {"min": None, "max": None, "currency": None, "period": None},
        }
    ],
    "pagination": {"page": 1, "perPage": 50, "total": 1, "totalPages": 1},
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
            "app.collectors.okemprego.get_settings",
            return_value=MagicMock(okemprego_countries="pt"),
        ),
        patch("app.collectors.okemprego.httpx.AsyncClient", return_value=mock_client),
    ):
        result = asyncio.run(OkEmpregoCollector().collect())

    assert result.errors == []
    assert len(result.records) == 1
    job = result.records[0]
    assert job.source_job_id == "job-1"
    assert "okemprego.com" in job.url
    assert job.company == "Devoteam"
    assert job.raw.get("country") == "PT"
    assert "Python" in job.tags
    call = mock_client.get.await_args
    assert call.args[0] == API_URL
    assert call.kwargs["params"]["country"] == "PT"
    assert call.kwargs["params"]["category"] == "it-data"


def test_collect_passes_query():
    mock_client = _mock_client()
    with (
        patch(
            "app.collectors.okemprego.get_settings",
            return_value=MagicMock(okemprego_countries="pt"),
        ),
        patch("app.collectors.okemprego.httpx.AsyncClient", return_value=mock_client),
    ):
        asyncio.run(OkEmpregoCollector().collect("python OR java"))

    assert mock_client.get.await_args.kwargs["params"]["q"] == "python"


def test_registered():
    from app.collectors.registry import COLLECTOR_GEO, COLLECTORS

    assert "okemprego" in COLLECTORS
    assert COLLECTORS["okemprego"].collection_mode == "dump"
    assert "PT" in COLLECTOR_GEO["okemprego"]
