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
import { RelationsGraphPanel } from "./RelationsGraphPanel";
import {
  RelationsViewTabs,
  type RelationsView,
} from "./RelationsViewTabs";
import type { TechGraphPair } from "@/shared/lib/buildTechGraph";
import { useLocalProfile } from "@/features/user-profile";

type CooccurrencePayload = {
  jobs_analyzed: number;
  period_days: number;
  items: CooccurrencePairLike[];
  excluded_thin_n?: number;
};

const COOC_TOP_N = 12;
const DEFAULT_VIEW: RelationsView = "heat";

function parseRelationsView(
  raw: string | null,
  hasSeed = false,
): RelationsView {
  if (raw === "series" || raw === "graph") return raw;
  if (hasSeed) return "graph";
  return DEFAULT_VIEW;
}

function writeRelationsUrl(
  pathname: string,
  searchParams: URLSearchParams,
  router: ReturnType<typeof useRouter>,
  next: { view?: RelationsView; seed?: string | null },
) {
  const params = new URLSearchParams(searchParams.toString());
  if (next.view != null) {
    if (next.view === DEFAULT_VIEW) params.delete("view");
    else params.set("view", next.view);
  }
  if (next.seed !== undefined) {
    if (!next.seed) params.delete("seed");
    else params.set("seed", next.seed);
  }
  const qs = params.toString();
  startTransition(() => {
    router.replace(qs ? `${pathname}?${qs}` : pathname, { scroll: false });
  });
}

function toGraphPairs(
  items: (CooccurrencePairLike & { lift?: number | null })[],
): TechGraphPair[] {
  return items.map((p) => ({
    tech_a: String(p.tech_a),
    tech_b: String(p.tech_b),
    support: Number(p.support) || 0,
    lift: typeof p.lift === "number" ? p.lift : null,
  }));
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

  const { profile: localProfile, hydrated: profileHydrated } = useLocalProfile();
  const seedFromUrl = searchParams.get("seed")?.trim() || null;
  const viewFromUrl = parseRelationsView(
    searchParams.get("view"),
    Boolean(seedFromUrl),
  );
  const [view, setViewState] = useState<RelationsView>(viewFromUrl);
  const [seed, setSeedState] = useState<string | null>(seedFromUrl);

  useEffect(() => {
    setViewState(viewFromUrl);
  }, [viewFromUrl]);

  useEffect(() => {
    setSeedState(seedFromUrl);
  }, [seedFromUrl]);

  // When graph is open without ?seed=, default to first owned skill (My Stack).
  useEffect(() => {
    if (!profileHydrated) return;
    if (seedFromUrl) return;
    if (view !== "graph") return;
    const first = localProfile.skills[0]?.trim();
    if (!first) return;
    writeRelationsUrl(pathname, searchParams, router, {
      view: "graph",
      seed: first,
    });
  }, [
    profileHydrated,
    seedFromUrl,
    view,
    localProfile.skills,
    pathname,
    router,
    searchParams,
  ]);

  // Normalize bare ?seed= (no view) → graph. Explicit view=series|heat wins.
  useEffect(() => {
    if (!seedFromUrl) return;
    if (searchParams.get("view") != null) return;
    writeRelationsUrl(pathname, searchParams, router, {
      view: "graph",
      seed: seedFromUrl,
    });
  }, [seedFromUrl, pathname, router, searchParams]);

  const setView = (next: RelationsView) => {
    setViewState(next);
    const leavingGraph = next !== "graph";
    if (leavingGraph) setSeedState(null);
    writeRelationsUrl(pathname, searchParams, router, {
      view: next,
      seed: leavingGraph ? null : undefined,
    });
  };

  const setSeed = (next: string | null) => {
    setSeedState(next);
    writeRelationsUrl(pathname, searchParams, router, {
      view: next ? "graph" : undefined,
      seed: next,
    });
    if (next) setViewState("graph");
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
      ) : view === "series" ? (
        <RelationsSeriesPanel
          periodDays={periodDays}
          techSeries={techSeries}
          countrySeries={countrySeries}
          ratesSeries={ratesSeries}
        />
      ) : (
        <RelationsGraphPanel
          periodDays={periodDays}
          lens={lens}
          queryIds={queryIds}
          countries={countries}
          overviewPairs={toGraphPairs(cooc?.items ?? [])}
          jobsAnalyzed={cooc?.jobs_analyzed ?? null}
          seed={seed}
          onSeedChange={setSeed}
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
