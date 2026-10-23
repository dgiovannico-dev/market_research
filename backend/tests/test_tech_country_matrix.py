"""Unit / smoke tests for tech×country matrix."""

from unittest.mock import MagicMock

from app.analytics.tech_country import tech_country_matrix


def test_empty_corpus_matrix():
    db = MagicMock()
    db.scalar.return_value = 0
    db.execute.return_value.all.return_value = []

    out = tech_country_matrix(db, days=30, min_evidence="all")
    assert out["period_days"] == 30
    assert out["sample_size"] == 0
    assert out["technologies"] == []
    assert out["countries"] == []
    assert out["cells"] == []
    assert "limits" in out
    assert out["excluded_thin_n"] == 0


def test_matrix_top_axes_and_min_cell():
    """Aggregate path: top tech/country by totals; cells below min_cell dropped."""
    db = MagicMock()
    # First scalar = sample_size from corpus subquery
    db.scalar.return_value = 10
    # (technology, country_code, distinct jobs)
    db.execute.return_value.all.return_value = [
        ("Java", "CH", 5),
        ("Java", "DE", 3),
        ("Python", "CH", 4),
        ("Python", "DE", 1),  # below min_cell=2
        ("Rust", "CH", 2),
        ("Go", "AT", 1),  # Go/AT may fall off top axes
    ]

    out = tech_country_matrix(
        db,
        days=30,
        min_evidence="all",
        top_tech=2,
        top_country=2,
        min_cell=2,
    )
    assert out["sample_size"] == 10
    assert out["technologies"] == ["Java", "Python"]  # 8 and 5
    assert out["countries"] == ["CH", "DE"]  # CH=11, DE=4
    cell_map = {(c["technology"], c["country_code"]): c["jobs"] for c in out["cells"]}
    assert cell_map[("Java", "CH")] == 5
    assert cell_map[("Java", "DE")] == 3
    assert cell_map[("Python", "CH")] == 4
    assert ("Python", "DE") not in cell_map  # min_cell
    assert ("Rust", "CH") not in cell_map  # not in top_tech
