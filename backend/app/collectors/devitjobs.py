"""DevITJobs — free public jobsLight JSON dump (UK + EU sister hosts; no key).

The API exposes one full dump per host (no page/query params). Coverage is
deepened via multi-host fan-out, client-side query-term fan-out, stratified
tech-category selection, and in-run dedupe.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Optional

import httpx

from app.collectors.base import BaseCollector, CollectorResult, RawJob
from app.core.config import get_settings

# Known sister TLDs with live jobsLight dumps (no overlap on _id).
DEFAULT_HOSTS = ("uk", "com", "nl", "fr")
MAX_HOSTS = 4
MAX_PER_HOST = 120
MAX_PER_CATEGORY = 24
MAX_TOTAL = 400
MAX_QUERY_TERMS = 4

_TOKEN_RE = re.compile(r"[a-z0-9+#.]{2,}", re.IGNORECASE)
_OR_SPLIT = re.compile(r"\s+OR\s+", re.IGNORECASE)

# Extra match terms when the crawl query is generic / IT-related (client-side only).
_IT_FANOUT = (
    "python",
    "java",
    "javascript",
    "typescript",
    "react",
    "devops",
    "kubernetes",
    "aws",
    "data",
    "security",
)
_GENERIC = frozenset({"it", "tech", "software", "developer", "engineer", "engineering"})
_TECH = frozenset(_IT_FANOUT) | frozenset(
    {"golang", "go", "rust", "php", "ruby", "scala", "kotlin", "dotnet", ".net", "ml", "ai"}
)

_CURRENCY = {
    "uk": "GBP",
    "com": "GBP",
    "nl": "EUR",
    "fr": "EUR",
}


class DevITJobsCollector(BaseCollector):
    name = "DevITJobs"
    source_key = "devitjobs"
    collection_mode = "dump"
    base_url = "https://devitjobs.uk/api/jobsLight"

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        settings = get_settings()
        hosts = _resolve_hosts(settings.devitjobs_hosts or "")
        terms = _query_terms(query)
        headers = {"User-Agent": "FMI-MarketIntel/1.0", "Accept": "application/json"}
        records: list[RawJob] = []
        errors: list[str] = []
        pages = 0
        seen_ids: set[str] = set()
        seen_urls: set[str] = set()

        async with httpx.AsyncClient(timeout=60.0, headers=headers) as client:
            for host in hosts:
                if len(records) >= MAX_TOTAL:
                    break
                pages += 1
                url = f"https://devitjobs.{host}/api/jobsLight"
                try:
                    resp = await client.get(url)
                    resp.raise_for_status()
                    payload = resp.json() or []
                except Exception as exc:  # noqa: BLE001
                    errors.append(f"{host}: {exc}")
                    continue
                if not isinstance(payload, list):
                    errors.append(f"{host}: unexpected payload")
                    continue

                room = min(MAX_PER_HOST, MAX_TOTAL - len(records))
                for item in _select_items(payload, terms, room):
                    raw = _to_raw(item, host, errors)
                    if raw is None:
                        continue
                    key = str(item.get("_id") or "")
                    if key and key in seen_ids:
                        continue
                    if raw.url in seen_urls:
                        continue
                    if key:
                        seen_ids.add(key)
                    seen_urls.add(raw.url)
                    records.append(raw)
                    if len(records) >= MAX_TOTAL:
                        break

        return CollectorResult(records=records, pages_scanned=pages, errors=errors)


def _resolve_hosts(configured: str) -> list[str]:
    """Configured TLDs first, then fill from DEFAULT_HOSTS up to MAX_HOSTS."""
    out: list[str] = []
    for part in configured.split(","):
        h = part.strip().lower().lstrip(".")
        if h and h not in out:
            out.append(h)
        if len(out) >= MAX_HOSTS:
            return out
    for h in DEFAULT_HOSTS:
        if h not in out:
            out.append(h)
        if len(out) >= MAX_HOSTS:
            break
    return out or ["uk"]


def _query_terms(query: Optional[str]) -> list[str]:
    """Client-side match terms; empty means dump (no filter).

    Keeps OR clauses as separate terms (API has no server-side query).
    Generic/IT queries get a small synonym fan-out for recall.
    """
    raw = (query or "").strip()
    if not raw:
        return []
    parts = [p.strip().lower() for p in _OR_SPLIT.split(raw) if p.strip()]
    terms: list[str] = []
    for part in parts:
        if part and part not in terms:
            terms.append(part)
    # Fan-out only when a single short/generic clause was provided.
    if len(terms) == 1 and _should_fan_out(terms[0]):
        lower = terms[0]
        for extra in _IT_FANOUT:
            if extra in lower:
                continue
            terms.append(extra)
            if len(terms) >= MAX_QUERY_TERMS:
                break
    return terms[:MAX_QUERY_TERMS]


def _should_fan_out(q: str) -> bool:
    tokens = {t.lower() for t in _TOKEN_RE.findall(q)}
    if not tokens:
        return False
    if tokens & _TECH or len(tokens) <= 1:
        return True
    return bool(tokens & _GENERIC)


def _select_items(payload: list, terms: list[str], limit: int) -> list[dict]:
    """Filter, freshest-first, then stratify by techCategory (bounded)."""
    if limit <= 0:
        return []
    candidates: list[tuple[datetime, dict]] = []
    for item in payload:
        if not isinstance(item, dict) or item.get("isPaused"):
            continue
        if not item.get("_id") or not item.get("jobUrl"):
            continue
        if terms and not _matches_any(item, terms):
            continue
        candidates.append((_active_at(item), item))
    candidates.sort(key=lambda pair: pair[0], reverse=True)

    if not candidates:
        return []

    # Stratify so dumps are not dominated by a single techCategory.
    per_cat: dict[str, int] = {}
    picked: list[dict] = []
    for _, item in candidates:
        cat = str(item.get("techCategory") or "other")
        if per_cat.get(cat, 0) >= MAX_PER_CATEGORY:
            continue
        per_cat[cat] = per_cat.get(cat, 0) + 1
        picked.append(item)
        if len(picked) >= limit:
            break

    # If stratification left unused budget (few categories), fill from remainder.
    if len(picked) < limit:
        seen = {id(x) for x in picked}
        for _, item in candidates:
            if id(item) in seen:
                continue
            picked.append(item)
            if len(picked) >= limit:
                break
    return picked


def _matches_any(item: dict, terms: list[str]) -> bool:
    hay = " ".join(
        str(x)
        for x in (
            item.get("name"),
            item.get("techCategory"),
            item.get("metaCategory"),
            item.get("company"),
            " ".join(item.get("technologies") or []),
            " ".join(item.get("filterTags") or []),
        )
        if x
    ).lower()
    return any(term in hay for term in terms)


def _active_at(item: dict) -> datetime:
    active = item.get("activeFrom")
    if active:
        try:
            return datetime.fromisoformat(str(active).replace("Z", "+00:00"))
        except ValueError:
            pass
    return datetime.min.replace(tzinfo=timezone.utc)


def _to_raw(item: dict, host: str, errors: list[str]) -> RawJob | None:
    job_id = item.get("_id")
    slug = item.get("jobUrl")
    if not job_id or not slug:
        return None
    title = item.get("name") or "Untitled"
    job_url = f"https://devitjobs.{host}/jobs/{slug}"
    published = datetime.now(timezone.utc)
    active = item.get("activeFrom")
    if active:
        try:
            published = datetime.fromisoformat(str(active).replace("Z", "+00:00"))
        except ValueError:
            errors.append(f"invalid activeFrom for {job_id}")
    loc_bits = [
        x
        for x in (item.get("cityCategory"), item.get("actualCity"), item.get("workplace"))
        if x
    ]
    tags = list(item.get("technologies") or [])[:20]
    if item.get("techCategory"):
        tags.insert(0, str(item["techCategory"]))
    return RawJob(
        source_job_id=f"{host}:{job_id}",
        url=job_url,
        title=title,
        company=item.get("company"),
        description=None,
        location=", ".join(loc_bits) or host.upper(),
        published_at=published,
        salary_text=_salary_text(item, host),
        tags=tags,
        job_type=item.get("jobType"),
        remote_hint=_remote_hint(item),
        raw=item,
    )


def _salary_text(item: dict, host: str) -> str | None:
    lo = item.get("annualSalaryFrom")
    hi = item.get("annualSalaryTo")
    if lo is None and hi is None:
        return None
    currency = _CURRENCY.get(host, "GBP")
    if lo is not None and hi is not None and lo == hi:
        return f"{lo} {currency}/year"
    return f"{lo or '?'}-{hi or '?'} {currency}/year"


def _remote_hint(item: dict) -> bool | None:
    workplace = str(item.get("workplace") or "").lower()
    remote_type = str(item.get("remoteType") or "").lower()
    if workplace == "remote" or remote_type in {"full", "onlycountry", "worldwide"}:
        return True
    if workplace in {"office", "hybrid"}:
        return False
    return None
