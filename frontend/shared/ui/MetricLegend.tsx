type MetricLegendItem = {
  term: string;
  definition: string;
};

export type MetricLegendProps = {
  items: MetricLegendItem[];
  /** Visible heading above the list (i18n). */
  title?: string;
  /** plain = no card chrome (e.g. inside ChartFrame). */
  variant?: "card" | "plain";
  className?: string;
};

/**
 * Plain-language glossary for technical column headers / metrics.
 * Keep definitions short; one term per row.
 */
export function MetricLegend({
  items,
  title,
  variant = "card",
  className = "",
}: MetricLegendProps) {
  if (items.length === 0) return null;
  const shell =
    variant === "plain"
      ? className
      : `rounded-xl border border-[var(--line)] bg-[var(--card)] px-4 py-3 ${className}`.trim();
  return (
    <aside className={shell} aria-label={title}>
      {title ? (
        <h3 className="mb-2 text-[0.7rem] font-semibold uppercase tracking-[0.12em] text-[var(--muted)]">
          {title}
        </h3>
      ) : null}
      <dl className="grid gap-2 sm:grid-cols-2">
        {items.map((item) => (
          <div key={item.term} className="min-w-0">
            <dt
              className="text-xs font-semibold text-[var(--ink)]"
              style={{ fontFamily: "var(--mono)" }}
            >
              {item.term}
            </dt>
            <dd className="mt-0.5 text-xs leading-snug text-[var(--muted)]">
              {item.definition}
            </dd>
          </div>
        ))}
      </dl>
    </aside>
  );
}
