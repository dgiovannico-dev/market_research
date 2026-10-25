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


def test_propose_dashboard_skill_compare_avoids_global_rise_cool():
    spec = propose_dashboard("Meglio java o python e perchè scegliere uno o l'altro?")
    techs = [t.lower() for t in spec.filters.technologies]
    assert "java" in techs and "python" in techs
    widget_ids = {w.id for w in spec.widgets}
    assert "chart_compare_trends" in widget_ids
    assert "chart_trends" not in widget_ids
    assert "chart_countries" not in widget_ids
    compare_w = next(w for w in spec.widgets if w.id == "chart_compare_trends")
    assert compare_w.params.get("focus_technologies")
    assert "vs" in (spec.title or "").lower() or "compare" in (spec.title or "").lower()
    assert validate_spec(spec).ok


def test_propose_report_observed_only():
    spec = propose_report("Report settimanale rates e skill gaps")
    assert spec.narrative_policy == "observed_only"
    assert any(s.kind == "rates" for s in spec.sections)
    assert validate_spec(spec).ok


def test_report_rejects_non_observed_policy():
    with pytest.raises(ValidationError):
        ReportSpec(title="x", narrative_policy="creative")  # type: ignore[arg-type]
