"""France Travail Offres d'emploi v2 — OAuth2 client credentials.

Fail-closed without FRANCE_TRAVAIL_CLIENT_ID + FRANCE_TRAVAIL_CLIENT_SECRET.
When a query is set, search uses Offres v2 ``motsCles`` plus up to three IT
``codeROME`` values (M1805/M1802/M1806) for denser tech market intel. Fetches
at most two pages via ``range`` when Content-Range (or a full page) indicates
more results.
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
from app.core.config import get_settings
from app.secrets.resolve import credential_bundle

_TOKEN_URL = (
    "https://entreprise.francetravail.fr/connexion/oauth2/access_token"
    "?realm=%2Fpartenaire"
)
_SEARCH_URL = "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search"

# Offres v2 allows 1–3 codeROME values. IT / SI cluster for market intel.
_IT_ROME_CODES: tuple[str, ...] = (
    "M1805",  # Études et développement informatique
    "M1802",  # Expertise et support en systèmes d'information
    "M1806",  # Conseil et maîtrise d'ouvrage en systèmes d'information
)

PAGE_SIZE = 50
MAX_PAGES = 2
_CONTENT_RANGE_RE = re.compile(
    r"(?:offres\s+)?(?P<start>\d+)\s*-\s*(?P<end>\d+)\s*/\s*(?P<total>\d+)",
    re.IGNORECASE,
)


def build_search_params(mots: str, *, start: int = 0) -> dict[str, Any]:
    """Offres v2 query params for one page (``motsCles``, ``codeROME``, ``range``)."""
    end = start + PAGE_SIZE - 1
    return {
        "motsCles": mots,
        "codeROME": list(_IT_ROME_CODES),
        "range": f"{start}-{end}",
    }


def parse_content_range_total(header: str | None) -> int | None:
    """Parse Offres Content-Range total, e.g. ``offres 0-49/120`` → 120."""
    if not header:
        return None
    match = _CONTENT_RANGE_RE.search(header.strip())
    if not match:
        return None
    try:
        return int(match.group("total"))
    except ValueError:
        return None


def _parse_item(item: dict[str, Any]) -> RawJob | None:
    job_id = item.get("id")
    if not job_id:
        return None
    lieu = item.get("lieuTravail") or {}
    location = lieu.get("libelle") if isinstance(lieu, dict) else None
    company = None
    entreprise = item.get("entreprise") or {}
    if isinstance(entreprise, dict):
        company = entreprise.get("nom")
    pub_raw = item.get("dateCreation") or item.get("dateActualisation")
    published = datetime.now(timezone.utc)
    if pub_raw:
        try:
            published = datetime.fromisoformat(str(pub_raw).replace("Z", "+00:00"))
        except ValueError:
            pass
    salary = item.get("salaire") or {}
    salary_text = salary.get("libelle") if isinstance(salary, dict) else None
    origine = item.get("origineOffre") if isinstance(item.get("origineOffre"), dict) else {}
    url = (origine or {}).get("urlOrigine") or item.get("url") or ""
    return RawJob(
        source_job_id=str(job_id),
        url=url,
        title=item.get("intitule") or "Untitled",
        company=company,
        description=item.get("description"),
        location=location,
        published_at=published,
        salary_text=salary_text,
        tags=[],
        job_type=item.get("typeContrat"),
        remote_hint=None,
        raw=item,
    )


def _should_fetch_next(page_len: int, start: int, total: int | None) -> bool:
    if page_len < PAGE_SIZE:
        return False
    if total is None:
        return True
    return start + page_len < total


class FranceTravailCollector(BaseCollector):
    name = "France Travail"
    source_key = "france_travail"
    collection_mode = "search"
    base_url = _SEARCH_URL

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        if is_blank_query(query):
            return missing_query_result()
        settings = get_settings()
        creds = credential_bundle("france_travail")
        client_id = (creds.get("client_id") or "").strip()
        client_secret = (creds.get("client_secret") or "").strip()
        if not client_id or not client_secret:
            return CollectorResult(
                records=[],
                pages_scanned=0,
                errors=["FRANCE_TRAVAIL_CLIENT_ID and FRANCE_TRAVAIL_CLIENT_SECRET are required"],
            )

        scope = settings.france_travail_scope.strip() or "api_offresdemploiv2 o2dsoffre"
        mots = simplify_query_for(self, query or "")
        records: list[RawJob] = []
        seen: set[str] = set()
        pages_scanned = 0
        errors: list[str] = []

        async with httpx.AsyncClient(timeout=45.0) as client:
            try:
                token_resp = await client.post(
                    _TOKEN_URL,
                    data={
                        "grant_type": "client_credentials",
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "scope": scope,
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
                if token_resp.status_code in (400, 401, 403):
                    return CollectorResult(
                        records=[],
                        pages_scanned=0,
                        errors=[f"France Travail token failed HTTP {token_resp.status_code}"],
                    )
                token_resp.raise_for_status()
                access = (token_resp.json() or {}).get("access_token")
                if not access:
                    return CollectorResult(
                        records=[],
                        pages_scanned=0,
                        errors=["France Travail token response missing access_token"],
                    )
            except Exception as exc:  # noqa: BLE001
                return CollectorResult(records=[], pages_scanned=0, errors=[str(exc)])

            auth_headers = {
                "Authorization": f"Bearer {access}",
                "Accept": "application/json",
            }

            for page_idx in range(MAX_PAGES):
                start = page_idx * PAGE_SIZE
                params = build_search_params(mots, start=start)
                try:
                    resp = await client.get(
                        _SEARCH_URL,
                        params=params,
                        headers=auth_headers,
                    )
                    pages_scanned += 1
                    if resp.status_code in (401, 403):
                        errors.append(f"France Travail search failed HTTP {resp.status_code}")
                        break
                    resp.raise_for_status()
                    payload: dict[str, Any] = resp.json() or {}
                except Exception as exc:  # noqa: BLE001
                    errors.append(str(exc))
                    break

                results = payload.get("resultats") or []
                for item in results:
                    if not isinstance(item, dict):
                        continue
                    job = _parse_item(item)
                    if job is None or job.source_job_id in seen:
                        continue
                    seen.add(job.source_job_id)
                    records.append(job)

                total = parse_content_range_total(resp.headers.get("Content-Range"))
                if page_idx + 1 >= MAX_PAGES or not _should_fetch_next(
                    len(results), start, total
                ):
                    break

        return CollectorResult(records=records, pages_scanned=pages_scanned, errors=errors)
