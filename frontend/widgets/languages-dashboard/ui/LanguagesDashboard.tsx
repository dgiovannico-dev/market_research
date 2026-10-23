"use client";

import { Suspense, useMemo } from "react";
import { useTranslations } from "next-intl";
import { RankBarsLazy } from "@/shared/ui/charts";
import { MetricLegend } from "@/shared/ui/MetricLegend";
import { ScrollLoadFooter } from "@/shared/ui/ScrollLoadFooter";
import { SortableTh } from "@/shared/ui/SortableTh";
import { TableGuide } from "@/shared/ui/TableGuide";
import { TableSearch } from "@/shared/ui/TableSearch";
import { useDashboardLensQuery } from "@/features/dashboard-query";
import { api, type MarketLanguages } from "@/lib/api";
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

function LanguagesDashboardInner() {
  const t = useTranslations("languages");
  const tCharts = useTranslations("charts");
  const tCommon = useTranslations("common");
  const tCompass = useTranslations("compass");
  const { prefs, hydrated } = useDashboardPrefs();
  const { lens, queryIds } = useDashboardLens();
  const { countries } = useDashboardCountries();
  const loadFailedMsg = t("loadFailed");
  const { data, error, isStale } = useDashboardLensQuery<MarketLanguages>({
    hydrated,
    days: Math.min(prefs.period_days, 365),
    lens,
    queryIds,
    countries,
    fallbackError: loadFailedMsg,
    fetcher: (ctx) =>
      api.languages({
        days: ctx.days,
        lens: ctx.lens,
        queryIds: ctx.queryIds,
        countries: ctx.countries,
        limit: 50,
      }),
  });

  const body =
    data?.lens === "compare" ? (data.market ?? null) : data;
  const items = body?.items ?? [];
  const rankItems = items.map((it) => ({
    label: it.language,
    value: it.jobs,
  }));

  const {
    query: tableQuery,
    setQuery: setTableQuery,
    filtered: filteredItems,
  } = useClientTableFilter(items, (r) =>
    joinSearchParts(r.language, r.jobs, r.share),
  );
  const { sorted, sortKey, order, toggle } = useClientTableSort(
    filteredItems,
    {
      language: (r) => r.language,
      jobs: (r) => r.jobs,
      share: (r) => r.share ?? 0,
    },
    "jobs",
    "desc",
  );
  const {
    visible: visibleRows,
    hasMore,
    loadMore,
    shown,
    total: listTotal,
  } = useClientPageWindow(
    sorted,
    30,
    `${tableQuery}|${sortKey}|${order}|${sorted.length}|${lens}`,
  );

  const legend = useMemo(
    () => [
      { term: t("colLanguage"), definition: t("hintLanguage") },
      { term: t("colJobs"), definition: t("hintJobs") },
      { term: t("colShare"), definition: t("hintShare") },
      { term: t("termCoverage"), definition: t("hintCoverage") },
    ],
    [t],
  );

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
      className="space-y-4"
      style={isStale ? { opacity: 0.72 } : undefined}
    >
      <section className="space-y-3 rounded-xl border border-[var(--line)] bg-[var(--card)] p-4">
        <div className="flex flex-wrap items-end justify-between gap-3">
          <div className="space-y-1">
            <h2 className="font-display text-2xl font-semibold tracking-tight text-[var(--ink)]">
              {t("title")}
            </h2>
            <p className="max-w-2xl text-sm text-[var(--muted)]">
              {body?.disclaimer ?? t("subtitle", { days: prefs.period_days })}
            </p>
            <p className="text-xs text-[var(--muted)]" style={{ fontFamily: "var(--mono)" }}>
              {body
                ? t("coverageLine", {
                    pct: ((body.coverage_pct ?? 0) * 100).toFixed(1),
                    withLang: body.jobs_with_language_requirements ?? 0,
                    n: body.sample_size ?? 0,
                  })
                : error
                  ? null
                  : tCommon("loading")}
            </p>
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
        </div>
        <MarketCoverageBanner sampleSize={body?.sample_size ?? null} />
        <MetricLegend title={tCommon("metricLegendTitle")} items={legend} />
      </section>

      {error ? (
        <div className="rounded-xl border border-[var(--warn)]/40 bg-[var(--card)] p-4 text-sm text-[var(--warn)]">
          {error}
        </div>
      ) : null}

      <RankBarsLazy
        items={rankItems}
        periodDays={body?.period_days ?? prefs.period_days}
        sampleSize={body?.sample_size ?? null}
        title={tCharts("langRankTitle")}
      />

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
                <SortableTh
                  label={t("colLanguage")}
                  sortKey="language"
                  activeSort={sortKey}
                  order={order}
                  onSort={toggle}
                  ariaLabel={tCommon("sortBy", { column: t("colLanguage") })}
                />
                <SortableTh
                  label={t("colJobs")}
                  sortKey="jobs"
                  activeSort={sortKey}
                  order={order}
                  onSort={toggle}
                  ariaLabel={tCommon("sortBy", { column: t("colJobs") })}
                  align="right"
                />
                <SortableTh
                  label={t("colShare")}
                  sortKey="share"
                  activeSort={sortKey}
                  order={order}
                  onSort={toggle}
                  ariaLabel={tCommon("sortBy", { column: t("colShare") })}
                  align="right"
                />
              </tr>
            </thead>
            <tbody>
              {!data && !error ? (
                <tr>
                  <td className="px-3 py-4 text-[var(--muted)]" colSpan={3}>
                    {tCommon("loading")}
                  </td>
                </tr>
              ) : sorted.length === 0 ? (
                <tr>
                  <td className="px-3 py-4 text-[var(--muted)]" colSpan={3}>
                    {tableQuery ? tCommon("tableFilterEmpty") : t("empty")}
                  </td>
                </tr>
              ) : (
                visibleRows.map((row) => (
                  <tr key={row.language} className="border-b border-[var(--line)]">
                    <td className="px-3 py-2.5" style={{ fontFamily: "var(--mono)" }}>
                      {row.language}
                    </td>
                    <td className="px-3 py-2.5 text-right" style={{ fontFamily: "var(--mono)" }}>
                      {row.jobs}
                    </td>
                    <td className="px-3 py-2.5 text-right" style={{ fontFamily: "var(--mono)" }}>
                      {((row.share ?? 0) * 100).toFixed(1)}%
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        {sorted.length > 0 ? (
          <ScrollLoadFooter
            hasMore={hasMore}
            onLoadMore={loadMore}
            shown={shown}
            total={listTotal}
          />
        ) : null}
      </section>
    </div>
  );
}

export function LanguagesDashboard() {
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
        <LanguagesDashboardInner />
      </LensToggle.Provider>
    </Suspense>
  );
}
