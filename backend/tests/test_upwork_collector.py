from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.collectors.upwork import UpworkCollector, _parse_node, _salary_text


def test_upwork_constants():
    assert UpworkCollector.source_key == "upwork"
    assert UpworkCollector.collection_mode == "search"


def test_helpers():
    assert _salary_text({"amount": {"displayValue": "$50", "currency": "USD"}}) == "USD $50"
    job = _parse_node(
        {
            "id": "abc",
            "ciphertext": "~0123",
            "title": "Build a React app",
            "description": "Need SPA",
            "createdDateTime": "2024-01-01T00:00:00Z",
            "skills": [{"name": "React"}],
        }
    )
    assert job is not None
    assert job.source_job_id == "abc"
    assert "upwork.com" in job.url
    assert "React" in job.tags


@pytest.mark.asyncio
async def test_upwork_requires_token():
    with patch("app.collectors.upwork.get_settings") as mock_settings:
        mock_settings.return_value.upwork_oauth_token = ""
        mock_settings.return_value.upwork_tenant_id = ""
        result = await UpworkCollector().collect("python")
    assert result.records == []
    assert any("required" in e.lower() for e in result.errors)


@pytest.mark.asyncio
async def test_upwork_maps_edges():
    payload = {
        "data": {
            "marketplaceJobPostingsSearch": {
                "totalCount": 1,
                "edges": [
                    {
                        "node": {
                            "id": "1",
                            "ciphertext": "~abc",
                            "title": "Python ETL",
                            "description": "Airflow",
                            "createdDateTime": "2024-06-01T12:00:00Z",
                        }
                    }
                ],
            }
        }
    }
    mock_resp = AsyncMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status = lambda: None
    mock_resp.json = lambda: payload
    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_resp)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    with patch("app.collectors.upwork.get_settings") as mock_settings:
        mock_settings.return_value.upwork_oauth_token = "tok"
        mock_settings.return_value.upwork_tenant_id = "org-1"
        with patch("app.collectors.upwork.httpx.AsyncClient", return_value=mock_client):
            result = await UpworkCollector().collect("python")
    assert len(result.records) == 1
    assert result.records[0].title == "Python ETL"
    mock_client.post.assert_awaited()
