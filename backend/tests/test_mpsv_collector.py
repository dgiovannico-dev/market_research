"""MPSV CZ open-data dump collector — mocked JSON / stream fixtures."""

from __future__ import annotations

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.collectors.mpsv import (
    DUMP_JSON_URL,
    DUMP_JSONLD_URL,
    MAX_RECORDS,
    MpsvCollector,
    _map_record,
)
from app.collectors.mpsv_stream import ArrayObjectDecoder, iter_polozky_payload
from app.collectors.registry import COLLECTOR_GEO, COLLECTORS, get_collection_mode


def _vacancy(
    portal_id: int,
    title: str,
    *,
    company: str = "Acme CZ",
    desc: str = "",
) -> dict:
    return {
        "portalId": portal_id,
        "id": f"VolneMisto/{portal_id}",
        "referencniCislo": f"REF{portal_id}",
        "pozadovanaProfese": {"cs": title},
        "upresnujiciInformace": {"cs": desc or title},
        "zamestnavatel": {"nazev": company, "ico": "12345678"},
        "mesicniMzdaOd": 50000,
        "mesicniMzdaDo": 80000,
        "datumVlozeni": "2026-10-16T00:00:00.000Z",
        "mistoVykonuPrace": {"adresaText": "Praha"},
        "profeseCzIsco": {"id": "2512"},
        "pocetMist": 1,
    }


SAMPLE_DUMP = {
    "@context": {"polozky": "@graph"},
    "polozky": [
        _vacancy(1, "MANIPULAČNÍ PRACOVNÍK DO VÝROBY"),
        _vacancy(2, "Programátor Java", desc="Vývoj backend služeb v Javě"),
        _vacancy(3, "Softwarový tester", desc="QA software"),
        _vacancy(4, "Řidič kamionu"),
        _vacancy(5, "Python developer", company="DataFirm"),
    ],
}


def test_mpsv_registered_as_dump():
    assert "mpsv" in COLLECTORS
    assert get_collection_mode(COLLECTORS["mpsv"]) == "dump"
    assert COLLECTOR_GEO["mpsv"] == frozenset({"CZ"})


def test_iter_polozky_payload():
    items = iter_polozky_payload(SAMPLE_DUMP)
    assert len(items) == 5
    assert items[1]["portalId"] == 2


def test_map_record_fields():
    job = _map_record(SAMPLE_DUMP["polozky"][1])
    assert job is not None
    assert job.source_job_id == "2"
    assert job.title == "Programátor Java"
    assert job.company == "Acme CZ"
    assert job.salary_text == "50000-80000 CZK"
    assert job.location == "Praha"
    assert "data.mpsv.cz/zdroj/VolneMisto/2" in job.url


def test_array_object_decoder_chunked():
    raw = json.dumps(SAMPLE_DUMP, ensure_ascii=False).encode("utf-8")
    dec = ArrayObjectDecoder(keys=("polozky", "@graph"))
    mid = len(raw) // 2
    objs = dec.feed(raw[:mid]) + dec.feed(raw[mid:]) + dec.flush()
    assert len(objs) == 5
    assert dec.done is True


def _stream_response(body: bytes, *, status: int = 200, ctype: str = "application/ld+json"):
    async def aiter_bytes(_size=65536):
        yield body

    resp = MagicMock()
    resp.status_code = status
    resp.headers = {"content-type": ctype}
    resp.aiter_bytes = aiter_bytes
    resp.aclose = AsyncMock()
    return resp


def _mock_client_sequence(responses: list[MagicMock]):
    client = AsyncMock()
    client.build_request = MagicMock(side_effect=lambda method, url: MagicMock(url=url))
    client.send = AsyncMock(side_effect=responses)
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=None)
    return client


def test_collect_filters_it_and_caps():
    body = json.dumps(SAMPLE_DUMP, ensure_ascii=False).encode("utf-8")
    # JSON path 404 HTML, then JSON-LD OK
    html_404 = _stream_response(b"<html>404</html>", status=404, ctype="text/html")
    ok = _stream_response(body)
    client = _mock_client_sequence([html_404, ok])

    with patch("app.collectors.mpsv.httpx.AsyncClient", return_value=client):
        result = asyncio.run(MpsvCollector().collect(None))

    assert result.errors == []
    titles = {r.title for r in result.records}
    assert "Programátor Java" in titles
    assert "Python developer" in titles
    assert "Softwarový tester" in titles
    assert "Řidič kamionu" not in titles
    assert "MANIPULAČNÍ PRACOVNÍK DO VÝROBY" not in titles
    assert len(result.records) <= MAX_RECORDS
    assert client.send.await_count == 2
    urls = []
    for call in client.build_request.call_args_list:
        args, kwargs = call
        urls.append(args[1] if len(args) > 1 else kwargs.get("url"))
    assert DUMP_JSON_URL in urls
    assert DUMP_JSONLD_URL in urls


def test_collect_query_overrides_default_it_filter():
    body = json.dumps(SAMPLE_DUMP, ensure_ascii=False).encode("utf-8")
    client = _mock_client_sequence([_stream_response(body, ctype="application/json")])

    with patch("app.collectors.mpsv.httpx.AsyncClient", return_value=client):
        result = asyncio.run(MpsvCollector().collect("řidič"))

    assert len(result.records) == 1
    assert result.records[0].title == "Řidič kamionu"


def test_collect_fails_closed_when_dumps_unavailable():
    bad = _stream_response(b"<html>nope</html>", status=404, ctype="text/html")
    bad2 = _stream_response(b"<html>nope</html>", status=404, ctype="text/html")
    client = _mock_client_sequence([bad, bad2])

    with patch("app.collectors.mpsv.httpx.AsyncClient", return_value=client):
        result = asyncio.run(MpsvCollector().collect(None))

    assert result.records == []
    assert result.errors
    assert "dump_unavailable" in result.errors[0]


@pytest.mark.parametrize("missing", ["portalId", "title"])
def test_map_skips_invalid(missing: str):
    item = _vacancy(99, "Developer")
    if missing == "portalId":
        item.pop("portalId")
        item.pop("referencniCislo")
        item.pop("id")
        assert _map_record(item) is None
    else:
        item["pozadovanaProfese"] = {"cs": ""}
        job = _map_record(item)
        assert job is not None
        assert job.title == "Untitled"
