"""Himalayas pubDate is a Unix epoch (int), not ISO-8601."""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from app.collectors.himalayas import HimalayasCollector


def test_himalayas_parses_epoch_pubdate(monkeypatch):
    monkeypatch.setenv("HIMALAYAS_PAGE_LIMIT", "40")
    payload = {
        "jobs": [
            {
                "title": "Senior Data Engineer",
                "guid": "https://himalayas.app/companies/x/jobs/y",
                "applicationLink": "https://himalayas.app/companies/x/jobs/y",
                "companyName": "Acme",
                "description": "Build pipelines",
                "pubDate": 1792532881,
                "categories": ["Engineering"],
                "employmentType": "full-time",
            }
        ],
        "nextCursor": None,
    }
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = payload

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_resp)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("app.collectors.himalayas.httpx.AsyncClient", return_value=mock_client):
        result = asyncio.run(HimalayasCollector().collect(None))

    assert result.errors == []
    assert len(result.records) == 1
    assert result.records[0].published_at == datetime.fromtimestamp(
        1792532881, tz=timezone.utc
    )
