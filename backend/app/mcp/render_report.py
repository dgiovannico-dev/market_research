"""MCP re-export — materialize lives in ``app.application.assistant``."""

from app.application.assistant.materialize import materialize_report

__all__ = ["materialize_report"]
