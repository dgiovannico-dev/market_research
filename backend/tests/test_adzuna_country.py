"""Adzuna raw geo tag → Job.country_code mapping."""

from app.ingestion.adzuna_country import (
    country_code_from_adzuna_raw,
    country_code_from_collector_raw,
    normalize_adzuna_country_code,
)


def test_normalize_gb_and_uk_to_gb():
    assert normalize_adzuna_country_code("gb") == "GB"
    assert normalize_adzuna_country_code("UK") == "GB"
    assert normalize_adzuna_country_code(" Gb ") == "GB"


def test_normalize_iso_alpha2_uppercases():
    assert normalize_adzuna_country_code("it") == "IT"
    assert normalize_adzuna_country_code("de") == "DE"
    assert normalize_adzuna_country_code("us") == "US"


def test_normalize_rejects_invalid():
    assert normalize_adzuna_country_code(None) is None
    assert normalize_adzuna_country_code("") is None
    assert normalize_adzuna_country_code("   ") is None
    assert normalize_adzuna_country_code("gbr") is None
    assert normalize_adzuna_country_code("1") is None


def test_country_code_from_adzuna_raw():
    assert country_code_from_adzuna_raw({"_adzuna_country": "gb"}) == "GB"
    assert country_code_from_adzuna_raw({"id": 1}) is None
    assert country_code_from_adzuna_raw(None) is None


def test_country_code_from_collector_raw_generic_iso():
    assert country_code_from_collector_raw({"country": "bg"}) == "BG"
    assert country_code_from_collector_raw({"country_code": "AU"}) == "AU"
    assert country_code_from_collector_raw({"_adzuna_country": "it"}) == "IT"
    assert country_code_from_collector_raw({"country": "Bulgaria"}) is None


def test_stamp_country_code():
    from app.ingestion.adzuna_country import stamp_country_code

    assert stamp_country_code(None, "no") == {"country_code": "NO"}
    assert stamp_country_code({"x": 1}, "ph")["country_code"] == "PH"
    assert "country_code" not in stamp_country_code({}, "sweden")
