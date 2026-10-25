"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import {
  loadCalendarFeedUrl,
  mergeCalendarBusy,
  saveCalendarFeedUrl,
  studyAdvisorApi,
  type BusySlot,
} from "@/entities/study-advisor";

type Props = {
  busySlots: BusySlot[];
  onBusyChange: (next: BusySlot[]) => void;
  onReplan: (slots: BusySlot[]) => void | Promise<void>;
  disabled?: boolean;
};

export function CalendarFeedSync({
  busySlots,
  onBusyChange,
  onReplan,
  disabled,
}: Props) {
  const t = useTranslations("studyAdvisor");
  const [url, setUrl] = useState(() => loadCalendarFeedUrl());
  const [status, setStatus] = useState("");
  const [syncing, setSyncing] = useState(false);

  async function sync(andReplan: boolean) {
    const trimmed = url.trim();
    if (!trimmed) {
      setStatus(t("calNeedUrl"));
      return;
    }
    setSyncing(true);
    setStatus("");
    saveCalendarFeedUrl(trimmed);
    try {
      const timezone =
        typeof Intl !== "undefined"
          ? Intl.DateTimeFormat().resolvedOptions().timeZone
          : "Europe/Rome";
      const res = await studyAdvisorApi.calendarBusy({
        ics_url: trimmed,
        timezone,
      });
      const merged = mergeCalendarBusy(busySlots, res.busy_slots || []);
      onBusyChange(merged);
      setStatus(
        t("calSyncOk", {
          imported: String(res.imported ?? 0),
          events: String(res.event_count ?? 0),
          week: res.week_start || "",
        }),
      );
      if (andReplan) await onReplan(merged);
    } catch (e) {
      setStatus(e instanceof Error ? e.message : t("calSyncFail"));
    } finally {
      setSyncing(false);
    }
  }

  return (
    <section className="space-y-3 rounded-xl border border-[var(--line)] bg-[var(--card)] p-4">
      <header className="space-y-1">
        <h2 className="text-sm font-semibold text-[var(--ink)]">{t("calTitle")}</h2>
        <p className="text-xs text-[var(--muted)]">{t("calHint")}</p>
      </header>
      <label className="block text-sm">
        {t("calUrlLabel")}
        <input
          className="mt-1 w-full rounded border border-[var(--line)] bg-transparent px-2 py-1.5 text-xs"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder={t("calUrlPh")}
          spellCheck={false}
          autoComplete="off"
        />
      </label>
      <p className="text-[11px] text-[var(--muted)]">{t("calHowTo")}</p>
      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          disabled={disabled || syncing}
          onClick={() => void sync(false)}
          className="rounded border border-[var(--line)] px-3 py-2 text-sm hover:border-[var(--signal)] disabled:opacity-50"
        >
          {syncing ? t("calSyncing") : t("calSync")}
        </button>
        <button
          type="button"
          disabled={disabled || syncing}
          onClick={() => void sync(true)}
          className="rounded border border-[var(--line)] px-3 py-2 text-sm hover:border-[var(--signal)] disabled:opacity-50"
        >
          {t("calReplan")}
        </button>
      </div>
      {status ? (
        <p className="text-xs text-[var(--muted)]" role="status">
          {status}
        </p>
      ) : null}
    </section>
  );
}
