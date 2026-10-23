"""Research intents application slice (ADR-007 / Wave 6)."""

from app.application.research_intents.accept_watch import accept_watch_suggestion
from app.application.research_intents.crud import (
    create_research_intent,
    get_active_intent,
    list_research_intents,
    patch_research_intent,
    soft_delete_research_intent,
)
from app.application.research_intents.rematch import rematch_intents
from app.application.research_intents.serialize import serialize_intent
from app.application.research_intents.sync import sync_research_intent

__all__ = [
    "accept_watch_suggestion",
    "create_research_intent",
    "get_active_intent",
    "list_research_intents",
    "patch_research_intent",
    "rematch_intents",
    "serialize_intent",
    "soft_delete_research_intent",
    "sync_research_intent",
]
