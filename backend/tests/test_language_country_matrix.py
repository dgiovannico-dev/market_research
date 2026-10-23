"""Unit / smoke tests for language×country matrix."""

from unittest.mock import MagicMock

from app.analytics.language_country import language_country_matrix


def test_empty_corpus_language_country_matrix():
    db = MagicMock()
    db.scalar.return_value = 0
    db.execute.return_value.all.return_value = []

    out = language_country_matrix(db, days=30, min_evidence="all")
    assert out["period_days"] == 30
    assert out["sample_size"] == 0
    assert out["languages"] == []
    assert out["countries"] == []
    assert out["cells"] == []
    assert "limits" in out
    assert out["excluded_thin_n"] == 0


def test_language_country_aggregation_and_min_cell():
    """Top language/country by totals; cells below min_cell dropped."""
    db = MagicMock()
    db.scalar.return_value = 10
    # (language_requirements list, country_code)
    db.execute.return_value.all.return_value = [
        (["en", "de"], "CH"),
        (["en"], "CH"),
        (["en"], "DE"),
        (["en"], "DE"),
        (["de"], "CH"),
        (["fr"], "CH"),  # fr may fall off top_language
        (["en"], "AT"),  # AT may fall off top_country
        (["de"], "DE"),  # de×DE = 1 → below min_cell=2
    ]

    out = language_country_matrix(
        db,
        days=30,
        min_evidence="all",
        top_language=2,
        top_country=2,
        min_cell=2,
    )
    assert out["sample_size"] == 10
    # en: CH+CH+DE+DE+AT = 5; de: CH+CH+DE = 3; fr: 1
    assert out["languages"] == ["en", "de"]
    # CH: en×2 + de×2 + fr = 5 job-lang hits; DE: en×2 + de = 3
    assert out["countries"] == ["CH", "DE"]
    cell_map = {(c["language"], c["country_code"]): c["jobs"] for c in out["cells"]}
    assert cell_map[("en", "CH")] == 2
    assert cell_map[("en", "DE")] == 2
    assert cell_map[("de", "CH")] == 2
    assert ("de", "DE") not in cell_map  # min_cell
    assert ("fr", "CH") not in cell_map  # not in top_language
    assert ("en", "AT") not in cell_map  # not in top_country


def test_language_country_normalizes_codes():
    db = MagicMock()
    db.scalar.return_value = 3
    db.execute.return_value.all.return_value = [
        (["EN", " De "], "ch"),
        (["en"], "CH"),
        ([123, None, ""], "CH"),  # ignored junk
    ]

    out = language_country_matrix(
        db,
        days=14,
        min_evidence="all",
        top_language=5,
        top_country=5,
        min_cell=1,
    )
    assert out["languages"] == ["en", "de"]
    cell_map = {(c["language"], c["country_code"]): c["jobs"] for c in out["cells"]}
    assert cell_map[("en", "CH")] == 2
    assert cell_map[("de", "CH")] == 1
