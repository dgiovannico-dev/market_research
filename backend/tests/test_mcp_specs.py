import pytest
from pydantic import ValidationError

from app.mcp.propose import propose_dashboard, propose_report
from app.mcp.semantics import get_semantic_catalog, metric_keys
from app.mcp.specs import DashboardSpec, DashboardWidget, ReportSpec
from app.mcp.validate import validate_spec


def test_semantic_catalog_has_core_metrics():
    keys = metric_keys()
    assert "unique_jobs_observed" in keys
    assert "rates_distribution" in keys
    assert "technology_trends" in keys
    catalog = get_semantic_catalog()
    assert all(m.definition for m in catalog)


def test_dashboard_spec_round_trip():
    spec = DashboardSpec(
        title="Java remote 90d",
        period_days=90,
        view_mode="guided",
        widgets=[
            DashboardWidget(id="k1", type="kpi", metric_key="unique_jobs_observed"),
        ],
    )
    raw = spec.model_dump()
    again = DashboardSpec.model_validate(raw)
    assert again.title == "Java remote 90d"
    assert again.disclaimer_mode == "guided"


def test_unknown_widget_type_rejected_by_pydantic():
    with pytest.raises(ValidationError):
        DashboardWidget(id="x", type="magic", metric_key="unique_jobs_observed")  # type: ignore[arg-type]


def test_validate_unknown_metric_fails_closed():
    spec = DashboardSpec(
        title="bad",
        widgets=[DashboardWidget(id="k1", type="kpi", metric_key="not_a_real_metric")],
    )
    result = validate_spec(spec)
    assert result.ok is False
    assert any("unknown metric_key" in e for e in result.errors)


def test_propose_dashboard_from_prompt():
    spec = propose_dashboard("Mostra trend Java + RAG ultimi 90 giorni")
    assert spec.period_days == 90
    assert "java" in [t.lower() for t in spec.filters.technologies]
    assert validate_spec(spec).ok


def test_propose_report_observed_only():
    spec = propose_report("Report settimanale rates e skill gaps")
    assert spec.narrative_policy == "observed_only"
    assert any(s.kind == "rates" for s in spec.sections)
    assert validate_spec(spec).ok


def test_report_rejects_non_observed_policy():
    with pytest.raises(ValidationError):
        ReportSpec(title="x", narrative_policy="creative")  # type: ignore[arg-type]
