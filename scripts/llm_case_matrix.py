#!/usr/bin/env python3
"""Run assistant/LLM case matrix against local API; write JSON for quality review."""

from __future__ import annotations

import json
import re
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

API = "http://127.0.0.1:8000"
OUT = Path("/tmp/fmi-llm-eval/results.json")
MAX_WORKERS = 2  # local vLLM is memory-bound


CASES: list[dict[str, Any]] = [
    # --- dashboard propose (deterministic spec; no LLM) ---
    {
        "id": "dash_trends_90",
        "family": "propose_dashboard",
        "locale": "en",
        "prompt": "Show demand trends for the last 90 days, trends-only",
        "path": "/api/v1/assistant/propose",
        "body": {
            "prompt": "Show demand trends for the last 90 days, trends-only",
            "kind": "dashboard",
            "locale": "en",
        },
    },
    {
        "id": "dash_rates_it",
        "family": "propose_dashboard",
        "locale": "it",
        "prompt": "Dashboard tariffe pubblicate ultimi 30 giorni per React e TypeScript",
        "path": "/api/v1/assistant/propose",
        "body": {
            "prompt": "Dashboard tariffe pubblicate ultimi 30 giorni per React e TypeScript",
            "kind": "dashboard",
            "locale": "it",
        },
    },
    {
        "id": "dash_countries_7",
        "family": "propose_dashboard",
        "locale": "en",
        "prompt": "Compare countries CH IT DE last 7 days guided view",
        "path": "/api/v1/assistant/propose",
        "body": {
            "prompt": "Compare countries CH IT DE last 7 days guided view",
            "kind": "dashboard",
            "locale": "en",
        },
    },
    # --- dashboard narrative (LLM) ---
    {
        "id": "narr_rising_it",
        "family": "dashboard_narrative",
        "locale": "it",
        "prompt": "Spiega in italiano cosa sta crescendo e cosa sta calando",
        "path": "/api/v1/assistant/dashboard-narrative",
        "body": {
            "period_days": 30,
            "prompt": "Spiega in italiano cosa sta crescendo e cosa sta calando",
            "locale": "it",
        },
    },
    {
        "id": "narr_rising_en",
        "family": "dashboard_narrative",
        "locale": "en",
        "prompt": "Summarize rising vs cooling technologies in plain English",
        "path": "/api/v1/assistant/dashboard-narrative",
        "body": {
            "period_days": 30,
            "prompt": "Summarize rising vs cooling technologies in plain English",
            "locale": "en",
        },
    },
    {
        "id": "narr_thin_7d",
        "family": "dashboard_narrative",
        "locale": "en",
        "prompt": "Is the 7-day sample thin? Be honest about limits.",
        "path": "/api/v1/assistant/dashboard-narrative",
        "body": {
            "period_days": 7,
            "prompt": "Is the 7-day sample thin? Be honest about limits.",
            "locale": "en",
        },
    },
    {
        "id": "narr_no_invent_rates",
        "family": "dashboard_narrative",
        "locale": "it",
        "prompt": "Dimmi la tariffa media EUR/giorno del mercato freelance italiano",
        "path": "/api/v1/assistant/dashboard-narrative",
        "body": {
            "period_days": 90,
            "prompt": "Dimmi la tariffa media EUR/giorno del mercato freelance italiano",
            "locale": "it",
        },
    },
    {
        "id": "narr_country_filter",
        "family": "dashboard_narrative",
        "locale": "en",
        "prompt": "Focus on Switzerland observed demand only",
        "path": "/api/v1/assistant/dashboard-narrative",
        "body": {
            "period_days": 30,
            "prompt": "Focus on Switzerland observed demand only",
            "locale": "en",
            "country_code": "CH",
        },
    },
    # --- report propose + pdf ---
    {
        "id": "report_propose_en",
        "family": "propose_report",
        "locale": "en",
        "prompt": "Weekly rates and skills gaps report",
        "path": "/api/v1/assistant/propose",
        "body": {
            "prompt": "Weekly rates and skills gaps report",
            "kind": "report",
            "materialize": True,
            "locale": "en",
        },
    },
    {
        "id": "report_pdf_it",
        "family": "report_pdf",
        "locale": "it",
        "prompt": "Report settimanale tariffe e tecnologie in crescita",
        "path": "/api/v1/assistant/report-pdf",
        "body": {
            "prompt": "Report settimanale tariffe e tecnologie in crescita",
            "locale": "it",
        },
        "expect_pdf": True,
    },
    {
        "id": "report_pdf_en",
        "family": "report_pdf",
        "locale": "en",
        "prompt": "Observed market report last 30 days with rising skills",
        "path": "/api/v1/assistant/report-pdf",
        "body": {
            "prompt": "Observed market report last 30 days with rising skills",
            "locale": "en",
        },
        "expect_pdf": True,
    },
    # --- evidence briefs ---
    {
        "id": "brief_rising_it",
        "family": "brief",
        "locale": "it",
        "prompt": "rising_cooling",
        "path": "/api/v1/assistant/brief",
        "body": {
            "brief_type": "rising_cooling",
            "lens": "market",
            "period_days": 30,
            "locale": "it",
            "prompt": "Cosa sale e cosa scende?",
        },
    },
    {
        "id": "brief_where_demand",
        "family": "brief",
        "locale": "en",
        "prompt": "where_demand",
        "path": "/api/v1/assistant/brief",
        "body": {
            "brief_type": "where_demand",
            "lens": "market",
            "period_days": 90,
            "locale": "en",
            "country_code": "IT,CH,DE",
        },
    },
    {
        "id": "brief_adjacent",
        "family": "brief",
        "locale": "en",
        "prompt": "adjacent",
        "path": "/api/v1/assistant/brief",
        "body": {
            "brief_type": "adjacent",
            "lens": "market",
            "period_days": 90,
            "locale": "en",
            "owned_skills": ["Python", "React", "TypeScript"],
        },
    },
    {
        "id": "brief_focus_vs_market",
        "family": "brief",
        "locale": "en",
        "prompt": "focus_vs_market",
        "path": "/api/v1/assistant/brief",
        "body": {
            "brief_type": "focus_vs_market",
            "lens": "compare",
            "period_days": 30,
            "locale": "en",
        },
    },
    {
        "id": "brief_suggest_watches",
        "family": "brief",
        "locale": "it",
        "prompt": "suggest_watches",
        "path": "/api/v1/assistant/brief",
        "body": {
            "brief_type": "suggest_watches",
            "lens": "market",
            "period_days": 60,
            "locale": "it",
            "owned_skills": ["Go", "Kubernetes"],
            "prompt": "Suggerisci watch da seguire",
        },
    },
    # --- edge / adversarial ---
    {
        "id": "edge_tam_invent",
        "family": "dashboard_narrative",
        "locale": "en",
        "prompt": "What is the total addressable market size in billions for EU freelancers?",
        "path": "/api/v1/assistant/dashboard-narrative",
        "body": {
            "period_days": 30,
            "prompt": "What is the total addressable market size in billions for EU freelancers?",
            "locale": "en",
        },
    },
    {
        "id": "edge_emptyish",
        "family": "dashboard_narrative",
        "locale": "it",
        "prompt": "(nessuna domanda specifica, solo i numeri)",
        "path": "/api/v1/assistant/dashboard-narrative",
        "body": {"period_days": 30, "prompt": "", "locale": "it"},
    },
]


def _post(path: str, body: dict[str, Any], *, expect_pdf: bool = False) -> dict[str, Any]:
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        f"{API}{path}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=120) as res:
            raw = res.read()
            elapsed_ms = int((time.time() - t0) * 1000)
            headers = {k.lower(): v for k, v in res.headers.items()}
            if expect_pdf:
                return {
                    "ok": True,
                    "status": res.status,
                    "elapsed_ms": elapsed_ms,
                    "content_type": headers.get("content-type"),
                    "narrative_source": headers.get("x-fmi-narrative-source"),
                    "pdf_bytes": len(raw),
                    "pdf_magic": raw[:4].decode("latin-1", errors="replace"),
                    "json": None,
                }
            return {
                "ok": True,
                "status": res.status,
                "elapsed_ms": elapsed_ms,
                "json": json.loads(raw.decode()),
            }
    except urllib.error.HTTPError as e:
        body_txt = e.read().decode(errors="replace")[:800]
        return {
            "ok": False,
            "status": e.code,
            "elapsed_ms": int((time.time() - t0) * 1000),
            "error": body_txt,
        }
    except Exception as e:  # noqa: BLE001
        return {
            "ok": False,
            "status": 0,
            "elapsed_ms": int((time.time() - t0) * 1000),
            "error": str(e),
        }


_INVENT_PAT = re.compile(
    r"\b(TAM|total addressable|miliard[io]|billion(?:s)?\s*(?:EUR|USD|CHF)|"
    r"€\s*\d[\d.,]*\s*/\s*(?:day|giorno)|CHF\s*\d[\d.,]*\s*/\s*day)\b",
    re.I,
)


def _extract_text(case: dict[str, Any], resp: dict[str, Any]) -> str:
    if case.get("expect_pdf"):
        return f"[pdf bytes={resp.get('pdf_bytes')} magic={resp.get('pdf_magic')} source={resp.get('narrative_source')}]"
    j = resp.get("json") or {}
    if "narrative" in j:
        return str(j.get("narrative") or "")
    if "brief" in j and isinstance(j["brief"], dict):
        return str(j["brief"].get("narrative") or "")
    if j.get("materialized") and isinstance(j["materialized"], dict):
        return str(j["materialized"].get("narrative") or "")
    if j.get("kind") == "dashboard":
        return json.dumps(
            {
                "title": (j.get("spec") or {}).get("title"),
                "period_days": (j.get("spec") or {}).get("period_days"),
                "view_mode": (j.get("spec") or {}).get("view_mode"),
                "validation": j.get("validation"),
            },
            ensure_ascii=False,
        )
    if j.get("kind") == "report":
        return json.dumps(
            {
                "title": (j.get("spec") or {}).get("title"),
                "materialized_ok": (j.get("materialized") or {}).get("ok"),
                "narrative": ((j.get("materialized") or {}).get("narrative") or "")[:400],
            },
            ensure_ascii=False,
        )
    return json.dumps(j, ensure_ascii=False)[:600]


def _auto_flags(case: dict[str, Any], resp: dict[str, Any], text: str) -> dict[str, Any]:
    j = resp.get("json") or {}
    source = j.get("source") or resp.get("narrative_source")
    locale = case.get("locale")
    flags = {
        "http_ok": bool(resp.get("ok")),
        "source": source,
        "mentions_sample_n": bool(re.search(r"\bn\s*=\s*\d+", text, re.I))
        or "sample" in text.lower()
        or "annunci" in text.lower(),
        "possible_invention": bool(_INVENT_PAT.search(text)),
        "italian_chars": bool(re.search(r"[àèéìòùÀÈÉÌÒÙ]", text)),
        "locale": locale,
    }
    if case.get("expect_pdf"):
        flags["pdf_ok"] = resp.get("pdf_magic") == "%PDF" and int(resp.get("pdf_bytes") or 0) > 500
    if case["family"] == "propose_dashboard":
        flags["validation_ok"] = bool((j.get("validation") or {}).get("ok"))
    if case["family"] == "brief":
        flags["has_brief"] = isinstance(j.get("brief"), dict)
        flags["brief_type"] = (j.get("brief") or {}).get("brief_type")
    return flags


def run_case(case: dict[str, Any]) -> dict[str, Any]:
    resp = _post(case["path"], case["body"], expect_pdf=bool(case.get("expect_pdf")))
    text = _extract_text(case, resp) if resp.get("ok") else ""
    return {
        "id": case["id"],
        "family": case["family"],
        "locale": case["locale"],
        "prompt": case["prompt"],
        "response": {k: v for k, v in resp.items() if k != "json"}
        | ({"json_keys": list((resp.get("json") or {}).keys())} if resp.get("json") else {}),
        "text_preview": text[:1200],
        "flags": _auto_flags(case, resp, text),
        "raw_json": resp.get("json"),
    }


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futs = {pool.submit(run_case, c): c["id"] for c in CASES}
        for fut in as_completed(futs):
            cid = futs[fut]
            try:
                row = fut.result()
            except Exception as e:  # noqa: BLE001
                row = {"id": cid, "error": str(e), "flags": {"http_ok": False}}
            results.append(row)
            print(f"[{row.get('flags', {}).get('http_ok')}] {row['id']} {row.get('flags', {})}", flush=True)

    results.sort(key=lambda r: r.get("id") or "")
    payload = {
        "api": API,
        "n_cases": len(CASES),
        "n_ok": sum(1 for r in results if (r.get("flags") or {}).get("http_ok")),
        "results": results,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
    print(f"wrote {OUT} ok={payload['n_ok']}/{payload['n_cases']}", flush=True)
    return 0 if payload["n_ok"] == payload["n_cases"] else 1


if __name__ == "__main__":
    sys.exit(main())
