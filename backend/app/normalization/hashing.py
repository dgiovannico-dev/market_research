import hashlib
import re


_WS = re.compile(r"\s+")


def normalize_text(value: str | None) -> str:
    if not value:
        return ""
    return _WS.sub(" ", value).strip().lower()


def content_hash(value: str | None) -> str | None:
    text = normalize_text(value)
    if not text:
        return None
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
