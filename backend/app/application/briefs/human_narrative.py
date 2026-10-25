"""Plain-language brief narratives (en/it). Keep ``n=`` for evidence grounding tests."""

from __future__ import annotations

from typing import Any, Literal, Optional, Sequence

Locale = Literal["en", "it"]


def _lens_label(lens: str, locale: Locale) -> str:
    labels = {
        "en": {"market": "whole market scan", "focus": "your focus intents", "compare": "market vs focus"},
        "it": {"market": "scan di mercato", "focus": "i tuoi intent focus", "compare": "mercato vs focus"},
    }
    return labels.get(locale, labels["en"]).get(lens, lens)


def _tech_bits(rows: Sequence[dict[str, Any]], *, limit: int = 5) -> str:
    parts: list[str] = []
    for t in list(rows)[:limit]:
        name = t.get("technology") or t.get("name") or "?"
        g = t.get("growth_pct")
        n = t.get("sample_size")
        try:
            g_s = f"{float(g):+.0f}%"
        except (TypeError, ValueError):
            g_s = "?"
        parts.append(f"{name} ({g_s}, n={n})")
    return ", ".join(parts)


def rising_cooling_narrative(
    *,
    locale: Locale,
    lens: str,
    n: int,
    period_days: int,
    rising: Sequence[dict[str, Any]],
    cooling: Sequence[dict[str, Any]],
    rate_buckets: int,
    jobs_with_rates: int,
    thin: bool,
    thin_threshold: int,
    geo: str = "",
) -> str:
    lens_l = _lens_label(lens, locale)
    r = _tech_bits(rising) or ("none with enough mentions" if locale == "en" else "nessuna con abbastanza menzioni")
    c = _tech_bits(cooling) or ("none with enough mentions" if locale == "en" else "nessuna con abbastanza menzioni")
    if locale == "it":
        parts = [
            f"Su n={n} annunci osservati negli ultimi {period_days} giorni "
            f"({lens_l}{geo}), confrontiamo la metà recente del periodo con quella precedente.",
            f"In crescita (più menzioni di recente): {r}.",
            f"In calo: {c}.",
        ]
        if thin:
            parts.insert(
                1,
                f"Attenzione: campione sottile (n={n} < {thin_threshold}) — prendi i segnali con cautela.",
            )
        if rate_buckets > 0:
            parts.append(
                f"Ci sono tariffe pubblicate in {rate_buckets} gruppi paese/unità "
                f"(annunci con tariffa: {jobs_with_rates}). Non inventiamo medie se mancano i dati."
            )
        else:
            parts.append("Nessun gruppo stabile di tariffe pubblicate in questa finestra.")
        return " ".join(parts)
    parts = [
        f"Based on n={n} observed jobs over the last {period_days} days "
        f"({lens_l}{geo}), we compare the recent half of the window to the earlier half.",
        f"Rising (more mentions lately): {r}.",
        f"Cooling: {c}.",
    ]
    if thin:
        parts.insert(
            1,
            f"Caution: thin sample (n={n} < {thin_threshold}) — treat signals carefully.",
        )
    if rate_buckets > 0:
        parts.append(
            f"Published rates appear in {rate_buckets} country/unit buckets "
            f"(jobs_with_rates={jobs_with_rates}). We never invent averages when rates are missing."
        )
    else:
        parts.append("No stable published-rate buckets in this window.")
    return " ".join(parts)


def where_demand_narrative(
    *,
    locale: Locale,
    lens: str,
    n: int,
    period_days: int,
    items: Sequence[dict[str, Any]],
    thin: bool,
    thin_threshold: int,
    geo: str = "",
) -> str:
    lens_l = _lens_label(lens, locale)
    if not items:
        if locale == "it":
            return (
                f"Su n={n} annunci ({lens_l}{geo}) non ci sono abbastanza paesi "
                f"con attività nella finestra di {period_days} giorni."
            )
        return (
            f"With n={n} jobs ({lens_l}{geo}) there are no country buckets "
            f"with activity in the {period_days}d window."
        )
    top = ", ".join(
        f"{c.get('country_code')} ({c.get('jobs_observed')} jobs, "
        f"{float(c.get('remote_share') or 0):.0%} remote)"
        for c in list(items)[:5]
    )
    if locale == "it":
        text = (
            f"Su n={n} annunci negli ultimi {period_days} giorni ({lens_l}{geo}), "
            f"dove compare più domanda osservata: {top}."
        )
        if thin:
            text += f" Campione sottile (n={n} < {thin_threshold})."
        return text
    text = (
        f"With n={n} jobs over {period_days} days ({lens_l}{geo}), "
        f"observed demand concentrates in: {top}."
    )
    if thin:
        text += f" Thin sample (n={n} < {thin_threshold})."
    return text


def adjacent_narrative(
    *,
    locale: Locale,
    lens: str,
    n: int,
    owned: bool,
    candidates: Sequence[dict[str, Any]],
    min_support: int,
    thin: bool,
    thin_threshold: int,
    geo: str = "",
) -> str:
    lens_l = _lens_label(lens, locale)
    if not owned:
        if locale == "it":
            return (
                f"Su n={n} annunci ({lens_l}{geo}) non posso suggerire skill adiacenti: "
                "aggiungi le tue skill nel profilo."
            )
        return (
            f"With n={n} jobs ({lens_l}{geo}) I cannot rank adjacent skills — "
            "add skills to your profile first."
        )
    if not candidates:
        if locale == "it":
            return (
                f"Su n={n} annunci ({lens_l}{geo}) nessuna skill adiacente "
                f"con supporto ≥{min_support} vicino al tuo profilo."
            )
        return (
            f"With n={n} jobs ({lens_l}{geo}) no adjacent skills near your profile "
            f"with support ≥{min_support}."
        )
    bits = ", ".join(
        f"{c.get('adjacent')} (spesso con {c.get('owned')}, {c.get('support')} annunci)"
        if locale == "it"
        else f"{c.get('adjacent')} (often with {c.get('owned')}, support={c.get('support')})"
        for c in list(candidates)[:5]
    )
    if locale == "it":
        text = (
            f"Su n={n} annunci ({lens_l}{geo}), skill che compaiono spesso "
            f"vicino alle tue ma che non hai ancora: {bits}."
        )
    else:
        text = (
            f"With n={n} jobs ({lens_l}{geo}), skills that often appear near yours "
            f"but are not in your profile yet: {bits}."
        )
    if thin:
        text += (
            f" Campione sottile (n={n} < {thin_threshold})."
            if locale == "it"
            else f" Thin sample (n={n} < {thin_threshold})."
        )
    return text


def focus_vs_market_narrative(
    *,
    locale: Locale,
    n: int,
    period_days: int,
    market_n: int,
    focus_n: int,
    overlap_n: int,
    focus_thin: bool,
    min_sample: int,
    thin: bool,
    thin_threshold: int,
    geo: str = "",
) -> str:
    if locale == "it":
        text = (
            f"Confronto mercato vs focus{geo} su n={n} annunci unione "
            f"negli ultimi {period_days} giorni: mercato={market_n}, "
            f"focus={focus_n}, in comune={overlap_n}."
        )
        if focus_thin:
            text += (
                f" Il lato focus è sottile (n={focus_n} < {min_sample}) — "
                "abilita intent focus e sincronizza prima di confrontare."
            )
        elif thin:
            text += f" Campione complessivo sottile (n={n} < {thin_threshold})."
        return text
    text = (
        f"Market vs focus compare{geo} on n={n} union jobs over {period_days} days: "
        f"Market jobs={market_n}, focus={focus_n}, overlap={overlap_n}."
    )
    if focus_thin:
        text += (
            f" Focus side thin (n={focus_n} < {min_sample}) — "
            "enable focus intents and sync before comparing growth."
        )
    elif thin:
        text += f" Thin overall sample (n={n} < {thin_threshold})."
    return text


def suggest_watches_narrative(
    *,
    locale: Locale,
    lens: str,
    n: int,
    proposed_count: int,
    min_support: int,
    thin: bool,
    thin_threshold: int,
    geo: str = "",
) -> str:
    lens_l = _lens_label(lens, locale)
    if proposed_count > 0:
        if locale == "it":
            text = (
                f"Su n={n} annunci ({lens_l}{geo}) propongo {proposed_count} watch da seguire. "
                "Non viene salvato nulla finché non le accetti — Nothing saved yet."
            )
        else:
            text = (
                f"With n={n} jobs ({lens_l}{geo}) I propose {proposed_count} watch(es). "
                "Nothing is saved until you accept via /research/watches/accept. Nothing saved yet."
            )
    elif locale == "it":
        text = (
            f"Su n={n} annunci ({lens_l}{geo}) nessuna candidata watch "
            f"con supporto ≥{min_support}."
        )
    else:
        text = (
            f"With n={n} jobs ({lens_l}{geo}) no watch candidates "
            f"with support ≥{min_support}."
        )
    if thin:
        text += (
            f" Campione sottile (n={n} < {thin_threshold})."
            if locale == "it"
            else f" Thin sample (n={n} < {thin_threshold})."
        )
    return text


def refused_narrative(*, locale: Locale, n: int, min_sample: int) -> str:
    if locale == "it":
        return (
            f"Campione troppo sottile (n={n}, servono almeno {min_sample} annunci). "
            "Sincronizza i collector di discovery/focus e riprova."
        )
    return (
        f"Refused: sample too thin (n={n}, need ≥{min_sample}). "
        "Sync discovery/focus crawlers and retry."
    )


def normalize_locale(locale: Optional[str]) -> Locale:
    return "it" if (locale or "").lower().startswith("it") else "en"
