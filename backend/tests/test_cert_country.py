"""Unit / smoke tests for certifications × country."""

from unittest.mock import MagicMock

from app.analytics.cert_country import certifications_by_country


def test_empty_corpus_by_country():
    db = MagicMock()
    db.scalar.return_value = 0
    db.execute.return_value.all.return_value = []

    out = certifications_by_country(db, days=30, min_evidence="all")
    assert out["period_days"] == 30
    assert out["sample_size"] == 0
    assert out["map_items"] == []
    assert out["countries"] == []
    assert out["unknown_jobs"] == 0


def test_by_country_ranks_and_map():
    db = MagicMock()
    db.scalar.return_value = 20

    jobs_rows = [
        ("IT", 8),
        ("CH", 5),
        ("unknown", 2),
        ("DE", 1),
    ]
    cell_rows = [
        ("IT", "AWS SAA", "aws-saa", 4),
        ("IT", "CKA", "cka", 3),
        ("CH", "AWS SAA", "aws-saa", 3),
        ("CH", "PMP", "pmp", 2),
        ("DE", "CKA", "cka", 1),
        ("unknown", "AWS SAA", "aws-saa", 1),
    ]

    def _exec_side_effect(*_a, **_k):
        mock = MagicMock()
        # First execute = jobs_with_cert; second = cells
        if not hasattr(_exec_side_effect, "n"):
            _exec_side_effect.n = 0
        _exec_side_effect.n += 1
        if _exec_side_effect.n == 1:
            mock.all.return_value = jobs_rows
        else:
            mock.all.return_value = cell_rows
        return mock

    db.execute.side_effect = _exec_side_effect

    out = certifications_by_country(
        db,
        days=90,
        min_evidence="all",
        top_n_per_country=2,
        top_countries=10,
    )
    assert out["sample_size"] == 20
    assert out["unknown_jobs"] == 2
    codes = [m["country_code"] for m in out["map_items"]]
    assert codes == ["IT", "CH", "DE"]
    assert out["map_items"][0]["jobs"] == 8

    it = next(c for c in out["countries"] if c["country_code"] == "IT")
    assert it["jobs_with_certs"] == 8
    assert it["top_certification"] == "AWS SAA"
    assert it["top_mentions"] == 4
    assert [x["slug"] for x in it["top"]] == ["aws-saa", "cka"]
