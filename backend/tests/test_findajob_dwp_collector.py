from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.collectors.findajob_dwp import FindAJobDwpCollector, _as_list, _parse_item


def test_findajob_dwp_constants():
    assert FindAJobDwpCollector.source_key == "findajob_dwp"
    assert FindAJobDwpCollector.collection_mode == "search"


def test_helpers():
    assert len(_as_list({"results": [{"id": 1}]})) == 1
    job = _parse_item(
        {
            "id": "abc",
            "title": "Software Engineer",
            "employer": "Acme",
            "location": "London",
            "url": "https://findajob.dwp.gov.uk/details/abc",
        }
    )
    assert job is not None
    assert job.source_job_id == "abc"
    assert job.company == "Acme"


@pytest.mark.asyncio
async def test_findajob_dwp_requires_keys():
    with patch("app.collectors.findajob_dwp.get_settings") as mock_settings:
        mock_settings.return_value.findajob_dwp_api_id = ""
        mock_settings.return_value.findajob_dwp_api_key = ""
        result = await FindAJobDwpCollector().collect("software")
    assert result.records == []
    assert any("required" in e.lower() for e in result.errors)


@pytest.mark.asyncio
async def test_findajob_dwp_maps_results():
    payload = {
        "results": [
            {
                "id": "42",
                "title": "Data Analyst",
                "employer": "Gov Dept",
                "location": "Manchester",
                "url": "https://findajob.dwp.gov.uk/details/42",
                "description": "Analyse data",
            }
        ]
    }
    mock_resp = AsyncMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status = lambda: None
    mock_resp.headers = {"content-type": "application/json"}
    mock_resp.text = "{}"
    mock_resp.json = lambda: payload
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_resp)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    with patch("app.collectors.findajob_dwp.get_settings") as mock_settings:
        mock_settings.return_value.findajob_dwp_api_id = "id"
        mock_settings.return_value.findajob_dwp_api_key = "key"
        mock_settings.return_value.findajob_dwp_location = "London"
        with patch("app.collectors.findajob_dwp.httpx.AsyncClient", return_value=mock_client):
            result = await FindAJobDwpCollector().collect("analyst")
    assert len(result.records) == 1
    assert result.records[0].source_job_id == "42"
    assert "Manchester" in (result.records[0].location or "")
