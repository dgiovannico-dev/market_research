"""Load / save LLM runtime config (DB overrides env)."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.secrets.crypto import CredentialsCryptoError, decrypt_bytes, encrypt_bytes
from app.storage.models_llm import LlmAdminAudit, LlmRuntimeConfig

log = logging.getLogger(__name__)

RUNTIME_ROW_ID = 1
_VALID_PROVIDERS = frozenset({"none", "ollama", "openai_compatible", "gemini", "vllm"})


@dataclass(frozen=True)
class ResolvedLlmSettings:
    provider: str
    base_url: str
    model: str
    temperature: float
    timeout_s: int
    max_tokens: Optional[int]
    api_key: str
    enable_classify: bool
    enable_weekly_report: bool
    enable_study_advisor: bool
    enable_brief_narrative: bool
    source: str  # "db" | "env"


def _env_resolved(settings: Settings) -> ResolvedLlmSettings:
    provider = (settings.llm_provider or "none").strip().lower()
    if provider == "vllm":
        # Treat legacy vllm env as openai_compatible endpoint shape.
        return ResolvedLlmSettings(
            provider="openai_compatible",
            base_url=(settings.vllm_base_url or "").rstrip("/"),
            model=settings.vllm_model or "",
            temperature=0.1,
            timeout_s=120,
            max_tokens=None,
            api_key=settings.vllm_api_key or "",
            enable_classify=True,
            enable_weekly_report=True,
            enable_study_advisor=True,
            enable_brief_narrative=False,
            source="env",
        )
    if provider == "ollama":
        return ResolvedLlmSettings(
            provider="ollama",
            base_url=(settings.ollama_base_url or "").rstrip("/"),
            model=settings.ollama_model or "llama3.2",
            temperature=0.1,
            timeout_s=120,
            max_tokens=None,
            api_key="",
            enable_classify=True,
            enable_weekly_report=True,
            enable_study_advisor=True,
            enable_brief_narrative=False,
            source="env",
        )
    return ResolvedLlmSettings(
        provider="none",
        base_url="",
        model="",
        temperature=0.1,
        timeout_s=120,
        max_tokens=None,
        api_key="",
        enable_classify=False,
        enable_weekly_report=False,
        enable_study_advisor=False,
        enable_brief_narrative=False,
        source="env",
    )


def _decrypt_key(blob: Optional[bytes]) -> str:
    if not blob:
        return ""
    try:
        return decrypt_bytes(bytes(blob)).decode("utf-8")
    except (CredentialsCryptoError, UnicodeDecodeError) as exc:
        log.warning("llm api_key decrypt failed (%s)", type(exc).__name__)
        return ""


def resolve_llm_settings(db: Session | None = None) -> ResolvedLlmSettings:
    settings = get_settings()
    if db is None:
        return _env_resolved(settings)
    row = db.get(LlmRuntimeConfig, RUNTIME_ROW_ID)
    if row is None:
        return _env_resolved(settings)
    provider = (row.provider or "none").strip().lower()
    if provider == "vllm":
        provider = "openai_compatible"
    if provider not in _VALID_PROVIDERS:
        provider = "none"
    return ResolvedLlmSettings(
        provider=provider,
        base_url=(row.base_url or "").rstrip("/"),
        model=row.model or "",
        temperature=float(row.temperature if row.temperature is not None else 0.1),
        timeout_s=int(row.timeout_s or 120),
        max_tokens=row.max_tokens,
        api_key=_decrypt_key(row.api_key_ciphertext),
        enable_classify=bool(row.enable_classify),
        enable_weekly_report=bool(row.enable_weekly_report),
        enable_study_advisor=bool(row.enable_study_advisor),
        enable_brief_narrative=bool(row.enable_brief_narrative),
        source="db",
    )


def settings_public_dict(resolved: ResolvedLlmSettings, row: LlmRuntimeConfig | None) -> dict[str, Any]:
    return {
        "provider": resolved.provider,
        "base_url": resolved.base_url,
        "model": resolved.model,
        "temperature": resolved.temperature,
        "timeout_s": resolved.timeout_s,
        "max_tokens": resolved.max_tokens,
        "api_key_set": bool(resolved.api_key) or bool(row and row.api_key_ciphertext),
        "enable_classify": resolved.enable_classify,
        "enable_weekly_report": resolved.enable_weekly_report,
        "enable_study_advisor": resolved.enable_study_advisor,
        "enable_brief_narrative": resolved.enable_brief_narrative,
        "source": resolved.source,
        "updated_by": row.updated_by if row else None,
        "updated_at": row.updated_at.isoformat() if row and row.updated_at else None,
    }


def upsert_runtime_config(
    db: Session,
    *,
    payload: dict[str, Any],
    actor: Optional[str] = None,
) -> LlmRuntimeConfig:
    provider = str(payload.get("provider") or "none").strip().lower()
    if provider == "vllm":
        provider = "openai_compatible"
    if provider not in _VALID_PROVIDERS:
        raise ValueError(f"invalid provider: {provider}")

    row = db.get(LlmRuntimeConfig, RUNTIME_ROW_ID)
    if row is None:
        row = LlmRuntimeConfig(id=RUNTIME_ROW_ID)
        db.add(row)

    row.provider = provider
    if "base_url" in payload:
        row.base_url = (payload.get("base_url") or "").strip() or None
    if "model" in payload:
        row.model = (payload.get("model") or "").strip() or None
    if "temperature" in payload and payload["temperature"] is not None:
        row.temperature = float(payload["temperature"])
    if "timeout_s" in payload and payload["timeout_s"] is not None:
        row.timeout_s = int(payload["timeout_s"])
    if "max_tokens" in payload:
        row.max_tokens = (
            int(payload["max_tokens"]) if payload["max_tokens"] is not None else None
        )
    for flag in (
        "enable_classify",
        "enable_weekly_report",
        "enable_study_advisor",
        "enable_brief_narrative",
    ):
        if flag in payload and payload[flag] is not None:
            setattr(row, flag, bool(payload[flag]))

    api_key = payload.get("api_key")
    if isinstance(api_key, str) and api_key.strip():
        row.api_key_ciphertext = encrypt_bytes(api_key.strip().encode("utf-8"))
    elif payload.get("clear_api_key"):
        row.api_key_ciphertext = None

    row.updated_by = actor
    db.add(
        LlmAdminAudit(
            action="runtime_config_upsert",
            actor=actor,
            details={"provider": provider, "model": row.model},
        )
    )
    db.commit()
    db.refresh(row)
    invalidate_llm_factory()
    return row


_factory_generation = 0


def invalidate_llm_factory() -> None:
    global _factory_generation
    _factory_generation += 1


def llm_factory_generation() -> int:
    return _factory_generation
