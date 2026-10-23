"use client";

import { useId } from "react";
import { useTranslations } from "next-intl";
import { useDashboardPrefs } from "@/features/dashboard-prefs";

/** Sticky period options shared across Executive / Relations (and prefs). */
export const PERIOD_CHIP_OPTIONS = [7, 14, 30, 90, 180, 365] as const;

export type PeriodChipDays = (typeof PERIOD_CHIP_OPTIONS)[number];

function nearestPeriodDays(
  days: number,
  options: readonly number[] = PERIOD_CHIP_OPTIONS,
): number {
  return options.reduce((best, opt) =>
    Math.abs(opt - days) < Math.abs(best - days) ? opt : best,
  );
}

export type PeriodChipProps = {
  className?: string;
};

/**
 * Sticky analysis window chips — writes `prefs.period_days` via DashboardPrefs.
 * When the stored value is not in the preset list, the nearest option is highlighted.
 */
export function PeriodChip({ className = "" }: PeriodChipProps) {
  const t = useTranslations("common");
  const labelId = useId();
  const { prefs, setPeriodDays } = useDashboardPrefs();
  const current = prefs.period_days;
  const exact = (PERIOD_CHIP_OPTIONS as readonly number[]).includes(current);
  const activeDays = exact ? current : nearestPeriodDays(current);

  return (
    <div
      className={`inline-flex flex-wrap items-center gap-1.5 ${className}`.trim()}
    >
      <span className="text-xs text-[var(--muted)]" id={labelId}>
        {t("periodChipLabel")}
      </span>
      <div
        className="inline-flex flex-wrap gap-0.5 rounded-full border border-[var(--line)] p-0.5 text-xs"
        role="radiogroup"
        aria-labelledby={labelId}
        aria-label={t("periodChipAria")}
      >
        {PERIOD_CHIP_OPTIONS.map((days) => {
          const active = days === activeDays;
          return (
            <button
              key={days}
              type="button"
              role="radio"
              aria-checked={active}
              aria-pressed={active}
              className={`rounded-full px-2.5 py-1.5 transition-colors duration-200 ${
                active
                  ? "bg-[var(--signal)] text-white"
                  : "text-[var(--ink)] opacity-70 hover:opacity-100"
              }`}
              onClick={() => setPeriodDays(days)}
            >
              {days}d
            </button>
          );
        })}
      </div>
    </div>
  );
}
