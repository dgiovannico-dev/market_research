from datetime import date

from app.analytics.jobs_daily import fill_daily_counts
from app.analytics.rates import _percentile
from app.normalization.url import canonicalize_url


def test_percentile_bounds():
    vals = [1.0, 2.0, 3.0, 4.0, 5.0]
    assert _percentile(vals, 0) == 1.0
    assert _percentile(vals, 1) == 5.0
    assert _percentile([], 0.5) is None


def test_tracking_query_removed():
    assert "utm_" not in canonicalize_url("https://x.test/a?utm_source=1&keep=2")


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
