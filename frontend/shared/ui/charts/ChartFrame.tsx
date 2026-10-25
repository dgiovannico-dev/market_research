"use client";

import { useTranslations } from "next-intl";
import { useMemo, useRef, useState, type ReactNode } from "react";
import { CHART_TOP_N_OPTIONS } from "./chartTopN";
import { MetricLegend } from "@/shared/ui/MetricLegend";
import { ScrollLoadFooter } from "@/shared/ui/ScrollLoadFooter";
import { SortableTh } from "@/shared/ui/SortableTh";
import { TableGuide } from "@/shared/ui/TableGuide";
import { TableSearch } from "@/shared/ui/TableSearch";
import { useClientPageWindow } from "@/shared/hooks/useClientPageWindow";
import { useClientTableFilter } from "@/shared/hooks/useClientTableFilter";
import { useClientTableSort } from "@/shared/hooks/useClientTableSort";
import { joinSearchParts } from "@/shared/lib/tableFilter";
import type { SortValue } from "@/shared/lib/tableSort";

export type ChartTable = {
  columns: string[];
  rows: (string | number | null)[][];
};

export type ChartLegendItem = {
  term: string;
  definition: string;
};

export type ChartFrameProps = {
  title: string;
  periodDays?: number | null;
  sampleSize?: number | null;
  empty?: boolean;
  thin?: boolean;
  emptyMessage?: string;
  thinMessage?: string;
  /** Non-thin advisory banner (e.g. rise/cool side imbalance). */
  note?: string | null;
  table?: ChartTable | null;
  /** Plain-language glossary under the header (chart jargon). */
  legendItems?: ChartLegendItem[];
  /** What this chart/table measures. */
  guideRepresents?: string;
  /** How to interpret axes, colours, or rows. */
  guideHowToRead?: string;
  children?: ReactNode;
  className?: string;
  /** When set with onTopNChange, shows 5/10/15/… selector in the header. */
  topN?: number;
  topNOptions?: readonly number[];
  onTopNChange?: (n: number) => void;
  /** Override default charts.topNAria (e.g. rise/cool half-half wording). */
  topNAriaLabel?: string;
  /**
   * Axis captions rendered outside the plot (HTML). Prefer these over
   * ECharts axis `name` — that name overlaps tick labels with containLabel.
   */
  xAxisLabel?: string;
  yAxisLabel?: string;
};

type ChartTableRow = {
  cells: (string | number | null)[];
  id: number;
};

function buildAccessors(columnCount: number) {
  const accessors: Record<string, (row: ChartTableRow) => SortValue> = {};
  for (let i = 0; i < columnCount; i += 1) {
    const idx = i;
    accessors[String(idx)] = (row) => row.cells[idx] ?? null;
  }
  return accessors;
}

export function ChartFrame({
  title,
  periodDays,
  sampleSize,
  empty = false,
  thin = false,
  emptyMessage,
  thinMessage,
  note = null,
  table = null,
  legendItems,
  guideRepresents,
  guideHowToRead,
  children,
  className = "",
  topN,
  topNOptions = CHART_TOP_N_OPTIONS,
  onTopNChange,
  topNAriaLabel,
  xAxisLabel,
  yAxisLabel,
}: ChartFrameProps) {
  const t = useTranslations("charts");
  const tCommon = useTranslations("common");
  const tableScrollRef = useRef<HTMLDivElement | null>(null);
  const [showTable, setShowTable] = useState(false);
  const showTopN = typeof topN === "number" && typeof onTopNChange === "function";
  const showChart = !empty && !showTable;
  const resolvedEmpty = emptyMessage ?? t("empty");
  const resolvedThin =
    thinMessage ?? t("thinSample", { n: sampleSize ?? 0 });

  const tableRows: ChartTableRow[] = useMemo(
    () =>
      (table?.rows ?? []).map((cells, id) => ({
        cells,
        id,
      })),
    [table],
  );

  const accessors = useMemo(
    () => buildAccessors(table?.columns.length ?? 0),
    [table?.columns.length],
  );

  const {
    query: tableQuery,
    setQuery: setTableQuery,
    filtered: filteredRows,
  } = useClientTableFilter(tableRows, (row) => joinSearchParts(...row.cells));
  const { sorted, sortKey, order, toggle } = useClientTableSort(
    filteredRows,
    accessors,
    "0",
    "asc",
  );
  const page = useClientPageWindow(
    sorted,
    40,
    `${tableQuery}|${sortKey}|${order}|${sorted.length}|${table?.columns.length ?? 0}`,
  );

  return (
    <section className={`card overflow-hidden ${className}`.trim()}>
      <header className="flex flex-wrap items-start justify-between gap-2 border-b border-[var(--line)] px-4 py-3">
        <div>
          <h2 className="text-base font-semibold tracking-tight">{title}</h2>
          <p
            className="mt-0.5 text-xs opacity-70"
            style={{ fontFamily: "var(--mono)" }}
          >
            {periodDays != null && sampleSize != null
              ? t("periodFooter", { days: periodDays, n: sampleSize })
              : periodDays != null
                ? `${periodDays}d`
                : sampleSize != null
                  ? `n=${sampleSize}`
                  : "—"}
            {thin && !empty ? ` · ${t("thinBadge")}` : null}
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          {showTopN ? (
            <label className="flex items-center gap-1.5 text-xs text-[var(--muted)]">
              <span>{t("topNLabel")}</span>
              <select
                className="rounded border border-[var(--line)] bg-transparent px-1.5 py-1 text-[var(--ink)]"
                value={topN}
                aria-label={topNAriaLabel ?? t("topNAria")}
                onChange={(e) => onTopNChange?.(Number(e.target.value))}
              >
                {topNOptions.map((n) => (
                  <option key={n} value={n}>
                    {n}
                  </option>
                ))}
              </select>
            </label>
          ) : null}
          {table && table.rows.length > 0 ? (
            <button
              type="button"
              className="rounded border border-[var(--line)] px-2.5 py-1 text-xs hover:border-[var(--signal)]"
              onClick={() => setShowTable((v) => !v)}
              aria-pressed={showTable}
            >
              {showTable ? t("showChart") : t("showTable")}
            </button>
          ) : null}
        </div>
      </header>

      {/* Guides/legend collapsed by default — keeps the plot above the fold. */}
      {(guideRepresents && guideHowToRead) ||
      (legendItems && legendItems.length > 0) ? (
        <details className="group border-b border-[var(--line)]">
          <summary className="cursor-pointer list-none px-4 py-2.5 text-xs font-medium text-[var(--muted)] marker:content-none hover:text-[var(--ink)] [&::-webkit-details-marker]:hidden">
            <span className="flex items-center justify-between gap-2">
              {t("howToReadTitle")}
              <span className="text-[0.65rem] uppercase tracking-wide opacity-70">
                <span className="group-open:hidden">{t("showGuide")}</span>
                <span className="hidden group-open:inline">{t("hideGuide")}</span>
              </span>
            </span>
          </summary>
          <div className="space-y-3 border-t border-[var(--line)] px-4 py-3">
            {guideRepresents && guideHowToRead ? (
              <TableGuide
                variant="plain"
                represents={guideRepresents}
                howToRead={guideHowToRead}
              />
            ) : null}
            {legendItems && legendItems.length > 0 ? (
              <MetricLegend
                variant="plain"
                title={t("legendTitle")}
                items={legendItems}
              />
            ) : null}
          </div>
        </details>
      ) : null}

      {empty ? (
        <div className="px-4 py-10 text-center text-sm opacity-75">{resolvedEmpty}</div>
      ) : null}

      {!empty && thin ? (
        <p className="border-b border-[var(--line)] bg-[color-mix(in_srgb,var(--rise)_10%,transparent)] px-4 py-2 text-xs text-[var(--ink)]">
          {resolvedThin}
        </p>
      ) : null}

      {!empty && note ? (
        <p className="border-b border-[var(--line)] bg-[color-mix(in_srgb,var(--cool)_12%,transparent)] px-4 py-2 text-xs text-[var(--ink)]">
          {note}
        </p>
      ) : null}

      {showChart ? (
        <div className="px-2 pb-3 pt-1">
          <div className="flex items-stretch gap-1">
            {yAxisLabel ? (
              <div
                className="flex w-6 shrink-0 items-center justify-center self-stretch py-2"
                aria-hidden
              >
                <span
                  className="text-center text-[0.65rem] font-medium tracking-wide text-[var(--muted)]"
                  style={{
                    fontFamily: "var(--mono)",
                    writingMode: "vertical-rl",
                    transform: "rotate(180deg)",
                  }}
                >
                  {yAxisLabel}
                </span>
              </div>
            ) : null}
            <div className="min-w-0 flex-1">
              {children}
              {xAxisLabel ? (
                <p
                  className="mt-1 text-center text-[0.65rem] font-medium tracking-wide text-[var(--muted)]"
                  style={{ fontFamily: "var(--mono)" }}
                >
                  {xAxisLabel}
                </p>
              ) : null}
            </div>
          </div>
        </div>
      ) : null}

      {!empty && showTable && table ? (
        <div className="px-2 pb-3 pt-1">
          <div className="mb-2 px-1">
            <TableSearch value={tableQuery} onChange={setTableQuery} />
          </div>
          <div
            ref={tableScrollRef}
            className="max-h-96 overflow-auto overscroll-contain"
          >
            <table className="min-w-full text-sm">
              <thead className="sticky top-0 z-10 bg-[var(--card)] text-xs uppercase shadow-[0_1px_0_var(--line)]">
                <tr>
                  {table.columns.map((col, i) => (
                    <SortableTh
                      key={`${col}-${i}`}
                      label={col}
                      sortKey={String(i)}
                      activeSort={sortKey}
                      order={order}
                      onSort={toggle}
                      ariaLabel={tCommon("sortBy", { column: col })}
                      className="bg-[var(--card)] px-2 py-1.5 text-left font-medium text-[var(--muted)]"
                    />
                  ))}
                </tr>
              </thead>
              <tbody>
                {sorted.length === 0 ? (
                  <tr>
                    <td
                      colSpan={Math.max(table.columns.length, 1)}
                      className="px-2 py-4 text-[var(--muted)]"
                    >
                      {tCommon("tableFilterEmpty")}
                    </td>
                  </tr>
                ) : (
                  page.visible.map((row) => (
                    <tr key={row.id} className="border-t border-[var(--line)]">
                      {row.cells.map((cell, j) => (
                        <td
                          key={j}
                          className="px-2 py-1.5"
                          style={
                            j > 0 ? { fontFamily: "var(--mono)" } : undefined
                          }
                        >
                          {cell == null ? "—" : cell}
                        </td>
                      ))}
                    </tr>
                  ))
                )}
              </tbody>
            </table>
            {sorted.length > 0 ? (
              <ScrollLoadFooter
                hasMore={page.hasMore}
                isExpanded={page.isExpanded}
                onLoadMore={page.loadMore}
                onExpandAll={page.expandAll}
                onCollapse={page.collapse}
                shown={page.shown}
                total={page.total}
                scrollRootRef={tableScrollRef}
              />
            ) : null}
          </div>
        </div>
      ) : null}
    </section>
  );
}
