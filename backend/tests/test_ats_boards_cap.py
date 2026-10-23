from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.collectors.ats_boards import (
    MAX_PER_TENANT,
    GreenhouseCollector,
    PersonioCollector,
    _personio_job_url,
)


def test_max_per_tenant_bound():
    assert MAX_PER_TENANT == 40
    assert GreenhouseCollector.source_key == "greenhouse"
    assert PersonioCollector.source_key == "personio"
    assert _personio_job_url("tado", 1) == "https://tado.jobs.personio.de/job/1?language=en"


@pytest.mark.asyncio
async def test_personio_collect_maps_listing_json():
    payload = [{"id": 100, "name": "Engineer", "keywords": "python", "office": "Berlin"}]
    mock_resp = AsyncMock()
    mock_resp.raise_for_status = lambda: None
    mock_resp.json = lambda: payload
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_resp)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    with patch("app.collectors.ats_boards.get_settings") as mock_settings:
        mock_settings.return_value.personio_companies = "demo-co"
        with patch("app.collectors.ats_boards.httpx.AsyncClient", return_value=mock_client):
            result = await PersonioCollector().collect()
    assert len(result.records) == 1
    assert result.records[0].source_job_id == "demo-co:100"
