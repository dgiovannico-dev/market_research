"""Unit tests for budgeted daily crawlers (rotation + ceiling, no network)."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import date
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.collectors.base import BaseCollector, CollectorResult
from app.scheduler.daily_crawlers import pick_search_collectors, run_daily_crawlers
from app.scheduler.tick_state import clear_tick_state


def _fake_container(db: MagicMock) -> MagicMock:
    """Stand-in for bootstrap.get_container() in crawler unit tests."""
    container = MagicMock()
    container.open_session.return_value = db
    container.credentials.has_credentials.return_value = True

    @contextmanager
    def session_scope():
        yield db

    container.session_scope = session_scope
    return container


@dataclass
class FakeCollector(BaseCollector):
    name: str = "Fake"
    source_key: str = "fake"
    collection_mode: str = "search"
    calls: list[dict[str, Any]] = field(default_factory=list)

    async def collect(self, query: str | None = None) -> CollectorResult:
        self.calls.append({"query": query})
        return CollectorResult(records=[], pages_scanned=1)


def _source(connector: str, source_id: int = 1) -> MagicMock:
    src = MagicMock()
    src.id = source_id
    src.name = connector
    src.connector_type = connector
    src.last_success_at = None
    src.last_error = None
    src.last_error_at = None
    return src


def test_pick_search_collectors_respects_lim_and_rotation():
    pool = [
        (_source("b", 2), FakeCollector(source_key="b")),
        (_source("a", 1), FakeCollector(source_key="a")),
        (_source("c", 3), FakeCollector(source_key="c")),
    ]
    intent = SimpleNamespace(id=0, query_text="java", countries=[])
    # sorted keys a,b,c; offset = (0 + 0) % 3 = 0 → a,b
    picked0 = pick_search_collectors(intent, pool, lim=2, global_left=10, day_ordinal=0)
    assert [c.source_key for _, c in picked0] == ["a", "b"]
    # offset = (1 + 0) % 3 = 1 → b,c
    picked1 = pick_search_collectors(intent, pool, lim=2, global_left=10, day_ordinal=1)
    assert [c.source_key for _, c in picked1] == ["b", "c"]
    # intent.id shifts rotation: offset = (0 + 1) % 3 = 1 → b,c
    intent_shift = SimpleNamespace(id=1, query_text="java", countries=[])
    picked_id = pick_search_collectors(intent_shift, pool, lim=2, global_left=10, day_ordinal=0)
    assert [c.source_key for _, c in picked_id] == ["b", "c"]
    capped = pick_search_collectors(intent, pool, lim=5, global_left=1, day_ordinal=0)
    assert len(capped) == 1


def test_pick_search_collectors_prefers_geo():
    pool = [
        (_source("usajobs", 1), FakeCollector(source_key="usajobs")),
        (_source("reed", 2), FakeCollector(source_key="reed")),
        (_source("jooble", 3), FakeCollector(source_key="jooble")),
    ]
    intent = SimpleNamespace(id=0, query_text="java", countries=["US"])
    picked = pick_search_collectors(intent, pool, lim=2, global_left=10, day_ordinal=0)
    assert picked[0][1].source_key == "usajobs"


@pytest.mark.asyncio
async def test_run_daily_crawlers_order_and_budget_ceiling():
    dump = FakeCollector(name="Dump", source_key="remotive", collection_mode="dump")
    search_a = FakeCollector(name="SearchA", source_key="adzuna", collection_mode="search")
    search_b = FakeCollector(name="SearchB", source_key="reed", collection_mode="search")
    search_c = FakeCollector(name="SearchC", source_key="jooble", collection_mode="search")

    collectors = {
        "remotive": dump,
        "adzuna": search_a,
        "reed": search_b,
        "jooble": search_c,
    }
    sources = [
        _source("remotive", 10),
        _source("adzuna", 11),
        _source("reed", 12),
        _source("jooble", 13),
    ]
    discovery = [
        SimpleNamespace(
            id=101,
            query_text="kubernetes OR k8s",
            countries=[],
            kind="discovery",
            enabled=True,
            schedule_hint="daily",
            deleted_at=None,
        )
    ]
    focus = [
        SimpleNamespace(
            id=201,
            query_text="rust",
            countries=[],
            kind="focus",
            enabled=True,
            schedule_hint="daily",
            deleted_at=None,
        ),
        SimpleNamespace(
            id=202,
            query_text="go",
            countries=[],
            kind="focus",
            enabled=True,
            schedule_hint="daily",
            deleted_at=None,
        ),
    ]

    crawl_log: list[tuple[str | None, int | None, str]] = []

    async def fake_crawl_one(db, *, source, collector, query, query_id, phase):
        crawl_log.append((query, query_id, collector.source_key))
        return {
            "source": source.name,
            "connector": collector.source_key,
            "query_id": query_id,
            "phase": phase,
        }

    settings = SimpleNamespace(
        sync_max_discovery_per_tick=12,
        sync_max_focus_per_tick=10,
        sync_max_collector_calls_per_intent=2,
        sync_max_total_collector_calls_per_tick=4,
    )

    db = MagicMock()
    day = date(2026, 10, 20)
    clear_tick_state(day)

    with (
        patch("app.scheduler.daily_crawlers.get_settings", return_value=settings),
        patch("app.scheduler.daily_crawlers.get_container", return_value=_fake_container(db)),
        patch("app.scheduler.daily_crawlers.already_succeeded", return_value=False),
        patch("app.scheduler.daily_crawlers.mark_succeeded") as mark,
        patch("app.scheduler.daily_crawlers.persist_crawler_tick") as persist,
        patch(
            "app.scheduler.daily_crawlers.count_enabled_intents",
            return_value={"discovery_intents_enabled": 3, "focus_intents_enabled": 2},
        ),
        patch("app.scheduler.daily_crawlers._load_enabled_sources", return_value=sources),
        patch(
            "app.scheduler.daily_crawlers.get_collector",
            side_effect=lambda key: collectors.get(key),
        ),
        patch(
            "app.scheduler.daily_crawlers._scheduled_intents",
            side_effect=lambda _db, kind, _limit: discovery if kind == "discovery" else focus,
        ),
        patch("app.scheduler.daily_crawlers.crawl_one", new=AsyncMock(side_effect=fake_crawl_one)),
        patch("app.scheduler.daily_crawlers.utc_today", return_value=day),
    ):
        result = await run_daily_crawlers(force=True)

    assert result["status"] == "succeeded"
    assert result["idempotent"] is False
    assert result["calls"] == 4
    assert result["dump_ran"] == 1
    assert result["discovery_ran"] == 2
    assert result["focus_ran"] == 1
    assert len(crawl_log) == 4
    assert crawl_log[0] == (None, None, "remotive")
    assert crawl_log[1][1] == 101
    assert crawl_log[2][1] == 101
    assert crawl_log[3][1] == 201
    mark.assert_called_once_with(day)
    persist.assert_called_once()
    summary = result["summary"]
    assert summary["discovery_intents_enabled"] == 3
    assert summary["focus_intents_enabled"] == 2
    assert summary["discovery_ran"] == 2
    assert summary["focus_ran"] == 1
    assert summary["skips"] == {"budget": 1}
    assert any(s.get("query_id") == 202 and s.get("reason") == "budget" for s in result["skipped"])


@pytest.mark.asyncio
async def test_run_daily_crawlers_skips_idempotent():
    settings = SimpleNamespace(
        sync_max_discovery_per_tick=12,
        sync_max_focus_per_tick=10,
        sync_max_collector_calls_per_intent=5,
        sync_max_total_collector_calls_per_tick=100,
    )
    day = date(2026, 10, 20)
    clear_tick_state(day)

    with (
        patch("app.scheduler.daily_crawlers.get_settings", return_value=settings),
        patch("app.scheduler.daily_crawlers.utc_today", return_value=day),
        patch("app.scheduler.daily_crawlers.already_succeeded", return_value=True),
        patch(
            "app.scheduler.daily_crawlers.get_container",
            return_value=_fake_container(MagicMock()),
        ),
        patch(
            "app.scheduler.daily_crawlers.load_last_tick_summary",
            return_value={
                "day": day.isoformat(),
                "status": "succeeded",
                "dump_ran": 1,
                "discovery_ran": 2,
                "focus_ran": 1,
                "calls": 4,
                "skips": {"missing_query": 1},
            },
        ),
        patch(
            "app.scheduler.daily_crawlers.count_enabled_intents",
            return_value={"discovery_intents_enabled": 1, "focus_intents_enabled": 1},
        ),
        patch("app.scheduler.daily_crawlers.crawl_one", new=AsyncMock()) as crawl,
    ):
        result = await run_daily_crawlers(force=False)

    assert result["status"] == "skipped_idempotent"
    assert result["idempotent"] is True
    assert result["calls"] == 0
    assert result["summary"]["idempotent"] is True
    assert result["summary"]["skips"] == {"missing_query": 1}
    crawl.assert_not_called()

    # force bypasses idempotency even when a prior tick succeeded
    db = MagicMock()
    with (
        patch("app.scheduler.daily_crawlers.get_settings", return_value=settings),
        patch("app.scheduler.daily_crawlers.utc_today", return_value=day),
        patch("app.scheduler.daily_crawlers.already_succeeded", return_value=True),
        patch("app.scheduler.daily_crawlers.get_container", return_value=_fake_container(db)),
        patch("app.scheduler.daily_crawlers._load_enabled_sources", return_value=[]),
        patch("app.scheduler.daily_crawlers._scheduled_intents", return_value=[]),
        patch(
            "app.scheduler.daily_crawlers.count_enabled_intents",
            return_value={"discovery_intents_enabled": 0, "focus_intents_enabled": 0},
        ),
        patch("app.scheduler.daily_crawlers.persist_crawler_tick"),
        patch("app.scheduler.daily_crawlers.mark_succeeded"),
    ):
        forced = await run_daily_crawlers(force=True)
    assert forced["idempotent"] is False
    assert forced["status"] == "succeeded"
    assert forced["summary"]["calls"] == 0
