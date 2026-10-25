"""Resolve free-text profile skills to taxonomy canonical names."""

from __future__ import annotations

from functools import lru_cache

from app.classification.taxonomy import build_alias_index


@lru_cache(maxsize=1)
def _alias_index() -> dict[str, str]:
    return build_alias_index()


def resolve_owned_skill_names(raw: list[str] | None) -> set[str]:
    """Map user-entered skills (any case/alias) to taxonomy canonical names.

    Unknown tokens are kept trimmed as entered so custom labels still match
    if they equal a ``Technology.canonical_name`` exactly; comparisons against
    the corpus should use :func:`names_match_owned`.
    """
    out: set[str] = set()
    index = _alias_index()
    for item in raw or []:
        s = str(item).strip()
        if not s:
            continue
        out.add(index.get(s.lower(), s))
    return out


def names_match_owned(technology: str, owned: set[str]) -> bool:
    """Case-insensitive membership of a corpus technology in the owned set."""
    if not technology:
        return False
    if technology in owned:
        return True
    lower = technology.lower()
    return any(o.lower() == lower for o in owned)
