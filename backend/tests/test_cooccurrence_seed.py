"""skill_cooccurrence seed / neighbor_limit filtering."""

from app.analytics.cooccurrence import _clamp_neighbor_limit, skill_cooccurrence
from app.storage.db import SessionLocal


def test_clamp_neighbor_limit():
    assert _clamp_neighbor_limit(None) is None
    assert _clamp_neighbor_limit(0) == 1
    assert _clamp_neighbor_limit(30) == 30
    assert _clamp_neighbor_limit(500) == 100


def test_cooccurrence_seed_pairs_involve_seed_only():
    db = SessionLocal()
    try:
        global_out = skill_cooccurrence(db, days=90, min_support=2, lens="market")
        items = global_out.get("items") or []
        if not items:
            # Empty corpus — still assert metadata shape.
            seeded = skill_cooccurrence(
                db, days=90, min_support=2, lens="market", seed="Python", neighbor_limit=5
            )
            assert seeded.get("seed") == "Python"
            assert seeded.get("neighbor_limit") == 5
            assert isinstance(seeded.get("items"), list)
            return

        seed = items[0]["tech_a"]
        seeded = skill_cooccurrence(
            db,
            days=90,
            min_support=2,
            lens="market",
            seed=seed,
            neighbor_limit=5,
        )
        assert seeded.get("seed") == seed
        assert seeded.get("neighbor_limit") == 5
        assert len(seeded.get("items") or []) <= 5
        for row in seeded.get("items") or []:
            assert seed in (row["tech_a"], row["tech_b"])

        # Case-insensitive seed resolves to canonical Technology label.
        seeded_ci = skill_cooccurrence(
            db,
            days=90,
            min_support=2,
            lens="market",
            seed=seed.lower(),
            neighbor_limit=5,
        )
        assert seeded_ci.get("seed") == seed
        assert len(seeded_ci.get("items") or []) == len(seeded.get("items") or [])
    finally:
        db.rollback()
        db.close()
