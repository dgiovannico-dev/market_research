"""Country hint expansion + backfill resolution."""

from app.classification.rules import _detect_country, classify_job
from app.ingestion.adzuna_country import stamp_country_code
from app.ingestion.country_backfill import resolve_country_code
from app.ingestion.geo_defaults import SOURCE_DEFAULT_COUNTRY


def test_detect_endonims_and_us_cities():
    assert _detect_country("Solna, Stockholms län, Sverige", None) == "SE"
    assert _detect_country("Czechia", None) == "CZ"
    assert _detect_country("Bucharest, Romania", None) == "RO"
    assert _detect_country("Santiago, Chile", None) == "CL"
    assert _detect_country("San Francisco, California", None) == "US"
    assert _detect_country("Remote US", None) == "US"
    assert _detect_country("서울, 강남구, 한국", None) == "KR"


def test_detect_it_ch_city_hints():
    assert _detect_country("Milan", None) == "IT"
    assert _detect_country("Rivalta di Torino", None) == "IT"
    assert _detect_country("Bologna", None) == "IT"
    assert _detect_country("Bern", None) == "CH"
    assert _detect_country("Basel", None) == "CH"
    assert _detect_country("Geneva (Genève)", None) == "CH"


def test_stamp_country_code_sets_iso():
    stamped = stamp_country_code({"id": 1}, "se")
    assert stamped["country_code"] == "SE"
    assert stamped["id"] == 1


def test_resolve_prefers_text_over_source_default():
    assert (
        resolve_country_code(
            title="Engineer",
            description=None,
            location="Singapore",
            connector_type="greenhouse",
        )
        == "SG"
    )


def test_resolve_falls_back_to_national_board():
    assert (
        resolve_country_code(
            title="Developer",
            description=None,
            location="Remote",
            connector_type="mpsv",
        )
        == "CZ"
    )
    assert SOURCE_DEFAULT_COUNTRY["arbetsformedlingen"] == "SE"


def test_classify_uses_expanded_hints():
    result = classify_job(
        title="Backend",
        description="Team in Prague",
        location="Praha",
    )
    assert result.country_code == "CZ"
