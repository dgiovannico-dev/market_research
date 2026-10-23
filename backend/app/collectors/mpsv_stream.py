"""Incremental JSON array object decoder for large MPSV dumps."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from typing import Any

import httpx

STREAM_CHUNK = 64 * 1024


async def empty_aiter() -> AsyncIterator[dict[str, Any]]:
    if False:  # pragma: no cover
        yield {}


async def iter_polozky_stream(
    resp: httpx.Response,
    *,
    max_bytes: int,
    keys: tuple[str, ...] = ("polozky", "@graph"),
) -> AsyncIterator[dict[str, Any]]:
    """Yield objects from the top-level ``polozky`` / ``@graph`` array while streaming."""
    decoder = ArrayObjectDecoder(keys=keys)
    bytes_read = 0
    try:
        async for chunk in resp.aiter_bytes(STREAM_CHUNK):
            bytes_read += len(chunk)
            if bytes_read > max_bytes:
                break
            for obj in decoder.feed(chunk):
                yield obj
            if decoder.done:
                break
        for obj in decoder.flush():
            yield obj
    finally:
        await resp.aclose()


def iter_polozky_payload(payload: Any) -> list[dict[str, Any]]:
    """Extract vacancy dicts from a parsed dump payload (tests / small fixtures)."""
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    if isinstance(payload, dict):
        for key in ("polozky", "@graph"):
            items = payload.get(key)
            if isinstance(items, list):
                return [x for x in items if isinstance(x, dict)]
    return []


class ArrayObjectDecoder:
    """Incremental extractor for objects inside a named JSON array."""

    def __init__(self, keys: tuple[str, ...]) -> None:
        self._buf = ""
        self._keys = keys
        self._in_array = False
        self._done = False
        self._obj_start: int | None = None
        self._depth = 0
        self._in_str = False
        self._esc = False

    @property
    def done(self) -> bool:
        return self._done

    def feed(self, chunk: bytes) -> list[dict[str, Any]]:
        self._buf += chunk.decode("utf-8", errors="replace")
        if not self._in_array:
            if not self._locate_array():
                if len(self._buf) > 8_000:
                    self._buf = self._buf[-4_000:]
                return []
        return self._consume_objects()

    def flush(self) -> list[dict[str, Any]]:
        if self._done or not self._in_array:
            return []
        return self._consume_objects()

    def _locate_array(self) -> bool:
        for key in self._keys:
            token = f'"{key}"'
            idx = self._buf.find(token)
            if idx < 0:
                continue
            colon = self._buf.find(":", idx + len(token))
            if colon < 0:
                return False
            bracket = self._buf.find("[", colon)
            if bracket < 0:
                return False
            self._buf = self._buf[bracket + 1 :]
            self._in_array = True
            return True
        return False

    def _consume_objects(self) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        buf = self._buf
        # Mid-object resume: buffer starts at '{', already counted in _depth.
        i = 1 if self._obj_start == 0 and self._depth > 0 and buf[:1] == "{" else 0
        while i < len(buf):
            c = buf[i]
            if self._obj_start is None:
                if c.isspace() or c == ",":
                    i += 1
                    continue
                if c == "]":
                    self._done = True
                    i += 1
                    break
                if c == "{":
                    self._obj_start = i
                    self._depth = 1
                    self._in_str = False
                    self._esc = False
                    i += 1
                    continue
                i += 1
                continue

            if self._in_str:
                if self._esc:
                    self._esc = False
                elif c == "\\":
                    self._esc = True
                elif c == '"':
                    self._in_str = False
            else:
                if c == '"':
                    self._in_str = True
                elif c == "{":
                    self._depth += 1
                elif c == "}":
                    self._depth -= 1
                    if self._depth == 0:
                        raw = buf[self._obj_start : i + 1]
                        self._obj_start = None
                        i += 1
                        try:
                            obj = json.loads(raw)
                        except json.JSONDecodeError:
                            continue
                        if isinstance(obj, dict):
                            out.append(obj)
                        continue
            i += 1

        if self._obj_start is not None:
            # Keep the full in-progress object and re-parse it next feed.
            self._buf = buf[self._obj_start :]
            self._obj_start = 0
            self._depth = 1
            self._in_str = False
            self._esc = False
        else:
            self._buf = buf[i:]
        return out
