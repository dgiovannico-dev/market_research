"""Careerjet Partner API v4 — requires CAREERJET_API_KEY.

Official docs:
  https://www.careerjet.com/partners/api/
  https://www.careerjet.it/partners/api/

Endpoint: GET https://search.api.careerjet.net/v4/query
Auth: HTTP Basic (API key as username, empty password).
Required query params: user_ip, user_agent (per publisher terms).
Locales for IT/DE/CH/LU: it_IT, de_DE, de_CH, fr_CH, fr_LU.
Optional filters: contract_type (e.g. ``c`` = contract), keywords, location.
"""

from __future__ import annotations

import base64
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
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
from app.core.config import get_settings
from app.secrets.resolve import credential_bundle

API_URL = "https://search.api.careerjet.net/v4/query"
DEFAULT_LOCALES = ("it_IT", "de_DE", "de_CH", "fr_CH", "fr_LU")
MAX_PAGES_PER_LOCALE = 2
PAGE_SIZE = 50


def resolve_careerjet_locales(locales_csv: str) -> list[str]:
    """Parse CAREERJET_LOCALES or fall back to DEFAULT_LOCALES (deduped, order kept)."""
    parts = [p.strip() for p in (locales_csv or "").split(",") if p.strip()]
    if parts:
        return list(dict.fromkeys(parts))
    return list(DEFAULT_LOCALES)


def _basic_auth_header(api_key: str) -> str:
    token = base64.b64encode(f"{api_key}:".encode()).decode("ascii")
    return f"Basic {token}"


def _parse_date(value: Any) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    text = str(value).strip()
    try:
        dt = parsedate_to_datetime(text)
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt
    except (TypeError, ValueError):
        pass
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return datetime.now(timezone.utc)


def _parse_item(item: dict[str, Any], locale: str) -> RawJob | None:
    url = (item.get("url") or "").strip()
    if not url:
        return None
    title = (item.get("title") or "").strip() or "Untitled"
    raw = dict(item) if isinstance(item, dict) else {}
    raw["_careerjet_locale"] = locale
    locations = item.get("locations")
    if isinstance(locations, list):
        location = ", ".join(str(x) for x in locations if x)
    else:
        location = str(locations).strip() if locations else None
    return RawJob(
        source_job_id=url,
        url=url,
        title=title,
        company=item.get("company"),
        description=item.get("description"),
        location=location or None,
        published_at=_parse_date(item.get("date")),
        salary_text=item.get("salary"),
        tags=[],
        job_type=None,
        remote_hint=None,
        raw=raw,
    )


class CareerjetCollector(BaseCollector):
    name = "Careerjet"
    source_key = "careerjet"
    collection_mode = "search"

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        if is_blank_query(query):
            return missing_query_result()
        settings = get_settings()
        creds = credential_bundle("careerjet")
        api_key = (creds.get("api_key") or "").strip()
        if not api_key:
            return CollectorResult(
                records=[],
                pages_scanned=0,
                errors=["CAREERJET_API_KEY is required"],
            )

        user_ip = (creds.get("user_ip") or "").strip()
        if not user_ip:
            return CollectorResult(
                records=[],
                pages_scanned=0,
                errors=["CAREERJET_USER_IP is required for partner API calls"],
            )

        user_agent = settings.careerjet_user_agent.strip() or "FMI-MarketIntel/1.0"
        keywords = simplify_query_for(self, query or "")
        locales = resolve_careerjet_locales(settings.careerjet_locales)
        location = settings.careerjet_location.strip()
        contract_type = settings.careerjet_contract_type.strip()

        headers = {
            "Authorization": _basic_auth_header(api_key),
            "Accept": "application/json",
            "User-Agent": user_agent,
        }
        errors: list[str] = []
        seen: set[str] = set()
        records: list[RawJob] = []
        pages_scanned = 0

        async with httpx.AsyncClient(timeout=45.0, headers=headers) as client:
            for locale in locales:
                for page in range(1, MAX_PAGES_PER_LOCALE + 1):
                    params: dict[str, Any] = {
                        "locale_code": locale,
                        "keywords": keywords,
                        "page": page,
                        "page_size": PAGE_SIZE,
                        "user_ip": user_ip,
                        "user_agent": user_agent,
                        "sort": "date",
                    }
                    if location:
                        params["location"] = location
                    if contract_type:
                        params["contract_type"] = contract_type

                    try:
                        resp = await client.get(API_URL, params=params)
                        pages_scanned += 1
                        if resp.status_code in (401, 403):
                            return CollectorResult(
                                records=records,
                                pages_scanned=pages_scanned,
                                errors=[
                                    *errors,
                                    f"Careerjet auth failed HTTP {resp.status_code}",
                                ],
                            )
                        resp.raise_for_status()
                        payload = resp.json() or {}
                    except Exception as exc:  # noqa: BLE001
                        errors.append(f"{locale} p{page}: {exc}")
                        break

                    if payload.get("type") == "LOCATIONS":
                        msg = payload.get("message") or "location resolution required"
                        errors.append(f"{locale}: {msg}")
                        break

                    jobs = payload.get("jobs") or []
                    if not isinstance(jobs, list):
                        break
                    for item in jobs:
                        if not isinstance(item, dict):
                            continue
                        job = _parse_item(item, locale)
                        if job is None or job.source_job_id in seen:
                            continue
                        seen.add(job.source_job_id)
                        records.append(job)

                    total_pages = payload.get("pages")
                    if isinstance(total_pages, int) and page >= total_pages:
                        break
                    if len(jobs) < PAGE_SIZE:
                        break

        return CollectorResult(records=records, pages_scanned=pages_scanned, errors=errors)
