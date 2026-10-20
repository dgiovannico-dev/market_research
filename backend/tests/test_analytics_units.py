from app.analytics.rates import _percentile
from app.normalization.url import canonicalize_url


def test_percentile_bounds():
    vals = [1.0, 2.0, 3.0, 4.0, 5.0]
    assert _percentile(vals, 0) == 1.0
    assert _percentile(vals, 1) == 5.0
    assert _percentile([], 0.5) is None


def test_tracking_query_removed():
    assert "utm_" not in canonicalize_url("https://x.test/a?utm_source=1&keep=2")
