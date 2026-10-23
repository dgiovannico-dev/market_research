from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.collectors.teamtailor import MAX_PER_TENANT, TeamtailorCollector, _job_id, _location_from_jobposting


def test_teamtailor_constants():
    assert MAX_PER_TENANT == 40
    assert TeamtailorCollector.source_key == "teamtailor"
    assert TeamtailorCollector.collection_mode == "dump"


def test_job_id_prefers_numeric_identifier():
    item = {
        "id": "uuid-1",
        "_jobposting": {"identifier": {"value": 12345}},
    }
    assert _job_id(item, "polestar.teamtailor.com") == "polestar.teamtailor.com:12345"


def test_location_from_jobposting():
    loc = _location_from_jobposting(
        {
            "jobLocation": [
                {
                    "address": {
                        "addressLocality": "Göteborg",
                        "addressCountry": "SE",
                        "addressRegion": "Nordics",
                    }
                }
            ]
        }
    )
    assert loc == "Göteborg, Nordics, SE"


@pytest.mark.asyncio
async def test_teamtailor_collect_maps_feed():
    payload = {
        "title": "Polestar",
        "items": [
            {
                "id": "a775edab",
                "title": "Engineer",
                "url": "https://polestar.teamtailor.com/jobs/1-engineer",
                "date_published": "2026-10-15T13:14:55+02:00",
                "content_html": "<p>Build cars</p>",
                "_jobposting": {
                    "identifier": {"value": 8551558},
                    "hiringOrganization": {"name": "Polestar"},
                    "jobLocation": [{"address": {"addressLocality": "Beesd", "addressCountry": "NL"}}],
                },
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
    with patch("app.collectors.teamtailor.get_settings") as mock_settings:
        mock_settings.return_value.teamtailor_hosts = "polestar.teamtailor.com"
        with patch("app.collectors.teamtailor.httpx.AsyncClient", return_value=mock_client):
            result = await TeamtailorCollector().collect()
    assert len(result.records) == 1
    rec = result.records[0]
    assert rec.source_job_id == "polestar.teamtailor.com:8551558"
    assert rec.company == "Polestar"
    assert rec.location == "Beesd, NL"
    assert "Build cars" in (rec.description or "")


@pytest.mark.asyncio
async def test_teamtailor_empty_hosts():
    with patch("app.collectors.teamtailor.get_settings") as mock_settings:
        mock_settings.return_value.teamtailor_hosts = ""
        result = await TeamtailorCollector().collect()
    assert result.records == []
    assert result.errors == ["TEAMTAILOR_HOSTS empty"]
