"""Upwork GraphQL marketplace job search — requires UPWORK_OAUTH_TOKEN.

Docs: https://www.upwork.com/developer/
Endpoint: POST https://api.upwork.com/graphql
Auth: Authorization: Bearer <token>; optional X-Upwork-API-TenantId
Query: marketplaceJobPostingsSearch (scope: Read marketplace Job Postings)

API key eligibility is partner-gated (manual review). Scaffold stays
NEEDS_CREDENTIALS until an approved token returns live jobs.
"""

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
from app.core.config import get_settings
from app.secrets.resolve import credential_bundle

MAX_RECORDS = 50
GRAPHQL_URL = "https://api.upwork.com/graphql"

_SEARCH_QUERY = """
query SearchJobs($filter: MarketplaceJobPostingsSearchFilter) {
  marketplaceJobPostingsSearch(
    marketPlaceJobFilter: $filter
    searchType: USER_JOBS_SEARCH
    sortAttributes: [{ field: RECENCY }]
  ) {
    totalCount
    edges {
      node {
        id
        title
        description
        ciphertext
        createdDateTime
        amount { displayValue currency }
        skills { name }
      }
    }
  }
}
""".strip()


def _parse_published(value: Any) -> datetime:
    if value is None or value == "":
        return datetime.now(timezone.utc)
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return datetime.now(timezone.utc)


def _salary_text(node: dict[str, Any]) -> str | None:
    amount = node.get("amount")
    if not isinstance(amount, dict):
        return None
    display = amount.get("displayValue")
    currency = amount.get("currency") or ""
    if display:
        return f"{currency} {display}".strip() if currency else str(display)
    return None


def _tags(node: dict[str, Any]) -> list[str]:
    raw = node.get("skills") or []
    if not isinstance(raw, list):
        return []
    out: list[str] = []
    seen: set[str] = set()
    for item in raw:
        name = item.get("name") if isinstance(item, dict) else item
        if not name:
            continue
        text = str(name).strip()
        if text and text not in seen:
            seen.add(text)
            out.append(text)
        if len(out) >= 12:
            break
    return out


def _parse_node(node: dict[str, Any]) -> RawJob | None:
    job_id = node.get("id") or node.get("ciphertext")
    if job_id is None:
        return None
    cipher = node.get("ciphertext") or job_id
    url = f"https://www.upwork.com/jobs/~{cipher}"
    title = node.get("title") or "Untitled"
    desc = node.get("description")
    return RawJob(
        source_job_id=str(job_id),
        url=url,
        title=str(title),
        company=None,
        description=str(desc) if desc else None,
        location=None,
        published_at=_parse_published(node.get("createdDateTime")),
        salary_text=_salary_text(node),
        tags=_tags(node),
        job_type=None,
        remote_hint=True,
        raw=node,
    )


class UpworkCollector(BaseCollector):
    name = "Upwork GraphQL"
    source_key = "upwork"
    collection_mode = "search"

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        if is_blank_query(query):
            return missing_query_result()
        settings = get_settings()
        creds = credential_bundle("upwork")
        token = (creds.get("oauth_token") or "").strip()
        if not token:
            return CollectorResult(
                records=[],
                pages_scanned=0,
                errors=["UPWORK_OAUTH_TOKEN is required"],
            )

        search = simplify_query_for(self, query or "")
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "FMI-MarketIntel/1.0",
        }
        tenant = (creds.get("tenant_id") or "").strip()
        if tenant:
            headers["X-Upwork-API-TenantId"] = tenant

        variables = {
            "filter": {
                "searchExpression_eq": search,
                "pagination_eq": {"after": "0", "first": MAX_RECORDS},
            }
        }
        body = {"query": _SEARCH_QUERY, "variables": variables}

        async with httpx.AsyncClient(timeout=45.0, headers=headers) as client:
            try:
                resp = await client.post(GRAPHQL_URL, json=body)
                if resp.status_code in (401, 403):
                    return CollectorResult(
                        records=[],
                        pages_scanned=1,
                        errors=[f"Upwork auth failed HTTP {resp.status_code}"],
                    )
                resp.raise_for_status()
                payload = resp.json() or {}
            except Exception as exc:  # noqa: BLE001
                return CollectorResult(records=[], pages_scanned=1, errors=[str(exc)])

        if isinstance(payload, dict) and payload.get("errors"):
            msgs = []
            for err in payload["errors"]:
                if isinstance(err, dict) and err.get("message"):
                    msgs.append(str(err["message"]))
            return CollectorResult(
                records=[],
                pages_scanned=1,
                errors=msgs or ["Upwork GraphQL errors"],
            )

        data = payload.get("data") if isinstance(payload, dict) else None
        conn = (
            data.get("marketplaceJobPostingsSearch")
            if isinstance(data, dict)
            else None
        )
        edges = conn.get("edges") if isinstance(conn, dict) else None
        if not isinstance(edges, list):
            edges = []

        records: list[RawJob] = []
        seen: set[str] = set()
        for edge in edges:
            if not isinstance(edge, dict):
                continue
            node = edge.get("node")
            if not isinstance(node, dict):
                continue
            job = _parse_node(node)
            if job is None or job.source_job_id in seen:
                continue
            seen.add(job.source_job_id)
            records.append(job)
            if len(records) >= MAX_RECORDS:
                break

        return CollectorResult(records=records, pages_scanned=1, errors=[])
