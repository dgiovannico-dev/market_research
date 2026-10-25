"""Weekly report human formatting: compact time, 2-decimal percents."""

from __future__ import annotations

from datetime import datetime, timezone

from app.reports.weekly import (
    format_pct,
    format_report_timestamp,
    _render_markdown,
)


def test_format_report_timestamp_to_minutes():
    dt = datetime(2026, 10, 25, 22, 44, 16, 533089, tzinfo=timezone.utc)
    assert format_report_timestamp(dt) == "2026-10-25 22:44 UTC"
    assert format_report_timestamp("2026-10-25T22:44:16.533089+00:00") == (
        "2026-10-25 22:44 UTC"
    )


def test_format_pct_two_decimals_locale():
    assert format_pct(10.8642, locale="en") == "10.86%"
    assert format_pct(10.8642, locale="it") == "10,86%"
    assert format_pct(1006.9767441860465, locale="en") == "1006.98%"


def test_render_markdown_human_en():
    md = _render_markdown(
        {
            "generated_at": "2026-10-25T22:44:16.533089+00:00",
            "disclaimer": "Observed only.",
            "executive_kpis": [
                {
                    "metric_name": "observed_demand_growth_pct",
                    "metric_value": 12.3456,
                    "sample_size": 100,
                    "unit": "pct",
                    "limits": "Sensitive to source changes.",
                }
            ],
            "technologies_growing": [
                {
                    "technology": "Go",
                    "growth_pct": 10.8642,
                    "recent_mentions": 50,
                    "previous_mentions": 45,
                }
            ],
            "technologies_declining": [],
        },
        locale="en",
    )
    assert "Generated: 2026-10-25 22:44 UTC" in md
    assert "10.86%" in md
    assert "12.35%" in md
    assert "evidence_kind" not in md
    assert "Snapshot of the week" in md


def test_render_markdown_human_it():
    md = _render_markdown(
        {
            "generated_at_display": "2026-10-25 22:44 UTC",
            "disclaimer": "Solo osservati.",
            "executive_kpis": [],
            "technologies_growing": [
                {
                    "technology": "Python",
                    "growth_pct": 10.8642,
                    "recent_mentions": 10,
                    "previous_mentions": 5,
                }
            ],
            "technologies_declining": [],
        },
        locale="it",
    )
    assert "Generato: 2026-10-25 22:44 UTC" in md
    assert "10,86%" in md
    assert "Tecnologie in crescita" in md
