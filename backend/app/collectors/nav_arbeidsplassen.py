"""NAV Arbeidsplassen (Norway) — public stillinger search JSON (no key)."""

from __future__ import annotations

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

BASE_URL = "https://arbeidsplassen.nav.no/stillinger/api/search"
DETAIL_URL = "https://arbeidsplassen.nav.no/stillinger/stilling/{uuid}"
MAX_RECORDS = 50


class NavArbeidsplassenCollector(BaseCollector):
    name = "NAV Arbeidsplassen"
    source_key = "nav_arbeidsplassen"
    collection_mode = "search"
    base_url = BASE_URL

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        if is_blank_query(query):
            return missing_query_result()
        q = simplify_query_for(self, query or "")
        headers = {"User-Agent": "FMI-MarketIntel/1.0", "Accept": "application/json"}
        params = {"q": q, "size": MAX_RECORDS}
        try:
            async with httpx.AsyncClient(timeout=45.0, headers=headers, follow_redirects=True) as client:
                resp = await client.get(BASE_URL, params=params)
                resp.raise_for_status()
                payload = resp.json() or {}
        except Exception as exc:  # noqa: BLE001
            return CollectorResult(records=[], pages_scanned=1, errors=[str(exc)])

        hits = ((payload.get("hits") or {}).get("hits")) if isinstance(payload, dict) else None
        if not isinstance(hits, list):
            return CollectorResult(records=[], pages_scanned=1, errors=["unexpected payload"])

        records: list[RawJob] = []
        for hit in hits[:MAX_RECORDS]:
            if not isinstance(hit, dict):
                continue
            src = hit.get("_source") if isinstance(hit.get("_source"), dict) else hit
            if not isinstance(src, dict):
                continue
            uid = src.get("uuid") or hit.get("_id")
            title = src.get("title") or "Untitled"
            if not uid:
                continue
            props = src.get("properties") if isinstance(src.get("properties"), dict) else {}
            employer = src.get("employer") if isinstance(src.get("employer"), dict) else {}
            company = employer.get("name") or props.get("employer") or src.get("businessName")
            records.append(
                RawJob(
                    source_job_id=str(uid),
                    url=DETAIL_URL.format(uuid=uid),
                    title=title,
                    company=company,
                    description=_description(src),
                    location=_location(src, props),
                    published_at=_published(src),
                    salary_text=None,
                    tags=_tags(src, props),
                    job_type=None,
                    remote_hint=_remote_hint(props),
                    raw=_trim_raw(src),
                )
            )
        return CollectorResult(records=records, pages_scanned=1, errors=[])


def _description(src: dict[str, Any]) -> str | None:
    meta = src.get("generatedSearchMetadata") or {}
    if isinstance(meta, dict) and meta.get("shortSummary"):
        return str(meta["shortSummary"])
    return None


def _location(src: dict[str, Any], props: dict[str, Any]) -> str | None:
    if props.get("location"):
        return str(props["location"])
    locs = src.get("locationList") or []
    if isinstance(locs, list) and locs:
        loc = locs[0]
        if isinstance(loc, dict):
            bits = [loc.get("city"), loc.get("county"), loc.get("country")]
            joined = ", ".join(str(b) for b in bits if b)
            return joined or "Norway"
    return "Norway"


def _published(src: dict[str, Any]) -> datetime:
    raw = src.get("published")
    if raw:
        try:
            return datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
        except ValueError:
            pass
    return datetime.now(timezone.utc)


def _tags(src: dict[str, Any], props: dict[str, Any]) -> list[str]:
    tags: list[str] = []
    for key in ("searchtagsai", "keywords"):
        val = props.get(key)
        if isinstance(val, list):
            tags.extend(str(t) for t in val[:10] if t)
        elif isinstance(val, str) and val:
            tags.extend(p.strip() for p in val.split(",") if p.strip())
    for cat in (src.get("categoryList") or [])[:5]:
        if isinstance(cat, dict) and cat.get("name"):
            tags.append(str(cat["name"]))
    # dedupe preserve order
    seen: set[str] = set()
    out: list[str] = []
    for t in tags:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out[:20]


def _remote_hint(props: dict[str, Any]) -> bool | None:
    remote = str(props.get("remote") or "").lower()
    if not remote:
        return None
    if "hjemme" in remote or "remote" in remote or "hybrid" in remote:
        return True
    if "kontor" in remote or "stedbundet" in remote:
        return False
    return None


def _trim_raw(src: dict[str, Any]) -> dict[str, Any]:
    return {
        "uuid": src.get("uuid"),
        "title": src.get("title"),
        "published": src.get("published"),
        "businessName": src.get("businessName"),
        "properties": {
            "employer": (src.get("properties") or {}).get("employer"),
            "location": (src.get("properties") or {}).get("location"),
            "remote": (src.get("properties") or {}).get("remote"),
        }
        if isinstance(src.get("properties"), dict)
        else None,
        "country_code": "NO",
    }
