from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.analytics import kpis
from app.analytics.countries import country_comparison
from app.analytics.positioning import recommendations, skill_gaps
from app.analytics.rates import rate_explorer
from app.core.config import get_settings
from app.llm.provider import get_llm_provider


async def build_weekly_report(db: Session) -> dict[str, Any]:
    settings = get_settings()
    summary = kpis.dashboard_summary(db, days=7)
    trends = kpis.technology_trends(db, days=30, min_support=2)
    countries = country_comparison(db, days=30)
    rates = rate_explorer(db, days=90, min_sample=3)
    gaps = skill_gaps(db, days=90)
    recs = recommendations(db, days=30, limit=10)
    quality = kpis.data_quality_report(db)

    structured = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "methodology_version": settings.methodology_version,
        "period": "7d_summary_plus_30d_context",
        "executive_kpis": summary["kpis"],
        "disclaimer": summary["disclaimer"],
        "technologies_growing": [
            t for t in trends["items"] if t.get("status") == "ok" and (t.get("growth_pct") or 0) > 0
        ][:10],
        "technologies_declining": [
            t for t in trends["items"] if t.get("status") == "ok" and (t.get("growth_pct") or 0) < 0
        ][:10],
        "countries": countries["items"][:12],
        "rates": rates["items"][:12],
        "skill_gaps": gaps.get("gaps", [])[:10] if isinstance(gaps, dict) else [],
        "compatible_jobs": recs.get("items", [])[:10],
        "quality": quality,
        "evidence_policy": "LLM may only narrate numbers present in this structured payload.",
    }

    narrative = None
    provider = get_llm_provider()
    health = await provider.health()
    if health.get("healthy") and provider.name != "none":
        try:
            narrative = await provider.classify_text(
                text=(
                    "Write a weekly market brief in Markdown using ONLY these facts. "
                    "If evidence is insufficient say 'dati insufficienti'. Never invent numbers.\n"
                    f"{structured}"
                ),
                schema_hint={"report_markdown": "string"},
            )
        except Exception as exc:  # noqa: BLE001
            narrative = {"error": str(exc), "fallback": "rules_only_report"}

    markdown = _render_markdown(structured)
    return {
        "structured": structured,
        "markdown": markdown,
        "llm_narrative": narrative,
        "llm_health": health,
    }


def _render_markdown(data: dict[str, Any]) -> str:
    lines = [
        "# Weekly Freelance Market Intelligence Report",
        "",
        f"Generated: {data['generated_at']}",
        "",
        data["disclaimer"],
        "",
        "## Executive KPIs",
    ]
    for kpi in data["executive_kpis"]:
        lines.append(
            f"- **{kpi['metric_name']}**: {kpi['metric_value']} "
            f"(n={kpi['sample_size']}, {kpi['evidence_kind']}) — {kpi['limits']}"
        )
    lines += ["", "## Technologies growing (observed)"]
    if not data["technologies_growing"]:
        lines.append("- dati insufficienti")
    for t in data["technologies_growing"]:
        lines.append(
            f"- {t['technology']}: growth {t['growth_pct']}% "
            f"(recent={t['recent_mentions']}, previous={t['previous_mentions']})"
        )
    lines += ["", "## Technologies declining (observed)"]
    if not data["technologies_declining"]:
        lines.append("- dati insufficienti")
    for t in data["technologies_declining"]:
        lines.append(
            f"- {t['technology']}: growth {t['growth_pct']}% "
            f"(recent={t['recent_mentions']}, previous={t['previous_mentions']})"
        )
    lines += ["", "## Risks & uncertainty", "- Source coverage is partial.", "- Growth can reflect query/source changes."]
    return "\n".join(lines)
