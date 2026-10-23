"""Unit tests for NAV pam-stilling-feed dump collector (mocked HTTP)."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from app.collectors.nav_stilling_feed import (
    FEED_URL,
    TOKEN_URL,
    NavStillingFeedCollector,
    _map_item,
)
from app.collectors.registry import COLLECTOR_GEO, COLLECTORS, get_collection_mode

SAMPLE_ACTIVE = {
    "id": "858f6336-9a71-4242-aea0-2f29f63a7c93",
    "url": "/api/v1/feedentry/858f6336-9a71-4242-aea0-2f29f63a7c93",
    "title": "Regnskapscontroller",
    "content_text": "Stillingsannonse",
    "date_modified": "2026-10-07T20:36:18.092934+02:00",
    "_feed_entry": {
        "uuid": "858f6336-9a71-4242-aea0-2f29f63a7c93",
        "status": "ACTIVE",
        "title": "Regnskapscontroller",
        "businessName": "Oslo kommune",
        "municipal": "OSLO",
        "sistEndret": "2026-10-07T20:36:18.092934+02:00",
    },
}

SAMPLE_INACTIVE = {
    "id": "aacf9c18-bcef-48c0-968e-238c5b88eff4",
    "url": "/api/v1/feedentry/aacf9c18-bcef-48c0-968e-238c5b88eff4",
    "title": "Sjåfør",
    "date_modified": "2023-06-14T12:21:40.222423+02:00",
    "_feed_entry": {
        "uuid": "aacf9c18-bcef-48c0-968e-238c5b88eff4",
        "status": "INACTIVE",
        "title": "Sjåfør",
        "businessName": "ARNESEN HVITEVARER AS",
        "municipal": "BERGEN",
        "sistEndret": "2023-06-14T12:21:40.222423+02:00",
    },
}

TOKEN_BODY = (
    "Current public token for Nav Job Vacancy Feed:\n"
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0In0.signature"
)


def test_nav_stilling_feed_registered_as_dump():
    assert "nav_stilling_feed" in COLLECTORS
    assert get_collection_mode(COLLECTORS["nav_stilling_feed"]) == "dump"
    assert COLLECTOR_GEO["nav_stilling_feed"] == frozenset({"NO"})


def test_map_item_active_only():
    job = _map_item(SAMPLE_ACTIVE)
    assert job is not None
    assert job.source_job_id == "858f6336-9a71-4242-aea0-2f29f63a7c93"
    assert job.company == "Oslo kommune"
    assert job.location == "OSLO, Norway"
    assert "arbeidsplassen.nav.no/stillinger/stilling/" in job.url
    assert job.published_at is not None
    assert job.published_at.tzinfo is not None
    assert job.published_at.year == 2026
    assert job.published_at.month == 10
    assert job.published_at.day == 7
    assert _map_item(SAMPLE_INACTIVE) is None


def _mock_response(payload: dict | str, *, text: str | None = None):
    resp = MagicMock()
    resp.raise_for_status = MagicMock()
    if isinstance(payload, dict):
        resp.json.return_value = payload
        resp.text = text or ""
    else:
        resp.json.return_value = {}
        resp.text = payload
    return resp


def test_collect_uses_token_and_filters_active():
    page1 = {
        "version": "1.0",
        "next_url": "/api/v1/feed/page-2",
        "items": [SAMPLE_INACTIVE, SAMPLE_ACTIVE],
    }
    page2_active = {
        **SAMPLE_ACTIVE,
        "id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        "_feed_entry": {
            **SAMPLE_ACTIVE["_feed_entry"],
            "uuid": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
            "title": "Python utvikler",
            "businessName": "Tech AS",
        },
        "title": "Python utvikler",
    }
    page2 = {"version": "1.0", "next_url": None, "items": [page2_active]}

    async def fake_get(url, headers=None):
        if url == TOKEN_URL or str(url).endswith("/api/publicToken"):
            return _mock_response(TOKEN_BODY)
        if url == FEED_URL or str(url).rstrip("/").endswith("/api/v1/feed"):
            assert headers and "Authorization" in headers
            assert "If-Modified-Since" in (headers or {})
            return _mock_response(page1)
        if "page-2" in str(url):
            return _mock_response(page2)
        raise AssertionError(f"unexpected url {url}")

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(side_effect=fake_get)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("app.collectors.nav_stilling_feed.httpx.AsyncClient", return_value=mock_client):
        result = asyncio.run(NavStillingFeedCollector().collect(None))

    assert result.errors == []
    assert result.dump_complete is False
    assert len(result.records) == 2
    assert result.pages_scanned == 2
    ids = {r.source_job_id for r in result.records}
    assert "858f6336-9a71-4242-aea0-2f29f63a7c93" in ids
    assert "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb" in ids


def test_collect_query_filters_title():
    page = {
        "version": "1.0",
        "next_url": None,
        "items": [
            SAMPLE_ACTIVE,
            {
                **SAMPLE_ACTIVE,
                "id": "cccccccc-cccc-cccc-cccc-cccccccccccc",
                "title": "Python utvikler Oslo",
                "_feed_entry": {
                    **SAMPLE_ACTIVE["_feed_entry"],
                    "uuid": "cccccccc-cccc-cccc-cccc-cccccccccccc",
                    "title": "Python utvikler Oslo",
                },
            },
        ],
    }

    async def fake_get(url, headers=None):
        if "publicToken" in str(url):
            return _mock_response(TOKEN_BODY)
        return _mock_response(page)

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(side_effect=fake_get)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("app.collectors.nav_stilling_feed.httpx.AsyncClient", return_value=mock_client):
        result = asyncio.run(NavStillingFeedCollector().collect("python"))

    assert result.errors == []
    assert len(result.records) == 1
    assert result.records[0].source_job_id == "cccccccc-cccc-cccc-cccc-cccccccccccc"
