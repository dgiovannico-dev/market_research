"""Driven port: external reference stats (Eurostat / ADEM) — mockable HTTP."""

from __future__ import annotations

from typing import Any, Protocol


class ExternalStatsGateway(Protocol):
    async def eurostat_series(
        self,
        dataset: str,
        *,
        geo: str = "DE",
        time: str | None = "2022",
        limit: int = 20,
    ) -> dict[str, Any]:
        ...

    def eurostat_datasets(self) -> dict[str, Any]:
        ...

    def adem_skills_summary(
        self,
        *,
        nace_prefix: str | None = None,
        limit: int = 50,
    ) -> dict[str, Any]:
        ...
