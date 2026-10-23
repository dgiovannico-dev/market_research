"""Unit / smoke tests for role×technology matrix."""

from unittest.mock import MagicMock

from app.analytics.role_tech import role_tech_matrix


def test_empty_corpus_role_tech_matrix():
    db = MagicMock()
    db.scalar.return_value = 0
    db.execute.return_value.all.return_value = []

    out = role_tech_matrix(db, days=30, min_evidence="all")
    assert out["period_days"] == 30
    assert out["sample_size"] == 0
    assert out["role_families"] == []
    assert out["technologies"] == []
    assert out["cells"] == []
    assert "limits" in out
    assert "role_family" in out["limits"]
    assert out["excluded_thin_n"] == 0


def test_role_tech_aggregation_ranking():
    """Top role/tech by totals; lower ranks fall off axes."""
    db = MagicMock()
    db.scalar.return_value = 12
    # (role_family, technology, distinct jobs)
    db.execute.return_value.all.return_value = [
        ("backend", "Java", 5),
        ("backend", "Python", 4),
        ("devops", "Java", 3),
        ("devops", "Go", 2),
        ("frontend", "TypeScript", 2),
        ("data", "Python", 1),
    ]

    out = role_tech_matrix(
        db,
        days=30,
        min_evidence="all",
        top_role=2,
        top_tech=2,
        min_cell=1,
    )
    assert out["sample_size"] == 12
    # backend=9, devops=5, frontend=2, data=1
    assert out["role_families"] == ["backend", "devops"]
    # Java=8, Python=5, Go=2, TypeScript=2
    assert out["technologies"] == ["Java", "Python"]
    cell_map = {(c["role_family"], c["technology"]): c["jobs"] for c in out["cells"]}
    assert cell_map[("backend", "Java")] == 5
    assert cell_map[("backend", "Python")] == 4
    assert cell_map[("devops", "Java")] == 3
    assert ("devops", "Go") not in cell_map  # not in top_tech
    assert ("frontend", "TypeScript") not in cell_map  # not in top_role


def test_role_tech_min_cell_and_empty_role():
    """Cells below min_cell dropped; null/empty role_family excluded from axes."""
    db = MagicMock()
    db.scalar.return_value = 10
    db.execute.return_value.all.return_value = [
        ("backend", "Java", 5),
        ("backend", "Python", 1),  # below min_cell=2
        ("devops", "Java", 3),
        (None, "Java", 4),  # excluded
        ("", "Python", 3),  # excluded
        ("  ", "Go", 2),  # excluded (whitespace-only)
    ]

    out = role_tech_matrix(
        db,
        days=30,
        min_evidence="all",
        top_role=5,
        top_tech=5,
        min_cell=2,
    )
    assert out["role_families"] == ["backend", "devops"]  # 6 and 3; empty roles ignored
    assert out["technologies"] == ["Java", "Python"]  # Go never counted (empty role)
    cell_map = {(c["role_family"], c["technology"]): c["jobs"] for c in out["cells"]}
    assert cell_map[("backend", "Java")] == 5
    assert cell_map[("devops", "Java")] == 3
    assert ("backend", "Python") not in cell_map  # min_cell
    assert all(c["role_family"].strip() for c in out["cells"])
