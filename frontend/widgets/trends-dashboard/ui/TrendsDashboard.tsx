"use client";

import { Suspense, useMemo } from "react";
import { useTranslations } from "next-intl";
import { useDashboardLensQuery } from "@/features/dashboard-query";
import { api, type TechnologyTrendItem, type TechnologyTrends } from "@/lib/api";
import { useDashboardPrefs } from "@/features/dashboard-prefs";
import { useDashboardCountries } from "@/features/country-filter";
import {
  LensToggle,
  useDashboardLens,
} from "@/features/lens-toggle";
import { extractComparePoints } from "@/features/dashboard-chrome";
import { CompareDualLazy, RiseCoolChartLazy } from "@/shared/ui/charts";
import { MetricLegend } from "@/shared/ui/MetricLegend";
import { ScrollLoadFooter } from "@/shared/ui/ScrollLoadFooter";
import { SortableTh } from "@/shared/ui/SortableTh";
import { TableGuide } from "@/shared/ui/TableGuide";
import { TableSearch } from "@/shared/ui/TableSearch";
import { useClientPageWindow } from "@/shared/hooks/useClientPageWindow";
import { useClientTableFilter } from "@/shared/hooks/useClientTableFilter";
import { useClientTableSort } from "@/shared/hooks/useClientTableSort";
import { formatPercentNumber } from "@/shared/lib/formatPercent";
import { joinSearchParts } from "@/shared/lib/tableFilter";

const theadClass =
  "border-b border-[var(--line)] text-[0.65rem] font-semibold uppercase tracking-[0.12em] text-[var(--muted)]";
const theadStyle = {
  background: "color-mix(in srgb, var(--paper) 85%, var(--card))",
} as const;

function nestPeriod(trends: TechnologyTrends | null, fallback: number): number {
  return (
    trends?.period_days ??
    trends?.market?.period_days ??
    trends?.focus?.period_days ??
    fallback
  );
}

function nestExcludedThin(trends: TechnologyTrends | null): number {
  return (
    trends?.excluded_thin_n ??
    trends?.market?.excluded_thin_n ??
    trends?.focus?.excluded_thin_n ??
    0
  );
}

function lensItems(trends: TechnologyTrends | null, lens: string): TechnologyTrendItem[] {
  if (!trends) return [];
  if (lens === "focus" && trends.focus?.items) return trends.focus.items;
  if (lens === "market" && trends.market?.items) return trends.market.items;
  return trends.items ?? [];
}

function TrendsDashboardInner() {
  const t = useTranslations("trends");
  const tCharts = useTranslations("charts");
  const tCompass = useTranslations("compass");
  const { prefs, hydrated } = useDashboardPrefs();
  const { lens, queryIds } = useDashboardLens();
  const { countries } = useDashboardCountries();
  const guided = prefs.view_mode === "guided";
  const loadFailedMsg = t("loadFailed");
  const {
    data: trends,
    error,
    isStale,
  } = useDashboardLensQuery<TechnologyTrends>({
    hydrated,
    days: Math.min(prefs.period_days, 365),
    lens,
    queryIds,
    countries,
    fallbackError: loadFailedMsg,
    fetcher: (ctx) =>
      api.trends({
        days: ctx.days,
        lens: ctx.lens,
        queryIds: ctx.queryIds,
        countries: ctx.countries,
      }),
  });

  const focus = new Set(prefs.focus_technologies.map((x) => x.toLowerCase()));
  /** Match Executive: only narrow on focus lens (market must stay full corpus). */
  const narrowToTechFocus = lens === "focus" && focus.size > 0;
  const rawItems = lensItems(trends, lens);
  const filtered = narrowToTechFocus
    ? rawItems.filter((item) => focus.has(String(item.technology).toLowerCase()))
    : rawItems;

  const periodDays = nestPeriod(trends, prefs.period_days);
  const excludedThin = nestExcludedThin(trends);
  const comparePoints = extractComparePoints(trends);
  const filteredCompare = comparePoints;
  const tCommon = useTranslations("common");
  const columnLegend = useMemo(
    () =>
      lens === "compare"
        ? [
            { term: t("colTechnology"), definition: t("hintTechnology") },
            { term: tCharts("legendMarket"), definition: t("hintMarket") },
            { term: tCharts("legendFocus"), definition: t("hintFocus") },
          ]
        : [
            { term: t("colRecent"), definition: t("hintRecent") },
            { term: t("colPrevious"), definition: t("hintPrevious") },
            { term: t("colGrowth"), definition: t("hintGrowth") },
            { term: t("colStatus"), definition: t("hintStatus") },
          ],
    [lens, t, tCharts],
  );
  const compareFilter = useClientTableFilter(filteredCompare, (p) =>
    joinSearchParts(p.label, p.market, p.focus),
  );
  const trendFilter = useClientTableFilter(filtered, (item) =>
    joinSearchParts(
      item.technology,
      item.category,
      item.recent_mentions,
      item.previous_mentions,
      item.growth_pct,
      item.status,
    ),
  );
  const compareSort = useClientTableSort(
    compareFilter.filtered,
    {
      technology: (p) => p.label,
      market: (p) => p.market,
      focus: (p) => p.focus,
    },
    "technology",
    "asc",
  );
  const trendSort = useClientTableSort(
    trendFilter.filtered,
    {
      technology: (item) => String(item.technology),
      category: (item) => String(item.category),
      recent: (item) => Number(item.recent_mentions) || 0,
      previous: (item) => Number(item.previous_mentions) || 0,
      growth: (item) =>
        item.growth_pct == null ? null : Number(item.growth_pct),
      status: (item) => String(item.status),
    },
    "growth",
    "desc",
  );
  const compareReady =
    filteredCompare.length >= 2 &&
    filteredCompare.some((p) => p.market != null) &&
    filteredCompare.some((p) => p.focus != null);

  const sampleSize =
    lens === "compare" && (trends?.market_n != null || trends?.focus_n != null)
      ? (trends?.market_n ?? 0) + (trends?.focus_n ?? 0)
      : filtered.reduce((s, it) => s + (it.sample_size || 0), 0) || null;

  const compareWindow = useClientPageWindow(
    compareSort.sorted,
    30,
    `compare|${compareFilter.query}|${compareSort.sortKey}|${compareSort.order}|${compareSort.sorted.length}`,
  );
  const trendWindow = useClientPageWindow(
    trendSort.sorted,
    30,
    `trend|${trendFilter.query}|${trendSort.sortKey}|${trendSort.order}|${trendSort.sorted.length}`,
  );

  return (
    <div
      className="space-y-5"
      style={isStale ? { opacity: 0.72 } : undefined}
    >
      <header className="flex flex-wrap items-end justify-between gap-3">
        <div className="space-y-1">
          <h2 className="font-display text-2xl font-semibold tracking-tight text-[var(--ink)]">
            {t("title")}
          </h2>
          <p className="max-w-2xl text-sm text-[var(--muted)]">
            {guided
              ? t("subtitleGuided", { days: prefs.period_days })
              : t("subtitleTrendsOnly", { days: prefs.period_days })}
          </p>
          {excludedThin > 0 ? (
            <p
              className="text-xs text-[var(--muted)]"
              style={{ fontFamily: "var(--mono)" }}
            >
              {t("excludedThin", { n: excludedThin })}
            </p>
          ) : null}
        </div>
        <LensToggle.Control />
      </header>

      <MetricLegend title={tCommon("metricLegendTitle")} items={columnLegend} />

      {error ? (
        <div
          className="rounded-xl border border-[var(--warn)]/40 bg-[var(--card)] p-4 text-sm text-[var(--warn)]"
          role="alert"
        >
          {error}
        </div>
      ) : null}

      {lens === "compare" ? (
        compareReady ? (
          <CompareDualLazy
            points={filteredCompare}
            periodDays={periodDays}
            sampleSize={sampleSize}
            title={tCharts("compareTitle")}
            emptyMessage={tCompass("compareUnavailable")}
          />
        ) : (
          <div className="rounded-xl border border-[var(--line)] bg-[var(--card)] p-4 text-sm text-[var(--muted)]">
            {t("compareEmpty")}
          </div>
        )
      ) : (
        <RiseCoolChartLazy
          items={filtered}
          periodDays={periodDays}
          sampleSize={sampleSize}
          title={tCharts("riseCoolTitle")}
        />
      )}

      <TableGuide
        represents={t("tableRepresents")}
        howToRead={t("tableHowToRead")}
      />

      {lens === "compare" ? (
        <section className="overflow-hidden rounded-xl border border-[var(--line)] bg-[var(--card)]">
          <div className="border-b border-[var(--line)] px-3 py-2">
            <TableSearch
              value={compareFilter.query}
              onChange={compareFilter.setQuery}
            />
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full text-left text-sm text-[var(--ink)]">
              <thead className={theadClass} style={theadStyle}>
                <tr>
                  <SortableTh label={t("colTechnology")} sortKey="technology" activeSort={compareSort.sortKey} order={compareSort.order} onSort={compareSort.toggle} ariaLabel={tCommon("sortBy", { column: t("colTechnology") })} hint={t("hintTechnology")} />
                  <SortableTh label={tCharts("legendMarket")} sortKey="market" activeSort={compareSort.sortKey} order={compareSort.order} onSort={compareSort.toggle} ariaLabel={tCommon("sortBy", { column: tCharts("legendMarket") })} align="right" hint={t("hintMarket")} />
                  <SortableTh label={tCharts("legendFocus")} sortKey="focus" activeSort={compareSort.sortKey} order={compareSort.order} onSort={compareSort.toggle} ariaLabel={tCommon("sortBy", { column: tCharts("legendFocus") })} align="right" hint={t("hintFocus")} />
                </tr>
              </thead>
              <tbody>
                {!trends && !error ? (
                  <tr>
                    <td colSpan={3} className="px-3 py-6 text-sm text-[var(--muted)]">
                      {tCommon("loading")}
                    </td>
                  </tr>
                ) : compareSort.sorted.length === 0 ? (
                  <tr>
                    <td colSpan={3} className="px-3 py-6 text-sm text-[var(--muted)]">
                      {compareFilter.query
                        ? tCommon("tableFilterEmpty")
                        : t("emptyTable")}
                    </td>
                  </tr>
                ) : (
                  compareWindow.visible.map((p) => (
                    <tr key={p.label} className="border-b border-[var(--line)]">
                      <td className="px-3 py-2.5">{p.label}</td>
                      <td
                        className="px-3 py-2.5 text-right"
                        style={{ fontFamily: "var(--mono)" }}
                      >
                        {p.market == null ? "—" : p.market}
                      </td>
                      <td
                        className="px-3 py-2.5 text-right"
                        style={{ fontFamily: "var(--mono)" }}
                      >
                        {p.focus == null ? "—" : p.focus}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
          {compareSort.sorted.length > 0 ? (
            <ScrollLoadFooter
              hasMore={compareWindow.hasMore}
              isExpanded={compareWindow.isExpanded}
              onLoadMore={compareWindow.loadMore}
              onExpandAll={compareWindow.expandAll}
              onCollapse={compareWindow.collapse}
              shown={compareWindow.shown}
              total={compareWindow.total}
            />
          ) : null}
        </section>
      ) : (
        <section className="overflow-hidden rounded-xl border border-[var(--line)] bg-[var(--card)]">
          <div className="border-b border-[var(--line)] px-3 py-2">
            <TableSearch
              value={trendFilter.query}
              onChange={trendFilter.setQuery}
            />
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full text-left text-sm text-[var(--ink)]">
              <thead className={theadClass} style={theadStyle}>
                <tr>
                  <SortableTh label={t("colTechnology")} sortKey="technology" activeSort={trendSort.sortKey} order={trendSort.order} onSort={trendSort.toggle} ariaLabel={tCommon("sortBy", { column: t("colTechnology") })} hint={t("hintTechnology")} />
                  <SortableTh label={t("colCategory")} sortKey="category" activeSort={trendSort.sortKey} order={trendSort.order} onSort={trendSort.toggle} ariaLabel={tCommon("sortBy", { column: t("colCategory") })} hint={t("hintCategory")} />
                  <SortableTh label={t("colRecent")} sortKey="recent" activeSort={trendSort.sortKey} order={trendSort.order} onSort={trendSort.toggle} ariaLabel={tCommon("sortBy", { column: t("colRecent") })} align="right" hint={t("hintRecent")} />
                  <SortableTh label={t("colPrevious")} sortKey="previous" activeSort={trendSort.sortKey} order={trendSort.order} onSort={trendSort.toggle} ariaLabel={tCommon("sortBy", { column: t("colPrevious") })} align="right" hint={t("hintPrevious")} />
                  <SortableTh label={t("colGrowth")} sortKey="growth" activeSort={trendSort.sortKey} order={trendSort.order} onSort={trendSort.toggle} ariaLabel={tCommon("sortBy", { column: t("colGrowth") })} align="right" hint={t("hintGrowth")} />
                  <SortableTh label={t("colStatus")} sortKey="status" activeSort={trendSort.sortKey} order={trendSort.order} onSort={trendSort.toggle} ariaLabel={tCommon("sortBy", { column: t("colStatus") })} hint={t("hintStatus")} />
                </tr>
              </thead>
              <tbody>
                {!trends && !error ? (
                  <tr>
                    <td colSpan={6} className="px-3 py-6 text-sm text-[var(--muted)]">
                      {tCommon("loading")}
                    </td>
                  </tr>
                ) : trendSort.sorted.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-3 py-6 text-sm text-[var(--muted)]">
                      {trendFilter.query
                        ? tCommon("tableFilterEmpty")
                        : t("emptyTable")}
                    </td>
                  </tr>
                ) : (
                  trendWindow.visible.map((item) => (
                    <tr
                      key={String(item.technology)}
                      className="border-b border-[var(--line)]"
                    >
                      <td className="px-3 py-2.5">{String(item.technology)}</td>
                      <td className="px-3 py-2.5 text-[var(--muted)]">
                        {String(item.category)}
                      </td>
                      <td className="px-3 py-2.5 text-right">
                        {String(item.recent_mentions)}
                      </td>
                      <td className="px-3 py-2.5 text-right text-[var(--muted)]">
                        {String(item.previous_mentions)}
                      </td>
                      <td className="px-3 py-2.5 text-right">
                        {item.growth_pct == null
                          ? "—"
                          : formatPercentNumber(Number(item.growth_pct))}
                      </td>
                      <td className="px-3 py-2.5 text-[var(--muted)]">
                        {String(item.status)}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
          {trendSort.sorted.length > 0 ? (
            <ScrollLoadFooter
              hasMore={trendWindow.hasMore}
              isExpanded={trendWindow.isExpanded}
              onLoadMore={trendWindow.loadMore}
              onExpandAll={trendWindow.expandAll}
              onCollapse={trendWindow.collapse}
              shown={trendWindow.shown}
              total={trendWindow.total}
            />
          ) : null}
        </section>
      )}
    </div>
  );
}

export function TrendsDashboard() {
  const t = useTranslations("common");
  return (
    <Suspense
      fallback={
        <div className="rounded-xl border border-[var(--line)] bg-[var(--card)] p-6 text-sm text-[var(--muted)]">
          {t("loading")}
        </div>
      }
    >
      <LensToggle.Provider>
        <TrendsDashboardInner />
      </LensToggle.Provider>
    </Suspense>
  );
}
