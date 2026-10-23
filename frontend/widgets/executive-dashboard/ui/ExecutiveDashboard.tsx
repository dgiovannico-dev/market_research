"use client";

import { Suspense, useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import {
  api,
  type DashboardSummary,
  type TechnologyTrendItem,
  type TechnologyTrends,
} from "@/lib/api";
import { useDashboardPrefs } from "@/features/dashboard-prefs";
import { useDashboardCountries } from "@/features/country-filter";
import {
  LensToggle,
  useDashboardLens,
} from "@/features/lens-toggle";
import { PeriodChip } from "@/features/dashboard-chrome";
import { MarketCoverageBanner } from "@/features/dashboard-chrome";
import {
  CoverageNotesList,
  resolveCoverageNotes,
} from "@/features/dashboard-chrome";
import { extractComparePoints } from "@/features/dashboard-chrome";
import { extractJobsPerDayPoints } from "@/features/dashboard-chrome";
import {
  CompareDualLazy,
  GeoStripLazy,
  RiseCoolChartLazy,
  SparklineLazy,
} from "@/shared/ui/charts";
import { ExecutiveMixCharts } from "./ExecutiveMixCharts";
import { Link } from "@/i18n/navigation";
import { formatDateMinute } from "@/shared/lib/formatDateTime";

function formatKpi(value: number, unit: string) {
  if (unit === "percent") return `${value.toFixed(1)}%`;
  return new Intl.NumberFormat("en").format(value);
}

function totalObservedN(summary: DashboardSummary | null, trends: TechnologyTrends | null): number | null {
  const kpis = summary?.kpis ?? summary?.market?.kpis;
  if (kpis?.length) {
    const jobs = kpis.find((k) => k.metric_name === "unique_jobs_observed");
    if (jobs) return jobs.sample_size;
  }
  const trendItems = trends?.items ?? trends?.market?.items;
  if (trendItems?.length) {
    return trendItems.reduce((s, it) => s + (it.sample_size || 0), 0);
  }
  return null;
}

/** Compare lens nests market/focus; data_quality may only live on those children. */
function resolveDataQuality(summary: DashboardSummary | null) {
  return (
    summary?.data_quality ??
    summary?.market?.data_quality ??
    summary?.focus?.data_quality ??
    null
  );
}

function ExecutiveDashboardInner() {
  const t = useTranslations("executive");
  const tCharts = useTranslations("charts");
  const tCompass = useTranslations("compass");
  const { prefs, hydrated } = useDashboardPrefs();
  const { lens, queryIds } = useDashboardLens();
  const { countries: countryCodes } = useDashboardCountries();
  const guided = prefs.view_mode === "guided";
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [trends, setTrends] = useState<TechnologyTrends | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loadingData, setLoadingData] = useState(false);
  const loadFailedMsg = t("loadFailed");

  useEffect(() => {
    if (!hydrated) return;
    let cancelled = false;
    const days = Math.min(prefs.period_days, 365);
    setError(null);
    setLoadingData(true);

    const lensOpts = { days, lens, queryIds, countries: countryCodes };
    Promise.all([api.summary(lensOpts), api.trends(lensOpts)])
      .then(([sum, tr]) => {
        if (!cancelled) {
          setSummary(sum);
          setTrends(tr);
          setLoadingData(false);
        }
      })
      .catch((e: unknown) => {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : loadFailedMsg);
          setLoadingData(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [hydrated, prefs.period_days, lens, queryIds, countryCodes, loadFailedMsg]);

  if (!hydrated) {
    return (
      <div className="rounded-xl border border-[var(--line)] bg-[var(--card)] p-6 text-sm text-[var(--muted)]">
        {t("loadingPrefs")}
      </div>
    );
  }

  if (error && !summary && !trends) {
    return (
      <div className="rounded-xl border border-[var(--line)] bg-[var(--card)] p-6">
        <h2 className="font-display text-lg font-semibold text-[var(--ink)]">
          {t("apiOfflineTitle")}
        </h2>
        <p className="mt-2 text-sm text-[var(--muted)]">{error}</p>
        <p className="mt-4 text-sm text-[var(--ink)]">{t("startBackend")}</p>
      </div>
    );
  }

  const periodDays =
    summary?.period_days ??
    summary?.market?.period_days ??
    trends?.period_days ??
    trends?.market?.period_days ??
    prefs.period_days;
  const n = totalObservedN(summary, trends);
  const dataQuality = resolveDataQuality(summary);
  const lastCrawl = dataQuality?.last_source_success_at
    ? formatDateMinute(dataQuality.last_source_success_at)
    : t("never");
  /**
   * Prefs `focus_technologies` is a personal stack highlight — not an API filter
   * on `/dashboard/summary` (unlike `focus_countries` → `country_code`).
   * Applying it as a hard client filter on market/compare blanks "Top technologies"
   * whenever the stack is outside the returned top-N (common with assistant/presets).
   * Only narrow rise/cool rows when the lens is already focus-scoped.
   */
  const techFocus = new Set(prefs.focus_technologies.map((x) => x.toLowerCase()));
  const narrowToTechFocus = lens === "focus" && techFocus.size > 0;
  /** Compare nests market/focus; guided UI may only find kpis on children. */
  const summaryKpis = summary?.kpis ?? summary?.market?.kpis ?? [];
  const growthStatus =
    summary?.growth_status ?? summary?.market?.growth_status ?? null;
  const summaryDisclaimer =
    summary?.disclaimer ?? summary?.market?.disclaimer ?? null;

  const rawTrendItems: TechnologyTrendItem[] =
    trends?.items ?? trends?.market?.items ?? [];
  const trendItems = narrowToTechFocus
    ? rawTrendItems.filter((item) => techFocus.has(item.technology.toLowerCase()))
    : rawTrendItems;
  const countries =
    summary?.top_countries ?? summary?.market?.top_countries ?? [];
  /** Always show API top techs for market/compare; never client-filter the list away. */
  const techs =
    summary?.top_technologies ?? summary?.market?.top_technologies ?? [];

  const compareFromSummary = extractComparePoints(summary);
  const comparePoints = compareFromSummary.length
    ? compareFromSummary
    : extractComparePoints(trends);
  const compareReady =
    comparePoints.length >= 2 &&
    comparePoints.some((p) => p.market != null) &&
    comparePoints.some((p) => p.focus != null);
  const sparkPoints = extractJobsPerDayPoints(summary);

  const modeLabel = guided ? t("modeGuided") : t("modeTrends");
  const lensLabel =
    lens === "focus"
      ? tCompass("lensFocus")
      : lens === "compare"
        ? tCompass("lensCompare")
        : tCompass("lensMarket");
  const statusLine =
    n != null
      ? t("statusLine", { days: periodDays, crawl: lastCrawl, mode: `${modeLabel} · ${lensLabel}`, n })
      : t("statusNoN", { days: periodDays, crawl: lastCrawl, mode: `${modeLabel} · ${lensLabel}` });
  const compareHint =
    lens === "compare" && summary
      ? t("compareCounts", {
          market: summary.market_n ?? 0,
          focus: summary.focus_n ?? 0,
          overlap: summary.overlap_n ?? 0,
        })
      : null;
  const coverageNotes = resolveCoverageNotes(summary);

  return (
    <div className="space-y-6">
      <section className="space-y-3">
        <div className="flex flex-wrap items-end justify-between gap-3">
          <div className="space-y-1">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] signal-text">
              {t("brandCompass")}
            </p>
            <p className="text-sm text-[var(--muted)]" style={{ fontFamily: "var(--mono)" }}>
              {statusLine}
            </p>
            {compareHint ? (
              <p className="text-xs text-[var(--muted)]" style={{ fontFamily: "var(--mono)" }}>
                {compareHint}
              </p>
            ) : null}
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <PeriodChip />
            <LensToggle.Control />
          </div>
        </div>
        {error ? <p className="text-xs text-[var(--warn)]">{t("partialLoad", { error })}</p> : null}
        <MarketCoverageBanner sampleSize={n} />
        <CoverageNotesList notes={coverageNotes} />
      </section>

      {lens === "compare" ? (
        compareReady ? (
          <CompareDualLazy
            points={comparePoints}
            periodDays={periodDays}
            sampleSize={n}
            title={tCharts("compareTitle")}
          />
        ) : (
          <div className="rounded-xl border border-[var(--line)] bg-[var(--card)] p-4 text-sm text-[var(--muted)]">
            {tCompass("compareUnavailable")}
          </div>
        )
      ) : (
        <RiseCoolChartLazy
          items={trendItems}
          periodDays={periodDays}
          sampleSize={n}
          title={tCharts("riseCoolTitle")}
        />
      )}

      <nav className="flex flex-wrap gap-2" aria-label={t("actionsAria")}>
        <Link
          href="/assistant"
          className="rounded-md bg-[var(--signal)] px-4 py-2 text-sm font-medium text-white transition-opacity hover:opacity-90"
        >
          {t("askBrief")}
        </Link>
        <Link
          href="/focus"
          className="rounded-md border border-[var(--line)] bg-[var(--card)] px-4 py-2 text-sm text-[var(--ink)] transition-colors hover:border-[var(--signal)] hover:text-[var(--signal)]"
        >
          {tCompass("myFocus")}
        </Link>
        <Link
          href={lens === "market" ? "/trends" : `/trends?lens=${lens}`}
          className="rounded-md border border-[var(--line)] bg-[var(--card)] px-4 py-2 text-sm text-[var(--ink)] transition-colors hover:border-[var(--signal)] hover:text-[var(--signal)]"
        >
          {t("openTrends")}
        </Link>
      </nav>

      <div className="grid gap-4 lg:grid-cols-2">
        <SparklineLazy
          points={sparkPoints}
          periodDays={periodDays}
          sampleSize={n}
          title={t("jobsDayTitle")}
          emptyMessage={tCharts("empty")}
        />
        <GeoStripLazy
          items={countries}
          periodDays={periodDays}
          title={t("whereDemand")}
        />
      </div>

      <ExecutiveMixCharts
        periodDays={periodDays}
        lens={lens}
        queryIds={queryIds}
        countries={countryCodes}
        techItems={techs}
        techSampleSize={n}
      />

      {guided ? (
        <details className="group overflow-hidden rounded-xl border border-[var(--line)] bg-[var(--card)]">
          <summary className="cursor-pointer list-none px-4 py-3 text-sm font-medium text-[var(--ink)] marker:content-none [&::-webkit-details-marker]:hidden">
            <span className="flex items-center justify-between gap-2">
              {t("methodology")}
              <span className="text-xs text-[var(--muted)] group-open:hidden">{t("show")}</span>
              <span className="hidden text-xs text-[var(--muted)] group-open:inline">{t("hide")}</span>
            </span>
          </summary>
          <div className="space-y-4 border-t border-[var(--line)] px-4 py-4">
            {summary ? (
              <>
                {summaryDisclaimer ? (
                  <p className="text-sm text-[var(--muted)]">{summaryDisclaimer}</p>
                ) : null}
                {growthStatus ? (
                  <p className="text-xs font-semibold uppercase tracking-[0.12em] rise-text">
                    {t("growthStatus", { status: growthStatus })}
                  </p>
                ) : null}
                <div className="grid gap-3 md:grid-cols-2">
                  {summaryKpis.map((kpi) => (
                    <article
                      key={kpi.metric_name}
                      className="rounded-lg border border-[var(--line)] p-3"
                      style={{
                        background: "color-mix(in srgb, var(--paper) 45%, transparent)",
                      }}
                    >
                      <p className="text-xs uppercase tracking-[0.12em] text-[var(--muted)]">
                        {kpi.metric_name}
                      </p>
                      <p
                        className="mt-1 text-2xl font-semibold tracking-tight text-[var(--ink)]"
                        style={{ fontFamily: "var(--mono)" }}
                      >
                        {formatKpi(kpi.metric_value, kpi.unit)}
                      </p>
                      <p className="mt-2 text-sm text-[var(--muted)]">{kpi.definition}</p>
                      <div className="mt-2 flex flex-wrap gap-2">
                        <span className="badge" style={{ fontFamily: "var(--mono)" }}>
                          {t("sampleN", { n: kpi.sample_size })}
                        </span>
                        <span className="badge">{kpi.evidence_kind}</span>
                      </div>
                      <p className="mt-2 text-xs text-[var(--muted)]">
                        {t("limits", { limits: kpi.limits })}
                      </p>
                    </article>
                  ))}
                </div>
                {dataQuality ? (
                  <p className="text-xs text-[var(--muted)]" style={{ fontFamily: "var(--mono)" }}>
                    {t("sourcesEnabled", {
                      enabled: dataQuality.sources_enabled,
                      total: dataQuality.sources_total,
                      lastSuccess: lastCrawl,
                    })}
                  </p>
                ) : null}
              </>
            ) : (
              <p className="text-sm text-[var(--muted)]">{t("summaryLoading")}</p>
            )}
          </div>
        </details>
      ) : (
        <p className="text-xs text-[var(--muted)]" style={{ fontFamily: "var(--mono)" }}>
          {t("trendsOnlyHint")}
        </p>
      )}

      <section className="grid gap-4 md:grid-cols-2">
        <article className="rounded-xl border border-[var(--line)] bg-[var(--card)] p-4">
          <h2 className="font-display text-base font-semibold tracking-tight text-[var(--ink)]">
            {t("topTechnologies")}
          </h2>
          <ul className="mt-3 space-y-0 text-sm">
            {loadingData && techs.length === 0 ? (
              <li className="text-[var(--muted)]">{t("summaryLoading")}</li>
            ) : techs.length === 0 ? (
              <li className="text-[var(--muted)]">{t("noTechnologies")}</li>
            ) : (
              techs.map((item) => (
                <li
                  key={item.technology}
                  className="flex justify-between border-b border-[var(--line)] py-2 last:border-b-0"
                >
                  <Link
                    href={`/explorer?technology=${encodeURIComponent(item.technology)}`}
                    className="text-[var(--ink)] hover:text-[var(--signal)]"
                  >
                    {item.technology}
                  </Link>
                  <span className="text-[var(--muted)]" style={{ fontFamily: "var(--mono)" }}>
                    {item.job_skill_mentions}
                  </span>
                </li>
              ))
            )}
          </ul>
        </article>
        <article className="rounded-xl border border-[var(--line)] bg-[var(--card)] p-4">
          <h2 className="font-display text-base font-semibold tracking-tight text-[var(--ink)]">
            {t("topCountries")}
          </h2>
          <ul className="mt-3 space-y-0 text-sm">
            {loadingData && countries.length === 0 ? (
              <li className="text-[var(--muted)]">{t("summaryLoading")}</li>
            ) : countries.length === 0 ? (
              <li className="text-[var(--muted)]">{t("noCountries")}</li>
            ) : (
              countries.map((c) => (
                <li
                  key={c.country_code}
                  className="flex justify-between border-b border-[var(--line)] py-2 last:border-b-0"
                >
                  <span className="text-[var(--ink)]" style={{ fontFamily: "var(--mono)" }}>
                    {c.country_code}
                  </span>
                  <span className="text-[var(--muted)]" style={{ fontFamily: "var(--mono)" }}>
                    {c.jobs}
                  </span>
                </li>
              ))
            )}
          </ul>
        </article>
      </section>
    </div>
  );
}

export function ExecutiveDashboard() {
  const t = useTranslations("executive");
  return (
    <Suspense
      fallback={
        <div className="rounded-xl border border-[var(--line)] bg-[var(--card)] p-6 text-sm text-[var(--muted)]">
          {t("loadingPrefs")}
        </div>
      }
    >
      <LensToggle.Provider>
        <ExecutiveDashboardInner />
      </LensToggle.Provider>
    </Suspense>
  );
}
