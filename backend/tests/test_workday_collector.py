from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.collectors.workday import (
    MAX_PER_TENANT,
    WorkdayCollector,
    _job_id,
    _job_url,
    _remote_hint,
    _split_tenants,
)


def test_workday_constants():
    assert MAX_PER_TENANT == 40
    assert WorkdayCollector.source_key == "workday"
    assert WorkdayCollector.collection_mode == "dump"


def test_split_tenants():
    assert _split_tenants("nvidia:wd5:NVIDIAExternalCareerSite") == [
        ("nvidia", "wd5", "NVIDIAExternalCareerSite")
    ]
    assert _split_tenants("intel:1:External") == [("intel", "wd1", "External")]
    assert _split_tenants("bad,also:bad") == []


def test_helpers():
    assert _job_id("nvidia", {"bulletFields": ["JR2010334"], "externalPath": "/job/x"}) == (
        "nvidia:JR2010334"
    )
    assert _job_url("nvidia", "wd5", "NVIDIAExternalCareerSite", "/job/US/x_JR1") == (
        "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite/job/US/x_JR1"
    )
    assert _remote_hint({"locationsText": "Remote - US"}) is True
    assert _remote_hint({"locationsText": "Santa Clara, CA"}) is None


@pytest.mark.asyncio
async def test_workday_collect_maps_cxs():
    payload = {
        "total": 1,
        "jobPostings": [
            {
                "title": "Senior SDE",
                "externalPath": "/job/US-CA-Santa-Clara/Senior-SDE_JR2010334",
                "locationsText": "US, CA, Santa Clara",
                "postedOn": "Posted Today",
                "bulletFields": ["JR2010334"],
            }
        ],
    }
    mock_resp = AsyncMock()
    mock_resp.raise_for_status = lambda: None
    mock_resp.json = lambda: payload
    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_resp)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    with patch("app.collectors.workday.get_settings") as mock_settings:
        mock_settings.return_value.workday_tenants = "nvidia:wd5:NVIDIAExternalCareerSite"
        with patch("app.collectors.workday.httpx.AsyncClient", return_value=mock_client):
            result = await WorkdayCollector().collect()
    assert len(result.records) == 1
    rec = result.records[0]
    assert rec.source_job_id == "nvidia:JR2010334"
    assert rec.company == "Nvidia"
    assert "Santa Clara" in (rec.location or "")
    assert "NVIDIAExternalCareerSite" in rec.url
    mock_client.post.assert_called()


@pytest.mark.asyncio
async def test_workday_empty_tenants():
    with patch("app.collectors.workday.get_settings") as mock_settings:
        mock_settings.return_value.workday_tenants = ""
        result = await WorkdayCollector().collect()
    assert result.records == []
    assert result.errors == ["WORKDAY_TENANTS empty"]
