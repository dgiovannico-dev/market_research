"use client";

import { Suspense, useMemo } from "react";
import { useTranslations } from "next-intl";
import { useDashboardLensQuery } from "@/features/dashboard-query";
import { api, type CountryComparison, type CountryComparisonItem } from "@/lib/api";
import { useDashboardPrefs } from "@/features/dashboard-prefs";
import { useDashboardCountries } from "@/features/country-filter";
import {
  LensToggle,
  useDashboardLens,
} from "@/features/lens-toggle";
import { MarketCoverageBanner } from "@/features/dashboard-chrome";
import {
  CoverageNotesList,
  resolveCoverageNotes,
} from "@/features/dashboard-chrome";
import { MetricLegend } from "@/shared/ui/MetricLegend";
import { ScrollLoadFooter } from "@/shared/ui/ScrollLoadFooter";
import { SortableTh } from "@/shared/ui/SortableTh";
import { TableGuide } from "@/shared/ui/TableGuide";
import { TableSearch } from "@/shared/ui/TableSearch";
import { GeoWorldMapLazy } from "@/shared/ui/charts";
import { useClientPageWindow } from "@/shared/hooks/useClientPageWindow";
import { useClientTableFilter } from "@/shared/hooks/useClientTableFilter";
import { useClientTableSort } from "@/shared/hooks/useClientTableSort";
import { joinSearchParts } from "@/shared/lib/tableFilter";

type CountriesBundle = {
  table: CountryComparison;
  map: CountryComparison;
};

const theadClass =
  "border-b border-[var(--line)] text-[0.65rem] font-semibold uppercase tracking-[0.12em] text-[var(--muted)]";
const theadStyle = {
  background: "color-mix(in srgb, var(--paper) 85%, var(--card))",
} as const;

function CountriesTable({ items }: { items: CountryComparisonItem[] }) {
  const t = useTranslations("countries");
  const tCommon = useTranslations("common");
  const {
    query: tableQuery,
    setQuery: setTableQuery,
    filtered,
  } = useClientTableFilter(items, (c) =>
    joinSearchParts(
      c.country_code,
      c.jobs_observed,
      c.remote_share,
      c.b2b_freelance_share,
      c.explicitly_allowed_residence,
      c.explicitly_restricted_residence,
      ...(c.top_technologies ?? []).map((tech) => tech.name),
    ),
  );
  const { sorted, sortKey, order, toggle } = useClientTableSort(
    filtered,
    {
      country: (c) => c.country_code,
      jobs: (c) => c.jobs_observed,
      remote: (c) => Number(c.remote_share) || 0,
      b2b: (c) => Number(c.b2b_freelance_share) || 0,
      tech: (c) =>
        (c.top_technologies ?? [])
          .map((tech) => tech.name)
          .join(" "),
    },
    "jobs",
    "desc",
  );
  const page = useClientPageWindow(
    sorted,
    30,
    `${tableQuery}|${sortKey}|${order}|${sorted.length}`,
  );

  return (
    <div className="space-y-3">
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
                label={t("colCountry")}
                sortKey="country"
                activeSort={sortKey}
                order={order}
                onSort={toggle}
                ariaLabel={tCommon("sortBy", { column: t("colCountry") })}
                hint={t("hintJobsObserved")}
              />
              <SortableTh
                label={t("termJobsObserved")}
                sortKey="jobs"
                activeSort={sortKey}
                order={order}
                onSort={toggle}
                ariaLabel={tCommon("sortBy", { column: t("termJobsObserved") })}
                align="right"
                hint={t("hintJobsObserved")}
              />
              <SortableTh
                label={t("termRemoteShare")}
                sortKey="remote"
                activeSort={sortKey}
                order={order}
                onSort={toggle}
                ariaLabel={tCommon("sortBy", { column: t("termRemoteShare") })}
                align="right"
                hint={t("hintRemoteShare")}
              />
              <SortableTh
                label={t("termB2bShare")}
                sortKey="b2b"
                activeSort={sortKey}
                order={order}
                onSort={toggle}
                ariaLabel={tCommon("sortBy", { column: t("termB2bShare") })}
                align="right"
                hint={t("hintB2bShare")}
              />
              <SortableTh
                label={t("termTopTech")}
                sortKey="tech"
                activeSort={sortKey}
                order={order}
                onSort={toggle}
                ariaLabel={tCommon("sortBy", { column: t("termTopTech") })}
                hint={t("hintTopTech")}
              />
            </tr>
          </thead>
          <tbody>
            {sorted.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-3 py-4 text-sm text-[var(--muted)]">
                  {tableQuery ? tCommon("tableFilterEmpty") : t("empty")}
                </td>
              </tr>
            ) : (
              page.visible.map((c) => (
                <tr
                  key={c.country_code}
                  className="border-b border-[var(--line)] align-top"
                >
                  <td
                    className="px-3 py-2.5 font-semibold"
                    style={{ fontFamily: "var(--mono)" }}
                  >
                    {c.country_code}
                  </td>
                  <td
                    className="px-3 py-2.5 text-right"
                    style={{ fontFamily: "var(--mono)" }}
                  >
                    {c.jobs_observed}
                  </td>
                  <td
                    className="px-3 py-2.5 text-right text-[var(--muted)]"
                    style={{ fontFamily: "var(--mono)" }}
                  >
                    {(Number(c.remote_share) * 100).toFixed(1)}%
                  </td>
                  <td
                    className="px-3 py-2.5 text-right text-[var(--muted)]"
                    style={{ fontFamily: "var(--mono)" }}
                  >
                    {(Number(c.b2b_freelance_share) * 100).toFixed(1)}%
                  </td>
                  <td className="px-3 py-2.5 text-xs text-[var(--muted)]">
                    {(c.top_technologies ?? [])
                      .map((tech) => `${tech.name}(${tech.mentions})`)
                      .join(", ") || "—"}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
      {sorted.length > 0 ? (
        <ScrollLoadFooter
          hasMore={page.hasMore}
          onLoadMore={page.loadMore}
          shown={page.shown}
          total={page.total}
        />
      ) : null}
    </section>
    </div>
  );
}

function CountriesDashboardInner() {
  const t = useTranslations("countries");
  const tCommon = useTranslations("common");
  const tCompass = useTranslations("compass");
  const { prefs, hydrated } = useDashboardPrefs();
  const { lens, queryIds } = useDashboardLens();
  const { countries: countryCodes } = useDashboardCountries();
  const loadFailedMsg = t("loadFailed");
  const metricLegend = useMemo(
    () => [
      { term: t("termJobsObserved"), definition: t("hintJobsObserved") },
      { term: t("termRemoteShare"), definition: t("hintRemoteShare") },
      { term: t("termB2bShare"), definition: t("hintB2bShare") },
      { term: t("termResidence"), definition: t("hintResidence") },
      { term: t("termTopTech"), definition: t("hintTopTech") },
    ],
    [t],
  );
  const { data: bundle, error, isStale } = useDashboardLensQuery<CountriesBundle>({
    hydrated,
    days: Math.min(prefs.period_days, 365),
    lens,
    queryIds,
    countries: countryCodes,
    fallbackError: loadFailedMsg,
    fetcher: async (ctx) => {
      const opts = {
        days: ctx.days,
        lens: ctx.lens,
        queryIds: ctx.queryIds,
        countries: ctx.countries,
      };
      const [table, map] = await Promise.all([
        api.countries(opts),
        api.countries({ ...opts, forMap: true }),
      ]);
      return { table, map };
    },
  });
  const data = bundle?.table ?? null;
  const mapData = bundle?.map ?? null;

  const sampleSize =
    data?.items?.reduce((s, it) => s + (it.jobs_observed || 0), 0) ??
    (typeof data?.market_n === "number" ? data.market_n : null);

  const compareReady =
    lens === "compare" &&
    Boolean(data?.market?.items?.length || data?.focus?.items?.length) &&
    (data?.focus_n ?? 0) > 0;

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
              {data?.disclaimer ??
                data?.market?.disclaimer ??
                t("subtitle", { days: prefs.period_days })}
            </p>
            <p className="mt-2 text-xs text-[var(--warn)]">{t("legalNote")}</p>
          </div>
          <LensToggle.Control />
        </div>
        <MarketCoverageBanner sampleSize={data ? sampleSize : null} />
        <MetricLegend title={tCommon("metricLegendTitle")} items={metricLegend} />
        <CoverageNotesList notes={resolveCoverageNotes(data)} />
      </section>

      {error ? (
        <div className="rounded-xl border border-[var(--warn)]/40 bg-[var(--card)] p-4 text-sm text-[var(--warn)]">
          {error}
        </div>
      ) : null}

      {lens !== "compare" ? (
        <GeoWorldMapLazy
          items={
            mapData?.map_items ??
            (data?.items ?? []).map((c) => ({
              country_code: c.country_code,
              jobs: c.jobs_observed,
            }))
          }
          unknownJobs={mapData?.unknown_jobs ?? 0}
          periodDays={prefs.period_days}
          sampleSize={sampleSize}
          title={t("worldMapTitle")}
        />
      ) : null}

      {!data && !error ? (
        <p className="rounded-xl border border-[var(--line)] bg-[var(--card)] p-4 text-sm text-[var(--muted)]">
          {tCommon("loading")}
        </p>
      ) : lens === "compare" ? (
        compareReady ? (
          <div className="space-y-6">
            <div className="space-y-2">
              <h3 className="text-[0.65rem] font-semibold uppercase tracking-[0.12em] text-[var(--muted)]">
                {tCompass("lensMarket")}
                {data?.market_n != null ? ` · n=${data.market_n}` : ""}
              </h3>
              <CountriesTable items={data?.market?.items ?? []} />
            </div>
            <div className="space-y-2">
              <h3 className="text-[0.65rem] font-semibold uppercase tracking-[0.12em] text-[var(--muted)]">
                {tCompass("lensFocus")}
                {data?.focus_n != null ? ` · n=${data.focus_n}` : ""}
              </h3>
              <CountriesTable items={data?.focus?.items ?? []} />
            </div>
          </div>
        ) : (
          <div className="rounded-xl border border-[var(--line)] bg-[var(--card)] p-4 text-sm text-[var(--muted)]">
            {tCompass("compareUnavailable")}
          </div>
        )
      ) : (
        <CountriesTable items={data?.items ?? []} />
      )}
    </div>
  );
}

export function CountriesDashboard() {
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
        <CountriesDashboardInner />
      </LensToggle.Provider>
    </Suspense>
  );
}
