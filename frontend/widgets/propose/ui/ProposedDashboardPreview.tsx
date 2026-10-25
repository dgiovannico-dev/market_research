"use client";

import { useEffect, useMemo, useState } from "react";
import { useLocale, useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";
import {
  api,
  type AssistantLocale,
  type DashboardSummary,
  type TechnologyTrends,
} from "@/lib/api";
import { assistantApi } from "@/entities/assistant";
import { RankBarsLazy, RiseCoolChartLazy } from "@/shared/ui/charts";

type Props = {
  periodDays: number;
  title?: string;
  prompt?: string;
  focusTechnologies?: string[];
};

function formatKpi(value: number | null | undefined, unit: string | null | undefined) {
  if (value == null || Number.isNaN(Number(value))) return "—";
  if (unit === "percent") return `${Number(value).toFixed(1)}%`;
  return new Intl.NumberFormat("en").format(Number(value));
}

function isComparePrompt(prompt: string, techs: string[]): boolean {
  if (techs.length < 2) return false;
  const lower = prompt.toLowerCase();
  return /\b(vs\.?|versus|meglio|oppure|better|prefer|scegliere|confront[ao]|compare|which)\b/.test(
    lower,
  ) || (/\bo\b/.test(lower) && techs.length >= 2);
}

export function ProposedDashboardPreview({
  periodDays,
  title,
  prompt = "",
  focusTechnologies = [],
}: Props) {
  const t = useTranslations("assistant");
  const tCharts = useTranslations("charts");
  const locale = useLocale() as AssistantLocale;
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [trends, setTrends] = useState<TechnologyTrends | null>(null);
  const [narrative, setNarrative] = useState<string | null>(null);
  const [narrativeSource, setNarrativeSource] = useState<string | null>(null);
  const [narrativeBusy, setNarrativeBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const techs = useMemo(
    () =>
      focusTechnologies
        .map((x) => String(x || "").trim())
        .filter(Boolean)
        .slice(0, 4),
    [focusTechnologies],
  );
  const compareMode = isComparePrompt(prompt, techs) || /observed compare/i.test(title || "");

  useEffect(() => {
    let cancelled = false;
    const days = Math.min(Math.max(periodDays, 1), 365);
    setLoading(true);
    setError(null);
    setNarrative(null);
    setNarrativeSource(null);
    Promise.all([
      api.summary({ days, lens: "market" }),
      api.trends({ days, lens: "market" }),
    ])
      .then(([sum, tr]) => {
        if (cancelled) return;
        setSummary(sum);
        setTrends(tr);
        setLoading(false);
      })
      .catch((e: unknown) => {
        if (cancelled) return;
        setError(e instanceof Error ? e.message : t("previewFailed"));
        setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [periodDays, t]);

  useEffect(() => {
    if (loading || error) return;
    let cancelled = false;
    const days = Math.min(Math.max(periodDays, 1), 365);
    setNarrativeBusy(true);
    assistantApi
      .dashboardNarrative({
        period_days: days,
        prompt,
        locale,
      })
      .then((res) => {
        if (cancelled) return;
        setNarrative(res.narrative);
        setNarrativeSource(res.source);
        setNarrativeBusy(false);
      })
      .catch(() => {
        if (cancelled) return;
        setNarrative(null);
        setNarrativeSource(null);
        setNarrativeBusy(false);
      });
    return () => {
      cancelled = true;
    };
  }, [loading, error, periodDays, prompt, locale]);

  const kpis = summary?.kpis ?? summary?.market?.kpis ?? [];
  const trendItems = trends?.items ?? trends?.market?.items ?? [];
  const jobsKpi = kpis.find((k) => k.metric_name === "unique_jobs_observed");
  const n =
    jobsKpi?.sample_size ??
    (trendItems.length
      ? trendItems.reduce((s, it) => s + (it.sample_size || 0), 0)
      : null);

  const compareBars = useMemo(() => {
    if (!compareMode || techs.length < 2) return [];
    const byLower = new Map(
      trendItems.map((it) => [String(it.technology || "").toLowerCase(), it]),
    );
    return techs.map((name) => {
      const hit = byLower.get(name.toLowerCase());
      return {
        label: hit?.technology || name,
        value: Number(hit?.sample_size || hit?.recent_mentions || 0),
      };
    });
  }, [compareMode, techs, trendItems]);

  return (
    <section className="card space-y-4 p-5" aria-label={t("previewAria")}>
      <header className="flex flex-wrap items-end justify-between gap-3">
        <div className="space-y-1">
          <h3 className="font-display text-base font-semibold tracking-tight text-[var(--ink)]">
            {t("previewTitle")}
          </h3>
          <p className="text-sm text-[var(--muted)]">
            {title ? `${title} · ` : null}
            {t("periodDays", { days: periodDays })}
            {n != null ? ` · ${t("sampleSize", { n })}` : null}
          </p>
        </div>
        <Link
          href="/"
          className="rounded-md bg-[var(--signal)] px-3 py-1.5 text-sm font-medium text-white transition-opacity hover:opacity-90"
        >
          {t("openFullDashboard")}
        </Link>
      </header>

      {loading ? <p className="text-sm text-[var(--muted)]">{t("previewLoading")}</p> : null}
      {error ? <p className="text-sm text-[var(--warn)]">{error}</p> : null}

      {!loading && !error ? (
        <>
          <div className="space-y-2 rounded-lg border border-[var(--line)] bg-[var(--card)] p-4">
            <h4 className="font-display text-sm font-semibold text-[var(--ink)]">
              {t("narrativeTitle")}
            </h4>
            {narrativeBusy ? (
              <p className="text-sm text-[var(--muted)]">{t("narrativeLoading")}</p>
            ) : narrative ? (
              <>
                <p className="whitespace-pre-wrap text-sm leading-relaxed text-[var(--ink)]">
                  {narrative}
                </p>
                {narrativeSource ? (
                  <p className="text-xs text-[var(--muted)]">
                    {t("narrativeSource", { source: narrativeSource })}
                  </p>
                ) : null}
              </>
            ) : (
              <p className="text-sm text-[var(--muted)]">{t("narrativeMissing")}</p>
            )}
          </div>

          {kpis.length > 0 ? (
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
              {kpis.slice(0, 4).map((k) => (
                <div
                  key={k.metric_name}
                  className="rounded-lg border border-[var(--line)] bg-[var(--card)] px-3 py-2"
                >
                  <p className="text-xs uppercase tracking-wide text-[var(--muted)]">
                    {k.metric_name.replaceAll("_", " ")}
                  </p>
                  <p className="font-display text-lg font-semibold text-[var(--ink)]">
                    {formatKpi(k.metric_value, k.unit)}
                  </p>
                </div>
              ))}
            </div>
          ) : null}

          {compareMode && compareBars.length >= 2 ? (
            <RankBarsLazy
              items={compareBars}
              periodDays={periodDays}
              sampleSize={typeof n === "number" ? n : null}
              title={t("skillCompareTitle")}
              maxBars={Math.max(2, compareBars.length)}
              valueLabel={t("skillCompareValue")}
            />
          ) : (
            <RiseCoolChartLazy
              items={trendItems}
              periodDays={periodDays}
              sampleSize={typeof n === "number" ? n : null}
              title={tCharts("riseCoolTitle")}
            />
          )}
        </>
      ) : null}
    </section>
  );
}
