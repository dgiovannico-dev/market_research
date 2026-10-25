"""Driven port: optional LLM I/O (classification / chat / health)."""

from __future__ import annotations

from typing import Any, Optional, Protocol


class LlmGateway(Protocol):
    name: str

    async def health(self) -> dict[str, Any]:
        ...

    async def classify_text(self, text: str, schema_hint: dict[str, Any]) -> dict[str, Any]:
        ...

    async def chat(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: Optional[float] = None,
        response_json: bool = False,
    ) -> str:
        ...
