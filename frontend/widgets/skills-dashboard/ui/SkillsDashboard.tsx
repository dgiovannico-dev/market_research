"use client";

import { Suspense, useMemo } from "react";
import { useTranslations } from "next-intl";
import { TaxonomySearchPanel } from "./TaxonomySearchPanel";
import { MetricLegend } from "@/shared/ui/MetricLegend";
import { ScrollLoadFooter } from "@/shared/ui/ScrollLoadFooter";
import { SortableTh } from "@/shared/ui/SortableTh";
import { TableGuide } from "@/shared/ui/TableGuide";
import { TableSearch } from "@/shared/ui/TableSearch";
import { useDashboardLensQuery } from "@/features/dashboard-query";
import { useClientPageWindow } from "@/shared/hooks/useClientPageWindow";
import { useClientTableFilter } from "@/shared/hooks/useClientTableFilter";
import { api } from "@/lib/api";
import { joinSearchParts } from "@/shared/lib/tableFilter";
import { useDashboardPrefs } from "@/features/dashboard-prefs";
import { useDashboardCountries } from "@/features/country-filter";
import {
  LensToggle,
  useDashboardLens,
} from "@/features/lens-toggle";
import { MarketCoverageBanner } from "@/features/dashboard-chrome";
import { useClientTableSort } from "@/shared/hooks/useClientTableSort";

type Pair = {
  tech_a: string;
  tech_b: string;
  support: number;
  lift: number | null;
  jaccard: number | null;
  freq_a: number;
  freq_b: number;
  limits?: string;
};

type CooccurrencePayload = {
  jobs_analyzed: number;
  period_days: number;
  items: Pair[];
  market_n?: number;
  focus_n?: number;
  overlap_n?: number;
  min_evidence?: string;
  excluded_thin_n?: number;
};

const theadClass =
  "border-b border-[var(--line)] text-[0.65rem] font-semibold uppercase tracking-[0.12em] text-[var(--muted)]";
const theadStyle = {
  background: "color-mix(in srgb, var(--paper) 85%, var(--card))",
};

function SkillsDashboardInner() {
  const t = useTranslations("skills");
  const tCommon = useTranslations("common");
  const tCompass = useTranslations("compass");
  const { prefs, hydrated } = useDashboardPrefs();
  const { lens, queryIds } = useDashboardLens();
  const { countries } = useDashboardCountries();
  const loadFailedMsg = t("loadFailed");
  const periodDays = prefs.period_days;
  const { data, error, isStale } = useDashboardLensQuery<CooccurrencePayload>({
    hydrated,
    days: Math.min(Math.max(periodDays, 7), 365),
    lens,
    queryIds,
    countries,
    fallbackError: loadFailedMsg,
    fetcher: async (ctx) => {
      const res = await api.cooccurrence({
        days: ctx.days,
        minSupport: 2,
        lens: ctx.lens,
        queryIds: ctx.queryIds,
        countries: ctx.countries,
      });
      return {
        jobs_analyzed: res.jobs_analyzed ?? 0,
        period_days: res.period_days ?? periodDays,
        items: (res.items ?? []) as Pair[],
        market_n: res.market_n,
        focus_n: res.focus_n,
        overlap_n: res.overlap_n,
        min_evidence: res.min_evidence,
        excluded_thin_n: res.excluded_thin_n,
      };
    },
  });

  const items = data?.items ?? [];
  const columnLegend = useMemo(
    () => [
      { term: t("colTechA"), definition: t("hintTechA") },
      { term: t("colTechB"), definition: t("hintTechB") },
      { term: t("colSupport"), definition: t("hintSupport") },
      { term: t("colLift"), definition: t("hintLift") },
      { term: t("colJaccard"), definition: t("hintJaccard") },
    ],
    [t],
  );
  const {
    query: tableQuery,
    setQuery: setTableQuery,
    filtered: filteredItems,
  } = useClientTableFilter(items, (r) =>
    joinSearchParts(r.tech_a, r.tech_b, r.support, r.lift, r.jaccard),
  );
  const { sorted, sortKey, order, toggle } = useClientTableSort(
    filteredItems,
    {
      tech_a: (r) => r.tech_a,
      tech_b: (r) => r.tech_b,
      support: (r) => r.support,
      lift: (r) => r.lift,
      jaccard: (r) => r.jaccard,
    },
    "support",
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
          <p className="max-w-2xl text-sm text-[var(--muted)]">{t("subtitle")}</p>
          <p className="text-xs text-[var(--muted)]" style={{ fontFamily: "var(--mono)" }}>
            {data
              ? t("jobsAnalyzed", {
                  n: data.jobs_analyzed ?? 0,
                  days: data.period_days ?? prefs.period_days,
                })
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

      <MarketCoverageBanner sampleSize={data ? data.jobs_analyzed : null} />

      <MetricLegend title={tCommon("metricLegendTitle")} items={columnLegend} />

      <TaxonomySearchPanel />

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
          <table className="min-w-[640px] w-full text-left text-sm text-[var(--ink)]">
            <thead className={theadClass} style={theadStyle}>
              <tr>
                <SortableTh label={t("colTechA")} sortKey="tech_a" activeSort={sortKey} order={order} onSort={toggle} ariaLabel={tCommon("sortBy", { column: t("colTechA") })} hint={t("hintTechA")} />
                <SortableTh label={t("colTechB")} sortKey="tech_b" activeSort={sortKey} order={order} onSort={toggle} ariaLabel={tCommon("sortBy", { column: t("colTechB") })} hint={t("hintTechB")} />
                <SortableTh label={t("colSupport")} sortKey="support" activeSort={sortKey} order={order} onSort={toggle} ariaLabel={tCommon("sortBy", { column: t("colSupport") })} hint={t("hintSupport")} />
                <SortableTh label={t("colLift")} sortKey="lift" activeSort={sortKey} order={order} onSort={toggle} ariaLabel={tCommon("sortBy", { column: t("colLift") })} hint={t("hintLift")} />
                <SortableTh label={t("colJaccard")} sortKey="jaccard" activeSort={sortKey} order={order} onSort={toggle} ariaLabel={tCommon("sortBy", { column: t("colJaccard") })} hint={t("hintJaccard")} />
              </tr>
            </thead>
            <tbody>
              {!data && !error ? (
                <tr>
                  <td colSpan={5} className="px-3 py-6 text-sm text-[var(--muted)]">
                    {tCommon("loading")}
                  </td>
                </tr>
              ) : sorted.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-3 py-6 text-sm text-[var(--muted)]">
                    {tableQuery ? tCommon("tableFilterEmpty") : t("empty")}
                  </td>
                </tr>
              ) : (
                visibleRows.map((row) => (
                  <tr
                    key={`${row.tech_a}-${row.tech_b}`}
                    className="border-b border-[var(--line)]"
                  >
                    <td className="px-3 py-2.5 font-medium">{row.tech_a}</td>
                    <td className="px-3 py-2.5 font-medium">{row.tech_b}</td>
                    <td className="px-3 py-2.5" style={{ fontFamily: "var(--mono)" }}>
                      {row.support}
                    </td>
                    <td className="px-3 py-2.5 text-[var(--muted)]">
                      {row.lift ?? "—"}
                    </td>
                    <td className="px-3 py-2.5 text-[var(--muted)]">
                      {row.jaccard ?? "—"}
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

export function SkillsDashboard() {
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
        <SkillsDashboardInner />
      </LensToggle.Provider>
    </Suspense>
  );
}
