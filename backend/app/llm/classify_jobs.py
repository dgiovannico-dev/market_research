"""Compatibility shim — prefer ``app.application.classification``."""

from app.application.classification.llm_classify import (
    LlmJobExtraction,
    run_llm_classification,
)

__all__ = ["LlmJobExtraction", "run_llm_classification"]
