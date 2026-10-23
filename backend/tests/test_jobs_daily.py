"""Unit tests for jobs-per-day sparkline series (dashboard summary.jobs_per_day)."""

from datetime import date

from app.analytics.jobs_daily import fill_daily_counts


def test_fill_daily_counts_zeros_quiet_days():
    series = fill_daily_counts(
        {date(2026, 10, 18): 3, date(2026, 10, 20): 1},
        start=date(2026, 10, 18),
        end=date(2026, 10, 20),
    )
    assert [p["day"] for p in series] == ["2026-10-18", "2026-10-19", "2026-10-20"]
    assert [p["jobs"] for p in series] == [3, 0, 1]
    for row in series:
        assert set(row) == {"day", "jobs"}
        assert isinstance(row["day"], str)
        assert isinstance(row["jobs"], int)


def test_fill_daily_counts_empty_range():
    assert fill_daily_counts({}, start=date(2026, 10, 20), end=date(2026, 10, 18)) == []


def test_jobs_per_day_all_zero_treated_as_empty():
    """Mirror jobs_per_day_series: continuous zeros → empty list for Sparkline."""
    series = fill_daily_counts({}, start=date(2026, 10, 18), end=date(2026, 10, 20))
    assert [p["jobs"] for p in series] == [0, 0, 0]
    assert sum(p["jobs"] for p in series) == 0
    # Production path returns [] when sum is 0 (see jobs_daily.jobs_per_day_series).
    assert (series if sum(p["jobs"] for p in series) else []) == []


def test_fill_daily_counts_single_day():
    series = fill_daily_counts({date(2026, 10, 21): 5}, start=date(2026, 10, 21), end=date(2026, 10, 21))
    assert series == [{"day": "2026-10-21", "jobs": 5}]
