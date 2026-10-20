from app.normalization.hashing import content_hash, normalize_text
from app.normalization.rates import parse_rate_text
from app.normalization.url import canonicalize_url


def test_canonicalize_strips_utm():
    url = "https://Example.com/jobs/1/?utm_source=x&id=9"
    assert canonicalize_url(url) == "https://example.com/jobs/1?id=9"


def test_content_hash_stable():
    assert content_hash("Hello   World") == content_hash("hello world")
    assert content_hash("") is None
    assert normalize_text("  A  B ") == "a b"


def test_parse_hourly_and_daily_rates():
    hourly = parse_rate_text("Rate: €85/hour")
    assert hourly is not None
    assert hourly.currency == "EUR"
    assert hourly.unit == "hour"
    assert hourly.amount_min == 85

    daily = parse_rate_text("Compensation 650 EUR/day")
    assert daily is not None
    assert daily.unit == "day"
    assert daily.amount_min == 650


def test_missing_rate_is_none_not_zero():
    assert parse_rate_text("Competitive salary") is None
    assert parse_rate_text(None) is None
