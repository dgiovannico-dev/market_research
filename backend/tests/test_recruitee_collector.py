from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.collectors.recruitee import MAX_PER_TENANT, RecruiteeCollector, _parse_published, _remote_hint


def test_recruitee_constants():
    assert MAX_PER_TENANT == 40
    assert RecruiteeCollector.source_key == "recruitee"
    assert RecruiteeCollector.collection_mode == "dump"


def test_parse_published_utc_space():
    dt = _parse_published("2026-10-15 09:31:36 UTC")
    assert dt.year == 2026
    assert dt.month == 10
    assert dt.day == 15
    assert dt.tzinfo is not None


def test_remote_hint():
    assert _remote_hint({"remote": True}) is True
    assert _remote_hint({"on_site": True, "remote": False}) is False
    assert _remote_hint({"hybrid": True, "remote": False, "on_site": False}) is None


@pytest.mark.asyncio
async def test_recruitee_collect_maps_offers():
    payload = {
        "offers": [
            {
                "id": 2783543,
                "slug": "head-of-product-6",
                "title": "Head of Product",
                "company_name": "bunq",
                "careers_url": "https://careers.bunq.com/o/head-of-product-6",
                "city": "Amsterdam",
                "country": "Netherlands",
                "department": "Product",
                "published_at": "2026-10-15 09:31:36 UTC",
                "description": "<p>Lead product</p>",
                "remote": False,
                "hybrid": True,
                "on_site": False,
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
    with patch("app.collectors.recruitee.get_settings") as mock_settings:
        mock_settings.return_value.recruitee_slugs = "bunq"
        with patch("app.collectors.recruitee.httpx.AsyncClient", return_value=mock_client):
            result = await RecruiteeCollector().collect()
    assert len(result.records) == 1
    rec = result.records[0]
    assert rec.source_job_id == "bunq:2783543"
    assert rec.url.startswith("https://careers.bunq.com/")
    assert rec.location == "Amsterdam, Netherlands"
    assert rec.tags == ["Product"]
    assert rec.remote_hint is None


@pytest.mark.asyncio
async def test_recruitee_empty_slugs():
    with patch("app.collectors.recruitee.get_settings") as mock_settings:
        mock_settings.return_value.recruitee_slugs = ""
        result = await RecruiteeCollector().collect()
    assert result.records == []
    assert result.errors == ["RECRUITEE_SLUGS empty"]
