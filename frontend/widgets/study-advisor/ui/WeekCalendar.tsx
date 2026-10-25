"use client";

import { useTranslations } from "next-intl";
import {
  STUDY_WEEKDAYS,
  type BusySlot,
  type StudyCalendarSlot,
} from "@/entities/study-advisor";

type Props = {
  studySlots: StudyCalendarSlot[];
  busySlots: BusySlot[];
};

type CalEvent = {
  kind: "study" | "busy";
  startMin: number;
  endMin: number;
  label: string;
};

const HOUR_PX = 44;
const DEFAULT_START = 7 * 60;
const DEFAULT_END = 22 * 60;

function parseMin(hhmm: string): number {
  const [h, m] = String(hhmm || "0:0").split(":").map(Number);
  return (h || 0) * 60 + (m || 0);
}

function eventsForDay(
  day: string,
  studySlots: StudyCalendarSlot[],
  busySlots: BusySlot[],
): CalEvent[] {
  const out: CalEvent[] = [];
  for (const b of busySlots) {
    if (b.weekday !== day) continue;
    out.push({
      kind: "busy",
      startMin: parseMin(b.start),
      endMin: parseMin(b.end),
      label: b.label || "busy",
    });
  }
  for (const s of studySlots) {
    if (String(s.weekday).toLowerCase() !== day) continue;
    out.push({
      kind: "study",
      startMin: parseMin(String(s.start || "")),
      endMin: parseMin(String(s.end || "")),
      label: String(s.label || "study"),
    });
  }
  return out.sort((a, b) => a.startMin - b.startMin);
}

function fmtHour(min: number): string {
  const h = Math.floor(min / 60);
  return `${String(h).padStart(2, "0")}:00`;
}

function fmtClock(min: number): string {
  return `${String(Math.floor(min / 60)).padStart(2, "0")}:${String(min % 60).padStart(2, "0")}`;
}

export function WeekCalendar({ studySlots, busySlots }: Props) {
  const t = useTranslations("studyAdvisor");
  const totalMin = studySlots.reduce((acc, s) => {
    return acc + Math.max(0, parseMin(String(s.end)) - parseMin(String(s.start)));
  }, 0);

  const allEvents = STUDY_WEEKDAYS.flatMap((day) =>
    eventsForDay(day, studySlots, busySlots),
  );
  let rangeStart = DEFAULT_START;
  let rangeEnd = DEFAULT_END;
  if (allEvents.length > 0) {
    const earliest = Math.min(...allEvents.map((e) => e.startMin));
    const latest = Math.max(...allEvents.map((e) => e.endMin));
    rangeStart = Math.max(0, Math.floor(earliest / 60) * 60 - 60);
    rangeEnd = Math.min(24 * 60, Math.ceil(latest / 60) * 60 + 60);
    if (rangeEnd - rangeStart < 8 * 60) {
      rangeStart = Math.min(rangeStart, DEFAULT_START);
      rangeEnd = Math.max(rangeEnd, DEFAULT_END);
    }
  }
  const hours: number[] = [];
  for (let m = rangeStart; m < rangeEnd; m += 60) hours.push(m);
  const gridHeight = ((rangeEnd - rangeStart) / 60) * HOUR_PX;

  return (
    <section className="space-y-3 overflow-hidden rounded-xl border border-[var(--line)] bg-[var(--card)]">
      <header className="flex flex-wrap items-baseline justify-between gap-2 border-b border-[var(--line)] px-4 py-3">
        <div>
          <h2 className="text-sm font-semibold text-[var(--ink)]">
            {t("calendarTitle")}
          </h2>
          <p className="text-[11px] text-[var(--muted)]">{t("calendarWlbHint")}</p>
        </div>
        <p className="text-xs text-[var(--muted)]">
          {t("calendarTotal", {
            hours: String(Math.floor(totalMin / 60)),
            minutes: String(totalMin % 60).padStart(2, "0"),
          })}
        </p>
      </header>

      <div className="overflow-x-auto px-2 pb-3">
        <div
          className="grid min-w-[720px]"
          style={{ gridTemplateColumns: "52px repeat(7, minmax(0, 1fr))" }}
        >
          <div className="sticky left-0 z-[1] bg-[var(--card)]" />
          {STUDY_WEEKDAYS.map((day) => (
            <div
              key={`h-${day}`}
              className="border-b border-[var(--line)] py-2 text-center text-[11px] font-semibold uppercase tracking-wide text-[var(--muted)]"
            >
              {t(`day_${day}`)}
            </div>
          ))}

          <div
            className="relative sticky left-0 z-[1] bg-[var(--card)]"
            style={{ height: gridHeight }}
          >
            {hours.map((h) => (
              <div
                key={h}
                className="absolute right-1 -translate-y-1/2 text-[10px] tabular-nums text-[var(--muted)]"
                style={{ top: ((h - rangeStart) / 60) * HOUR_PX }}
              >
                {fmtHour(h)}
              </div>
            ))}
          </div>

          {STUDY_WEEKDAYS.map((day) => {
            const events = eventsForDay(day, studySlots, busySlots);
            return (
              <div
                key={day}
                className="relative border-l border-[var(--line)]"
                style={{ height: gridHeight }}
              >
                {hours.map((h) => (
                  <div
                    key={`${day}-${h}`}
                    className="absolute inset-x-0 border-t border-[color-mix(in_srgb,var(--line)_70%,transparent)]"
                    style={{ top: ((h - rangeStart) / 60) * HOUR_PX }}
                  />
                ))}
                {events.map((ev) => {
                  const top =
                    ((ev.startMin - rangeStart) / 60) * HOUR_PX + 1;
                  const height = Math.max(
                    18,
                    ((ev.endMin - ev.startMin) / 60) * HOUR_PX - 2,
                  );
                  const isStudy = ev.kind === "study";
                  return (
                    <div
                      key={`${day}-${ev.kind}-${ev.startMin}-${ev.endMin}`}
                      className={
                        isStudy
                          ? "absolute inset-x-0.5 overflow-hidden rounded-md border border-[color-mix(in_srgb,var(--signal)_45%,transparent)] bg-[color-mix(in_srgb,var(--signal)_22%,transparent)] px-1 py-0.5 text-[10px] leading-tight text-[var(--ink)] shadow-sm"
                          : "absolute inset-x-0.5 overflow-hidden rounded-md border border-[color-mix(in_srgb,var(--muted)_35%,transparent)] bg-[color-mix(in_srgb,var(--muted)_12%,transparent)] px-1 py-0.5 text-[10px] leading-tight text-[var(--muted)]"
                      }
                      style={{ top, height }}
                      title={`${fmtClock(ev.startMin)}–${fmtClock(ev.endMin)} ${isStudy ? t("calendarStudy") : ev.label}`}
                    >
                      <span className="block font-semibold tabular-nums">
                        {fmtClock(ev.startMin)}–{fmtClock(ev.endMin)}
                      </span>
                      <span className="block truncate opacity-90">
                        {isStudy ? t("calendarStudy") : ev.label}
                      </span>
                    </div>
                  );
                })}
              </div>
            );
          })}
        </div>
      </div>

      <div className="flex flex-wrap gap-3 border-t border-[var(--line)] px-4 py-2 text-[11px] text-[var(--muted)]">
        <span className="inline-flex items-center gap-1.5">
          <span className="inline-block h-2.5 w-2.5 rounded-sm bg-[color-mix(in_srgb,var(--signal)_55%,transparent)]" />
          {t("calendarStudy")}
        </span>
        <span className="inline-flex items-center gap-1.5">
          <span className="inline-block h-2.5 w-2.5 rounded-sm bg-[color-mix(in_srgb,var(--muted)_35%,transparent)]" />
          {t("calendarBusy")}
        </span>
      </div>
    </section>
  );
}
