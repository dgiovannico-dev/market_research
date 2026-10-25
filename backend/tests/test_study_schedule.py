"""Study calendar respects busy slots and hits weekly hours."""

from __future__ import annotations

from app.analytics.study_schedule import build_weekly_schedule, normalize_busy_slots


def test_normalize_busy_slots_drops_invalid():
    slots = normalize_busy_slots(
        [
            {"weekday": "mon", "start": "09:00", "end": "17:00", "label": "lavoro"},
            {"weekday": "zzz", "start": "09:00", "end": "10:00"},
            {"weekday": "tue", "start": "18:00", "end": "17:00"},
        ]
    )
    assert len(slots) == 1
    assert slots[0]["weekday"] == "mon"
    assert slots[0]["kind"] == "busy"


def test_schedule_avoids_busy_and_spreads():
    result = build_weekly_schedule(
        hours_per_week=6,
        modality="employed_part_time",
        busy_slots=[
            {"weekday": "mon", "start": "09:00", "end": "18:00", "label": "work"},
            {"weekday": "tue", "start": "09:00", "end": "18:00", "label": "work"},
            {"weekday": "wed", "start": "09:00", "end": "18:00", "label": "work"},
            {"weekday": "thu", "start": "09:00", "end": "18:00", "label": "work"},
            {"weekday": "fri", "start": "09:00", "end": "18:00", "label": "work"},
        ],
    )
    study = result["study_slots"]
    assert study
    assert result["scheduled_minutes"] >= 5 * 60
    for s in study:
        assert s["kind"] == "study"
        # evenings / weekend for employed modality
        assert s["weekday"] in {"mon", "tue", "wed", "thu", "fri", "sat", "sun"}
        start_h = int(s["start"].split(":")[0])
        if s["weekday"] in {"mon", "tue", "wed", "thu", "fri"}:
            assert start_h >= 18


def test_full_busy_evening_reduces_capacity():
    result = build_weekly_schedule(
        hours_per_week=6,
        modality="employed_part_time",
        busy_slots=[
            {"weekday": d, "start": "18:00", "end": "23:00", "label": "busy"}
            for d in ("mon", "tue", "wed", "thu", "fri")
        ]
        + [{"weekday": "sat", "start": "09:00", "end": "20:00", "label": "busy"}],
    )
    # Only Sunday morning window remains roughly
    assert result["scheduled_minutes"] < 6 * 60
    assert any(str(n).startswith("schedule_") for n in result["notes"])


def test_same_day_fragmented_busy_places_study_in_gaps():
    """Multiple busy blocks on one day leave study in the free gaps."""
    # Monday preferred window for employed_part_time: 19:00–22:00.
    # Busy 19–20 and 21–22 → only 20:00–21:00 is free.
    result = build_weekly_schedule(
        hours_per_week=1,
        modality="employed_part_time",
        busy_slots=[
            {"weekday": "mon", "start": "19:00", "end": "20:00", "label": "cena"},
            {"weekday": "mon", "start": "21:00", "end": "22:00", "label": "palestra"},
            # Block every other preferred evening so Mon gap is the only option.
            *[
                {"weekday": d, "start": "18:00", "end": "23:00", "label": "busy"}
                for d in ("tue", "wed", "thu", "fri")
            ],
            {"weekday": "sat", "start": "09:00", "end": "20:00", "label": "busy"},
            {"weekday": "sun", "start": "09:00", "end": "20:00", "label": "busy"},
        ],
    )
    study = result["study_slots"]
    assert len(study) == 1
    assert study[0]["weekday"] == "mon"
    assert study[0]["start"] == "20:00"
    assert study[0]["end"] == "21:00"
    assert study[0]["minutes"] == 60
    busy_mon = [b for b in result["busy_slots"] if b["weekday"] == "mon"]
    assert len(busy_mon) == 2


def test_same_day_overlapping_busy_still_subtracts():
    result = build_weekly_schedule(
        hours_per_week=1,
        modality="employed_part_time",
        busy_slots=[
            {"weekday": "mon", "start": "19:00", "end": "21:00", "label": "a"},
            {"weekday": "mon", "start": "20:00", "end": "22:00", "label": "b"},
            *[
                {"weekday": d, "start": "18:00", "end": "23:00", "label": "busy"}
                for d in ("tue", "wed", "thu", "fri")
            ],
            {"weekday": "sat", "start": "09:00", "end": "20:00", "label": "busy"},
            {"weekday": "sun", "start": "09:00", "end": "20:00", "label": "busy"},
        ],
    )
    # Entire Mon preferred window covered by overlapping busy → no study Mon.
    assert all(s["weekday"] != "mon" for s in result["study_slots"])
    assert result["scheduled_minutes"] == 0 or "schedule_" in " ".join(
        str(n) for n in result["notes"]
    )


def test_freelance_lunch_gap_between_busy_blocks():
    """Freelance day windows: busy morning + afternoon with lunch free."""
    result = build_weekly_schedule(
        hours_per_week=1,
        modality="freelance_full_time",
        busy_slots=[
            {"weekday": "mon", "start": "09:00", "end": "10:00", "label": "call"},
            {"weekday": "mon", "start": "11:00", "end": "12:00", "label": "client"},
            # Prefer Mon morning gap only: block other days' preferred windows.
            *[
                {"weekday": d, "start": "08:00", "end": "18:00", "label": "busy"}
                for d in ("tue", "wed", "thu", "fri", "sat", "sun")
            ],
        ],
    )
    mon = [s for s in result["study_slots"] if s["weekday"] == "mon"]
    assert mon
    assert mon[0]["start"] == "10:00"
    assert mon[0]["end"] == "11:00"


def test_wlb_spreads_across_seven_days_when_free():
    """Ideal plan spreads load across the week instead of dumping on few days."""
    result = build_weekly_schedule(
        hours_per_week=7,
        modality="employed_part_time",
        busy_slots=[],
    )
    study = result["study_slots"]
    days = {s["weekday"] for s in study}
    assert result["days_used"] >= 5
    assert len(days) >= 5
    # No single day should absorb more than ~2h when 7h are free to spread.
    by_day: dict[str, int] = {}
    for s in study:
        by_day[s["weekday"]] = by_day.get(s["weekday"], 0) + int(s["minutes"])
    assert max(by_day.values()) <= 120
    assert result["scheduled_minutes"] >= 6 * 60


def test_wlb_does_not_overload_weekend_when_weekdays_free():
    result = build_weekly_schedule(
        hours_per_week=6,
        modality="freelance_full_time",
        busy_slots=[],
    )
    by_day: dict[str, int] = {}
    for s in result["study_slots"]:
        by_day[s["weekday"]] = by_day.get(s["weekday"], 0) + int(s["minutes"])
    weekend = by_day.get("sat", 0) + by_day.get("sun", 0)
    weekday = sum(by_day.get(d, 0) for d in ("mon", "tue", "wed", "thu", "fri"))
    assert weekday >= weekend
    assert result["days_used"] >= 5
