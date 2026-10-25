"""Build a weekly study calendar that avoids busy slots with work-life balance."""

from __future__ import annotations

from typing import Any, Literal, Optional

Modality = Literal["employed_part_time", "freelance_full_time", "intensive"]
Weekday = Literal["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

_WEEKDAYS: tuple[Weekday, ...] = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")


def _day_windows(*pairs: tuple[int, int]) -> list[tuple[int, int]]:
    return list(pairs)


# Preferred study windows by modality (minutes from midnight).
# Every modality has windows on all 7 days so load can spread for WLB.
_PREF_WINDOWS: dict[str, dict[str, list[tuple[int, int]]]] = {
    "employed_part_time": {
        "mon": _day_windows((19 * 60, 22 * 60)),
        "tue": _day_windows((19 * 60, 22 * 60)),
        "wed": _day_windows((19 * 60, 22 * 60)),
        "thu": _day_windows((19 * 60, 22 * 60)),
        "fri": _day_windows((18 * 60, 21 * 60)),
        "sat": _day_windows((9 * 60, 12 * 60), (16 * 60, 18 * 60)),
        "sun": _day_windows((10 * 60, 13 * 60)),
    },
    "freelance_full_time": {
        "mon": _day_windows((9 * 60, 12 * 60), (14 * 60, 17 * 60)),
        "tue": _day_windows((9 * 60, 12 * 60), (14 * 60, 17 * 60)),
        "wed": _day_windows((9 * 60, 12 * 60), (14 * 60, 17 * 60)),
        "thu": _day_windows((9 * 60, 12 * 60), (14 * 60, 17 * 60)),
        "fri": _day_windows((9 * 60, 12 * 60), (14 * 60, 16 * 60)),
        "sat": _day_windows((10 * 60, 12 * 60)),
        "sun": _day_windows((10 * 60, 12 * 60)),
    },
    "intensive": {
        "mon": _day_windows((9 * 60, 13 * 60), (15 * 60, 18 * 60)),
        "tue": _day_windows((9 * 60, 13 * 60), (15 * 60, 18 * 60)),
        "wed": _day_windows((9 * 60, 13 * 60), (15 * 60, 18 * 60)),
        "thu": _day_windows((9 * 60, 13 * 60), (15 * 60, 18 * 60)),
        "fri": _day_windows((9 * 60, 13 * 60), (15 * 60, 18 * 60)),
        "sat": _day_windows((9 * 60, 12 * 60)),
        "sun": _day_windows((10 * 60, 12 * 60)),
    },
}


def _parse_hhmm(value: Any, default_min: int) -> int:
    if value is None:
        return default_min
    if isinstance(value, (int, float)):
        return max(0, min(24 * 60, int(value)))
    text = str(value).strip()
    if not text:
        return default_min
    parts = text.split(":")
    try:
        h = int(parts[0])
        m = int(parts[1]) if len(parts) > 1 else 0
    except (TypeError, ValueError):
        return default_min
    return max(0, min(24 * 60, h * 60 + m))


def _fmt(minutes: int) -> str:
    minutes = max(0, min(24 * 60, minutes))
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def normalize_busy_slots(raw: Optional[list[dict[str, Any]]]) -> list[dict[str, Any]]:
    """Validate and normalize busy slots from the client."""
    out: list[dict[str, Any]] = []
    for item in raw or []:
        if not isinstance(item, dict):
            continue
        wd = str(item.get("weekday") or "").lower().strip()
        if wd not in _WEEKDAYS:
            continue
        start = _parse_hhmm(item.get("start"), 9 * 60)
        end = _parse_hhmm(item.get("end"), 17 * 60)
        if end <= start:
            continue
        label = str(item.get("label") or "busy").strip() or "busy"
        out.append(
            {
                "weekday": wd,
                "start": _fmt(start),
                "end": _fmt(end),
                "label": label[:40],
                "kind": "busy",
            }
        )
    out.sort(key=lambda s: (_WEEKDAYS.index(s["weekday"]), s["start"]))
    return out


def _busy_by_day(busy: list[dict[str, Any]]) -> dict[Weekday, list[tuple[int, int]]]:
    by: dict[Weekday, list[tuple[int, int]]] = {d: [] for d in _WEEKDAYS}
    for slot in busy:
        wd = slot["weekday"]
        by[wd].append((_parse_hhmm(slot["start"], 0), _parse_hhmm(slot["end"], 0)))
    for wd in _WEEKDAYS:
        by[wd].sort()
    return by


def _subtract(
    window: tuple[int, int],
    blocked: list[tuple[int, int]],
) -> list[tuple[int, int]]:
    start, end = window
    free = [(start, end)]
    for b0, b1 in blocked:
        nxt: list[tuple[int, int]] = []
        for f0, f1 in free:
            if b1 <= f0 or b0 >= f1:
                nxt.append((f0, f1))
                continue
            if b0 > f0:
                nxt.append((f0, min(b0, f1)))
            if b1 < f1:
                nxt.append((max(b1, f0), f1))
        free = [(a, b) for a, b in nxt if b - a >= 30]
    return free


def _candidate_free(
    modality: Modality,
    busy_by: dict[Weekday, list[tuple[int, int]]],
) -> list[tuple[Weekday, int, int]]:
    prefs = _PREF_WINDOWS.get(modality) or _PREF_WINDOWS["employed_part_time"]
    free: list[tuple[Weekday, int, int]] = []
    for wd in _WEEKDAYS:
        for win in prefs.get(wd) or []:
            for a, b in _subtract(win, busy_by.get(wd) or []):
                free.append((wd, a, b))
    return free


def _pick_take(avail: int, remaining: int, day_room: int, block_min: int, block_max: int) -> int:
    """Choose a block length that respects day cap and prefers 45/60/90."""
    hard = min(block_max, avail, remaining, day_room)
    if hard < block_min:
        return 0
    if hard >= 90 and remaining >= 90 and day_room >= 90:
        return 90
    if hard >= 60 and remaining >= 60 and day_room >= 60:
        return 60
    if hard >= 45 and remaining >= 45 and day_room >= 45:
        return 45
    return hard


def _carve_blocks(
    free: list[tuple[Weekday, int, int]],
    target_minutes: int,
    *,
    block_min: int = 45,
    block_max: int = 90,
) -> list[dict[str, Any]]:
    """
    Work-life balance fill:
    - spread across as many days as possible (prefer days with least load)
    - soft daily cap ≈ weekly_target / available_days (capped at block_max)
    - never pile the whole week onto weekend alone when weekdays are free
    """
    remaining = max(block_min, int(round(target_minutes)))
    by_day: dict[Weekday, list[tuple[int, int]]] = {d: [] for d in _WEEKDAYS}
    for wd, a, b in free:
        by_day[wd].append((a, b))
    for wd in _WEEKDAYS:
        by_day[wd].sort(key=lambda x: (x[0], x[1] - x[0]))

    available = [d for d in _WEEKDAYS if by_day[d]]
    if not available:
        return []

    soft_cap = max(block_min, min(block_max, (remaining + len(available) - 1) // len(available)))
    # Weekend soft cap: same as weekdays (spread), never higher than soft_cap.
    day_cap: dict[Weekday, int] = {d: soft_cap for d in _WEEKDAYS}
    day_used: dict[Weekday, int] = {d: 0 for d in _WEEKDAYS}
    slots: list[dict[str, Any]] = []

    def day_room(wd: Weekday) -> int:
        return max(0, day_cap[wd] - day_used[wd])

    def place_one(wd: Weekday) -> bool:
        nonlocal remaining
        windows = by_day[wd]
        room = day_room(wd)
        if remaining < block_min or room < block_min or not windows:
            return False
        # Prefer earliest free window that fits.
        for i, (a, b) in enumerate(windows):
            avail = b - a
            take = _pick_take(avail, remaining, room, block_min, block_max)
            if take < block_min:
                if avail < block_min:
                    windows.pop(i)
                    return place_one(wd)
                continue
            end = a + take
            slots.append(
                {
                    "weekday": wd,
                    "start": _fmt(a),
                    "end": _fmt(end),
                    "label": "study",
                    "kind": "study",
                    "minutes": take,
                }
            )
            remaining -= take
            day_used[wd] += take
            if end < b and (b - end) >= block_min:
                windows[i] = (end, b)
            else:
                windows.pop(i)
            return True
        return False

    # Pass 1: one block per day (maximize coverage / WLB).
    guard = 0
    while remaining >= block_min and guard < 128:
        guard += 1
        # Prefer days with no study yet, then least load, then weekday before weekend.
        candidates = [
            d
            for d in available
            if by_day[d] and day_room(d) >= block_min
        ]
        if not candidates:
            break
        candidates.sort(
            key=lambda d: (
                0 if day_used[d] == 0 else 1,
                day_used[d],
                1 if d in ("sat", "sun") else 0,
                _WEEKDAYS.index(d),
            )
        )
        progressed = False
        for wd in candidates:
            if place_one(wd):
                progressed = True
                break
        if not progressed:
            break

    # Pass 2: if under target, raise soft caps evenly and fill leftover.
    if remaining >= block_min:
        for d in available:
            day_cap[d] = min(block_max * 2, day_cap[d] + block_max)
        guard = 0
        while remaining >= block_min and guard < 64:
            guard += 1
            candidates = [
                d for d in available if by_day[d] and day_room(d) >= block_min
            ]
            if not candidates:
                break
            candidates.sort(
                key=lambda d: (
                    day_used[d],
                    1 if d in ("sat", "sun") else 0,
                    _WEEKDAYS.index(d),
                )
            )
            if not place_one(candidates[0]):
                # Drop exhausted day from consideration.
                if not by_day[candidates[0]]:
                    available = [d for d in available if by_day[d]]
                    if not available:
                        break
                    continue
                break

    slots.sort(key=lambda s: (_WEEKDAYS.index(s["weekday"]), s["start"]))
    return slots


def build_weekly_schedule(
    *,
    hours_per_week: float,
    modality: Modality = "employed_part_time",
    busy_slots: Optional[list[dict[str, Any]]] = None,
) -> dict[str, Any]:
    """Return study slots (+ normalized busy) totaling ~hours_per_week."""
    busy = normalize_busy_slots(busy_slots)
    busy_by = _busy_by_day(busy)
    free = _candidate_free(modality, busy_by)
    target = max(60, int(round(float(hours_per_week) * 60)))
    study = _carve_blocks(free, target)
    scheduled = sum(int(s.get("minutes") or 0) for s in study)
    days_used = len({s["weekday"] for s in study})
    notes: list[str] = []
    if scheduled + 15 < target:
        notes.append(
            f"schedule_partial:{scheduled}:{int(round(float(hours_per_week) * 60))}"
        )
    if not study:
        notes.append("schedule_no_window")
    elif days_used >= 5:
        notes.append(f"schedule_wlb_days:{days_used}")
    return {
        "busy_slots": busy,
        "study_slots": study,
        "weekly_template": study,  # planner / ICS consume this
        "scheduled_minutes": scheduled,
        "target_minutes": target,
        "days_used": days_used,
        "notes": notes,
    }
