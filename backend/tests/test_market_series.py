"""Unit tests for temporal series grain / bucket helpers and rate medians."""

from datetime import date, datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest

from app.analytics.rate_series import rate_series
from app.analytics.series import (
    bucket_label_for_date,
    choose_grain,
    country_series,
    fill_bucket_counts,
    iter_bucket_labels,
    technology_series,
)


def test_choose_grain_auto():
    assert choose_grain(7) == "day"
    assert choose_grain(30) == "day"
    assert choose_grain(31) == "week"
    assert choose_grain(180) == "week"
    assert choose_grain(181) == "month"
    assert choose_grain(365) == "month"


def test_choose_grain_override():
    assert choose_grain(365, "day") == "day"
    assert choose_grain(7, "month") == "month"
    with pytest.raises(ValueError):
        choose_grain(30, "quarter")


def test_bucket_label_formats():
    d = date(2026, 3, 18)  # ISO week 12 of 2026
    assert bucket_label_for_date(d, "day") == "2026-03-18"
    assert bucket_label_for_date(d, "week") == "2026-W12"
    assert bucket_label_for_date(d, "month") == "2026-03"


def test_fill_bucket_counts_zeros():
    points = fill_bucket_counts(
        {"2026-W10": 3, "2026-W12": 1},
        ["2026-W10", "2026-W11", "2026-W12"],
    )
    assert [p["bucket"] for p in points] == ["2026-W10", "2026-W11", "2026-W12"]
    assert [p["count"] for p in points] == [3, 0, 1]


def test_iter_bucket_labels_day_continuous():
    labels = iter_bucket_labels(date(2026, 10, 18), date(2026, 10, 20), "day")
    assert labels == ["2026-10-18", "2026-10-19", "2026-10-20"]


def test_iter_bucket_labels_month():
    labels = iter_bucket_labels(date(2026, 1, 15), date(2026, 3, 2), "month")
    assert labels == ["2026-01", "2026-02", "2026-03"]


def test_iter_bucket_labels_empty_range():
    assert iter_bucket_labels(date(2026, 10, 20), date(2026, 10, 18), "day") == []


def test_empty_corpus_series_via_mock():
    """Empty job subquery → empty series without hitting real aggregation."""
    db = MagicMock()
    # scalar count from job_id_sub → 0; count_thin unused when sample empty after setup
    db.scalar.return_value = 0
    db.execute.return_value.all.return_value = []

    tech = technology_series(db, days=30, min_evidence="all")
    assert tech["sample_size"] == 0
    assert tech["series"] == []
    assert tech["grain"] == "day"
    assert tech["period_days"] == 30

    countries = country_series(db, days=90, min_evidence="all")
    assert countries["sample_size"] == 0
    assert countries["series"] == []
    assert countries["grain"] == "week"


def test_empty_corpus_rate_series():
    db = MagicMock()
    db.scalar.return_value = 0
    db.execute.return_value.all.return_value = []

    out = rate_series(db, days=90, min_evidence="all")
    assert out["sample_size"] == 0
    assert out["series"] == []
    assert out["grain"] == "week"
    assert out["period_days"] == 90
    assert "Median advertised" in out["limits"]


def test_rate_series_median_aggregation_and_grain():
    """Top currency/unit by sample; count field holds median; grain override."""
    db = MagicMock()
    db.scalar.return_value = 20
    # Dates must fall inside the rolling corpus window (now − days).
    now = datetime.now(timezone.utc)
    day_a = now.replace(hour=12, minute=0, second=0, microsecond=0)
    # Same ISO week as day_a when possible; else adjacent day still same week for Mon–Sat.
    day_b = day_a
    day_prev_week = day_a - timedelta(days=7)
    bucket_cur = bucket_label_for_date(day_a.date(), "week")
    bucket_prev = bucket_label_for_date(day_prev_week.date(), "week")
    db.execute.return_value.all.return_value = [
        ("EUR", "hour", day_a, 80.0),
        ("EUR", "hour", day_b, 100.0),  # median current week = 90
        ("EUR", "hour", day_prev_week, 110.0),
        ("CHF", "hour", day_a, 120.0),
        ("CHF", "hour", day_b, 140.0),
        ("CHF", "hour", day_prev_week, 130.0),
        ("USD", "day", day_a, 900.0),  # 2 obs → dropped by min_sample=3
        ("USD", "day", day_b, 950.0),
    ]

    out = rate_series(
        db,
        days=90,
        min_evidence="all",
        top=2,
        grain="week",
        min_sample=3,
    )
    assert out["grain"] == "week"
    assert out["sample_size"] == 20
    keys = [s["key"] for s in out["series"]]
    assert set(keys) == {"EUR/hour", "CHF/hour"}  # 3 each; USD/day has 2 < min_sample
    assert "USD/day" not in keys
    eur = next(s for s in out["series"] if s["key"] == "EUR/hour")
    by_bucket = {p["bucket"]: p["count"] for p in eur["points"]}
    assert by_bucket[bucket_cur] == 90.0
    assert by_bucket[bucket_prev] == 110.0
    # Continuous axis fills empty weeks with null (not invented rates)
    empty = [
        p["count"]
        for p in eur["points"]
        if p["bucket"] not in (bucket_cur, bucket_prev)
    ]
    assert all(v is None for v in empty)


def test_rate_series_unit_currency_filter():
    db = MagicMock()
    db.scalar.return_value = 5
    day = datetime.now(timezone.utc).replace(hour=12, minute=0, second=0, microsecond=0)
    day_label = day.date().isoformat()
    db.execute.return_value.all.return_value = [
        ("EUR", "hour", day, 70.0),
        ("EUR", "hour", day, 90.0),
        ("EUR", "hour", day, 80.0),
    ]

    out = rate_series(
        db,
        days=30,
        min_evidence="all",
        grain="day",
        unit="hour",
        currency="eur",
        min_sample=3,
        top=5,
    )
    assert out["grain"] == "day"
    assert len(out["series"]) == 1
    assert out["series"][0]["key"] == "EUR/hour"
    by_bucket = {p["bucket"]: p["count"] for p in out["series"][0]["points"]}
    assert by_bucket[day_label] == 80.0
