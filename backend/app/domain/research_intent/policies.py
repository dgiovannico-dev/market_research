"""Pure policies for research intents (no SQLAlchemy session I/O)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

VALID_KINDS = frozenset({"discovery", "focus"})


def resolve_display_name(
    *,
    name: Optional[str] = None,
    label: Optional[str] = None,
) -> str:
    value = (name or label or "").strip()
    if not value:
        raise ValueError("name or label is required")
    return value


def bump_version(row: Any) -> None:
    row.version = int(getattr(row, "version", None) or 1) + 1


def apply_soft_delete(row: Any, *, when: Optional[datetime] = None) -> None:
    """Soft-delete: set deleted_at and disable scheduling."""
    row.deleted_at = when or datetime.now(timezone.utc)
    row.enabled = False
