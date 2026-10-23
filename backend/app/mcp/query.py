"""Execute allowlisted read-only queries; observed counts live in application."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.application.assistant.observed import get_observed_counts
from app.mcp.allowlist import assert_readonly_sql, clamp_limit

__all__ = ["QueryResult", "get_observed_counts", "run_readonly_query"]


@dataclass
class QueryResult:
    ok: bool
    error: str | None = None
    columns: list[str] = field(default_factory=list)
    rows: list[dict[str, Any]] = field(default_factory=list)
    row_count: int = 0
    truncated: bool = False
    tables: list[str] = field(default_factory=list)


def run_readonly_query(
    db: Session,
    sql: str,
    params: dict[str, Any] | None = None,
    *,
    limit: int = 100,
) -> QueryResult:
    policy = assert_readonly_sql(sql, limit=limit)
    if not policy.ok:
        return QueryResult(ok=False, error=policy.error)
    lim = clamp_limit(limit)
    # Wrap to enforce LIMIT without trusting client SQL
    wrapped = f"SELECT * FROM ({sql.rstrip().rstrip(';')}) AS _fmi_mcp_q LIMIT :_fmi_limit"
    bind = dict(params or {})
    bind["_fmi_limit"] = lim
    try:
        result = db.execute(text(wrapped), bind)
        keys = list(result.keys())
        fetched = result.fetchall()
        rows = [dict(zip(keys, row, strict=True)) for row in fetched]
        safe_rows: list[dict[str, Any]] = []
        for row in rows:
            safe_rows.append({k: _jsonable(v) for k, v in row.items()})
        return QueryResult(
            ok=True,
            columns=keys,
            rows=safe_rows,
            row_count=len(safe_rows),
            truncated=len(safe_rows) >= lim,
            tables=list(policy.tables),
        )
    except Exception as exc:  # noqa: BLE001 — surface DB errors to MCP client
        return QueryResult(ok=False, error=f"query failed: {exc}")


def _jsonable(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, (list, dict)):
        return value
    return str(value)
