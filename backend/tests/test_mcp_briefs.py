"""MCP Demand Compass briefs (SPEC-research-intents §10 / SPEC-mcp-analytics)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from app.llm.briefs import BRIEF_TYPES
from app.mcp.briefs import render_demand_brief
from app.mcp.endpoints import list_analytics_endpoints
from app.mcp.handlers import tool_evidence_rules, tool_render_demand_brief
from app.mcp.server import build_mcp
from app.storage.models import SearchQuery

REQUIRED_KEYS = {"brief_type", "sample_size", "narrative", "limits"}


@pytest.fixture()
def db():
    return MagicMock(name="db")


def _stub_brief(brief_type: str) -> dict:
    return {
        "brief_type": brief_type,
        "lens": "market",
        "sample_size": 40,
        "evidence": [],
        "narrative": f"Lens=market, n=40. brief={brief_type}.",
        "limits": "Observed only; disclose n=.",
        "methodology_version": "test",
        "status": "ok",
    }


def test_render_demand_brief_tool_registered():
    mcp = build_mcp()
    names = set(mcp._tool_manager._tools.keys())  # noqa: SLF001
    assert "render_demand_brief" in names


def test_endpoints_include_brief_and_accept():
    paths = {e["path"] for e in list_analytics_endpoints()}
    assert "/api/v1/assistant/brief" in paths
    assert "/api/v1/research/watches/accept" in paths


def test_evidence_rules_mention_briefs():
    text = tool_evidence_rules().lower()
    assert "render_demand_brief" in text
    assert "suggest_watches" in text
    assert "evidence_tier" in text
    assert "min_evidence" in text
    assert "/api/v1/market/quality" in text


def test_endpoints_document_min_evidence_on_gated_routes():
    gated = {
        "/api/v1/market/rates",
        "/api/v1/market/skills/cooccurrence",
        "/api/v1/market/trends",
        "/api/v1/assistant/brief",
    }
    for ep in list_analytics_endpoints():
        if ep["path"] in gated:
            assert "min_evidence" in ep["purpose"].lower()


def test_quality_endpoint_documents_thin_share():
    for ep in list_analytics_endpoints():
        if ep["path"] == "/api/v1/market/quality":
            purpose = ep["purpose"].lower()
            assert "pct_thin" in purpose
            assert "thin" in purpose
            break
    else:
        raise AssertionError("quality endpoint missing from catalog")


@pytest.mark.parametrize("brief_type", sorted(BRIEF_TYPES))
@patch("app.mcp.handlers.render_demand_brief")
@patch("app.mcp.handlers._session_factory")
def test_tool_render_demand_brief_each_type(mock_factory, mock_render, brief_type):
    session = MagicMock(name="session")
    mock_factory.return_value = lambda: session
    mock_render.return_value = _stub_brief(brief_type)

    out = tool_render_demand_brief(brief_type, lens="market", period_days=90)

    assert REQUIRED_KEYS <= set(out.keys())
    assert out["brief_type"] == brief_type
    assert isinstance(out["sample_size"], int)
    assert isinstance(out["narrative"], str) and out["narrative"]
    assert isinstance(out["limits"], str) and out["limits"]
    mock_render.assert_called_once_with(
        session,
        brief_type=brief_type,
        lens="market",
        query_ids=None,
        period_days=90,
        country_code=None,
    )
    session.close.assert_called_once()
    if brief_type == "suggest_watches":
        session.add.assert_not_called()
        session.commit.assert_not_called()


@patch("app.mcp.handlers.render_demand_brief")
@patch("app.mcp.handlers._session_factory")
def test_tool_render_demand_brief_forwards_country_code(mock_factory, mock_render):
    session = MagicMock(name="session")
    mock_factory.return_value = lambda: session
    mock_render.return_value = _stub_brief("rising_cooling")

    tool_render_demand_brief("rising_cooling", lens="market", country_code="DE")

    mock_render.assert_called_once_with(
        session,
        brief_type="rising_cooling",
        lens="market",
        query_ids=None,
        period_days=90,
        country_code="DE",
    )


@patch("app.application.briefs.handlers_adjacent.skill_cooccurrence")
@patch("app.application.briefs.handlers_adjacent.profile_skill_names", return_value={"Python"})
@patch("app.application.briefs.handlers_adjacent.lens_excluded_thin_n", return_value=0)
@patch("app.application.briefs.handlers_adjacent.lens_sample_size", return_value=40)
def test_suggest_watches_does_not_create_search_query(mock_n, mock_ex, mock_owned, mock_co, db):
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
    out = render_demand_brief(db, brief_type="suggest_watches", lens="market")
    assert REQUIRED_KEYS <= set(out.keys())
    assert out["brief_type"] == "suggest_watches"
    assert out.get("min_evidence") == "standard"
    assert "proposed_intents" in out
    assert out["proposed_intents"]
    assert "n=" in out["narrative"]

    db.add.assert_not_called()
    db.commit.assert_not_called()
    for call in db.method_calls:
        assert "SearchQuery" not in str(call)
    assert SearchQuery.__tablename__  # model exists for accept API only


@patch("app.application.briefs.handlers.lens_excluded_thin_n", return_value=0)
@patch("app.application.briefs.handlers.lens_sample_size", return_value=2)
def test_wrapper_refuses_thin_and_discloses_n(mock_n, mock_ex, db):
    out = render_demand_brief(db, brief_type="rising_cooling", lens="market")
    assert REQUIRED_KEYS <= set(out.keys())
    assert out["status"] == "refused"
    assert out["sample_size"] == 2
    assert out["evidence"] == []
    assert out.get("min_evidence") == "standard"


def test_brief_types_match_spec():
    assert BRIEF_TYPES == {
        "rising_cooling",
        "where_demand",
        "adjacent",
        "focus_vs_market",
        "suggest_watches",
    }


def test_unknown_brief_type(db):
    out = render_demand_brief(db, brief_type="market_oracle")
    assert out["status"] == "refused"
    assert "Unknown brief_type" in out["narrative"]
