"""Read-only SQL policy for MCP queries."""

from __future__ import annotations

import re
from dataclasses import dataclass

ALLOWED_TABLES: frozenset[str] = frozenset(
    {
        "jobs",
        "job_skills",
        "job_rates",
        "job_snapshots",
        "sources",
        "source_verifications",
        "technologies",
        "collection_runs",
        "market_metrics_daily",
        "duplicate_groups",
        "search_queries",
        "user_profiles",
        "user_skills",
        "application_outcomes",
        "saved_filters",
        "alerts",
    }
)

DENIED_TABLES: frozenset[str] = frozenset({"audit_logs", "llm_models"})

_FORBIDDEN = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|GRANT|REVOKE|"
    r"COPY|CALL|EXECUTE|MERGE|REPLACE|ATTACH|DETACH|VACUUM|COMMENT|SECURITY)\b",
    re.IGNORECASE,
)
_FROM_JOIN = re.compile(r"\b(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_]*)", re.IGNORECASE)
_MAX_LIMIT = 500


@dataclass(frozen=True)
class SqlPolicyResult:
    ok: bool
    error: str | None = None
    tables: tuple[str, ...] = ()
    limit: int = 100


def clamp_limit(limit: int) -> int:
    if limit < 1:
        return 1
    return min(limit, _MAX_LIMIT)


def assert_readonly_sql(sql: str, *, limit: int = 100) -> SqlPolicyResult:
    """Validate SQL is a single allowlisted SELECT. Does not execute."""
    text = (sql or "").strip()
    if not text:
        return SqlPolicyResult(ok=False, error="empty SQL")
    if ";" in text.rstrip(";"):
        return SqlPolicyResult(ok=False, error="multi-statement SQL is not allowed")
    text = text.rstrip(";").strip()
    if not re.match(r"(?is)^with\b|^select\b", text):
        return SqlPolicyResult(ok=False, error="only SELECT (or WITH ... SELECT) is allowed")
    if _FORBIDDEN.search(text):
        return SqlPolicyResult(ok=False, error="forbidden keyword in SQL")
    tables = tuple(t.lower() for t in _FROM_JOIN.findall(text))
    if not tables:
        return SqlPolicyResult(ok=False, error="no FROM/JOIN table found")
    for t in tables:
        if t in DENIED_TABLES:
            return SqlPolicyResult(ok=False, error=f"table not allowed: {t}", tables=tables)
        if t not in ALLOWED_TABLES:
            return SqlPolicyResult(ok=False, error=f"table not allowlisted: {t}", tables=tables)
    return SqlPolicyResult(ok=True, tables=tables, limit=clamp_limit(limit))
