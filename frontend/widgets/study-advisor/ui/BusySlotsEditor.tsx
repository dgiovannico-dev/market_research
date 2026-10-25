"use client";

import { useTranslations } from "next-intl";
import {
  STUDY_WEEKDAYS,
  type BusySlot,
  type StudyWeekday,
} from "@/entities/study-advisor";

type Props = {
  slots: BusySlot[];
  onChange: (next: BusySlot[]) => void;
};

export function BusySlotsEditor({ slots, onChange }: Props) {
  const t = useTranslations("studyAdvisor");

  function update(i: number, patch: Partial<BusySlot>) {
    onChange(slots.map((s, idx) => (idx === i ? { ...s, ...patch } : s)));
  }

  function remove(i: number) {
    onChange(slots.filter((_, idx) => idx !== i));
  }

  function add() {
    onChange([
      ...slots,
      {
        weekday: "mon",
        start: "09:00",
        end: "18:00",
        label: "busy",
        origin: "manual",
      },
    ]);
  }

  return (
    <section className="space-y-3 rounded-xl border border-[var(--line)] bg-[var(--card)] p-4">
      <header className="space-y-1">
        <h2 className="text-sm font-semibold text-[var(--ink)]">{t("busyTitle")}</h2>
        <p className="text-xs text-[var(--muted)]">{t("busyHint")}</p>
      </header>
      <ul className="space-y-2">
        {slots.map((slot, i) => (
          <li
            key={`${slot.weekday}-${slot.start}-${i}`}
            className="grid grid-cols-[minmax(0,1fr)_auto_auto_auto_auto] items-center gap-2 text-sm"
          >
            <select
              className="rounded border border-[var(--line)] bg-transparent px-2 py-1"
              value={slot.weekday}
              onChange={(e) =>
                update(i, { weekday: e.target.value as StudyWeekday })
              }
              aria-label={t("busyWeekday")}
            >
              {STUDY_WEEKDAYS.map((d) => (
                <option key={d} value={d}>
                  {t(`day_${d}`)}
                </option>
              ))}
            </select>
            <input
              type="time"
              className="rounded border border-[var(--line)] bg-transparent px-2 py-1"
              value={slot.start}
              onChange={(e) => update(i, { start: e.target.value })}
              aria-label={t("busyStart")}
            />
            <input
              type="time"
              className="rounded border border-[var(--line)] bg-transparent px-2 py-1"
              value={slot.end}
              onChange={(e) => update(i, { end: e.target.value })}
              aria-label={t("busyEnd")}
            />
            <input
              className="w-24 rounded border border-[var(--line)] bg-transparent px-2 py-1"
              value={slot.label || ""}
              onChange={(e) =>
                update(i, { label: e.target.value, origin: "manual" })
              }
              placeholder={t("busyLabelPh")}
              aria-label={t("busyLabel")}
            />
            {slot.origin === "calendar" ? (
              <span className="text-[10px] uppercase tracking-wide text-[var(--muted)]">
                {t("busyFromCal")}
              </span>
            ) : (
              <span className="w-8" aria-hidden />
            )}
            <button
              type="button"
              className="text-xs text-[var(--muted)] underline"
              onClick={() => remove(i)}
            >
              {t("busyRemove")}
            </button>
          </li>
        ))}
      </ul>
      <button
        type="button"
        onClick={add}
        className="rounded border border-[var(--line)] px-3 py-1.5 text-xs hover:border-[var(--signal)]"
      >
        {t("busyAdd")}
      </button>
    </section>
  );
}
