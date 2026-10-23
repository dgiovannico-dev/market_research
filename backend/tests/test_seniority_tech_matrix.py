"""Unit / smoke tests for seniority×technology matrix."""

from unittest.mock import MagicMock

from app.analytics.seniority_tech import seniority_tech_matrix


def test_empty_corpus_seniority_tech_matrix():
    db = MagicMock()
    db.scalar.return_value = 0
    db.execute.return_value.all.return_value = []

    out = seniority_tech_matrix(db, days=30, min_evidence="all")
    assert out["period_days"] == 30
    assert out["sample_size"] == 0
    assert out["seniorities"] == []
    assert out["technologies"] == []
    assert out["cells"] == []
    assert "limits" in out
    assert "seniority" in out["limits"]
    assert out["excluded_thin_n"] == 0


def test_seniority_tech_aggregation_ranking():
    """Top seniority/tech by totals; lower ranks fall off axes."""
    db = MagicMock()
    db.scalar.return_value = 12
    # (seniority, technology, distinct jobs)
    db.execute.return_value.all.return_value = [
        ("senior", "Java", 5),
        ("senior", "Python", 4),
        ("mid", "Java", 3),
        ("mid", "Go", 2),
        ("junior", "TypeScript", 2),
        ("lead", "Python", 1),
    ]

    out = seniority_tech_matrix(
        db,
        days=30,
        min_evidence="all",
        top_seniority=2,
        top_tech=2,
        min_cell=1,
    )
    assert out["sample_size"] == 12
    # senior=9, mid=5, junior=2, lead=1
    assert out["seniorities"] == ["senior", "mid"]
    # Java=8, Python=5, Go=2, TypeScript=2
    assert out["technologies"] == ["Java", "Python"]
    cell_map = {(c["seniority"], c["technology"]): c["jobs"] for c in out["cells"]}
    assert cell_map[("senior", "Java")] == 5
    assert cell_map[("senior", "Python")] == 4
    assert cell_map[("mid", "Java")] == 3
    assert ("mid", "Go") not in cell_map  # not in top_tech
    assert ("junior", "TypeScript") not in cell_map  # not in top_seniority


def test_seniority_tech_min_cell_and_empty_seniority():
    """Cells below min_cell dropped; null/empty seniority excluded from axes."""
    db = MagicMock()
    db.scalar.return_value = 10
    db.execute.return_value.all.return_value = [
        ("senior", "Java", 5),
        ("senior", "Python", 1),  # below min_cell=2
        ("mid", "Java", 3),
        (None, "Java", 4),  # excluded
        ("", "Python", 3),  # excluded
        ("  ", "Go", 2),  # excluded (whitespace-only)
    ]

    out = seniority_tech_matrix(
        db,
        days=30,
        min_evidence="all",
        top_seniority=5,
        top_tech=5,
        min_cell=2,
    )
    assert out["seniorities"] == ["senior", "mid"]  # 6 and 3; empty seniority ignored
    assert out["technologies"] == ["Java", "Python"]  # Go never counted (empty seniority)
    cell_map = {(c["seniority"], c["technology"]): c["jobs"] for c in out["cells"]}
    assert cell_map[("senior", "Java")] == 5
    assert cell_map[("mid", "Java")] == 3
    assert ("senior", "Python") not in cell_map  # min_cell
    assert all(c["seniority"].strip() for c in out["cells"])
