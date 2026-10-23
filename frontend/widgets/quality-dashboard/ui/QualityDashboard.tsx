"use client";

import { Suspense, useEffect, useState, type ReactNode } from "react";
import { useTranslations } from "next-intl";
import { LlmOpsButtons } from "@/features/ops-llm";
import { api, type QualityPayload } from "@/lib/api";
import {
  LensToggle,
  useDashboardLens,
} from "@/features/lens-toggle";
import { useDashboardCountries } from "@/features/country-filter";
import { useDashboardPrefs } from "@/features/dashboard-prefs";
import { MarketCoverageBanner } from "@/features/dashboard-chrome";
import {
  QualityBySourceTable,
  QualityCatalogTable,
} from "./QualitySortableTables";
import { RankBarsLazy } from "@/shared/ui/charts";
import { MetricLegend } from "@/shared/ui/MetricLegend";

type Tone = "pass" | "warn" | "neutral";

const PCT_PASS = 70;
/** Thin share: low is good (unlike coverage % metrics). */
const PCT_THIN_WARN = 15;

const METRIC_ORDER = [
  "pct_with_valid_date",
  "pct_known_country",
  "pct_known_contract",
  "pct_with_rate",
  "pct_thin",
  "thin_n",
  "duplicate_non_canonical_count",
] as const;

function metricTone(key: string, value: number): Tone {
  if (key === "pct_thin") return value <= PCT_THIN_WARN ? "pass" : "warn";
  if (key.startsWith("pct_")) return value >= PCT_PASS ? "pass" : "warn";
  if (key.includes("duplicate")) return value === 0 ? "pass" : "warn";
  if (key === "thin_n") return value === 0 ? "pass" : "neutral";
  return "neutral";
}

function formatMetricValue(key: string, value: number): string {
  if (key.startsWith("pct_")) {
    const n = Number(value);
    return `${Number.isFinite(n) ? n.toFixed(n % 1 === 0 ? 0 : 2) : value}%`;
  }
  return String(value);
}

function orderedMetricEntries(
  metrics: Record<string, number>,
): [string, number][] {
  const seen = new Set<string>();
  const out: [string, number][] = [];
  for (const key of METRIC_ORDER) {
    if (key in metrics) {
      out.push([key, metrics[key]]);
      seen.add(key);
    }
  }
  for (const [k, v] of Object.entries(metrics)) {
    if (!seen.has(k)) out.push([k, v]);
  }
  return out;
}

function sourceStatusTone(status: string, enabled: boolean): Tone {
  if (!enabled) return "warn";
  if (status === "enabled") return "pass";
  if (status === "requires_credentials" || status === "unsupported") return "warn";
  return "neutral";
}

const TONE_STYLE: Record<Tone, { color: string; border: string; bg: string }> = {
  pass: {
    color: "var(--rise)",
    border: "color-mix(in srgb, var(--rise) 45%, var(--line))",
    bg: "color-mix(in srgb, var(--rise) 12%, transparent)",
  },
  warn: {
    color: "var(--warn)",
    border: "color-mix(in srgb, var(--warn) 45%, var(--line))",
    bg: "color-mix(in srgb, var(--warn) 12%, transparent)",
  },
  neutral: {
    color: "var(--muted)",
    border: "var(--line)",
    bg: "transparent",
  },
};

function ToneBadge({
  tone,
  children,
  title,
}: {
  tone: Tone;
  children: ReactNode;
  title?: string;
}) {
  const s = TONE_STYLE[tone];
  return (
    <span
      className="badge"
      title={title}
      style={{
        color: s.color,
        borderColor: s.border,
        background: s.bg,
        fontFamily: "var(--mono)",
      }}
    >
      {children}
    </span>
  );
}

function QualityDashboardInner() {
  const t = useTranslations("quality");
  const tCommon = useTranslations("common");
  const tCompass = useTranslations("compass");
  const tCharts = useTranslations("charts");
  const { hydrated } = useDashboardPrefs();
  const { lens, queryIds } = useDashboardLens();
  const { countries } = useDashboardCountries();
  const [quality, setQuality] = useState<QualityPayload | null>(null);
  const [error, setError] = useState<string | null>(null);
  const loadFailedMsg = t("loadFailed");
  const countriesKey = countries.join(",");
  const queryIdsKey = queryIds.join(",");

  useEffect(() => {
    if (!hydrated) return;
    let cancelled = false;
    setError(null);
    api
      .quality({ lens, queryIds, countries })
      .then((res) => {
        if (!cancelled) setQuality(res);
      })
      .catch((e: unknown) => {
        if (!cancelled) setError(e instanceof Error ? e.message : loadFailedMsg);
      });
    return () => {
      cancelled = true;
    };
    // Prefer *Key primitives over `t` / new [] identities (those abort in-flight loads).
    // eslint-disable-next-line react-hooks/exhaustive-deps -- queryIds/countries mirrored by *Key
  }, [hydrated, lens, queryIdsKey, countriesKey, loadFailedMsg]);

  const metrics = quality?.metrics ?? {};
  const bySource = quality?.by_source ?? [];
  const sources = quality?.sources ?? [];
  const sourceMix = bySource
    .filter((s) => (s.n ?? 0) > 0)
    .map((s) => ({
      label: String(s.name || s.connector_type || s.source_id || "source"),
      value: s.n,
    }));
  const compareHint =
    lens === "compare" && quality
      ? t("compareCounts", {
          market: quality.market_n ?? 0,
          focus: quality.focus_n ?? 0,
          overlap: quality.overlap_n ?? 0,
        })
      : null;

  return (
    <div className="space-y-4">
      <section className="card space-y-3 p-4">
        <div className="flex flex-wrap items-end justify-between gap-3">
          <div className="space-y-1">
            <h2
              className="text-lg font-semibold tracking-tight"
              style={{ fontFamily: "var(--display)" }}
            >
              {t("title")}
            </h2>
            <p className="text-sm text-[var(--muted)]">
              {quality?.disclaimer || t("subtitle")}
            </p>
            <p className="mt-2 text-sm">
              {quality ? (
                <>
                  {t("canonicalJobs")}{" "}
                  <strong style={{ fontFamily: "var(--mono)" }}>
                    {String(quality.total_canonical_jobs ?? 0)}
                  </strong>
                </>
              ) : error ? null : (
                <span className="text-[var(--muted)]">{tCommon("loading")}</span>
              )}
            </p>
            {compareHint ? (
              <p
                className="mt-1 text-xs text-[var(--muted)]"
                style={{ fontFamily: "var(--mono)" }}
              >
                {compareHint}
              </p>
            ) : null}
            {lens === "compare" && (quality?.focus_n ?? 0) === 0 ? (
              <p className="mt-2 text-sm text-[var(--muted)]">
                {tCompass("compareUnavailable")}
              </p>
            ) : null}
            <LlmOpsButtons />
          </div>
          <LensToggle.Control />
        </div>
        <MarketCoverageBanner
          sampleSize={quality ? (quality.total_canonical_jobs ?? 0) : null}
        />
      </section>

      {error ? (
        <div
          className="rounded-xl border px-3 py-2 text-sm"
          style={{
            color: "var(--warn)",
            borderColor: "color-mix(in srgb, var(--warn) 40%, var(--line))",
            background: "color-mix(in srgb, var(--warn) 12%, transparent)",
          }}
        >
          {error}
        </div>
      ) : null}

      <section className="grid gap-3 md:grid-cols-3">
        {orderedMetricEntries(metrics).map(([k, v]) => {
          const tone = metricTone(k, v);
          const labelKey = `metric_${k}_label` as Parameters<typeof t>[0];
          const hintKey = `metric_${k}_hint` as Parameters<typeof t>[0];
          const label = t.has(labelKey) ? t(labelKey) : k;
          const hint = t.has(hintKey) ? t(hintKey) : undefined;
          return (
            <div key={k} className="card space-y-2 p-4" title={hint}>
              <div className="flex flex-wrap items-start justify-between gap-2">
                <div className="min-w-0 space-y-1">
                  <div className="text-sm font-medium leading-snug text-[var(--ink)]">
                    {label}
                  </div>
                  {hint ? (
                    <p className="text-[0.7rem] leading-snug text-[var(--muted)]">
                      {hint}
                    </p>
                  ) : null}
                  <div
                    className="text-[0.65rem] uppercase tracking-wide text-[var(--muted)]"
                    style={{ fontFamily: "var(--mono)" }}
                  >
                    {k}
                  </div>
                </div>
                {tone !== "neutral" ? (
                  <ToneBadge tone={tone} title={hint ?? `${k}: ${v}`}>
                    {tone === "pass" ? t("badgePass") : t("badgeWarn")}
                  </ToneBadge>
                ) : null}
              </div>
              <div
                className="text-2xl font-semibold"
                style={{
                  fontFamily: "var(--mono)",
                  color:
                    tone === "pass"
                      ? "var(--rise)"
                      : tone === "warn"
                        ? "var(--warn)"
                        : undefined,
                }}
              >
                {formatMetricValue(k, v)}
              </div>
            </div>
          );
        })}
      </section>

      {sourceMix.length > 0 ? (
        <RankBarsLazy
          items={sourceMix}
          sampleSize={quality?.total_canonical_jobs ?? null}
          title={tCharts("sourceMixTitle")}
          valueLabel={t("colN")}
        />
      ) : null}

      {bySource.length > 0 ? (
        <section className="card space-y-2 overflow-x-auto p-0">
          <h3 className="border-b border-[var(--line)] px-3 py-2 text-[0.65rem] font-semibold uppercase tracking-[0.12em] text-[var(--muted)]">
            {t("bySourceTitle")}
          </h3>
          <div className="border-b border-[var(--line)] px-3 py-3">
            <MetricLegend
              variant="plain"
              title={tCommon("metricLegendTitle")}
              items={[
                { term: t("colN"), definition: t("hintN") },
                { term: t("colPctKnownCountry"), definition: t("hintPctKnownCountry") },
                { term: t("colPctThin"), definition: t("hintPctThin") },
                { term: t("colPctRate"), definition: t("hintPctRate") },
              ]}
            />
          </div>
          <QualityBySourceTable bySource={bySource} />
        </section>
      ) : null}

      <section className="card space-y-2 overflow-x-auto p-0">
        {bySource.length > 0 ? (
          <h3 className="border-b border-[var(--line)] px-3 py-2 text-[0.65rem] font-semibold uppercase tracking-[0.12em] text-[var(--muted)]">
            {t("sourcesCatalog")}
          </h3>
        ) : null}
        <QualityCatalogTable
          sources={sources}
          ToneBadge={ToneBadge}
          sourceStatusTone={sourceStatusTone}
        />
      </section>
    </div>
  );
}

export function QualityDashboard() {
  const t = useTranslations("common");
  return (
    <Suspense
      fallback={
        <div className="card p-6 text-sm text-[var(--muted)]">{t("loading")}</div>
      }
    >
      <LensToggle.Provider>
        <QualityDashboardInner />
      </LensToggle.Provider>
    </Suspense>
  );
}
