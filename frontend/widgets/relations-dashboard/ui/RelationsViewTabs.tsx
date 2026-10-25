"use client";

import { useId } from "react";
import { useTranslations } from "next-intl";

export type RelationsView = "heat" | "series" | "graph";

type RelationsViewTabsProps = {
  value: RelationsView;
  onChange: (next: RelationsView) => void;
  className?: string;
};

const OPTIONS: readonly RelationsView[] = ["heat", "series", "graph"];

/**
 * Sticky-ish segment control for Relations chart groups.
 * Composition: parent swaps HeatmapsPanel / SeriesPanel / GraphPanel.
 */
export function RelationsViewTabs({
  value,
  onChange,
  className = "",
}: RelationsViewTabsProps) {
  const t = useTranslations("relations");
  const labelId = useId();

  return (
    <div
      className={`sticky top-14 z-20 -mx-1 border-b border-[var(--line)] bg-[color-mix(in_srgb,var(--bg)_88%,transparent)] px-1 py-2 backdrop-blur-md ${className}`.trim()}
    >
      <span className="sr-only" id={labelId}>
        {t("tabsAria")}
      </span>
      <div
        className="inline-flex rounded-full border border-[var(--line)] p-0.5 text-xs"
        role="tablist"
        aria-labelledby={labelId}
        aria-label={t("tabsAria")}
      >
        {OPTIONS.map((option) => {
          const selected = value === option;
          const label =
            option === "heat"
              ? t("tabHeatmaps")
              : option === "series"
                ? t("tabSeries")
                : t("tabGraph");
          return (
            <button
              key={option}
              type="button"
              role="tab"
              id={`relations-tab-${option}`}
              aria-selected={selected}
              aria-controls={`relations-panel-${option}`}
              tabIndex={selected ? 0 : -1}
              className={`rounded-full px-3 py-1.5 transition-colors duration-200 ${
                selected
                  ? "bg-[var(--signal)] text-white"
                  : "text-[var(--ink)] opacity-70 hover:opacity-100"
              }`}
              onClick={() => onChange(option)}
            >
              {label}
            </button>
          );
        })}
      </div>
    </div>
  );
}
