"""LLM providers: none / ollama / openai_compatible / gemini (ADR-010)."""

from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Optional

import httpx
from sqlalchemy.orm import Session

from app.application.llm.runtime_config import (
    ResolvedLlmSettings,
    llm_factory_generation,
    resolve_llm_settings,
)

log = logging.getLogger(__name__)


class LLMProvider(ABC):
    name: str

    @abstractmethod
    async def health(self) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def classify_text(self, text: str, schema_hint: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def chat(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: Optional[float] = None,
        response_json: bool = False,
    ) -> str:
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

    async def chat(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: Optional[float] = None,
        response_json: bool = False,
    ) -> str:
        raise RuntimeError("LLM provider is disabled")


class OllamaProvider(LLMProvider):
    name = "ollama"

    def __init__(self, cfg: ResolvedLlmSettings) -> None:
        self.base_url = cfg.base_url.rstrip("/")
        self.model = cfg.model
        self.timeout = cfg.timeout_s
        self.temperature = cfg.temperature

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
                }
        except Exception as exc:  # noqa: BLE001
            return {"provider": self.name, "healthy": False, "error": str(exc)}

    async def chat(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: Optional[float] = None,
        response_json: bool = False,
    ) -> str:
        # Prefer /api/chat; fall back to concatenated generate.
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature if temperature is not None else self.temperature},
        }
        if response_json:
            payload["format"] = "json"
        async with httpx.AsyncClient(timeout=float(self.timeout)) as client:
            try:
                resp = await client.post(f"{self.base_url}/api/chat", json=payload)
                resp.raise_for_status()
                msg = resp.json().get("message") or {}
                return str(msg.get("content") or "")
            except Exception:
                prompt = "\n".join(f"{m['role']}: {m['content']}" for m in messages)
                gen: dict[str, Any] = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                }
                if response_json:
                    gen["format"] = "json"
                resp = await client.post(f"{self.base_url}/api/generate", json=gen)
                resp.raise_for_status()
                return str(resp.json().get("response") or "")

    async def classify_text(self, text: str, schema_hint: dict[str, Any]) -> dict[str, Any]:
        raw = await self.chat(
            [
                {
                    "role": "system",
                    "content": (
                        "Extract job classification as JSON matching this schema keys: "
                        f"{list(schema_hint.keys())}. Use only evidence from the text. "
                        "If unknown, use null/unknown. Do not invent rates."
                    ),
                },
                {"role": "user", "content": f"TEXT:\n{text[:12000]}"},
            ],
            response_json=True,
        )
        return json.loads(raw or "{}")


class OpenAICompatibleProvider(LLMProvider):
    """vLLM, OpenAI, ChatGPT API, and OpenAI-compatible proxies."""

    name = "openai_compatible"

    def __init__(self, cfg: ResolvedLlmSettings) -> None:
        self.base_url = cfg.base_url.rstrip("/")
        self.api_key = cfg.api_key
        self.model = cfg.model
        self.timeout = cfg.timeout_s
        self.temperature = cfg.temperature
        self.max_tokens = cfg.max_tokens

    def _headers(self) -> dict[str, str]:
        h = {"Content-Type": "application/json"}
        if self.api_key:
            h["Authorization"] = f"Bearer {self.api_key}"
        return h

    async def health(self) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=5.0, headers=self._headers()) as client:
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

    async def chat(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: Optional[float] = None,
        response_json: bool = False,
    ) -> str:
        body: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature if temperature is not None else self.temperature,
        }
        if self.max_tokens:
            body["max_tokens"] = self.max_tokens
        if response_json:
            body["response_format"] = {"type": "json_object"}
        async with httpx.AsyncClient(timeout=float(self.timeout), headers=self._headers()) as client:
            resp = await client.post(f"{self.base_url}/chat/completions", json=body)
            resp.raise_for_status()
            return str(resp.json()["choices"][0]["message"]["content"] or "")

    async def classify_text(self, text: str, schema_hint: dict[str, Any]) -> dict[str, Any]:
        raw = await self.chat(
            [
                {
                    "role": "system",
                    "content": "Return valid JSON only. Never invent missing rates or jobs.",
                },
                {
                    "role": "user",
                    "content": f"Schema keys: {list(schema_hint.keys())}\nTEXT:\n{text[:12000]}",
                },
            ],
            response_json=True,
        )
        return json.loads(raw or "{}")


class GeminiProvider(LLMProvider):
    name = "gemini"

    def __init__(self, cfg: ResolvedLlmSettings) -> None:
        self.api_key = cfg.api_key
        self.model = cfg.model or "gemini-2.0-flash"
        self.timeout = cfg.timeout_s
        self.temperature = cfg.temperature
        base = (cfg.base_url or "https://generativelanguage.googleapis.com/v1beta").rstrip("/")
        self.base_url = base

    async def health(self) -> dict[str, Any]:
        if not self.api_key:
            return {"provider": self.name, "healthy": False, "error": "api_key missing"}
        try:
            url = f"{self.base_url}/models?key={self.api_key}"
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                return {"provider": self.name, "healthy": True, "model": self.model}
        except Exception as exc:  # noqa: BLE001
            return {"provider": self.name, "healthy": False, "error": str(exc)}

    async def chat(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: Optional[float] = None,
        response_json: bool = False,
    ) -> str:
        system_parts = [m["content"] for m in messages if m.get("role") == "system"]
        user_parts = [m["content"] for m in messages if m.get("role") != "system"]
        contents = [{"role": "user", "parts": [{"text": "\n\n".join(user_parts)}]}]
        body: dict[str, Any] = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature if temperature is not None else self.temperature,
            },
        }
        if system_parts:
            body["systemInstruction"] = {"parts": [{"text": "\n".join(system_parts)}]}
        if response_json:
            body["generationConfig"]["responseMimeType"] = "application/json"
        url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"
        async with httpx.AsyncClient(timeout=float(self.timeout)) as client:
            resp = await client.post(url, json=body)
            resp.raise_for_status()
            data = resp.json()
            parts = (
                data.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])
            )
            return str(parts[0].get("text") or "") if parts else ""

    async def classify_text(self, text: str, schema_hint: dict[str, Any]) -> dict[str, Any]:
        raw = await self.chat(
            [
                {
                    "role": "system",
                    "content": "Return valid JSON only. Never invent missing rates or jobs.",
                },
                {
                    "role": "user",
                    "content": f"Schema keys: {list(schema_hint.keys())}\nTEXT:\n{text[:12000]}",
                },
            ],
            response_json=True,
        )
        return json.loads(raw or "{}")


def provider_from_settings(cfg: ResolvedLlmSettings) -> LLMProvider:
    if cfg.provider == "ollama":
        return OllamaProvider(cfg)
    if cfg.provider in ("openai_compatible", "vllm"):
        return OpenAICompatibleProvider(cfg)
    if cfg.provider == "gemini":
        return GeminiProvider(cfg)
    return NullLLMProvider()


_cached: tuple[int, LLMProvider] | None = None


def get_llm_provider(db: Session | None = None) -> LLMProvider:
    """Factory: DB config when session/row available, else env. Cached by generation."""
    global _cached
    gen = llm_factory_generation()
    if db is None and _cached is not None and _cached[0] == gen:
        return _cached[1]
    cfg = resolve_llm_settings(db)
    provider = provider_from_settings(cfg)
    if db is None:
        _cached = (gen, provider)
    return provider


# Backward-compatible alias used by older VLLM naming
VLLMProvider = OpenAICompatibleProvider
