"""Driven port: source catalog system of record (ADR-005)."""

from __future__ import annotations

from typing import Any, Protocol


class SourceCatalogPort(Protocol):
    def load(self) -> dict[str, Any]:
        """Full catalog document (sources list + metadata)."""
        ...

    def summary(self) -> dict[str, Any]:
        """Aggregated counts / ACTIVE connector keys."""
        ...
