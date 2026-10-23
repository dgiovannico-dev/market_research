"""CollectorGateway adapter over the in-process registry."""

from __future__ import annotations

from typing import Optional, Sequence

from app.collectors.base import BaseCollector, CollectionMode, CollectorResult
from app.collectors.registry import collectors_by_mode, get_collector


class RegistryCollectorGateway:
    def get(self, source_key: str) -> BaseCollector | None:
        return get_collector(source_key)

    def keys_by_mode(self, mode: CollectionMode) -> Sequence[str]:
        return list(collectors_by_mode(mode).keys())

    async def collect(
        self,
        source_key: str,
        query: Optional[str] = None,
    ) -> CollectorResult:
        collector = get_collector(source_key)
        if collector is None:
            return CollectorResult(
                records=[],
                pages_scanned=0,
                errors=[f"unknown_collector:{source_key}"],
            )
        return await collector.collect(query=query)


DEFAULT_COLLECTOR_GATEWAY = RegistryCollectorGateway()
