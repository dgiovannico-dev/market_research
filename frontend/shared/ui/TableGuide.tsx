"use client";

import { useTranslations } from "next-intl";

type Props = {
  /** What the table or chart measures / contains. */
  represents: string;
  /** How to interpret axes, rows, colours, or columns. */
  howToRead: string;
  /** Optional heading; defaults to common.tableGuideTitle */
  title?: string;
  className?: string;
  /** plain = no card chrome (inside ChartFrame / table toolbar). */
  variant?: "card" | "plain";
};

/**
 * Short reading guide for a data table or chart: what it shows and how to read it.
 * Pair with MetricLegend for per-column glossary when needed.
 */
export function TableGuide({
  represents,
  howToRead,
  title,
  className = "",
  variant = "card",
}: Props) {
  const t = useTranslations("common");
  const heading = title ?? t("tableGuideTitle");
  const shell =
    variant === "plain"
      ? className
      : `rounded-xl border border-[var(--line)] bg-[var(--card)] px-4 py-3 ${className}`.trim();

  return (
    <aside className={shell} aria-label={heading}>
      <h3 className="mb-2 text-[0.7rem] font-semibold uppercase tracking-[0.12em] text-[var(--muted)]">
        {heading}
      </h3>
      <div className="space-y-2 text-xs leading-snug text-[var(--muted)]">
        <p>
          <span className="font-semibold text-[var(--ink)]">
            {t("tableGuideRepresents")}{" "}
          </span>
          {represents}
        </p>
        <p>
          <span className="font-semibold text-[var(--ink)]">
            {t("tableGuideHowToRead")}{" "}
          </span>
          {howToRead}
        </p>
      </div>
    </aside>
  );
}
