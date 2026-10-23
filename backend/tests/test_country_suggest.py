"""Intent → CountryFilter suggestion helpers (C5)."""

from types import SimpleNamespace

from app.research.country_suggest import (
    missing_suggested_countries,
    suggested_countries_from_intents,
)


def test_suggested_skips_disabled_and_all():
    intents = [
        SimpleNamespace(enabled=True, countries=["it", "CH", "ALL", ""]),
        SimpleNamespace(enabled=False, countries=["DE"]),
        SimpleNamespace(enabled=True, countries=["IT", "fr"]),
    ]
    assert suggested_countries_from_intents(intents) == ["IT", "CH", "FR"]


def test_missing_against_current_filter():
    assert missing_suggested_countries(["IT"], ["IT", "CH", "DE"]) == ["CH", "DE"]
    assert missing_suggested_countries(["it", "ch"], ["IT", "CH"]) == []
