"""JobUp collector: IT fan-out, start/rows pagination, in-run dedupe."""
from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.collectors.base import MISSING_QUERY
from app.collectors.jobup import (
    MAX_PAGES,
    MAX_RECORDS,
    ROWS_PER_PAGE,
    JobUpCollector,
    _query_variants,
    _should_fan_out,
)


def _doc(job_id: str, title: str = "Engineer") -> dict:
    return {
        "job_id": job_id,
        "title": title,
        "company_name": "Acme",
        "place": "Zürich",
        "is_active": True,
        "preview": "Build things",
        "publication_date": "2026-01-15T10:00:00Z",
        "_links": {"detail_en": {"href": f"https://www.jobup.ch/en/jobs/detail/{job_id}/"}},
    }


def _mock_client(side_effect):
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(side_effect=side_effect)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    return mock_client


def _resp(docs: list[dict], **meta):
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = {
        "documents": docs,
        "start": meta.get("start", 0),
        "rows": meta.get("rows", len(docs)),
        "current_page": meta.get("current_page", 1),
        "num_pages": meta.get("num_pages", 10),
        "total_hits": meta.get("total_hits", 100),
    }
    return mock_resp


def test_blank_query_returns_missing():
    result = asyncio.run(JobUpCollector().collect(None))
    assert result.records == []
    assert MISSING_QUERY in result.errors
    assert result.pages_scanned == 0


def test_should_fan_out_generic_and_tech():
    assert _should_fan_out("it") is True
    assert _should_fan_out("java developer") is True
    assert _should_fan_out("software") is True
    assert _should_fan_out("nurse geneva") is False


def test_query_variants_adds_it_terms():
    variants = _query_variants("java developer")
    assert variants[0] == "java developer"
    assert "software" in variants
    assert len(variants) <= 3


def test_query_variants_skips_fan_out_for_non_tech():
    assert _query_variants("nurse geneva") == ["nurse geneva"]


def test_fan_out_issues_multiple_queries():
    calls: list[dict] = []

    def side_effect(_url, params=None, **_kwargs):
        calls.append(dict(params or {}))
        q = (params or {}).get("query", "")
        return _resp([_doc(f"{q}-1"), _doc(f"{q}-2")])

    mock_client = _mock_client(side_effect)
    with patch("app.collectors.jobup.httpx.AsyncClient", return_value=mock_client):
        result = asyncio.run(JobUpCollector().collect("java developer"))

    queries = [c["query"] for c in calls]
    assert queries[0] == "java developer"
    assert len(queries) >= 2
    assert "software" in queries or "devops" in queries
    assert result.errors == []
    assert len(result.records) >= 2
    assert result.pages_scanned >= 2


def test_paginate_with_start_for_non_tech():
    def side_effect(_url, params=None, **_kwargs):
        start = int((params or {}).get("start") or 0)
        if start == 0:
            return _resp([_doc("a"), _doc("b")], start=0, rows=50)
        if start == 50:
            return _resp([_doc("c")], start=50, rows=50)
        return _resp([], start=start, rows=50)

    mock_client = _mock_client(side_effect)
    with patch("app.collectors.jobup.httpx.AsyncClient", return_value=mock_client):
        # Force single-variant path by using a non-tech multi-token query
        with patch("app.collectors.jobup.ROWS_PER_PAGE", 50):
            result = asyncio.run(JobUpCollector().collect("nurse geneva"))

    starts = [
        int(c.kwargs.get("params", {}).get("start") or 0)
        for c in mock_client.get.await_args_list
    ]
    assert 0 in starts
    # Second page only if first returned a full page; our mock returns 2 < 50 so stop
    assert result.records[0].source_job_id == "a"
    assert len(result.records) == 2


def test_paginate_full_pages_advances_start():
    def side_effect(_url, params=None, **_kwargs):
        start = int((params or {}).get("start") or 0)
        rows = int((params or {}).get("rows") or 50)
        docs = [_doc(f"id-{start + i}") for i in range(rows)]
        return _resp(docs, start=start, rows=rows)

    mock_client = _mock_client(side_effect)
    with (
        patch("app.collectors.jobup.httpx.AsyncClient", return_value=mock_client),
        patch("app.collectors.jobup.ROWS_PER_PAGE", 2),
        patch("app.collectors.jobup.MAX_PAGES", 3),
        patch("app.collectors.jobup.MAX_RECORDS", 10),
        patch("app.collectors.jobup._should_fan_out", return_value=False),
    ):
        result = asyncio.run(JobUpCollector().collect("nurse geneva"))

    starts = [
        int(c.kwargs.get("params", {}).get("start") or 0)
        for c in mock_client.get.await_args_list
    ]
    assert starts == [0, 2, 4]
    assert result.pages_scanned == 3
    assert len(result.records) == 6
    assert len({r.source_job_id for r in result.records}) == 6


def test_dedupe_by_source_job_id_across_variants():
    def side_effect(_url, params=None, **_kwargs):
        # Same job_id returned for every variant
        return _resp([_doc("dup-1", "Same"), _doc(f"{params.get('query')}-x")])

    mock_client = _mock_client(side_effect)
    with patch("app.collectors.jobup.httpx.AsyncClient", return_value=mock_client):
        result = asyncio.run(JobUpCollector().collect("devops"))

    ids = [r.source_job_id for r in result.records]
    assert ids.count("dup-1") == 1
    assert len(ids) == len(set(ids))


def test_caps_total_pages():
    def side_effect(_url, params=None, **_kwargs):
        start = int((params or {}).get("start") or 0)
        return _resp([_doc(f"p-{params.get('query')}-{start}") for _ in range(50)])

    mock_client = _mock_client(side_effect)
    with patch("app.collectors.jobup.httpx.AsyncClient", return_value=mock_client):
        result = asyncio.run(JobUpCollector().collect("java"))

    assert mock_client.get.await_count <= MAX_PAGES
    assert result.pages_scanned <= MAX_PAGES
    assert len(result.records) <= MAX_RECORDS


@pytest.mark.parametrize(
    "query,expect_fan_out",
    [
        ("python", True),
        ("developer", True),
        ("chef paris", False),
    ],
)
def test_fan_out_gate(query: str, expect_fan_out: bool):
    assert _should_fan_out(query) is expect_fan_out


def test_search_rows_param_never_exceeds_public_api_limit():
    """JobUp returns HTTP 422 when rows > 20."""
    rows_seen: list[int] = []

    def side_effect(_url, params=None, **_kwargs):
        rows_seen.append(int((params or {}).get("rows") or 0))
        return _resp([_doc("only-one")])

    mock_client = _mock_client(side_effect)
    with patch("app.collectors.jobup.httpx.AsyncClient", return_value=mock_client):
        result = asyncio.run(JobUpCollector().collect("python"))

    assert result.errors == []
    assert rows_seen
    assert ROWS_PER_PAGE == 20
    assert all(r <= 20 for r in rows_seen)
