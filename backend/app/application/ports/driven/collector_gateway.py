"""Driven port: resolve and invoke job-board collectors."""

from __future__ import annotations

from typing import Optional, Protocol, Sequence

from app.collectors.base import BaseCollector, CollectionMode, CollectorResult


class CollectorGateway(Protocol):
    def get(self, source_key: str) -> BaseCollector | None:
        ...

    def keys_by_mode(self, mode: CollectionMode) -> Sequence[str]:
        ...

    async def collect(
        self,
        source_key: str,
        query: Optional[str] = None,
    ) -> CollectorResult:
        ...
