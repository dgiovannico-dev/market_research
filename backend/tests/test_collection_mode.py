"""collection_mode registry + no silent topic defaults (Demand Compass Tasks 1+3)."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from app.collectors.adzuna import AdzunaCollector
from app.collectors.arbetsformedlingen import ArbetsformedlingenCollector
from app.collectors.base import (
    MISSING_QUERY,
    BaseCollector,
    simplify_query_for,
)
from app.collectors.jobicy import JobicyCollector
from app.collectors.registry import (
    COLLECTORS,
    VALID_COLLECTION_MODES,
    collectors_by_mode,
    get_collection_mode,
    list_collectors_by_mode,
)
from app.core.config import get_settings


def test_every_registered_collector_has_explicit_mode():
    for key, collector in COLLECTORS.items():
        found = False
        for cls in type(collector).__mro__:
            if cls is BaseCollector:
                break
            if "collection_mode" in cls.__dict__:
                mode = cls.__dict__["collection_mode"]
                assert mode in VALID_COLLECTION_MODES, f"{key}: invalid mode {mode!r}"
                found = True
                break
        assert found, f"{key} missing explicit collection_mode on concrete class"
        assert get_collection_mode(collector) in VALID_COLLECTION_MODES


def test_list_collectors_by_mode_covers_registry():
    grouped = list_collectors_by_mode()
    listed = set(grouped["search"]) | set(grouped["dump"]) | set(grouped["feed"])
    assert listed == set(COLLECTORS)
    for mode in VALID_COLLECTION_MODES:
        assert set(collectors_by_mode(mode)) == set(grouped[mode])


def test_simplify_query_for_takes_first_or_clause():
    assert simplify_query_for("adzuna", "python OR java OR go") == "python"
    assert simplify_query_for(None, "rust") == "rust"


def test_settings_has_no_deprecated_default_query_fields():
    """Product Settings must not bind *_DEFAULT_QUERY / WHAT / TAG (extra=ignore)."""
    from app.core.config import Settings

    deprecated = [
        name
        for name in Settings.model_fields
        if name.endswith(("_default_query", "_default_what", "_default_tag"))
    ]
    assert deprecated == [], f"Settings still exposes deprecated topic defaults: {deprecated}"


def test_ops_smoke_query_not_wired_into_collect_path():
    """OPS_SMOKE_QUERY may exist for scripts; product collect/sync must not read it."""
    import inspect

    from app.api.v1 import router as api_router
    from app.research import sync as research_sync
    from app.scheduler import crawl_run, daily_crawlers, runner

    for mod in (crawl_run, daily_crawlers, runner, research_sync, api_router):
        src = inspect.getsource(mod)
        assert "ops_smoke_query" not in src, f"{mod.__name__} must not use ops_smoke_query"
        assert "DEFAULT_QUERY" not in src, f"{mod.__name__} must not reference DEFAULT_QUERY"


def test_search_collectors_ignore_default_query_env(monkeypatch):
    """Even with *_DEFAULT_QUERY set, every search collector fails closed on blank query."""
    search = collectors_by_mode("search")
    assert search, "expected at least one search-mode collector"
    for key in search:
        monkeypatch.setenv(f"{key.upper()}_DEFAULT_QUERY", "should-not-be-used")
    monkeypatch.setenv("ADZUNA_DEFAULT_QUERY", "should-not-be-used")
    monkeypatch.setenv("ARBETSFORMEDLINGEN_DEFAULT_QUERY", "should-not-be-used")
    get_settings.cache_clear()
    try:
        for key, collector in search.items():
            for blank in (None, "", "   "):
                result = asyncio.run(collector.collect(blank))
                assert result.records == [], f"{key}: must not invent records from DEFAULT_QUERY"
                assert (
                    MISSING_QUERY in result.errors
                ), f"{key}: expected {MISSING_QUERY}, got {result.errors}"
    finally:
        get_settings.cache_clear()


def test_adzuna_missing_query_no_default(monkeypatch):
    monkeypatch.setenv("ADZUNA_APP_ID", "id")
    monkeypatch.setenv("ADZUNA_APP_KEY", "key")
    monkeypatch.setenv("ADZUNA_DEFAULT_QUERY", "should-not-be-used")
    get_settings.cache_clear()
    result = asyncio.run(AdzunaCollector().collect(None))
    assert result.records == []
    assert MISSING_QUERY in result.errors
    result_blank = asyncio.run(AdzunaCollector().collect("  "))
    assert MISSING_QUERY in result_blank.errors


def test_arbetsformedlingen_missing_query_no_default(monkeypatch):
    monkeypatch.setenv("ARBETSFORMEDLINGEN_DEFAULT_QUERY", "should-not-be-used")
    get_settings.cache_clear()
    result = asyncio.run(ArbetsformedlingenCollector().collect(None))
    assert result.records == []
    assert MISSING_QUERY in result.errors


def test_jobicy_dump_works_with_query_none():
    payload = {
        "jobs": [
            {
                "id": 1,
                "jobTitle": "Engineer",
                "url": "https://example.com/j/1",
                "companyName": "Acme",
                "jobDescription": "desc",
                "jobGeo": "Remote",
                "pubDate": "2026-01-01T00:00:00Z",
                "jobType": ["full-time"],
                "jobTags": ["python"],
            }
        ]
    }
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = payload

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_resp)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("app.collectors.jobicy.httpx.AsyncClient", return_value=mock_client):
        result = asyncio.run(JobicyCollector().collect(None))

    assert MISSING_QUERY not in result.errors
    assert len(result.records) == 1
    assert result.records[0].title == "Engineer"
    # No tag param when query is None (no silent default tag)
    params = mock_client.get.await_args.kwargs.get("params") or {}
    assert "tag" not in params
