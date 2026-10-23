"use client";

import { useId } from "react";
import { useTranslations } from "next-intl";

export type RelationsHeatGroup = "skills" | "place";

type RelationsHeatGroupTabsProps = {
  value: RelationsHeatGroup;
  onChange: (next: RelationsHeatGroup) => void;
  className?: string;
};

const OPTIONS: readonly RelationsHeatGroup[] = ["skills", "place"];

/**
 * Second-level segment under Heatmaps: Skills vs Place matrix groups.
 */
export function RelationsHeatGroupTabs({
  value,
  onChange,
  className = "",
}: RelationsHeatGroupTabsProps) {
  const t = useTranslations("relations");
  const labelId = useId();

  return (
    <div className={className.trim() || undefined}>
      <span className="sr-only" id={labelId}>
        {t("heatGroupAria")}
      </span>
      <div
        className="inline-flex rounded-full border border-[var(--line)] p-0.5 text-xs"
        role="tablist"
        aria-labelledby={labelId}
        aria-label={t("heatGroupAria")}
      >
        {OPTIONS.map((option) => {
          const selected = value === option;
          const label =
            option === "skills" ? t("tabHeatSkills") : t("tabHeatPlace");
          return (
            <button
              key={option}
              type="button"
              role="tab"
              id={`relations-heat-tab-${option}`}
              aria-selected={selected}
              aria-controls={`relations-heat-panel-${option}`}
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
