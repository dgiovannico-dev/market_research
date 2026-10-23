"""Driven port: optional LLM I/O (classification / health). Briefs are rules-only."""

from __future__ import annotations

from typing import Any, Protocol


class LlmGateway(Protocol):
    name: str

    async def health(self) -> dict[str, Any]:
        ...

    async def classify_text(self, text: str, schema_hint: dict[str, Any]) -> dict[str, Any]:
        ...
