"""Parse ICS feeds into weekly busy slots for Study Advisor (Google / Aruba / Outlook)."""

from __future__ import annotations

import ipaddress
import re
import socket
from datetime import date, datetime, timedelta, timezone
from typing import Any, Optional
from urllib.parse import urlparse
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import httpx

_WEEKDAYS = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")
_MAX_ICS_BYTES = 2_000_000
_FETCH_TIMEOUT = 20.0


def _monday_of(d: date) -> date:
    return d - timedelta(days=d.weekday())


def unfold_ics(text: str) -> str:
    return re.sub(r"\r?\n[ \t]", "", text.replace("\r\n", "\n"))


def resolve_tz(name: Optional[str] = None):
    raw = (name or "").strip() or "Europe/Rome"
    try:
        return ZoneInfo(raw)
    except ZoneInfoNotFoundError:
        return ZoneInfo("Europe/Rome")


def _parse_ics_dt(
    raw: str, params: str = "", *, tz: Any = None
) -> Optional[datetime]:
    value = (raw or "").strip()
    if not value:
        return None
    local = tz or resolve_tz()
    # VALUE=DATE → floating local midnight (ICS all-day is exclusive on DTEND)
    if "VALUE=DATE" in params.upper() or (len(value) == 8 and value.isdigit()):
        try:
            d = datetime.strptime(value[:8], "%Y%m%d").date()
        except ValueError:
            return None
        return datetime(d.year, d.month, d.day, 0, 0, tzinfo=local)
    value = value.replace("Z", "+0000")
    for fmt in ("%Y%m%dT%H%M%S%z", "%Y%m%dT%H%M%S", "%Y%m%dT%H%M%z", "%Y%m%dT%H%M"):
        try:
            dt = datetime.strptime(value, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=local)
            return dt
        except ValueError:
            continue
    return None


def _extract_events(ics_text: str, *, tz: Any = None) -> list[dict[str, Any]]:
    body = unfold_ics(ics_text)
    local = tz or resolve_tz()
    events: list[dict[str, Any]] = []
    blocks = re.split(r"\nBEGIN:VEVENT", body, flags=re.IGNORECASE)
    for block in blocks[1:]:
        end = re.search(r"\nEND:VEVENT", block, flags=re.IGNORECASE)
        chunk = block[: end.start()] if end else block
        summary = ""
        dt_start: Optional[datetime] = None
        dt_end: Optional[datetime] = None
        for line in chunk.split("\n"):
            if ":" not in line:
                continue
            left, right = line.split(":", 1)
            key = left.split(";", 1)[0].upper()
            params = left[len(key) :]
            if key == "SUMMARY":
                summary = right.strip()
            elif key == "DTSTART":
                dt_start = _parse_ics_dt(right, params, tz=local)
            elif key == "DTEND":
                dt_end = _parse_ics_dt(right, params, tz=local)
        if not dt_start:
            continue
        if not dt_end:
            dt_end = dt_start + timedelta(hours=1)
        if dt_end <= dt_start:
            continue
        events.append({"summary": summary or "calendar", "start": dt_start, "end": dt_end})
    return events


def events_to_busy_slots(
    events: list[dict[str, Any]],
    *,
    week_start: Optional[date] = None,
    tz_name: Optional[str] = None,
) -> list[dict[str, Any]]:
    """Collapse events overlapping the local week into weekday HH:MM busy slots."""
    start_day = _monday_of(week_start or date.today())
    end_day = start_day + timedelta(days=7)
    local_tz = resolve_tz(tz_name)
    week_start_dt = datetime(
        start_day.year, start_day.month, start_day.day, tzinfo=local_tz
    )
    week_end_dt = datetime(
        end_day.year, end_day.month, end_day.day, tzinfo=local_tz
    )

    slots: list[dict[str, Any]] = []
    for ev in events:
        s = (
            ev["start"].astimezone(local_tz)
            if ev["start"].tzinfo
            else ev["start"].replace(tzinfo=local_tz)
        )
        e = (
            ev["end"].astimezone(local_tz)
            if ev["end"].tzinfo
            else ev["end"].replace(tzinfo=local_tz)
        )
        if e <= week_start_dt or s >= week_end_dt:
            continue
        # Clip to week
        if s < week_start_dt:
            s = week_start_dt
        if e > week_end_dt:
            e = week_end_dt
        cursor = s
        while cursor < e:
            next_midnight = datetime(
                cursor.year, cursor.month, cursor.day, tzinfo=local_tz
            ) + timedelta(days=1)
            piece_end = min(e, next_midnight)
            wd = _WEEKDAYS[cursor.weekday()]
            label = str(ev.get("summary") or "calendar")[:80]
            end_hhmm = (
                "23:59"
                if piece_end.hour == 0 and piece_end.minute == 0
                else f"{piece_end.hour:02d}:{piece_end.minute:02d}"
            )
            start_hhmm = f"{cursor.hour:02d}:{cursor.minute:02d}"
            if start_hhmm < end_hhmm or end_hhmm == "23:59":
                slots.append(
                    {
                        "weekday": wd,
                        "start": start_hhmm,
                        "end": end_hhmm,
                        "label": label,
                        "origin": "calendar",
                    }
                )
            cursor = piece_end
    return slots


def assert_safe_ics_url(url: str) -> str:
    """Normalize webcal→https and reject obvious SSRF targets."""
    raw = (url or "").strip()
    if not raw:
        raise ValueError("ics_url_required")
    if raw.lower().startswith("webcal://"):
        raw = "https://" + raw[9:]
    parsed = urlparse(raw)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("ics_url_scheme")
    host = parsed.hostname
    if not host:
        raise ValueError("ics_url_host")
    if host.lower() in ("localhost", "metadata.google.internal"):
        raise ValueError("ics_url_blocked_host")
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror as exc:
        raise ValueError("ics_url_dns") from exc
    for info in infos:
        ip_str = info[4][0]
        try:
            ip = ipaddress.ip_address(ip_str)
        except ValueError:
            continue
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_reserved
            or ip.is_multicast
        ):
            raise ValueError("ics_url_private_ip")
    return raw


async def fetch_ics_text(url: str) -> str:
    safe = assert_safe_ics_url(url)
    async with httpx.AsyncClient(
        timeout=_FETCH_TIMEOUT,
        follow_redirects=True,
        max_redirects=3,
    ) as client:
        res = await client.get(safe, headers={"User-Agent": "FMI-StudyAdvisor/1.0"})
        res.raise_for_status()
        content = res.content
        if len(content) > _MAX_ICS_BYTES:
            raise ValueError("ics_too_large")
        return content.decode("utf-8", errors="replace")


async def busy_slots_from_ics_url(
    url: str,
    *,
    week_start: Optional[date] = None,
    tz_name: Optional[str] = None,
) -> dict[str, Any]:
    text = await fetch_ics_text(url)
    tz = resolve_tz(tz_name)
    events = _extract_events(text, tz=tz)
    slots = events_to_busy_slots(events, week_start=week_start, tz_name=tz.key)
    start = _monday_of(week_start or date.today())
    return {
        "week_start": start.isoformat(),
        "timezone": tz.key,
        "event_count": len(events),
        "busy_slots": slots,
        "imported": len(slots),
    }
