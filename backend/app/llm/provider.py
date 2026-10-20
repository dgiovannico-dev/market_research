from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import httpx

from app.core.config import get_settings


class LLMProvider(ABC):
    name: str

    @abstractmethod
    async def health(self) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def classify_text(self, text: str, schema_hint: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError


class NullLLMProvider(LLMProvider):
    name = "none"

    async def health(self) -> dict[str, Any]:
        return {
            "provider": self.name,
            "healthy": True,
            "mode": "rules_only",
            "message": "LLM disabled; deterministic rules are used.",
        }

    async def classify_text(self, text: str, schema_hint: dict[str, Any]) -> dict[str, Any]:
        raise RuntimeError("LLM provider is disabled")


class OllamaProvider(LLMProvider):
    name = "ollama"

    def __init__(self) -> None:
        settings = get_settings()
        self.base_url = settings.ollama_base_url.rstrip("/")
        self.model = settings.ollama_model

    async def health(self) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                resp.raise_for_status()
                models = [m.get("name") for m in resp.json().get("models", [])]
                return {
                    "provider": self.name,
                    "healthy": True,
                    "model": self.model,
                    "available_models": models,
                    "structured_output": "model-dependent",
                }
        except Exception as exc:  # noqa: BLE001
            return {"provider": self.name, "healthy": False, "error": str(exc)}

    async def classify_text(self, text: str, schema_hint: dict[str, Any]) -> dict[str, Any]:
        prompt = (
            "Extract job classification as JSON matching this schema keys: "
            f"{list(schema_hint.keys())}. Use only evidence from the text. "
            "If unknown, use null/unknown. Do not invent rates.\n\n"
            f"TEXT:\n{text[:12000]}"
        )
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False, "format": "json"},
            )
            resp.raise_for_status()
            raw = resp.json().get("response", "{}")
            import json

            return json.loads(raw)


class VLLMProvider(LLMProvider):
    name = "vllm"

    def __init__(self) -> None:
        settings = get_settings()
        self.base_url = settings.vllm_base_url.rstrip("/")
        self.api_key = settings.vllm_api_key
        self.model = settings.vllm_model

    async def health(self) -> dict[str, Any]:
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        try:
            async with httpx.AsyncClient(timeout=5.0, headers=headers) as client:
                resp = await client.get(f"{self.base_url}/models")
                resp.raise_for_status()
                return {
                    "provider": self.name,
                    "healthy": True,
                    "model": self.model,
                    "models": resp.json(),
                }
        except Exception as exc:  # noqa: BLE001
            return {"provider": self.name, "healthy": False, "error": str(exc)}

    async def classify_text(self, text: str, schema_hint: dict[str, Any]) -> dict[str, Any]:
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        messages = [
            {
                "role": "system",
                "content": "Return valid JSON only. Never invent missing rates or jobs.",
            },
            {
                "role": "user",
                "content": f"Schema keys: {list(schema_hint.keys())}\nTEXT:\n{text[:12000]}",
            },
        ]
        async with httpx.AsyncClient(timeout=120.0, headers=headers) as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                json={"model": self.model, "messages": messages, "temperature": 0.1},
            )
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]
            import json

            return json.loads(content)


def get_llm_provider() -> LLMProvider:
    settings = get_settings()
    if settings.llm_provider == "ollama":
        return OllamaProvider()
    if settings.llm_provider == "vllm":
        return VLLMProvider()
    return NullLLMProvider()
