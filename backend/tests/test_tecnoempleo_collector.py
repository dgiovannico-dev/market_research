"""Tecnoempleo RSS collector — mocked feed (no network)."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from app.collectors.tecnoempleo import RSS_URL, TecnoempleoCollector

SAMPLE_RSS = """<?xml version="1.0" encoding="utf-8" ?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
    <title>Tecnoempleo.com - Ofertas</title>
    <link>https://www.tecnoempleo.com</link>
    <atom:link href="https://www.tecnoempleo.com/alertas-empleo-rss.php" rel="self" type="application/rss+xml" />
    <item>
        <title><![CDATA[Desarrollador Python]]></title>
        <link><![CDATA[https://www.tecnoempleo.com/desarrollador-python-acme/python-django/rf-abc123def456]]></link>
        <guid><![CDATA[https://www.tecnoempleo.com/desarrollador-python-acme/python-django/rf-abc123def456]]></guid>
        <description><![CDATA[<b>Empresa:</b>&nbsp;Acme SL<br /><b>Provincia:</b>&nbsp;Madrid<br /><b>Descripción:</b>&nbsp;Backend remoto<br /><b>Tecnologías:</b>&nbsp;python, django<br /><b>Tipo de Contrato:</b>&nbsp;Indefinido<br /><b>Salario:</b>&nbsp;40000 &euro; - 50000 &euro;  Bruto/año<br />]]></description>
        <pubDate>Tue, 20 Oct 2026 12:00:00 +0000</pubDate>
    </item>
    <item>
        <title><![CDATA[Sin enlace]]></title>
        <link></link>
        <description><![CDATA[skip me]]></description>
    </item>
</channel>
</rss>
"""


def _mock_client(body: bytes = SAMPLE_RSS.encode("utf-8")):
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.content = body
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_resp)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    return mock_client


def test_collect_maps_rss_item():
    mock_client = _mock_client()
    with patch("app.collectors.tecnoempleo.httpx.AsyncClient", return_value=mock_client):
        result = asyncio.run(TecnoempleoCollector().collect())

    assert result.errors == []
    assert result.pages_scanned == 1
    assert len(result.records) == 1
    job = result.records[0]
    assert job.source_job_id == "abc123def456"
    assert "tecnoempleo.com" in job.url
    assert job.title == "Desarrollador Python"
    assert job.company == "Acme SL"
    assert job.location == "Madrid"
    assert job.salary_text is not None and "40000" in job.salary_text
    assert "python" in [t.lower() for t in job.tags]
    assert job.remote_hint == "remote"
    assert job.job_type == "Indefinido"
    mock_client.get.assert_awaited_once()
    call_kwargs = mock_client.get.await_args
    assert call_kwargs.args[0] == RSS_URL
    assert call_kwargs.kwargs.get("params") is None


def test_collect_passes_te_query_param():
    mock_client = _mock_client()
    with patch("app.collectors.tecnoempleo.httpx.AsyncClient", return_value=mock_client):
        result = asyncio.run(TecnoempleoCollector().collect("software"))

    assert result.errors == []
    assert len(result.records) == 1
    params = mock_client.get.await_args.kwargs.get("params")
    assert params == {"te": "software"}


def test_collect_http_error():
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(side_effect=RuntimeError("boom"))
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    with patch("app.collectors.tecnoempleo.httpx.AsyncClient", return_value=mock_client):
        result = asyncio.run(TecnoempleoCollector().collect())
    assert result.records == []
    assert result.errors and "boom" in result.errors[0]
