"""Deterministic proposers for DashboardSpec / ReportSpec from intent hints."""

from __future__ import annotations

import re

from app.application.assistant.specs import (
    DashboardFilters,
    DashboardSpec,
    DashboardWidget,
    IntentHints,
    ReportSection,
    ReportSpec,
)
from app.application.assistant.validate import validate_spec

_TECH_HINTS = (
    "java",
    "spring",
    "python",
    "fastapi",
    "typescript",
    "react",
    "vue",
    "next.js",
    "nodejs",
    "golang",
    "rust",
    "kubernetes",
    "docker",
    "terraform",
    "aws",
    "azure",
    "gcp",
    "devops",
    "llm",
    "rag",
    "genai",
    "pytorch",
    "mlops",
    "langchain",
    "cybersecurity",
    "appsec",
    "devsecops",
    "siem",
    "pentest",
    "owasp",
)


def parse_intent_from_prompt(prompt: str, base: IntentHints | None = None) -> IntentHints:
    hints = base.model_copy(deep=True) if base else IntentHints()
    text = prompt or ""
    hints.user_prompt = text
    lower = text.lower()
    days = re.search(r"(\d+)\s*(?:giorni|days|d)\b", lower)
    if days:
        hints.period_days = max(1, min(int(days.group(1)), 3660))
    if "trends-only" in lower or "trends only" in lower or "solo trend" in lower:
        hints.view_mode = "trends_only"
    techs = list(hints.technologies)
    for t in _TECH_HINTS:
        if re.search(rf"\b{re.escape(t)}\b", lower) and t not in {x.lower() for x in techs}:
            techs.append(t)
    hints.technologies = techs
    if re.search(r"\beu\b|europe|remoto|remote", lower) and "EU" not in hints.countries:
        # soft geo hint — not ISO; UI filters may ignore
        pass
    if "rate" in lower or "tariff" in lower or "stipend" in lower:
        hints.include_rates = True
    if "quality" in lower or "copertura" in lower or "coverage" in lower:
        hints.include_quality = True
    if "skill gap" in lower or "profilo" in lower or "profile" in lower:
        hints.include_profile_gaps = True
    cooccur_cue = bool(
        re.search(
            r"\b("
            r"abbin\w*|co-?occurr\w*|pair(?:ed|ing|s)?|insieme|vicin\w*|"
            r"along\s+with|together\s+with|combin\w*|associat\w*|"
            r"neighbor\w*|adiacent\w*|related\s+to|stack\s+with|"
            r"si\s+abbina(?:no)?|di\s+solito\s+(?:con|insieme)|"
            r"which\s+tech(?:nolog(?:y|ies))?\s+(?:go\s+)?with|"
            r"technologies?\s+(?:that\s+)?(?:pair|combine|appear)"
            r")\b",
            lower,
        )
    )
    compare_cue = bool(
        re.search(
            r"\b(vs\.?|versus|meglio|oppure|oppure\s+scegliere|better|prefer|scegliere|"
            r"confront[ao]|compare|which\s+(?:is\s+)?better|o\s+il)\b",
            lower,
        )
        or (" o " in f" {lower} " and len(techs) >= 2)
    )
    # Pairing questions win over A-vs-B when both cues fire with a single seed tech.
    if cooccur_cue and len(techs) >= 1:
        hints.cooccur_mode = True
        hints.compare_mode = False
    elif compare_cue and len(techs) >= 2:
        hints.compare_mode = True
        hints.cooccur_mode = False
    if not hints.title:
        if hints.compare_mode and len(techs) >= 2:
            pair = " vs ".join(t.title() for t in techs[:2])
            hints.title = f"{pair} — observed compare"
        elif hints.cooccur_mode and techs:
            seed = techs[0].title()
            hints.title = f"{seed} — observed co-occurrence"
        else:
            hints.title = (text[:80] + "…") if len(text) > 80 else (text or "Observed market view")
    return hints


def propose_dashboard(intent: IntentHints | dict | str) -> DashboardSpec:
    hints = _coerce_hints(intent)
    filters = DashboardFilters(
        technologies=hints.technologies,
        countries=hints.countries,
        source_keys=hints.source_keys,
        contract_types=hints.contract_types,
    )
    widgets: list[DashboardWidget] = [
        DashboardWidget(id="kpi_unique", type="kpi", metric_key="unique_jobs_observed"),
        DashboardWidget(id="kpi_remote", type="kpi", metric_key="remote_jobs_observed"),
    ]
    compare = bool(hints.compare_mode and len(hints.technologies) >= 2)
    cooccur = bool(hints.cooccur_mode and hints.technologies)
    if compare:
        # Skill-vs-skill: volume/trends for the named techs — not the global rise/cool board.
        widgets.append(
            DashboardWidget(
                id="chart_compare_trends",
                type="chart",
                metric_key="technology_trends",
                params={"focus_technologies": hints.technologies[:4]},
            )
        )
        widgets.append(
            DashboardWidget(
                id="cooccur",
                type="table",
                metric_key="skill_cooccurrence",
                params={"seed": hints.technologies[0], "neighbor_limit": 15},
            )
        )
    elif cooccur:
        # "What pairs with X?" — neighbors for the seed, not global rise/cool.
        widgets.append(
            DashboardWidget(
                id="chart_cooccur",
                type="chart",
                metric_key="skill_cooccurrence",
                params={"seed": hints.technologies[0], "neighbor_limit": 15},
            )
        )
        widgets.append(
            DashboardWidget(
                id="cooccur",
                type="table",
                metric_key="skill_cooccurrence",
                params={"seed": hints.technologies[0], "neighbor_limit": 30},
            )
        )
    else:
        if hints.include_trends:
            widgets.append(
                DashboardWidget(id="chart_trends", type="chart", metric_key="technology_trends")
            )
        if hints.include_rates:
            widgets.append(
                DashboardWidget(id="table_rates", type="table", metric_key="rates_distribution")
            )
        widgets.append(
            DashboardWidget(id="chart_countries", type="chart", metric_key="countries_breakdown")
        )
        if hints.technologies:
            widgets.append(
                DashboardWidget(
                    id="cooccur",
                    type="table",
                    metric_key="skill_cooccurrence",
                    params={"seed": hints.technologies[0], "neighbor_limit": 20},
                )
            )
    if hints.include_quality and hints.view_mode == "guided":
        widgets.append(DashboardWidget(id="quality", type="quality", metric_key="data_quality"))

    notes = ["Proposed from intent; ground with get_observed_counts before presenting."]
    if compare:
        notes.append(
            "Compare mode: chart focuses on named technologies; "
            "do not substitute the global rising/cooling board."
        )
    if cooccur:
        notes.append(
            "Co-occurrence mode: chart lists skills that co-appear with the seed; "
            "do not substitute the global rising/cooling board."
        )
    spec = DashboardSpec(
        title=hints.title or "Observed market dashboard",
        period_days=hints.period_days,
        view_mode=hints.view_mode,
        filters=filters,
        widgets=widgets,
        grounding={
            "queries_used": [],
            "endpoints_used": [
                "GET /api/v1/dashboard/summary",
                "GET /api/v1/market/trends",
            ],
            "notes": notes,
        },
    )
    result = validate_spec(spec)
    if not result.ok:
        raise ValueError(f"proposed dashboard invalid: {result.errors}")
    return spec


def propose_report(intent: IntentHints | dict | str) -> ReportSpec:
    hints = _coerce_hints(intent)
    sections = [
        ReportSection(kind="summary", title="Observed summary"),
        ReportSection(kind="skills", title="Skills / technologies"),
        ReportSection(kind="sources", title="Source coverage"),
    ]
    if hints.include_rates:
        sections.insert(1, ReportSection(kind="rates", title="Declared rates"))
    if hints.include_profile_gaps:
        sections.append(ReportSection(kind="gaps", title="Profile skill gaps"))
    spec = ReportSpec(
        title=hints.title or "Observed market report",
        period_days=hints.period_days,
        sections=sections,
        include_profile_gaps=hints.include_profile_gaps,
        narrative_policy="observed_only",
        grounding={
            "notes": ["Materialize with materialize_report before narrative."],
            "endpoints_used": ["GET /api/v1/dashboard/summary", "GET /api/v1/reports/weekly"],
        },
    )
    result = validate_spec(spec)
    if not result.ok:
        raise ValueError(f"proposed report invalid: {result.errors}")
    return spec


def _coerce_hints(intent: IntentHints | dict | str) -> IntentHints:
    if isinstance(intent, IntentHints):
        return intent
    if isinstance(intent, str):
        return parse_intent_from_prompt(intent)
    if isinstance(intent, dict):
        if "user_prompt" in intent and len(intent) == 1:
            return parse_intent_from_prompt(str(intent["user_prompt"]))
        base = IntentHints.model_validate(intent)
        if base.user_prompt:
            return parse_intent_from_prompt(base.user_prompt, base)
        return base
    raise TypeError("intent must be IntentHints, dict, or str")
