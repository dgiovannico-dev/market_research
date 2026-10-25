"use client";

import { Suspense, useMemo } from "react";
import { useTranslations } from "next-intl";
import { EurostatStatsPanel } from "./EurostatStatsPanel";
import { RatesBoxLazy } from "@/shared/ui/charts";
import { MetricLegend } from "@/shared/ui/MetricLegend";
import { ScrollLoadFooter } from "@/shared/ui/ScrollLoadFooter";
import { SortableTh } from "@/shared/ui/SortableTh";
import { TableGuide } from "@/shared/ui/TableGuide";
import { TableSearch } from "@/shared/ui/TableSearch";
import { useDashboardLensQuery } from "@/features/dashboard-query";
import { api, type RateExplorer } from "@/lib/api";
import { joinSearchParts } from "@/shared/lib/tableFilter";
import { useDashboardPrefs } from "@/features/dashboard-prefs";
import { useDashboardCountries } from "@/features/country-filter";
import {
  LensToggle,
  useDashboardLens,
} from "@/features/lens-toggle";
import { MarketCoverageBanner } from "@/features/dashboard-chrome";
import { useClientPageWindow } from "@/shared/hooks/useClientPageWindow";
import { useClientTableFilter } from "@/shared/hooks/useClientTableFilter";
import { useClientTableSort } from "@/shared/hooks/useClientTableSort";

const theadClass =
  "border-b border-[var(--line)] text-[0.65rem] font-semibold uppercase tracking-[0.12em] text-[var(--muted)]";
const theadStyle = {
  background: "color-mix(in srgb, var(--paper) 85%, var(--card))",
} as const;

function ratesWindowDays(periodDays: number): number {
  return Math.min(Math.max(periodDays, 90), 730);
}

function RatesDashboardInner() {
  const t = useTranslations("rates");
  const tCompass = useTranslations("compass");
  const { prefs, hydrated } = useDashboardPrefs();
  const { lens, queryIds } = useDashboardLens();
  const { countries } = useDashboardCountries();
  const loadFailedMsg = t("loadFailed");
  const windowDays = ratesWindowDays(prefs.period_days);
  const { data, error, isStale } = useDashboardLensQuery<RateExplorer>({
    hydrated,
    days: windowDays,
    lens,
    queryIds,
    countries,
    fallbackError: loadFailedMsg,
    fetcher: (ctx) =>
      api.rates({
        days: ctx.days,
        minSample: 3,
        lens: ctx.lens,
        queryIds: ctx.queryIds,
        countries: ctx.countries,
      }),
  });

  const items = data?.items ?? [];
  const tCommon = useTranslations("common");
  const columnLegend = useMemo(
    () => [
      { term: t("colN"), definition: t("hintN") },
      { term: t("colMedian"), definition: t("hintMedian") },
      { term: t("colP25"), definition: t("hintP25") },
      { term: t("colP75"), definition: t("hintP75") },
      { term: t("colUnit"), definition: t("hintUnit") },
      { term: t("colStatus"), definition: t("hintStatus") },
    ],
    [t],
  );
  const {
    query: tableQuery,
    setQuery: setTableQuery,
    filtered: filteredItems,
  } = useClientTableFilter(items, (r) =>
    joinSearchParts(
      r.country_code,
      r.currency,
      r.unit,
      r.sample_size,
      r.median,
      r.p25,
      r.p75,
      r.status,
    ),
  );
  const { sorted, sortKey, order, toggle } = useClientTableSort(
    filteredItems,
    {
      country: (r) => r.country_code,
      currency: (r) => r.currency,
      unit: (r) => r.unit,
      n: (r) => r.sample_size,
      median: (r) => r.median,
      p25: (r) => r.p25,
      p75: (r) => r.p75,
      status: (r) => r.status,
    },
    "n",
    "desc",
  );
  const {
    visible: visibleRows,
    hasMore,
    isExpanded,
    loadMore,
    expandAll,
    collapse,
    shown,
    total: listTotal,
  } = useClientPageWindow(
    sorted,
    30,
    `${tableQuery}|${sortKey}|${order}|${sorted.length}|${lens}`,
  );
  const sampleSize = data?.jobs_with_rates ?? null;
  const compareHint =
    lens === "compare" && data
      ? t("compareCounts", {
          market: data.market_n ?? 0,
          focus: data.focus_n ?? 0,
          overlap: data.overlap_n ?? 0,
        })
      : null;

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
            {data?.disclaimer ?? t("subtitle", { days: data?.period_days ?? windowDays })}
          </p>
          <p className="text-xs text-[var(--muted)]" style={{ fontFamily: "var(--mono)" }}>
            {data
              ? t("jobsWithRates", { n: data.jobs_with_rates ?? 0 })
              : error
                ? null
                : tCommon("loading")}
          </p>
          {(data?.excluded_thin_n ?? 0) > 0 ? (
            <p className="text-xs text-[var(--muted)]" style={{ fontFamily: "var(--mono)" }}>
              {t("excludedThin", { n: data?.excluded_thin_n ?? 0 })}
            </p>
          ) : null}
          {compareHint ? (
            <p className="text-xs text-[var(--muted)]" style={{ fontFamily: "var(--mono)" }}>
              {compareHint}
            </p>
          ) : null}
          {lens === "compare" && (data?.focus_n ?? 0) === 0 ? (
            <p className="text-sm text-[var(--muted)]">{tCompass("compareUnavailable")}</p>
          ) : null}
        </div>
        <LensToggle.Control />
      </header>

      <MarketCoverageBanner sampleSize={data ? sampleSize : null} />

      <RatesBoxLazy
        items={items}
        periodDays={data?.period_days ?? prefs.period_days}
        sampleSize={sampleSize}
      />

      <MetricLegend title={tCommon("metricLegendTitle")} items={columnLegend} />

      <EurostatStatsPanel />

      {error ? (
        <div
          className="rounded-xl border border-[var(--warn)]/40 bg-[var(--card)] p-4 text-sm text-[var(--warn)]"
          role="alert"
        >
          {error}
        </div>
      ) : null}

      <TableGuide
        represents={t("tableRepresents")}
        howToRead={t("tableHowToRead")}
      />

      <section className="overflow-hidden rounded-xl border border-[var(--line)] bg-[var(--card)]">
        <div className="border-b border-[var(--line)] px-3 py-2">
          <TableSearch value={tableQuery} onChange={setTableQuery} />
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full text-left text-sm text-[var(--ink)]">
            <thead className={theadClass} style={theadStyle}>
              <tr>
                <SortableTh label={t("colCountry")} sortKey="country" activeSort={sortKey} order={order} onSort={toggle} ariaLabel={tCommon("sortBy", { column: t("colCountry") })} hint={t("hintCountry")} />
                <SortableTh label={t("colCurrency")} sortKey="currency" activeSort={sortKey} order={order} onSort={toggle} ariaLabel={tCommon("sortBy", { column: t("colCurrency") })} hint={t("hintCurrency")} />
                <SortableTh label={t("colUnit")} sortKey="unit" activeSort={sortKey} order={order} onSort={toggle} ariaLabel={tCommon("sortBy", { column: t("colUnit") })} hint={t("hintUnit")} />
                <SortableTh label={t("colN")} sortKey="n" activeSort={sortKey} order={order} onSort={toggle} ariaLabel={tCommon("sortBy", { column: t("colN") })} align="right" hint={t("hintN")} />
                <SortableTh label={t("colMedian")} sortKey="median" activeSort={sortKey} order={order} onSort={toggle} ariaLabel={tCommon("sortBy", { column: t("colMedian") })} align="right" hint={t("hintMedian")} />
                <SortableTh label={t("colP25")} sortKey="p25" activeSort={sortKey} order={order} onSort={toggle} ariaLabel={tCommon("sortBy", { column: t("colP25") })} align="right" hint={t("hintP25")} />
                <SortableTh label={t("colP75")} sortKey="p75" activeSort={sortKey} order={order} onSort={toggle} ariaLabel={tCommon("sortBy", { column: t("colP75") })} align="right" hint={t("hintP75")} />
                <SortableTh label={t("colStatus")} sortKey="status" activeSort={sortKey} order={order} onSort={toggle} ariaLabel={tCommon("sortBy", { column: t("colStatus") })} hint={t("hintStatus")} />
              </tr>
            </thead>
            <tbody>
              {!data && !error ? (
                <tr>
                  <td className="px-3 py-4 text-[var(--muted)]" colSpan={8}>
                    {tCommon("loading")}
                  </td>
                </tr>
              ) : sorted.length === 0 ? (
                <tr>
                  <td className="px-3 py-4 text-[var(--muted)]" colSpan={8}>
                    {tableQuery ? tCommon("tableFilterEmpty") : t("empty")}
                  </td>
                </tr>
              ) : (
                visibleRows.map((row, idx) => (
                  <tr
                    key={`${row.country_code}-${row.currency}-${row.unit}-${idx}`}
                    className="border-b border-[var(--line)]"
                  >
                    <td className="px-3 py-2.5" style={{ fontFamily: "var(--mono)" }}>
                      {row.country_code}
                    </td>
                    <td className="px-3 py-2.5">{row.currency}</td>
                    <td className="px-3 py-2.5 text-[var(--muted)]">{row.unit}</td>
                    <td className="px-3 py-2.5 text-right">{row.sample_size}</td>
                    <td className="px-3 py-2.5 text-right">
                      {row.median == null ? "—" : Number(row.median).toFixed(1)}
                    </td>
                    <td className="px-3 py-2.5 text-right text-[var(--muted)]">
                      {row.p25 == null ? "—" : Number(row.p25).toFixed(1)}
                    </td>
                    <td className="px-3 py-2.5 text-right text-[var(--muted)]">
                      {row.p75 == null ? "—" : Number(row.p75).toFixed(1)}
                    </td>
                    <td className="px-3 py-2.5 text-[var(--muted)]">{row.status}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        {sorted.length > 0 ? (
          <ScrollLoadFooter
            hasMore={hasMore}
            isExpanded={isExpanded}
            onLoadMore={loadMore}
            onExpandAll={expandAll}
            onCollapse={collapse}
            shown={shown}
            total={listTotal}
          />
        ) : null}
      </section>
    </div>
  );
}

export function RatesDashboard() {
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
        <RatesDashboardInner />
      </LensToggle.Provider>
    </Suspense>
  );
}
