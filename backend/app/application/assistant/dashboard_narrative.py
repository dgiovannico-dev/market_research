"""Human-language dashboard narrative grounded on observed KPIs / trends."""

from __future__ import annotations

import json
from typing import Any, Literal, Optional

from sqlalchemy.orm import Session

from app.adapters.driven.llm.provider import get_llm_provider
from app.analytics import kpis as kpi_mod
from app.application.assistant.propose import parse_intent_from_prompt
from app.application.llm.runtime_config import resolve_llm_settings

Locale = Literal["en", "it"]

_SYSTEM_EN = (
    "You are a freelance market analyst for FMI. "
    "Write a clear, human narrative (2–4 short paragraphs) about the observed data only. "
    "Use only numbers present in the JSON evidence. Never invent TAM, total market size, "
    "or rates that are not in the payload. Mention sample size (n). "
    "If evidence.compared is present, answer the user's A-vs-B question using ONLY those "
    "rows (mentions + growth_pct). Never claim two skills have the same job count unless "
    "the JSON shows identical values. Do not pivot to unrelated rising/cooling lists. "
    "If the sample is thin, say so. Plain language, no markdown headings."
)
_SYSTEM_IT = (
    "Sei un analista di mercato freelance per FMI. "
    "Scrivi una narrativa chiara in italiano (2–4 paragrafi brevi) basata solo sui dati osservati. "
    "Usa solo i numeri presenti nel JSON. Non inventare dimensioni di mercato o tariffe assenti. "
    "Se evidence.compared è presente, rispondi al confronto A-vs-B usando SOLO quelle righe "
    "(mentions + growth_pct). Non dire che due skill hanno lo stesso numero di job se i valori "
    "nel JSON sono diversi. Non spostarti su liste di crescita/calo non richieste. "
    "Cita il sample size (n). Se il campione è sottile, dillo. Linguaggio semplice, senza titoli markdown."
)


def _trend_slice(items: list[dict[str, Any]], *, rising: bool, limit: int = 8) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for it in items:
        if it.get("status") not in (None, "ok"):
            continue
        g = it.get("growth_pct")
        if g is None:
            continue
        try:
            g_f = float(g)
        except (TypeError, ValueError):
            continue
        if rising and g_f <= 0:
            continue
        if not rising and g_f >= 0:
            continue
        out.append(
            {
                "technology": it.get("technology") or it.get("name"),
                "growth_pct": round(g_f, 2),
                "sample_size": it.get("sample_size"),
            }
        )
        if len(out) >= limit:
            break
    return out


def _match_compared(
    items: list[dict[str, Any]], technologies: list[str]
) -> list[dict[str, Any]]:
    if not technologies:
        return []
    by_lower = {
        str(it.get("technology") or "").lower(): it
        for it in items
        if it.get("technology")
    }
    out: list[dict[str, Any]] = []
    for key in technologies:
        it = by_lower.get(str(key).lower())
        if not it:
            out.append(
                {
                    "technology": key,
                    "recent_mentions": 0,
                    "previous_mentions": 0,
                    "sample_size": 0,
                    "growth_pct": None,
                    "status": "not_found",
                }
            )
            continue
        out.append(
            {
                "technology": it.get("technology"),
                "recent_mentions": it.get("recent_mentions"),
                "previous_mentions": it.get("previous_mentions"),
                "sample_size": it.get("sample_size"),
                "growth_pct": it.get("growth_pct"),
                "status": it.get("status"),
            }
        )
    return out


def build_evidence_pack(
    db: Session,
    *,
    period_days: int,
    user_prompt: str = "",
    country_code: Optional[str] = None,
) -> dict[str, Any]:
    days = max(1, min(int(period_days), 365))
    summary = kpi_mod.dashboard_summary(db, days=days, top_n=10, country_code=country_code)
    trends = kpi_mod.technology_trends(
        db, days=days, min_support=2, country_code=country_code
    )
    items = list(trends.get("items") or [])
    kpis = list(summary.get("kpis") or [])
    jobs_n = next(
        (int(k["sample_size"]) for k in kpis if k.get("metric_name") == "unique_jobs_observed"),
        0,
    )
    hints = parse_intent_from_prompt(user_prompt or "")
    compared = (
        _match_compared(items, hints.technologies[:4])
        if hints.compare_mode and len(hints.technologies) >= 2
        else []
    )
    pack: dict[str, Any] = {
        "user_prompt": (user_prompt or "").strip()[:500],
        "period_days": days,
        "country_code": country_code,
        "disclaimer": summary.get("disclaimer"),
        "unique_jobs_observed": jobs_n,
        "compare_mode": bool(compared),
        "kpis": [
            {
                "metric_name": k.get("metric_name"),
                "metric_value": k.get("metric_value"),
                "sample_size": k.get("sample_size"),
                "unit": k.get("unit"),
            }
            for k in kpis[:8]
        ],
        "rising": _trend_slice(items, rising=True),
        "cooling": _trend_slice(items, rising=False),
    }
    if compared:
        pack["compared"] = compared
    return pack


def _compare_narrative(evidence: dict[str, Any], locale: Locale) -> str:
    days = evidence.get("period_days")
    n = int(evidence.get("unique_jobs_observed") or 0)
    rows = list(evidence.get("compared") or [])
    bits: list[str] = []
    for x in rows:
        name = x.get("technology")
        sample = x.get("sample_size") or 0
        recent = x.get("recent_mentions") or 0
        g = x.get("growth_pct")
        if locale == "it":
            g_txt = f", crescita metà-periodo {round(float(g), 1)}%" if g is not None else ""
            bits.append(f"{name}: {sample} menzioni osservate (recenti {recent}{g_txt})")
        else:
            g_txt = f", half-period growth {round(float(g), 1)}%" if g is not None else ""
            bits.append(f"{name}: {sample} observed mentions (recent {recent}{g_txt})")
    joined = "; ".join(bits) if bits else ("nessun dato" if locale == "it" else "no data")
    if locale == "it":
        return (
            f"Confronto sulle skill richieste (corpus FMI, ultimi {days} giorni, n={n} annunci unici). "
            f"{joined}. "
            "Queste sono menzioni negli annunci già raccolti — non una classifica di ROI o di dimensione di mercato. "
            "Scegli in base al tuo stack e al tipo di incarichi che cerchi, non solo al volume grezzo."
        )
    return (
        f"Skill compare in the FMI corpus (last {days} days, n={n} unique jobs). "
        f"{joined}. "
        "These are observed ad mentions — not training ROI or total market size. "
        "Pick based on your stack and the roles you want, not raw volume alone."
    )


def deterministic_narrative(evidence: dict[str, Any], locale: Locale) -> str:
    if evidence.get("compare_mode") and evidence.get("compared"):
        return _compare_narrative(evidence, locale)
    n = int(evidence.get("unique_jobs_observed") or 0)
    days = evidence.get("period_days")
    rising = evidence.get("rising") or []
    cooling = evidence.get("cooling") or []
    if locale == "it":
        if n <= 0:
            return (
                f"Nel periodo di {days} giorni non ci sono abbastanza annunci osservati "
                "in questo database per una lettura affidabile. Allarga la finestra o avvia i collector."
            )
        r_bits = ", ".join(
            f"{x['technology']} ({x['growth_pct']}%, n={x.get('sample_size')})" for x in rising[:5]
        ) or "nessuna tecnologia in forte crescita con campione sufficiente"
        c_bits = ", ".join(
            f"{x['technology']} ({x['growth_pct']}%, n={x.get('sample_size')})" for x in cooling[:5]
        ) or "nessuna tecnologia in chiaro calo con campione sufficiente"
        return (
            f"Nel corpus FMI osserviamo n={n} annunci unici negli ultimi {days} giorni. "
            f"Queste cifre descrivono solo gli annunci memorizzati qui, non la dimensione totale del mercato. "
            f"In crescita (Δ tra le due metà del periodo): {r_bits}. "
            f"In calo: {c_bits}."
        )
    if n <= 0:
        return (
            f"Insufficient observed jobs in the last {days} days in this database. "
            "Widen the period or run collectors."
        )
    r_bits = ", ".join(
        f"{x['technology']} ({x['growth_pct']}%, n={x.get('sample_size')})" for x in rising[:5]
    ) or "no strong risers with enough sample"
    c_bits = ", ".join(
        f"{x['technology']} ({x['growth_pct']}%, n={x.get('sample_size')})" for x in cooling[:5]
    ) or "no clear coolers with enough sample"
    return (
        f"In the FMI corpus we observe n={n} unique jobs over the last {days} days. "
        f"These figures describe stored ads only, not total market size. "
        f"Rising (half-period Δ): {r_bits}. Cooling: {c_bits}."
    )


async def narrate_dashboard(
    db: Session,
    *,
    period_days: int,
    user_prompt: str = "",
    locale: Locale = "en",
    country_code: Optional[str] = None,
) -> dict[str, Any]:
    evidence = build_evidence_pack(
        db,
        period_days=period_days,
        user_prompt=user_prompt,
        country_code=country_code,
    )
    fallback = deterministic_narrative(evidence, locale)
    cfg = resolve_llm_settings(db)
    provider = get_llm_provider(db)
    health = await provider.health()
    # Skill-vs-skill answers must stay numerically faithful — skip LLM paraphrase.
    if evidence.get("compare_mode") and evidence.get("compared"):
        return {
            "narrative": fallback,
            "source": "deterministic",
            "evidence": evidence,
            "llm_health": health,
        }
    use_llm = (
        cfg.provider != "none"
        and cfg.enable_brief_narrative
        and bool(health.get("healthy"))
        and provider.name != "none"
    )
    if not use_llm:
        return {
            "narrative": fallback,
            "source": "deterministic",
            "evidence": evidence,
            "llm_health": health,
        }

    system = _SYSTEM_IT if locale == "it" else _SYSTEM_EN
    user = (
        f"User ask: {evidence.get('user_prompt') or '(none)'}\n"
        f"Evidence JSON:\n{json.dumps(evidence, default=str)[:12000]}"
    )
    try:
        text = await provider.chat(
            [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.2,
        )
        narrative = (text or "").strip() or fallback
        source = "llm" if narrative != fallback else "deterministic"
        return {
            "narrative": narrative,
            "source": source,
            "evidence": evidence,
            "llm_health": health,
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "narrative": fallback,
            "source": "deterministic_fallback",
            "error": str(exc),
            "evidence": evidence,
            "llm_health": health,
        }
