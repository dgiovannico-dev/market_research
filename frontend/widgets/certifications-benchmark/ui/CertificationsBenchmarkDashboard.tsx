"use client";

import { Suspense, useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { RankBarsLazy } from "@/shared/ui/charts";
import {
  ADZUNA_US_ROLE_SHARE,
  PEARSON_SPECIALTY_INTEREST,
  SKILLSOFT_MOST_PURSUED,
  seriesToRankItems,
} from "@/entities/cert-benchmark";
import { useDashboardPrefs } from "@/features/dashboard-prefs";
import { useDashboardCountries } from "@/features/country-filter";
import { LensToggle, useDashboardLens } from "@/features/lens-toggle";
import { MarketCoverageBanner } from "@/features/dashboard-chrome";
import { api, type MarketCertifications } from "@/lib/api";
import { CertCountryMapPanel } from "./CertCountryMapPanel";

function unwrapCerts(
  data: MarketCertifications | null,
): MarketCertifications | null {
  if (!data) return null;
  if (data.lens === "compare") return data.market ?? null;
  return data;
}

function CertificationsBenchmarkInner() {
  const t = useTranslations("certificationsPage");
  const tCharts = useTranslations("charts");
  const { prefs, hydrated } = useDashboardPrefs();
  const { lens, queryIds } = useDashboardLens();
  const { countries } = useDashboardCountries();
  const [corpus, setCorpus] = useState<MarketCertifications | null>(null);
  const [corpusError, setCorpusError] = useState(false);

  useEffect(() => {
    if (!hydrated) return;
    let cancelled = false;
    setCorpusError(false);
    api
      .certificationsTop({
        days: Math.min(prefs.period_days, 365),
        lens,
        queryIds,
        countries,
        topN: 20,
      })
      .then((data) => {
        if (!cancelled) setCorpus(data);
      })
      .catch(() => {
        if (!cancelled) {
          setCorpus(null);
          setCorpusError(true);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [hydrated, prefs.period_days, lens, queryIds, countries]);

  const corpusBody = unwrapCerts(corpus);
  const corpusRank = (corpusBody?.items ?? []).map((it) => ({
    label: it.certification,
    value: it.job_mentions,
  }));

  const skillsoft = seriesToRankItems(SKILLSOFT_MOST_PURSUED);
  const adzuna = seriesToRankItems(ADZUNA_US_ROLE_SHARE);
  const pearson = seriesToRankItems(PEARSON_SPECIALTY_INTEREST);

  return (
    <div className="space-y-6">
      <header className="space-y-2">
        <div className="flex flex-wrap items-end justify-between gap-3">
          <div>
            <h1 className="text-xl font-semibold tracking-tight text-[var(--ink)]">
              {t("title")}
            </h1>
            <p className="mt-1 max-w-3xl text-sm text-[var(--muted)]">
              {t("subtitle")}
            </p>
          </div>
          <LensToggle.Control />
        </div>
        <MarketCoverageBanner />
        <p className="text-xs text-[var(--muted)]">{t("disclaimer")}</p>
      </header>

      <section className="space-y-2" aria-labelledby="cert-corpus">
        <h2
          id="cert-corpus"
          className="text-sm font-semibold uppercase tracking-[0.1em] text-[var(--muted)]"
        >
          {t("sourceFmi")}
        </h2>
        {corpusError ? (
          <p className="text-sm text-[var(--danger)]">{t("corpusLoadFailed")}</p>
        ) : null}
        {!corpusError && corpusRank.length === 0 ? (
          <p className="text-sm text-[var(--muted)]">{t("corpusEmpty")}</p>
        ) : null}
        {corpusRank.length > 0 ? (
          <RankBarsLazy
            items={corpusRank}
            periodDays={corpusBody?.period_days ?? prefs.period_days}
            sampleSize={corpusBody?.sample_size ?? null}
            title={t("corpusTitle")}
            valueLabel={tCharts("colMentions")}
          />
        ) : null}
      </section>

      <CertCountryMapPanel />

      <section className="space-y-2" aria-labelledby="cert-skillsoft">
        <h2
          id="cert-skillsoft"
          className="text-sm font-semibold uppercase tracking-[0.1em] text-[var(--muted)]"
        >
          {t("sourceSkillsoft")}
        </h2>
        <p className="text-xs text-[var(--muted)]">
          {t("skillsoftCaption")}{" "}
          <a
            className="underline underline-offset-2"
            href={SKILLSOFT_MOST_PURSUED.sourceUrl}
            target="_blank"
            rel="noopener noreferrer"
          >
            as-of {SKILLSOFT_MOST_PURSUED.asOf}
          </a>
        </p>
        <RankBarsLazy
          items={skillsoft}
          title={t("skillsoftTitle")}
          valueLabel={t("colValue")}
          sampleSize={null}
        />
      </section>

      <section className="space-y-2" aria-labelledby="cert-adzuna">
        <h2
          id="cert-adzuna"
          className="text-sm font-semibold uppercase tracking-[0.1em] text-[var(--muted)]"
        >
          {t("sourceAdzuna")}
        </h2>
        <p className="text-xs text-[var(--muted)]">
          {t("adzunaCaption")}{" "}
          <a
            className="underline underline-offset-2"
            href={ADZUNA_US_ROLE_SHARE.sourceUrl}
            target="_blank"
            rel="noopener noreferrer"
          >
            as-of {ADZUNA_US_ROLE_SHARE.asOf}
          </a>
        </p>
        <RankBarsLazy
          items={adzuna}
          title={t("adzunaTitle")}
          valueLabel="%"
          sampleSize={null}
        />
      </section>

      <section className="space-y-2" aria-labelledby="cert-pearson">
        <h2
          id="cert-pearson"
          className="text-sm font-semibold uppercase tracking-[0.1em] text-[var(--muted)]"
        >
          {t("sourcePearson")}
        </h2>
        <p className="text-xs text-[var(--muted)]">
          {t("pearsonCaption")}{" "}
          <a
            className="underline underline-offset-2"
            href={PEARSON_SPECIALTY_INTEREST.sourceUrl}
            target="_blank"
            rel="noopener noreferrer"
          >
            as-of {PEARSON_SPECIALTY_INTEREST.asOf}
          </a>
        </p>
        <RankBarsLazy
          items={pearson}
          title={t("pearsonTitle")}
          valueLabel="%"
          sampleSize={null}
        />
      </section>
    </div>
  );
}

export function CertificationsBenchmarkDashboard() {
  return (
    <Suspense fallback={null}>
      <LensToggle.Provider>
        <CertificationsBenchmarkInner />
      </LensToggle.Provider>
    </Suspense>
  );
}
