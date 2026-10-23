"""Focus starter intents stay unique and rematch-friendly."""

from app.research.rematch import query_signal_tokens
from app.storage.seed import _FOCUS_STARTERS


def test_focus_starters_unique_names():
    names = [n for n, _ in _FOCUS_STARTERS]
    assert len(names) == len(set(names))
    assert len(_FOCUS_STARTERS) >= 30


def test_focus_starters_have_signal_tokens():
    weak_only = []
    for name, text in _FOCUS_STARTERS:
        tokens = query_signal_tokens(text)
        if not tokens:
            weak_only.append(name)
    assert weak_only == [], f"intents without signal tokens: {weak_only}"


def test_focus_starters_cover_persona_families():
    blob = " ".join(t for _, t in _FOCUS_STARTERS).lower()
    for needle in (
        "java",
        "python",
        "kubernetes",
        "devops",
        "rag",
        "llm",
        "data",
        "security",
        "architect",
        "react",
    ):
        assert needle in blob, f"missing persona coverage for {needle}"
