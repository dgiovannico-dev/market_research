"""Resolve Job.evidence_tier from collector raw tags / heuristics."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.collectors.base import RawJob
from app.storage.enums import EvidenceTier

_VALID = {EvidenceTier.standard.value, EvidenceTier.thin.value}


def resolve_evidence_tier(raw: RawJob) -> str:
    """Prefer explicit collector tag; empty description → thin."""
    tagged = None
    if isinstance(raw.raw, dict):
        tagged = raw.raw.get("evidence_tier")
    if isinstance(tagged, str) and tagged.strip().lower() in _VALID:
        return tagged.strip().lower()
    if not (raw.description or "").strip():
        return EvidenceTier.thin.value
    return EvidenceTier.standard.value


def source_snapshot_at_from_raw(raw: RawJob) -> datetime | None:
    """Optional dump snapshot timestamp from collector raw."""
    if not isinstance(raw.raw, dict):
        return None
    val: Any = raw.raw.get("source_snapshot_at") or raw.raw.get("snapshot_at")
    if isinstance(val, datetime):
        return val if val.tzinfo else val.replace(tzinfo=timezone.utc)
    if isinstance(val, str) and val.strip():
        try:
            return datetime.fromisoformat(val.strip().replace("Z", "+00:00"))
        except ValueError:
            return None
    return None
