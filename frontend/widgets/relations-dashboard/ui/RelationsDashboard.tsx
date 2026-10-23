"use client";

import { Suspense, startTransition, useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import { usePathname, useRouter } from "@/i18n/navigation";
import { useTranslations } from "next-intl";
import {
  api,
  type LanguageCountryMatrix,
  type MarketSeriesPayload,
  type RoleTechMatrix,
  type SeniorityTechMatrix,
  type TechCountryMatrix,
} from "@/lib/api";
import { useDashboardPrefs } from "@/features/dashboard-prefs";
import { useDashboardCountries } from "@/features/country-filter";
import {
  LensToggle,
  useDashboardLens,
} from "@/features/lens-toggle";
import { PeriodChip } from "@/features/dashboard-chrome";
import {
  buildCooccurrenceHeat,
  languageCountryCellsToHeat,
  roleTechCellsToHeat,
  seniorityTechCellsToHeat,
  techCountryCellsToHeat,
  type CooccurrencePairLike,
} from "./cooccurrenceHeat";
import { RelationsHeatmapsPanel } from "./RelationsHeatmapsPanel";
import { RelationsSeriesPanel } from "./RelationsSeriesPanel";
import {
  RelationsViewTabs,
  type RelationsView,
} from "./RelationsViewTabs";

type CooccurrencePayload = {
  jobs_analyzed: number;
  period_days: number;
  items: CooccurrencePairLike[];
  excluded_thin_n?: number;
};

const COOC_TOP_N = 12;
const DEFAULT_VIEW: RelationsView = "heat";

function parseRelationsView(raw: string | null): RelationsView {
  return raw === "series" ? "series" : DEFAULT_VIEW;
}

function writeRelationsViewToUrl(
  pathname: string,
  searchParams: URLSearchParams,
  router: ReturnType<typeof useRouter>,
  next: RelationsView,
) {
  const params = new URLSearchParams(searchParams.toString());
  if (next === DEFAULT_VIEW) params.delete("view");
  else params.set("view", next);
  const qs = params.toString();
  startTransition(() => {
    router.replace(qs ? `${pathname}?${qs}` : pathname, { scroll: false });
  });
}

function RelationsDashboardInner() {
  const t = useTranslations("relations");
  const { prefs, hydrated } = useDashboardPrefs();
  const { lens, queryIds } = useDashboardLens();
  const { countries } = useDashboardCountries();
  const guided = prefs.view_mode === "guided";
  const searchParams = useSearchParams();
  const pathname = usePathname();
  const router = useRouter();

  const viewFromUrl = parseRelationsView(searchParams.get("view"));
  const [view, setViewState] = useState<RelationsView>(viewFromUrl);

  useEffect(() => {
    setViewState(viewFromUrl);
  }, [viewFromUrl]);

  const setView = (next: RelationsView) => {
    setViewState(next);
    writeRelationsViewToUrl(pathname, searchParams, router, next);
  };
  const [cooc, setCooc] = useState<CooccurrencePayload | null>(null);
  const [matrix, setMatrix] = useState<TechCountryMatrix | null>(null);
  const [langMatrix, setLangMatrix] = useState<LanguageCountryMatrix | null>(
    null,
  );
  const [roleTech, setRoleTech] = useState<RoleTechMatrix | null>(null);
  const [seniorityTech, setSeniorityTech] =
    useState<SeniorityTechMatrix | null>(null);
  const [techSeries, setTechSeries] = useState<MarketSeriesPayload | null>(null);
  const [countrySeries, setCountrySeries] =
    useState<MarketSeriesPayload | null>(null);
  const [ratesSeries, setRatesSeries] = useState<MarketSeriesPayload | null>(
    null,
  );
  const [error, setError] = useState<string | null>(null);
  const loadFailedMsg = t("loadFailed");

  useEffect(() => {
    if (!hydrated) return;
    let cancelled = false;
    const days = Math.min(Math.max(prefs.period_days, 7), 365);
    const lensOpts = { days, lens, queryIds, countries };

    Promise.all([
      api.cooccurrence({ ...lensOpts, minSupport: 2 }).catch(() => null),
      api
        .matrixTechCountry({ ...lensOpts, topTech: 12, topCountry: 10 })
        .catch(() => null),
      api.seriesTechnologies({ ...lensOpts, top: 8 }).catch(() => null),
      api.seriesCountries({ ...lensOpts, top: 8 }).catch(() => null),
    ]).then(([coocRes, matrixRes, techRes, countryRes]) => {
      if (cancelled) return;
      if (!coocRes && !matrixRes && !techRes && !countryRes) {
        setError(loadFailedMsg);
        return;
      }
      if (coocRes) {
        setCooc({
          jobs_analyzed: coocRes.jobs_analyzed ?? 0,
          period_days: coocRes.period_days ?? days,
          items: (coocRes.items ?? []) as CooccurrencePairLike[],
          excluded_thin_n: coocRes.excluded_thin_n,
        });
      }
      if (matrixRes) setMatrix(matrixRes);
      if (techRes) setTechSeries(techRes);
      if (countryRes) setCountrySeries(countryRes);
      setError(null);
    });

    // Soft-fail wave-3/4/5 endpoints so core charts stay up if any 404.
    Promise.all([
      api
        .matrixLanguageCountry({ ...lensOpts, topLang: 12, topCountry: 10 })
        .catch(() => null),
      api.seriesRates({ ...lensOpts, top: 8 }).catch(() => null),
      api
        .matrixRoleTech({ ...lensOpts, topRole: 12, topTech: 12 })
        .catch(() => null),
      api
        .matrixSeniorityTech({ ...lensOpts, topSeniority: 8, topTech: 12 })
        .catch(() => null),
    ]).then(([langRes, ratesRes, roleRes, seniorityRes]) => {
      if (cancelled) return;
      setLangMatrix(langRes);
      setRatesSeries(ratesRes);
      setRoleTech(roleRes);
      setSeniorityTech(seniorityRes);
    });

    return () => {
      cancelled = true;
    };
  }, [hydrated, prefs.period_days, lens, queryIds, countries, loadFailedMsg]);

  const techHeat = useMemo(
    () => buildCooccurrenceHeat(cooc?.items ?? [], COOC_TOP_N),
    [cooc],
  );

  const countryHeatValues = useMemo(
    () =>
      matrix
        ? techCountryCellsToHeat(
            matrix.technologies ?? [],
            matrix.countries ?? [],
            matrix.cells ?? [],
          )
        : [],
    [matrix],
  );

  const langCountryHeatValues = useMemo(
    () =>
      langMatrix
        ? languageCountryCellsToHeat(
            langMatrix.languages ?? [],
            langMatrix.countries ?? [],
            langMatrix.cells ?? [],
          )
        : [],
    [langMatrix],
  );

  const roleTechHeatValues = useMemo(
    () =>
      roleTech
        ? roleTechCellsToHeat(
            roleTech.role_families ?? [],
            roleTech.technologies ?? [],
            roleTech.cells ?? [],
          )
        : [],
    [roleTech],
  );

  const seniorityTechHeatValues = useMemo(
    () =>
      seniorityTech
        ? seniorityTechCellsToHeat(
            seniorityTech.seniorities ?? [],
            seniorityTech.technologies ?? [],
            seniorityTech.cells ?? [],
          )
        : [],
    [seniorityTech],
  );

  const periodDays =
    matrix?.period_days ??
    techSeries?.period_days ??
    cooc?.period_days ??
    prefs.period_days;

  return (
    <div className="space-y-5">
      <header className="flex flex-wrap items-end justify-between gap-3">
        <div className="space-y-1">
          <h2 className="font-display text-2xl font-semibold tracking-tight text-[var(--ink)]">
            {t("title")}
          </h2>
          <p className="max-w-2xl text-sm text-[var(--muted)]">
            {guided
              ? t("subtitleGuided", { days: prefs.period_days })
              : t("subtitle", { days: prefs.period_days })}
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <PeriodChip />
          <LensToggle.Control />
        </div>
      </header>

      {guided ? (
        <p className="rounded-xl border border-[var(--line)] bg-[var(--card)] px-4 py-3 text-sm text-[var(--muted)]">
          {t("methodologyNote")}
        </p>
      ) : null}

      {error ? (
        <div
          className="rounded-xl border border-[var(--warn)]/40 bg-[var(--card)] p-4 text-sm text-[var(--warn)]"
          role="alert"
        >
          {error}
        </div>
      ) : null}

      <RelationsViewTabs value={view} onChange={setView} />

      {view === "heat" ? (
        <RelationsHeatmapsPanel
          periodDays={periodDays}
          techHeat={techHeat}
          coocJobsAnalyzed={cooc?.jobs_analyzed ?? null}
          matrix={matrix}
          countryHeatValues={countryHeatValues}
          langMatrix={langMatrix}
          langCountryHeatValues={langCountryHeatValues}
          roleTech={roleTech}
          roleTechHeatValues={roleTechHeatValues}
          seniorityTech={seniorityTech}
          seniorityTechHeatValues={seniorityTechHeatValues}
        />
      ) : (
        <RelationsSeriesPanel
          periodDays={periodDays}
          techSeries={techSeries}
          countrySeries={countrySeries}
          ratesSeries={ratesSeries}
        />
      )}
    </div>
  );
}

export function RelationsDashboard() {
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
        <RelationsDashboardInner />
      </LensToggle.Provider>
    </Suspense>
  );
}
