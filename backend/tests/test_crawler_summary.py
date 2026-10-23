"""Unit tests for thin crawler tick summaries."""

from __future__ import annotations

from datetime import date, datetime, timezone

from app.scheduler.crawler_summary import build_tick_summary, summarize_skip_reasons


def test_summarize_skip_reasons():
    skipped = [
        {"reason": "missing_query"},
        {"reason": "budget"},
        {"reason": "missing_query"},
        {"phase": "focus", "skipped": True},
    ]
    assert summarize_skip_reasons(skipped) == {
        "missing_query": 2,
        "budget": 1,
        "unknown": 1,
    }


def test_build_tick_summary_compact():
    day = date(2026, 10, 20)
    completed = datetime(2026, 10, 20, 12, 0, tzinfo=timezone.utc)
    summary = build_tick_summary(
        day=day,
        status="succeeded",
        idempotent=False,
        dump_ran=1,
        discovery_ran=2,
        focus_ran=1,
        calls=4,
        discovery_scheduled=1,
        focus_scheduled=2,
        intents_enabled={"discovery_intents_enabled": 5, "focus_intents_enabled": 3},
        skipped=[{"reason": "budget"}, {"reason": "missing_query"}],
        errors=[{"error": "boom"}],
        completed_at=completed,
    )
    assert summary["day"] == "2026-10-20"
    assert summary["idempotent"] is False
    assert summary["discovery_intents_enabled"] == 5
    assert summary["focus_intents_scheduled"] == 2
    assert summary["errors_count"] == 1
    assert summary["skips"] == {"budget": 1, "missing_query": 1}
    assert summary["skips"].get("budget") == 1
    assert "collections" not in summary
    assert summary["completed_at"] == completed.isoformat()
