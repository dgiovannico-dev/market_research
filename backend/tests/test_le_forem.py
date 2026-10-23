"""Unit tests for Le Forem ODWB open-data collector (mocked JSON)."""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from app.collectors.le_forem import LeForemCollector, _map_record
from app.collectors.registry import COLLECTOR_GEO, COLLECTORS, get_collection_mode


SAMPLE_RECORD = {
    "numerooffreforem": "2080441",
    "titreoffre": "Responsable qualité (H/F/X)",
    "lieuxtravaillocalite": ["NEUFCHÂTEAU"],
    "lieuxtravailregion": ["Belgique", "Province du Luxembourg", "RÉGION WALLONNE"],
    "typecontrat": "Durée indéterminée",
    "nomemployeur": "Itzu Jobs",
    "regimetravail": "Temps plein",
    "secteurs": ["Activités liées à l'emploi"],
    "url": "https://www.leforem.be/recherche-offres/offre-detail/2080441",
    "datedebutdiffusion": "2026-10-03",
    "metier": "Management et ingénierie qualité industrielle",
    "metiercodedimeco": "H1502",
}


def test_le_forem_registered_as_dump():
    assert "le_forem" in COLLECTORS
    assert get_collection_mode(COLLECTORS["le_forem"]) == "dump"
    assert COLLECTOR_GEO["le_forem"] == frozenset({"BE"})


def test_map_record_sets_belgium_location():
    job = _map_record(SAMPLE_RECORD)
    assert job is not None
    assert job.source_job_id == "2080441"
    assert "Belgium" in (job.location or "")
    assert job.company == "Itzu Jobs"
    assert job.published_at == datetime(2026, 10, 3, tzinfo=timezone.utc)
    assert job.job_type == "Durée indéterminée"
    assert "H1502" in job.tags


def test_collect_paginates_and_caps(monkeypatch):
    page1 = {
        "total_count": 250,
        "results": [
            {**SAMPLE_RECORD, "numerooffreforem": str(i), "titreoffre": f"Job {i}"}
            for i in range(100)
        ],
    }
    page2 = {
        "total_count": 250,
        "results": [
            {
                **SAMPLE_RECORD,
                "numerooffreforem": str(100 + i),
                "titreoffre": f"Job {100 + i}",
            }
            for i in range(100)
        ],
    }
    calls: list[dict] = []

    async def fake_get(url, params=None):
        calls.append(dict(params or {}))
        resp = MagicMock()
        resp.raise_for_status = MagicMock()
        offset = (params or {}).get("offset", 0)
        resp.json.return_value = page1 if offset == 0 else page2
        return resp

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(side_effect=fake_get)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("app.collectors.le_forem.httpx.AsyncClient", return_value=mock_client):
        result = asyncio.run(LeForemCollector().collect(None))

    assert result.errors == []
    assert len(result.records) == 200
    assert result.pages_scanned == 2
    assert calls[0]["limit"] == 100
    assert calls[0]["offset"] == 0
    assert calls[1]["offset"] == 100
    assert all(r.location and "Belgium" in r.location for r in result.records)


def test_collect_filters_query():
    payload = {
        "total_count": 2,
        "results": [
            SAMPLE_RECORD,
            {
                **SAMPLE_RECORD,
                "numerooffreforem": "99",
                "titreoffre": "Développeur Python",
                "metier": "Développement informatique",
            },
        ],
    }
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = payload

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_resp)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("app.collectors.le_forem.httpx.AsyncClient", return_value=mock_client):
        result = asyncio.run(LeForemCollector().collect("python"))

    assert result.errors == []
    assert len(result.records) == 1
    assert result.records[0].source_job_id == "99"
