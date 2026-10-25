"""dashboard_summary top_n clamp for top_technologies / top_countries."""

from app.analytics.kpis import _clamp_top_n, dashboard_summary
from app.storage.db import SessionLocal


def test_clamp_top_n_bounds():
    assert _clamp_top_n(0) == 1
    assert _clamp_top_n(-5) == 1
    assert _clamp_top_n(5) == 5
    assert _clamp_top_n(100) == 100
    assert _clamp_top_n(500) == 100


def test_dashboard_summary_top_n_caps_lists():
    db = SessionLocal()
    try:
        out5 = dashboard_summary(db, days=30, lens="market", top_n=5)
        assert len(out5.get("top_technologies") or []) <= 5
        assert len(out5.get("top_countries") or []) <= 5

        out100 = dashboard_summary(db, days=30, lens="market", top_n=100)
        assert len(out100.get("top_technologies") or []) <= 100
        assert len(out100.get("top_countries") or []) <= 100
        # Default path must not explode past 100 even if DB has more.
        assert len(out100.get("top_technologies") or []) <= 100
    finally:
        db.rollback()
        db.close()
