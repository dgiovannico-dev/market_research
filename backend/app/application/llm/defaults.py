"""Seed prompt bodies for classify / weekly / study (ADR-010)."""

from __future__ import annotations

SEED_PROMPTS: list[dict[str, str]] = [
    {
        "slug": "classify_job",
        "purpose": "classify_job",
        "description": "Extract job classification JSON from ad text.",
        "system_text": (
            "Return valid JSON only matching the schema keys. "
            "Use only evidence from the text. If unknown, use null/unknown. "
            "Do not invent rates."
        ),
        "user_text": (
            "Extract job classification as JSON matching schema keys: {{schema_keys}}.\n\n"
            "TEXT:\n{{text}}"
        ),
    },
    {
        "slug": "weekly_report",
        "purpose": "weekly_report",
        "description": "Narrate weekly KPIs from structured payload only.",
        "system_text": (
            "Write a short weekly market brief in clear human language (no jargon like "
            "evidence_kind). Use ONLY the provided facts. Format timestamps as YYYY-MM-DD HH:MM UTC "
            "and percentages with exactly two decimals (e.g. 10.86%). "
            "If evidence is insufficient say so plainly. Never invent numbers."
        ),
        "user_text": "{{structured_json}}",
    },
    {
        "slug": "study_plan",
        "purpose": "study_plan",
        "description": "Build a grounded study plan from Stack Compass evidence.",
        "system_text": (
            "You are a freelance career study coach. Return ONLY valid JSON matching the schema. "
            "Every stack_target and milestone skill MUST appear in evidence.candidates. "
            "Never invent market size, rates, or skills not in evidence. "
            "If evidence is thin, keep stack_target short and set limits accordingly."
        ),
        "user_text": (
            "Modality={{modality}} hours_per_week={{hours_per_week}} "
            "horizon_weeks={{horizon_weeks}}\n"
            "Evidence JSON:\n{{evidence_json}}\n"
            "Return JSON with types: "
            "title:string, horizon_weeks:int, modality:string, hours_per_week:number, "
            "stack_target:string[] (technology names from candidates only), "
            "milestones:[{week:int,title:string,skills:string[],evidence_refs:string[]}], "
            "weekly_template:object[], limits:string[]"
        ),
    },
    {
        "slug": "study_refine",
        "purpose": "study_refine",
        "description": "Patch an existing study plan from a short user request.",
        "system_text": (
            "Return ONLY a JSON patch object for the study plan. "
            "Do not invent technologies absent from evidence. Keep evidence_refs intact."
        ),
        "user_text": (
            "Current plan:\n{{plan_json}}\n\nEvidence:\n{{evidence_json}}\n\n"
            "User request:\n{{user_message}}"
        ),
    },
]


def render_template(text: str, variables: dict[str, str]) -> str:
    out = text
    for key, value in variables.items():
        out = out.replace("{{" + key + "}}", value)
    return out
