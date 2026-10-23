"""Unit tests for Demand Compass evidence-coach briefs (Task 8)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from app.llm.briefs import BRIEF_TYPES, MIN_SAMPLE, render_brief
from app.llm.brief_support import THIN_SAMPLE, base_payload
from app.storage.models import SearchQuery

REQUIRED_KEYS = {
    "brief_type",
    "lens",
    "sample_size",
    "evidence",
    "narrative",
    "limits",
    "methodology_version",
    "status",
    "min_evidence",
    "excluded_thin_n",
}


@pytest.fixture()
def db():
    return MagicMock(name="db")


def _assert_structure(payload: dict, brief_type: str) -> None:
    assert REQUIRED_KEYS <= set(payload.keys())
    assert payload["brief_type"] == brief_type
    assert isinstance(payload["evidence"], list)
    assert isinstance(payload["narrative"], str)
    assert payload["methodology_version"]
    assert payload["min_evidence"] == "standard"
    assert "n=" in payload["narrative"] or payload["status"] == "refused"


def test_base_payload_includes_evidence_meta():
    out = base_payload(
        brief_type="rising_cooling",
        lens="market",
        sample_size=10,
        evidence=[],
        narrative="n=10",
        limits="x",
        status="thin_sample",
        excluded_thin_n=3,
    )
    assert out["min_evidence"] == "standard"
    assert out["excluded_thin_n"] == 3


@patch("app.application.briefs.handlers.lens_excluded_thin_n", return_value=0)
@patch("app.application.briefs.handlers.lens_sample_size", return_value=2)
def test_refuses_thin_sample(mock_n, mock_ex, db):
    out = render_brief(db, brief_type="rising_cooling", lens="market")
    _assert_structure(out, "rising_cooling")
    assert out["status"] == "refused"
    assert out["sample_size"] == 2
    assert out["evidence"] == []
    assert mock_n.called
    assert "min_evidence=standard" in out["limits"]


@patch("app.application.briefs.handlers.rate_explorer")
@patch("app.application.briefs.handlers.kpis.technology_trends")
@patch("app.application.briefs.handlers.lens_excluded_thin_n", return_value=4)
@patch("app.application.briefs.handlers.lens_sample_size", return_value=50)
def test_rising_cooling_wraps_technology_trends(mock_n, mock_ex, mock_trends, mock_rates, db):
    mock_trends.return_value = {
        "period_days": 90,
        "items": [
            {
                "technology": "Python",
                "growth_pct": 20.0,
                "sample_size": 12,
                "status": "ok",
                "recent_mentions": 8,
                "previous_mentions": 4,
            },
            {
                "technology": "Java",
                "growth_pct": -10.0,
                "sample_size": 10,
                "status": "ok",
                "recent_mentions": 4,
                "previous_mentions": 6,
            },
        ],
    }
    mock_rates.return_value = {"items": [], "jobs_with_rates": 0, "disclaimer": "x"}
    out = render_brief(db, brief_type="rising_cooling", lens="market", period_days=90)
    _assert_structure(out, "rising_cooling")
    assert out["status"] == "ok"
    assert out["lens"] == "market"
    assert out["sample_size"] == 50
    assert out["excluded_thin_n"] == 4
    assert any(e.get("metric") == "technology_trends" for e in out["evidence"])
    assert "Python" in out["narrative"]
    mock_trends.assert_called_once()
    assert mock_trends.call_args.kwargs.get("days") == 90


@patch("app.application.briefs.handlers.country_comparison")
@patch("app.application.briefs.handlers.lens_excluded_thin_n", return_value=0)
@patch("app.application.briefs.handlers.lens_sample_size", return_value=12)
def test_where_demand_thin_disclose(mock_n, mock_ex, mock_geo, db):
    mock_geo.return_value = {
        "period_days": 90,
        "disclaimer": "obs",
        "items": [
            {
                "country_code": "DE",
                "jobs_observed": 8,
                "remote_share": 0.5,
            }
        ],
    }
    out = render_brief(db, brief_type="where_demand")
    _assert_structure(out, "where_demand")
    assert out["status"] == "thin_sample"
    assert MIN_SAMPLE <= out["sample_size"] < THIN_SAMPLE
    assert "DE" in out["narrative"]


@patch("app.application.briefs.handlers_adjacent.skill_cooccurrence")
@patch("app.application.briefs.handlers_adjacent.profile_skill_names", return_value={"Python"})
@patch("app.application.briefs.handlers_adjacent.lens_excluded_thin_n", return_value=0)
@patch("app.application.briefs.handlers_adjacent.lens_sample_size", return_value=40)
def test_adjacent_uses_cooccurrence(mock_n, mock_ex, mock_owned, mock_co, db):
    mock_co.return_value = {
        "jobs_analyzed": 40,
        "items": [
            {
                "tech_a": "Python",
                "tech_b": "LangGraph",
                "support": 9,
                "lift": 2.1,
            }
        ],
    }
    out = render_brief(db, brief_type="adjacent", lens="market")
    _assert_structure(out, "adjacent")
    assert out["status"] == "ok"
    assert "LangGraph" in out["narrative"]


@patch("app.application.briefs.handlers.kpis.dashboard_summary")
@patch("app.application.briefs.handlers.lens_excluded_thin_n", return_value=0)
@patch("app.application.briefs.handlers.lens_sample_size", return_value=30)
def test_focus_vs_market_compare(mock_n, mock_ex, mock_summary, db):
    mock_summary.return_value = {
        "lens": "compare",
        "market_n": 20,
        "focus_n": 8,
        "overlap_n": 3,
        "market": {"kpis": []},
        "focus": {"kpis": []},
    }
    out = render_brief(db, brief_type="focus_vs_market", query_ids=[1])
    _assert_structure(out, "focus_vs_market")
    assert out["lens"] == "compare"
    assert "Market jobs=20" in out["narrative"]
    mock_summary.assert_called_once()
    assert mock_summary.call_args.kwargs.get("lens") == "compare"


@patch("app.application.briefs.handlers_adjacent.skill_cooccurrence")
@patch("app.application.briefs.handlers_adjacent.profile_skill_names", return_value={"Python"})
@patch("app.application.briefs.handlers_adjacent.lens_excluded_thin_n", return_value=0)
@patch("app.application.briefs.handlers_adjacent.lens_sample_size", return_value=40)
def test_suggest_watches_no_db_insert(mock_n, mock_ex, mock_owned, mock_co, db):
    mock_co.return_value = {
        "jobs_analyzed": 40,
        "items": [
            {
                "tech_a": "Python",
                "tech_b": "FastAPI",
                "support": 7,
                "lift": 1.5,
            }
        ],
    }
    out = render_brief(db, brief_type="suggest_watches", lens="market")
    _assert_structure(out, "suggest_watches")
    assert "proposed_intents" in out
    assert out["proposed_intents"]
    assert out["proposed_intents"][0]["query_text"] == "FastAPI"
    assert "Nothing saved" in out["narrative"] or "accept" in out["narrative"].lower()

    # Never persist SearchQuery
    db.add.assert_not_called()
    db.commit.assert_not_called()
    # Guard against accidental ORM construction via session
    for call in db.method_calls:
        assert "SearchQuery" not in str(call)


@patch("app.application.briefs.handlers.rate_explorer")
@patch("app.application.briefs.handlers.kpis.technology_trends")
@patch("app.application.briefs.handlers.lens_excluded_thin_n", return_value=0)
@patch("app.application.briefs.handlers.lens_sample_size", return_value=50)
def test_rising_cooling_passes_country_code(mock_n, mock_ex, mock_trends, mock_rates, db):
    mock_trends.return_value = {
        "period_days": 90,
        "countries": ["IT", "CH"],
        "items": [
            {
                "technology": "Python",
                "growth_pct": 15.0,
                "sample_size": 12,
                "status": "ok",
                "recent_mentions": 7,
                "previous_mentions": 5,
            }
        ],
    }
    mock_rates.return_value = {"items": [], "jobs_with_rates": 0, "disclaimer": "x"}
    out = render_brief(
        db,
        brief_type="rising_cooling",
        lens="market",
        country_code="IT,CH",
    )
    _assert_structure(out, "rising_cooling")
    assert out["countries"] == ["IT", "CH"]
    assert "countries=IT,CH" in out["narrative"]
    mock_n.assert_called_once()
    assert mock_n.call_args.kwargs.get("country_code") == "IT,CH"
    assert mock_trends.call_args.kwargs.get("country_code") == "IT,CH"
    assert mock_trends.call_args.kwargs.get("lens") == "market"


def test_brief_types_match_spec():
    assert BRIEF_TYPES == {
        "rising_cooling",
        "where_demand",
        "adjacent",
        "focus_vs_market",
        "suggest_watches",
    }


def test_unknown_brief_type(db):
    out = render_brief(db, brief_type="market_oracle")
    assert out["status"] == "refused"
    assert "Unknown brief_type" in out["narrative"]


def test_search_query_not_imported_for_persist_path():
    """suggest_watches module must not INSERT intents (accept is separate API)."""
    import app.application.briefs.handlers as h
    import app.application.briefs.handlers_adjacent as adj

    for mod in (h, adj):
        src = open(mod.__file__, encoding="utf-8").read()
        assert "db.add" not in src
        assert "db.commit" not in src
    assert SearchQuery.__name__  # model exists elsewhere for accept API
