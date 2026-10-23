"""Wave 4 deferred: LLM classify use case uses LlmGateway from the container."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.application.classification.llm_classify import run_llm_classification


@pytest.mark.asyncio
async def test_skips_when_provider_none():
    db = MagicMock()
    llm = MagicMock()
    llm.health = AsyncMock(return_value={"healthy": True, "provider": "none"})
    fake = MagicMock()
    fake.settings.llm_provider = "none"
    fake.llm.return_value = llm

    with patch("app.application.classification.llm_classify.get_container", return_value=fake):
        out = await run_llm_classification(db, limit=5, llm=llm)

    assert out["status"] == "skipped"
    db.scalars.assert_not_called()


@pytest.mark.asyncio
async def test_skips_when_llm_unhealthy():
    db = MagicMock()
    llm = MagicMock()
    llm.name = "ollama"
    llm.health = AsyncMock(return_value={"healthy": False, "provider": "ollama"})
    fake = MagicMock()
    fake.settings.llm_provider = "ollama"
    fake.llm.return_value = llm

    with patch("app.application.classification.llm_classify.get_container", return_value=fake):
        out = await run_llm_classification(db, limit=5, llm=llm)

    assert out["status"] == "skipped"
    assert "offline" in out["reason"].lower() or "provider" in out["reason"].lower()
