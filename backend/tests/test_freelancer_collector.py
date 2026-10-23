from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.collectors.freelancer import FreelancerCollector, _parse_item, _salary_text


def test_freelancer_constants():
    assert FreelancerCollector.source_key == "freelancer"
    assert FreelancerCollector.collection_mode == "search"


def test_helpers():
    assert _salary_text({"budget": {"minimum": 100, "maximum": 200}, "currency": {"code": "USD"}}) == (
        "USD 100-200"
    )
    job = _parse_item(
        {
            "id": 99,
            "title": "Build an API",
            "seo_url": "python/build-api",
            "preview_description": "Need Django",
            "time_updated": 1700000000,
            "jobs": [{"name": "Python"}],
        }
    )
    assert job is not None
    assert job.source_job_id == "99"
    assert "freelancer.com" in job.url
    assert "Python" in job.tags


@pytest.mark.asyncio
async def test_freelancer_requires_token():
    with patch("app.collectors.freelancer.get_settings") as mock_settings:
        mock_settings.return_value.freelancer_oauth_token = ""
        result = await FreelancerCollector().collect("python")
    assert result.records == []
    assert any("required" in e.lower() for e in result.errors)


@pytest.mark.asyncio
async def test_freelancer_maps_projects():
    payload = {
        "result": {
            "projects": [
                {
                    "id": 1,
                    "title": "React app",
                    "seo_url": "javascript/react-app",
                    "preview_description": "SPA",
                    "time_updated": 1700000000,
                }
            ]
        }
    }
    mock_resp = AsyncMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status = lambda: None
    mock_resp.json = lambda: payload
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_resp)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    with patch("app.collectors.freelancer.get_settings") as mock_settings:
        mock_settings.return_value.freelancer_oauth_token = "tok"
        mock_settings.return_value.freelancer_api_base = "https://www.freelancer.com/api"
        with patch("app.collectors.freelancer.httpx.AsyncClient", return_value=mock_client):
            result = await FreelancerCollector().collect("react")
    assert len(result.records) == 1
    assert result.records[0].title == "React app"
