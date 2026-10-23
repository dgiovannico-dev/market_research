"""findmethatdamjob.nl — documented public NL jobs API (careers-page aggregator).

Docs: https://findmethatdamjob.nl/docs/api/
Base: https://gigsignal-api.fly.dev — no key; cache 30m server-side.
``location=amsterdam`` matches Netherlands-wide listings per API docs.
Not UWV/Werk.nl PES — official NL vacancy listings remain blocked (ADR-003).
"""

from __future__ import annotations

import re
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

# Role fillers in focus labels — optional for client-side match (same idea as rematch).
_ROLE_FILLERS = frozenset(
    {
        "architect",
        "b2b",
        "consultant",
        "contract",
        "contractor",
        "engineer",
        "freelance",
        "independent",
        "junior",
        "lead",
        "principal",
        "remote",
        "senior",
        "staff",
    }
)
_STOPWORDS = frozenset({"a", "an", "and", "for", "in", "of", "or", "the", "to", "with"})
_TOKEN_RE = re.compile(r"[a-z0-9.+#]+", re.IGNORECASE)

API_BASE = "https://gigsignal-api.fly.dev"
JOBS_URL = f"{API_BASE}/api/jobs"
# Documented shortcut for any NL location (provinces, municipalities, country labels).
NL_LOCATION = "amsterdam"
MAX_RECORDS = 200
USER_AGENT = "FMI-MarketIntel/1.0 (findmethatdamjob.nl; market-research)"


class FindMeThatDamJobCollector(BaseCollector):
    name = "findmethatdamjob.nl"
    source_key = "findmethatdamjob"
    collection_mode = "search"
    base_url = JOBS_URL

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        # Search-mode: never fetch NL-wide dump without an explicit query (ADR-007).
        if is_blank_query(query):
            return missing_query_result()
        q = simplify_query_for(self, query or "").strip().lower()
        headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
        params = {"location": NL_LOCATION}
        try:
            async with httpx.AsyncClient(timeout=60.0, headers=headers) as client:
                resp = await client.get(JOBS_URL, params=params)
                resp.raise_for_status()
                payload = resp.json()
        except Exception as exc:  # noqa: BLE001
            return CollectorResult(records=[], pages_scanned=1, errors=[str(exc)])

        if not isinstance(payload, list):
            return CollectorResult(
                records=[], pages_scanned=1, errors=["unexpected payload"]
            )

        records: list[RawJob] = []
        for item in payload:
            if len(records) >= MAX_RECORDS:
                break
            if not isinstance(item, dict):
                continue
            if not _matches(item, q):
                continue
            mapped = _map_item(item)
            if mapped is not None:
                records.append(mapped)

        # Empty client-side filter is a normal miss for niche focus labels — not an API failure.
        # (Previously stamped source.last_error and showed as connector "error" in the UI.)
        return CollectorResult(records=records, pages_scanned=1, errors=[])


def _map_item(item: dict[str, Any]) -> RawJob | None:
    job_id = item.get("id")
    title = (item.get("title") or "").strip()
    apply_url = (item.get("apply_url") or "").strip()
    if not job_id or not title or not apply_url:
        return None
    facts = item.get("facts") if isinstance(item.get("facts"), dict) else {}
    skills = facts.get("skills") if isinstance(facts, dict) else None
    tags: list[str] = []
    if isinstance(skills, list):
        tags = [str(s).strip() for s in skills if str(s).strip()][:15]
    if facts.get("seniority"):
        tags.insert(0, str(facts["seniority"]))
    gist = item.get("gist")
    description = str(gist).strip() if gist else None
    return RawJob(
        source_job_id=str(job_id),
        url=apply_url,
        title=title,
        company=item.get("company_name"),
        description=description,
        location=item.get("location") or "Netherlands",
        published_at=_published(item.get("first_seen_at")),
        salary_text=_salary(facts),
        tags=tags,
        job_type=None,
        remote_hint=_remote_hint(facts),
        raw={
            "slug": item.get("slug"),
            "source_name": item.get("source_name"),
            "company_website": item.get("company_website"),
            "mode": "public_api",
        },
    )


def _match_tokens(q: str) -> list[str]:
    """Significant tokens for AND match; drop stopwords/role fillers when possible."""
    raw_tokens = [t.lower() for t in _TOKEN_RE.findall(q or "") if t]
    significant = [
        t
        for t in raw_tokens
        if t not in _STOPWORDS and t not in _ROLE_FILLERS and len(t) > 1
    ]
    return significant or raw_tokens


def _matches(item: dict[str, Any], q: str) -> bool:
    facts = item.get("facts") if isinstance(item.get("facts"), dict) else {}
    skills = facts.get("skills") if isinstance(facts, dict) else []
    skill_blob = " ".join(str(s) for s in skills) if isinstance(skills, list) else ""
    blob = " ".join(
        str(x)
        for x in (
            item.get("title"),
            item.get("company_name"),
            item.get("location"),
            item.get("gist"),
            skill_blob,
            facts.get("seniority") if isinstance(facts, dict) else None,
        )
        if x
    ).lower()
    # Phrase match first; else AND of significant tokens (focus labels are multi-word).
    if q and q in blob:
        return True
    tokens = _match_tokens(q)
    if not tokens:
        return False
    return all(t in blob for t in tokens)


def _published(raw: Any) -> datetime:
    if raw:
        try:
            return datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
        except ValueError:
            pass
    return datetime.now(timezone.utc)


def _salary(facts: dict[str, Any]) -> str | None:
    sal = facts.get("salary")
    if sal is None:
        return None
    if isinstance(sal, str) and sal.strip():
        return sal.strip()
    if isinstance(sal, dict):
        parts = [str(v) for v in sal.values() if v]
        return " ".join(parts) if parts else None
    return str(sal)


def _remote_hint(facts: dict[str, Any]) -> str | None:
    mode = str(facts.get("work_mode") or "").lower()
    if mode == "remote":
        return "remote"
    if mode == "hybrid":
        return "hybrid"
    if mode == "onsite":
        return "onsite"
    return None
