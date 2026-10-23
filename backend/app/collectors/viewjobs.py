"""ViewJobs Australia — free public MCP search (no key; attribution via utm).

Docs: https://www.viewjobs.com.au/for-agents
Transport: Streamable HTTP JSON-RPC at /api/mcp (tools/call search_jobs).
Not Seek scrape — authorized read-only agent search surface (ADR-003).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Optional

import httpx

from app.collectors.base import (
    BaseCollector,
    CollectorResult,
    RawJob,
    is_blank_query,
    missing_query_result,
    simplify_query_for,
)

MCP_URL = "https://www.viewjobs.com.au/api/mcp"
USER_AGENT = "FMI-MarketIntel/1.0 (viewjobs; market-research; +https://www.viewjobs.com.au/for-agents)"
MAX_RECORDS = 120
# Cap place fan-out so a single search stays bounded.
DEFAULT_PLACES = (
    "Sydney",
    "Melbourne",
    "Brisbane",
    "Perth",
    "Adelaide",
    "Canberra",
)


def _parse_sse_payload(text: str) -> dict[str, Any]:
    for line in text.splitlines():
        if line.startswith("data: "):
            data = line[6:].strip()
            if not data:
                continue
            try:
                parsed = json.loads(data)
            except json.JSONDecodeError:
                continue
            if isinstance(parsed, dict):
                return parsed
    try:
        parsed = json.loads(text)
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        return {}


def _jobs_from_result(payload: dict[str, Any]) -> list[dict[str, Any]]:
    result = payload.get("result")
    if not isinstance(result, dict):
        return []
    structured = result.get("structuredContent")
    if isinstance(structured, dict):
        jobs = structured.get("jobs")
        if isinstance(jobs, list):
            return [j for j in jobs if isinstance(j, dict)]
    return []


def _published(raw: object) -> datetime:
    if raw:
        try:
            return datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
        except ValueError:
            pass
    return datetime.now(timezone.utc)


def _map_job(item: dict[str, Any]) -> RawJob | None:
    job_id = item.get("id")
    title = (item.get("title") or "").strip()
    url = (item.get("url") or "").strip()
    if not job_id or not title or not url:
        return None
    loc = (item.get("location") or "").strip() or "Australia"
    if "australia" not in loc.lower() and " AU" not in f" {loc.upper()}":
        loc = f"{loc}, Australia"
    tags: list[str] = []
    if item.get("work_type"):
        tags.append(str(item["work_type"]))
    if item.get("apply_type"):
        tags.append(str(item["apply_type"]))
    pay = item.get("pay")
    salary = str(pay).strip() if pay else None
    return RawJob(
        source_job_id=str(job_id),
        url=url.split("?")[0],
        title=title,
        company=item.get("employer"),
        description=None,
        location=loc,
        published_at=_published(item.get("posted_at")),
        salary_text=salary,
        tags=tags[:8],
        job_type=item.get("work_type"),
        remote_hint=None,
        raw={
            "country": "AU",
            "country_code": "AU",
            "evidence_tier": "thin",
            "place": item.get("location"),
            "featured": item.get("featured"),
            "mode": "mcp_search_jobs",
            "attribution": "ViewJobs",
        },
    )


class ViewJobsCollector(BaseCollector):
    name = "ViewJobs"
    source_key = "viewjobs"
    collection_mode = "search"
    base_url = MCP_URL

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        # Search-mode: never fan out DEFAULT_QUERIES on blank (ADR-007).
        if is_blank_query(query):
            return missing_query_result()
        q = simplify_query_for(self, query or "").strip()
        if not q:
            return missing_query_result()
        queries = [q]

        headers = {
            "User-Agent": USER_AGENT,
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        errors: list[str] = []
        records: list[RawJob] = []
        seen: set[str] = set()
        pages = 0

        async with httpx.AsyncClient(timeout=45.0, headers=headers) as client:
            for q in queries:
                if len(records) >= MAX_RECORDS:
                    break
                for place in DEFAULT_PLACES:
                    if len(records) >= MAX_RECORDS:
                        break
                    body = {
                        "jsonrpc": "2.0",
                        "id": pages + 1,
                        "method": "tools/call",
                        "params": {
                            "name": "search_jobs",
                            "arguments": {"query": q, "place": place},
                        },
                    }
                    try:
                        resp = await client.post(MCP_URL, json=body)
                        resp.raise_for_status()
                        payload = _parse_sse_payload(resp.text)
                    except Exception as exc:  # noqa: BLE001
                        errors.append(f"{place}/{q}: {exc}")
                        continue
                    pages += 1
                    if payload.get("error"):
                        errors.append(f"{place}/{q}: {payload['error']}")
                        continue
                    for item in _jobs_from_result(payload):
                        if len(records) >= MAX_RECORDS:
                            break
                        mapped = _map_job(item)
                        if mapped is None or mapped.source_job_id in seen:
                            continue
                        seen.add(mapped.source_job_id)
                        records.append(mapped)

        return CollectorResult(
            records=records, pages_scanned=max(pages, 1), errors=errors
        )
