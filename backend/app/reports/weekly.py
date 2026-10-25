from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Literal, Optional

from sqlalchemy.orm import Session

from app.adapters.driven.llm.provider import get_llm_provider
from app.analytics import kpis
from app.analytics.countries import country_comparison
from app.analytics.positioning import recommendations, skill_gaps
from app.analytics.rates import rate_explorer
from app.application.llm.prompts import resolve_prompt
from app.application.llm.runtime_config import resolve_llm_settings
from app.core.config import get_settings

Locale = Literal["en", "it"]

_KPI_LABELS: dict[str, dict[str, str]] = {
    "unique_jobs_observed": {
        "en": "Unique jobs observed",
        "it": "Annunci unici osservati",
    },
    "freelance_b2b_verified": {
        "en": "Freelance / B2B jobs (high confidence)",
        "it": "Annunci freelance / B2B (alta confidenza)",
    },
    "observed_demand_growth_pct": {
        "en": "Observed demand change",
        "it": "Variazione della domanda osservata",
    },
    "jobs_with_published_rate": {
        "en": "Jobs with a published rate",
        "it": "Annunci con tariffa pubblicata",
    },
    "remote_jobs_observed": {
        "en": "Remote jobs observed",
        "it": "Annunci remote osservati",
    },
}


def format_report_timestamp(value: datetime | str | None = None) -> str:
    """Compact UTC timestamp down to minutes (no micros / seconds)."""
    if value is None:
        dt = datetime.now(timezone.utc)
    elif isinstance(value, datetime):
        dt = value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    else:
        raw = str(value).strip().replace("Z", "+00:00")
        try:
            dt = datetime.fromisoformat(raw)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
        except ValueError:
            return str(value)[:16]
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def format_pct(value: Any, *, locale: Locale = "en") -> str:
    """Percent with exactly two decimal places (locale decimal separator)."""
    try:
        n = float(value)
    except (TypeError, ValueError):
        return "—"
    formatted = f"{n:.2f}"
    if locale == "it":
        formatted = formatted.replace(".", ",")
    return f"{formatted}%"


def format_count(value: Any) -> str:
    try:
        n = float(value)
    except (TypeError, ValueError):
        return "—"
    if abs(n - round(n)) < 1e-9:
        return str(int(round(n)))
    return f"{n:.2f}"


def _kpi_label(name: str, locale: Locale) -> str:
    labels = _KPI_LABELS.get(name)
    if labels:
        return labels.get(locale) or labels["en"]
    return name.replace("_", " ")


def _normalize_locale(locale: Optional[str]) -> Locale:
    return "it" if (locale or "").lower().startswith("it") else "en"


async def build_weekly_report(
    db: Session,
    *,
    locale: Optional[str] = None,
) -> dict[str, Any]:
    loc = _normalize_locale(locale)
    settings = get_settings()
    now = datetime.now(timezone.utc)
    summary = kpis.dashboard_summary(db, days=7, top_n=10)
    trends = kpis.technology_trends(db, days=30, min_support=2)
    countries = country_comparison(db, days=30)
    rates = rate_explorer(db, days=90, min_sample=3)
    gaps = skill_gaps(db, days=90)
    recs = recommendations(db, days=30, limit=10)
    quality = kpis.data_quality_report(db)

    structured = {
        "generated_at": now.isoformat(),
        "generated_at_display": format_report_timestamp(now),
        "methodology_version": settings.methodology_version,
        "period": "7d_summary_plus_30d_context",
        "locale": loc,
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
    cfg = resolve_llm_settings(db)
    provider = get_llm_provider(db)
    health = await provider.health()
    if (
        cfg.provider != "none"
        and cfg.enable_weekly_report
        and health.get("healthy")
        and provider.name != "none"
    ):
        try:
            prompt = resolve_prompt(
                db,
                slug="weekly_report",
                variables={"structured_json": json.dumps(structured, default=str)[:24000]},
            )
            raw = await provider.chat(
                [
                    {"role": "system", "content": prompt["system"]},
                    {"role": "user", "content": prompt["user"]},
                ],
                response_json=True,
            )
            narrative = json.loads(raw or "{}")
            narrative["_prompt_version"] = prompt.get("version")
        except Exception as exc:  # noqa: BLE001
            narrative = {"error": str(exc), "fallback": "rules_only_report"}

    markdown = _render_markdown(structured, locale=loc)
    return {
        "structured": structured,
        "markdown": markdown,
        "llm_narrative": narrative,
        "llm_health": health,
    }


def _render_markdown(data: dict[str, Any], *, locale: Locale = "en") -> str:
    generated = data.get("generated_at_display") or format_report_timestamp(
        data.get("generated_at")
    )
    if locale == "it":
        return _render_markdown_it(data, generated=generated)
    return _render_markdown_en(data, generated=generated)


def _tech_line(t: dict[str, Any], *, locale: Locale, rising: bool) -> str:
    name = t.get("technology") or "?"
    try:
        magnitude = abs(float(t.get("growth_pct")))
    except (TypeError, ValueError):
        magnitude = None
    pct = format_pct(magnitude if magnitude is not None else t.get("growth_pct"), locale=locale)
    recent = format_count(t.get("recent_mentions"))
    previous = format_count(t.get("previous_mentions"))
    if locale == "it":
        direction = "in crescita" if rising else "in calo"
        return (
            f"- **{name}**: {direction} del {pct} "
            f"(menzioni recenti {recent} vs precedenti {previous})"
        )
    direction = "up" if rising else "down"
    return (
        f"- **{name}**: {direction} {pct} "
        f"(recent mentions {recent} vs earlier {previous})"
    )


_LIMIT_IT: dict[str, str] = {
    "Depends on active connectors, queries and import coverage.": (
        "Dipende dai connettori attivi, dalle query e dalla copertura degli import."
    ),
    "Classification is extracted/inferred from text; not manually verified by default.": (
        "Classificazione estratta/inferita dal testo; non verificata a mano di default."
    ),
    "Sensitive to source/query changes; not market growth.": (
        "Sensibile a cambi di fonte/query; non è crescita di mercato."
    ),
    "Many sources omit rates; NULL rates are not treated as zero.": (
        "Molte fonti omettono le tariffe; i valori mancanti non vengono trattati come zero."
    ),
    "Remote != acceptance of Italian residents.": (
        "Remote non implica accettazione di residenti in Italia."
    ),
}


def _human_note(note: str, *, locale: Locale) -> str:
    text = (note or "").strip()
    if not text:
        return ""
    if locale == "it":
        return _LIMIT_IT.get(text, text)
    return text


def _human_disclaimer(text: str, *, locale: Locale) -> str:
    raw = (text or "").strip()
    if locale != "it":
        return raw
    if "not estimates of total market size" in raw.lower() or "not a census" in raw.lower():
        return (
            "I conteggi riflettono solo record osservati e deduplicati in questo database "
            "dalle fonti/import configurati. Non sono stime della dimensione totale del mercato."
        )
    return _LIMIT_IT.get(raw, raw)


def _kpi_line(kpi: dict[str, Any], *, locale: Locale) -> str:
    name = str(kpi.get("metric_name") or "")
    label = _kpi_label(name, locale)
    unit = str(kpi.get("unit") or "")
    raw = kpi.get("metric_value")
    if unit == "pct" or name.endswith("_pct") or "growth_pct" in name:
        value = format_pct(raw, locale=locale)
    else:
        value = format_count(raw)
    n = format_count(kpi.get("sample_size"))
    note = _human_note(str(kpi.get("limits") or ""), locale=locale)
    if locale == "it":
        base = f"- **{label}**: {value} (su {n} annunci osservati)"
    else:
        base = f"- **{label}**: {value} (from {n} observed jobs)"
    if note:
        return f"{base}. {note}"
    return base


def _render_markdown_en(data: dict[str, Any], *, generated: str) -> str:
    lines = [
        "# Weekly Freelance Market Intelligence Report",
        "",
        f"Generated: {generated}",
        "",
        _human_disclaimer(str(data.get("disclaimer") or ""), locale="en"),
        "",
        "## Snapshot of the week",
        "These figures come from jobs we actually collected — not estimates of the whole market.",
        "",
    ]
    for kpi in data.get("executive_kpis") or []:
        lines.append(_kpi_line(kpi, locale="en"))

    lines += ["", "## Technologies gaining mentions"]
    growing = data.get("technologies_growing") or []
    if not growing:
        lines.append("- Not enough data in this window.")
    for t in growing:
        lines.append(_tech_line(t, locale="en", rising=True))

    lines += ["", "## Technologies losing mentions"]
    declining = data.get("technologies_declining") or []
    if not declining:
        lines.append("- Not enough data in this window.")
    for t in declining:
        lines.append(_tech_line(t, locale="en", rising=False))

    lines += [
        "",
        "## What to keep in mind",
        "- We only see sources that are configured and importing successfully.",
        "- A big jump can mean more queries or a new source, not only real demand growth.",
        "- Missing rates stay missing — we never invent averages.",
    ]
    return "\n".join(lines)


def _render_markdown_it(data: dict[str, Any], *, generated: str) -> str:
    lines = [
        "# Report settimanale Freelance Market Intelligence",
        "",
        f"Generato: {generated}",
        "",
        _human_disclaimer(str(data.get("disclaimer") or ""), locale="it"),
        "",
        "## Sintesi della settimana",
        "I numeri arrivano solo dagli annunci che abbiamo raccolto — non sono stime del mercato intero.",
        "",
    ]
    for kpi in data.get("executive_kpis") or []:
        lines.append(_kpi_line(kpi, locale="it"))

    lines += ["", "## Tecnologie in crescita di menzioni"]
    growing = data.get("technologies_growing") or []
    if not growing:
        lines.append("- Dati insufficienti in questa finestra.")
    for t in growing:
        lines.append(_tech_line(t, locale="it", rising=True))

    lines += ["", "## Tecnologie in calo di menzioni"]
    declining = data.get("technologies_declining") or []
    if not declining:
        lines.append("- Dati insufficienti in questa finestra.")
    for t in declining:
        lines.append(_tech_line(t, locale="it", rising=False))

    lines += [
        "",
        "## Cosa tenere a mente",
        "- Vediamo solo le fonti configurate e che importano correttamente.",
        "- Un salto netto può dipendere da nuove query o da una nuova fonte, non solo dalla domanda reale.",
        "- Le tariffe mancanti restano mancanti: non inventiamo medie.",
    ]
    return "\n".join(lines)
