"use client";

import { useTranslations } from "next-intl";
import { WatchCandidates } from "@/features/propose-watch";
import { briefChipKey } from "@/features/propose-watch";
import type { EvidenceBrief } from "@/lib/api";

type Props = {
  brief: EvidenceBrief;
};

type TechRow = {
  technology?: string;
  growth_pct?: number;
  sample_size?: number;
};

type GeoRow = {
  country_code?: string;
  jobs_observed?: number;
  remote_share?: number;
};

function trendsBlock(brief: EvidenceBrief): { rising: TechRow[]; cooling: TechRow[]; days?: number } {
  const block = brief.evidence.find((e) => e.metric === "technology_trends");
  if (!block) return { rising: [], cooling: [] };
  return {
    rising: Array.isArray(block.rising) ? (block.rising as TechRow[]) : [],
    cooling: Array.isArray(block.cooling) ? (block.cooling as TechRow[]) : [],
    days: typeof block.period_days === "number" ? block.period_days : undefined,
  };
}

function geoBlock(brief: EvidenceBrief): GeoRow[] {
  const block = brief.evidence.find((e) => e.metric === "countries_breakdown");
  if (!block || !Array.isArray(block.items)) return [];
  return block.items as GeoRow[];
}

function formatGrowth(value: number | undefined): string {
  if (value == null || Number.isNaN(Number(value))) return "—";
  const n = Number(value);
  return `${n > 0 ? "+" : ""}${n.toFixed(0)}%`;
}

export function BriefResult({ brief }: Props) {
  const t = useTranslations("assistant");
  const tCompass = useTranslations("compass");
  const candidates = brief.proposed_intents ?? [];
  const showWatches =
    brief.brief_type === "suggest_watches" || candidates.length > 0;
  const trends = trendsBlock(brief);
  const geos = geoBlock(brief);
  const titleKey = briefChipKey(brief.brief_type);
  const purposeKey =
    `briefPurpose_${brief.brief_type}` as
      | "briefPurpose_rising_cooling"
      | "briefPurpose_where_demand"
      | "briefPurpose_adjacent"
      | "briefPurpose_focus_vs_market"
      | "briefPurpose_suggest_watches";
  const limitsKey =
    `briefLimits_${brief.brief_type}` as
      | "briefLimits_rising_cooling"
      | "briefLimits_where_demand"
      | "briefLimits_adjacent"
      | "briefLimits_focus_vs_market"
      | "briefLimits_suggest_watches";
  const statusKey =
    brief.status === "ok"
      ? "briefStatusOk"
      : brief.status === "thin_sample"
        ? "briefStatusThin"
        : brief.status === "refused"
          ? "briefStatusRefused"
          : "briefStatusOk";
  const lensKey =
    brief.lens === "focus"
      ? "briefLensFocus"
      : brief.lens === "compare"
        ? "briefLensCompare"
        : "briefLensMarket";

  return (
    <section className="card space-y-5 p-5" aria-label={tCompass(titleKey)}>
      <header className="space-y-2">
        <h3 className="font-display text-lg font-semibold tracking-tight text-[var(--ink)]">
          {tCompass(titleKey)}
        </h3>
        <p className="max-w-2xl text-sm text-[var(--muted)]">{t(purposeKey)}</p>
        <p className="text-xs text-[var(--muted)]">
          {t("briefMetaHuman", {
            n: brief.sample_size,
            lens: t(lensKey),
            status: t(statusKey),
          })}
        </p>
      </header>

      <div className="space-y-2">
        <h4 className="font-display text-sm font-semibold text-[var(--ink)]">
          {t("briefSummaryTitle")}
        </h4>
        <p className="whitespace-pre-wrap text-sm leading-relaxed text-[var(--ink)]">
          {brief.narrative}
        </p>
      </div>

      {brief.brief_type === "rising_cooling" &&
      (trends.rising.length > 0 || trends.cooling.length > 0) ? (
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-2">
            <h4 className="font-display text-sm font-semibold text-[var(--ink)]">
              {t("briefRisingList")}
            </h4>
            {trends.rising.length > 0 ? (
              <ul className="space-y-1.5 text-sm text-[var(--ink)]">
                {trends.rising.slice(0, 6).map((row) => (
                  <li key={`r-${row.technology}`}>
                    <span className="font-medium">{row.technology}</span>
                    <span className="text-[var(--muted)]">
                      {" "}
                      · {formatGrowth(row.growth_pct)} ·{" "}
                      {t("sampleSize", { n: row.sample_size ?? 0 })}
                    </span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-[var(--muted)]">{t("briefListEmpty")}</p>
            )}
          </div>
          <div className="space-y-2">
            <h4 className="font-display text-sm font-semibold text-[var(--ink)]">
              {t("briefCoolingList")}
            </h4>
            {trends.cooling.length > 0 ? (
              <ul className="space-y-1.5 text-sm text-[var(--ink)]">
                {trends.cooling.slice(0, 6).map((row) => (
                  <li key={`c-${row.technology}`}>
                    <span className="font-medium">{row.technology}</span>
                    <span className="text-[var(--muted)]">
                      {" "}
                      · {formatGrowth(row.growth_pct)} ·{" "}
                      {t("sampleSize", { n: row.sample_size ?? 0 })}
                    </span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-[var(--muted)]">{t("briefListEmpty")}</p>
            )}
          </div>
        </div>
      ) : null}

      {brief.brief_type === "where_demand" && geos.length > 0 ? (
        <div className="space-y-2">
          <h4 className="font-display text-sm font-semibold text-[var(--ink)]">
            {t("briefGeoList")}
          </h4>
          <ul className="space-y-1.5 text-sm text-[var(--ink)]">
            {geos.slice(0, 8).map((row) => (
              <li key={row.country_code}>
                <span className="font-medium">{row.country_code}</span>
                <span className="text-[var(--muted)]">
                  {" "}
                  · {t("briefGeoJobs", { n: row.jobs_observed ?? 0 })} ·{" "}
                  {t("briefGeoRemote", {
                    pct: Math.round((row.remote_share ?? 0) * 100),
                  })}
                </span>
              </li>
            ))}
          </ul>
        </div>
      ) : null}

      <div className="space-y-1 rounded-md border border-[var(--line)] bg-[var(--card)] p-3">
        <h4 className="font-display text-sm font-semibold text-[var(--ink)]">
          {t("briefHowToRead")}
        </h4>
        <p className="text-sm leading-relaxed text-[var(--muted)]">{t(limitsKey)}</p>
      </div>

      {showWatches ? <WatchCandidates candidates={candidates} /> : null}
    </section>
  );
}
