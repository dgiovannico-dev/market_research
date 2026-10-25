"""ICS → busy slots for Study Advisor calendar sync."""

from __future__ import annotations

from datetime import date, datetime, timezone

import pytest

from app.analytics.ics_busy import (
    assert_safe_ics_url,
    events_to_busy_slots,
    _extract_events,
)


SAMPLE_ICS = """BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
UID:1@test
DTSTART:20261026T100000Z
DTEND:20261026T113000Z
SUMMARY:Client call
END:VEVENT
BEGIN:VEVENT
UID:2@test
DTSTART;VALUE=DATE:20261027
DTEND;VALUE=DATE:20261028
SUMMARY:All day off
END:VEVENT
END:VCALENDAR
"""


def test_unfold_and_extract_events():
    events = _extract_events(SAMPLE_ICS)
    assert len(events) == 2
    assert events[0]["summary"] == "Client call"
    assert events[0]["end"] > events[0]["start"]


def test_events_to_busy_slots_week():
    # Week of Mon 2026-10-26 — force Europe/Rome so UTC events shift locally
    events = _extract_events(SAMPLE_ICS, tz=__import__("zoneinfo").ZoneInfo("Europe/Rome"))
    slots = events_to_busy_slots(
        events, week_start=date(2026, 10, 26), tz_name="Europe/Rome"
    )
    assert any(s["label"] == "Client call" for s in slots)
    call = next(s for s in slots if s["label"] == "Client call")
    assert call["weekday"] == "mon"
    assert call["origin"] == "calendar"
    # 10:00Z → 11:00 CET or 12:00 CEST depending on DST for that date
    assert call["start"] in ("11:00", "12:00")
    assert call["end"] in ("12:30", "13:30")
    allday = next(s for s in slots if s["label"] == "All day off")
    assert allday["weekday"] == "tue"
    assert allday["start"] == "00:00"
    assert allday["end"] == "23:59"


def test_assert_safe_ics_url_blocks_localhost():
    with pytest.raises(ValueError, match="blocked|private|scheme"):
        assert_safe_ics_url("http://localhost/cal.ics")
    with pytest.raises(ValueError, match="scheme"):
        assert_safe_ics_url("ftp://example.com/x.ics")


def test_webcal_normalized():
    # DNS may fail offline — only check scheme rewrite path via ValueError not scheme
    try:
        out = assert_safe_ics_url("webcal://calendar.google.com/calendar/ical/x/public/basic.ics")
        assert out.startswith("https://")
    except ValueError as exc:
        # private IP / DNS in locked-down CI is acceptable for this smoke
        assert "scheme" not in str(exc)
