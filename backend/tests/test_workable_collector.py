from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.collectors.workable import MAX_PER_TENANT, WorkableCollector, _location, _parse_published


def test_workable_constants():
    assert MAX_PER_TENANT == 40
    assert WorkableCollector.source_key == "workable"
    assert WorkableCollector.collection_mode == "dump"


def test_helpers():
    assert _location({"city": "Paris", "country": "France"}) == "Paris, France"
    dt = _parse_published("2026-05-29")
    assert dt.year == 2026 and dt.month == 5 and dt.day == 29


@pytest.mark.asyncio
async def test_workable_collect_maps_widget():
    payload = {
        "name": "Hugging Face",
        "jobs": [
            {
                "title": "ML Engineer",
                "shortcode": "81B46579FE",
                "url": "https://apply.workable.com/j/81B46579FE",
                "city": "Paris",
                "country": "France",
                "telecommuting": True,
                "published_on": "2026-05-29",
                "department": "Open Source",
                "employment_type": "Full-time",
                "description": "<p>Build models</p>",
            }
        ],
    }
    mock_resp = AsyncMock()
    mock_resp.raise_for_status = lambda: None
    mock_resp.json = lambda: payload
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_resp)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    with patch("app.collectors.workable.get_settings") as mock_settings:
        mock_settings.return_value.workable_slugs = "huggingface"
        with patch("app.collectors.workable.httpx.AsyncClient", return_value=mock_client):
            result = await WorkableCollector().collect()
    assert len(result.records) == 1
    rec = result.records[0]
    assert rec.source_job_id == "huggingface:81B46579FE"
    assert rec.company == "Hugging Face"
    assert rec.remote_hint is True
    assert "Paris" in (rec.location or "")


@pytest.mark.asyncio
async def test_workable_empty_slugs():
    with patch("app.collectors.workable.get_settings") as mock_settings:
        mock_settings.return_value.workable_slugs = ""
        result = await WorkableCollector().collect()
    assert result.records == []
    assert result.errors == ["WORKABLE_SLUGS empty"]
