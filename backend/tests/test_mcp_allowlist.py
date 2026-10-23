import os

import pytest

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://fmi:fmi_dev_password_change_me@localhost:5432/fmi",
)
os.environ["ENABLE_SCHEDULER"] = "false"

from app.mcp.allowlist import assert_readonly_sql, clamp_limit
from app.mcp.handlers import tool_get_observed_counts, tool_run_readonly_query
from app.mcp.render_report import materialize_report
from app.mcp.specs import ReportSection, ReportSpec
from app.storage.db import SessionLocal


def test_reject_delete():
    r = assert_readonly_sql("DELETE FROM jobs")
    assert r.ok is False


def test_reject_non_allowlisted_table():
    r = assert_readonly_sql("SELECT * FROM audit_logs")
    assert r.ok is False
    assert "not allowed" in (r.error or "") or "not allowlisted" in (r.error or "")


def test_accept_select_jobs():
    r = assert_readonly_sql("SELECT count(*) AS c FROM jobs")
    assert r.ok is True
    assert "jobs" in r.tables


def test_clamp_limit():
    assert clamp_limit(9999) == 500
    assert clamp_limit(0) == 1


def test_run_readonly_query_live():
    out = tool_run_readonly_query("SELECT count(*) AS c FROM jobs", limit=10)
    assert out["ok"] is True
    assert out["row_count"] >= 1
    assert "c" in out["columns"]


def test_get_observed_counts_live():
    out = tool_get_observed_counts(90)
    assert "unique_jobs_in_period" in out
    assert out["evidence_kind"] == "observed"


def test_materialize_report_no_invented_rates():
    db = SessionLocal()
    try:
        spec = ReportSpec(
            title="rates check",
            period_days=1,
            sections=[ReportSection(kind="rates"), ReportSection(kind="summary")],
        )
        # Force empty sample path by using a tiny window; still must not invent EUR
        result = materialize_report(db, spec)
        assert result["ok"] is True
        narrative = result["narrative"].lower()
        assert "eur" not in narrative or "undeclared" in narrative or "insufficient" in narrative
        rates_sec = next(s for s in result["sections"] if s["kind"] == "rates")
        if rates_sec.get("insufficient_data"):
            assert "undeclared" in (rates_sec.get("note") or "").lower() or rates_sec["data"][
                "jobs_with_rate_in_period"
            ] == 0
    finally:
        db.close()
