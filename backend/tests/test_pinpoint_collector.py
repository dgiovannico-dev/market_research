from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.collectors.pinpoint import (
    MAX_PER_TENANT,
    PinpointCollector,
    _location,
    _remote_hint,
    _salary_text,
)


def test_pinpoint_constants():
    assert MAX_PER_TENANT == 40
    assert PinpointCollector.source_key == "pinpoint"
    assert PinpointCollector.collection_mode == "dump"


def test_location_and_salary_helpers():
    assert _location({"location": {"name": "London", "city": "l"}}) == "London"
    assert _location({"location": {"city": "l", "province": "l"}}) is None
    assert _salary_text({"compensation": "£41,500 - £55,000 / year"}) == "£41,500 - £55,000 / year"
    assert _remote_hint({"workplace_type": "remote"}) is True
    assert _remote_hint({"workplace_type": "hybrid"}) is None


@pytest.mark.asyncio
async def test_pinpoint_collect_maps_postings():
    payload = {
        "data": [
            {
                "id": "223214",
                "title": "Data Engineer",
                "url": "https://made-tech.pinpointhq.com/en/postings/873e31d7",
                "description": "<p>Build pipelines</p>",
                "location": {"name": "Any UK Office Hub", "city": "l"},
                "workplace_type": "hybrid",
                "workplace_type_text": "Hybrid",
                "employment_type_text": "Permanent - Full Time",
                "compensation": "£41,500 - £55,000 / year",
                "compensation_minimum": 41500.0,
                "compensation_maximum": 55000.0,
                "compensation_currency": "GBP",
                "job": {"department": {"name": "Technology"}},
            }
        ]
    }
    mock_resp = AsyncMock()
    mock_resp.raise_for_status = lambda: None
    mock_resp.json = lambda: payload
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_resp)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    with patch("app.collectors.pinpoint.get_settings") as mock_settings:
        mock_settings.return_value.pinpoint_subdomains = "made-tech"
        with patch("app.collectors.pinpoint.httpx.AsyncClient", return_value=mock_client):
            result = await PinpointCollector().collect()
    assert len(result.records) == 1
    rec = result.records[0]
    assert rec.source_job_id == "made-tech:223214"
    assert rec.salary_text and "41,500" in rec.salary_text
    assert "Technology" in rec.tags
    assert rec.remote_hint is None


@pytest.mark.asyncio
async def test_pinpoint_empty_subdomains():
    with patch("app.collectors.pinpoint.get_settings") as mock_settings:
        mock_settings.return_value.pinpoint_subdomains = ""
        result = await PinpointCollector().collect()
    assert result.records == []
    assert result.errors == ["PINPOINT_SUBDOMAINS empty"]
