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
import type { CooccurrencePayload } from "@/entities/market";
import { RankBarsLazy, RiseCoolChartLazy } from "@/shared/ui/charts";

export type ProposeWidget = {
  id?: string;
  type?: string;
  metric_key?: string;
  params?: Record<string, unknown>;
};

type Props = {
  periodDays: number;
  title?: string;
  prompt?: string;
  focusTechnologies?: string[];
  widgets?: ProposeWidget[];
  /** Bump on each successful propose so consecutive asks remount cleanly. */
  requestKey?: string | number;
};

type PreviewMode = "compare" | "cooccur" | "trends";

function formatKpi(value: number | null | undefined, unit: string | null | undefined) {
  if (value == null || Number.isNaN(Number(value))) return "—";
  if (unit === "percent") return `${Number(value).toFixed(1)}%`;
  return new Intl.NumberFormat("en").format(Number(value));
}

function resolveMode(
  widgets: ProposeWidget[],
  prompt: string,
  techs: string[],
  title: string,
): PreviewMode {
  const ids = new Set(widgets.map((w) => String(w.id || "")));
  if (ids.has("chart_cooccur")) return "cooccur";
  if (ids.has("chart_compare_trends")) return "compare";
  if (/co-occurrence/i.test(title)) return "cooccur";
  if (/observed compare/i.test(title)) return "compare";
  const lower = prompt.toLowerCase();
  if (
    techs.length >= 1 &&
    /\b(abbin|co-?occurr|pair|insieme|vicin|along with|together with|combin|associat|adiacent|si\s+abbina)\b/.test(
      lower,
    )
  ) {
    return "cooccur";
  }
  if (
    techs.length >= 2 &&
    (/\b(vs\.?|versus|meglio|oppure|better|prefer|scegliere|confront[ao]|compare|which)\b/.test(
      lower,
    ) ||
      /\bo\b/.test(lower))
  ) {
    return "compare";
  }
  return "trends";
}

function neighborsFromCooccur(
  payload: CooccurrencePayload | null,
  seed: string,
): { label: string; value: number }[] {
  if (!payload?.items?.length || !seed) return [];
  const seedL = seed.toLowerCase();
  const out: { label: string; value: number }[] = [];
  for (const row of payload.items) {
    const a = String(row.tech_a || "");
    const b = String(row.tech_b || "");
    const other =
      a.toLowerCase() === seedL ? b : b.toLowerCase() === seedL ? a : "";
    if (!other) continue;
    out.push({ label: other, value: Number(row.support || 0) });
  }
  return out.slice(0, 15);
}

export function ProposedDashboardPreview({
  periodDays,
  title,
  prompt = "",
  focusTechnologies = [],
  widgets = [],
  requestKey = "0",
}: Props) {
  const t = useTranslations("assistant");
  const tCharts = useTranslations("charts");
  const locale = useLocale() as AssistantLocale;
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [trends, setTrends] = useState<TechnologyTrends | null>(null);
  const [cooccur, setCooccur] = useState<CooccurrencePayload | null>(null);
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
  const mode = resolveMode(widgets, prompt, techs, title || "");
  const seed =
    String(
      widgets.find((w) => w.id === "chart_cooccur" || w.id === "cooccur")?.params
        ?.seed || techs[0] || "",
    ).trim() || techs[0] || "";

  useEffect(() => {
    let cancelled = false;
    const days = Math.min(Math.max(periodDays, 1), 365);
    setLoading(true);
    setError(null);
    setNarrative(null);
    setNarrativeSource(null);
    setCooccur(null);
    setTrends(null);
    setSummary(null);

    const tasks: Promise<unknown>[] = [
      api.summary({ days, lens: "market" }),
    ];
    if (mode === "cooccur" && seed) {
      tasks.push(
        api.cooccurrence({
          days,
          lens: "market",
          minSupport: 2,
          seed,
          neighborLimit: 15,
        }),
      );
    } else {
      tasks.push(api.trends({ days, lens: "market" }));
    }

    Promise.all(tasks)
      .then((results) => {
        if (cancelled) return;
        setSummary(results[0] as DashboardSummary);
        if (mode === "cooccur" && seed) {
          setCooccur(results[1] as CooccurrencePayload);
        } else {
          setTrends(results[1] as TechnologyTrends);
        }
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
  }, [periodDays, t, mode, seed, requestKey]);

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
  }, [loading, error, periodDays, prompt, locale, requestKey]);

  const kpis = summary?.kpis ?? summary?.market?.kpis ?? [];
  const trendItems = trends?.items ?? trends?.market?.items ?? [];
  const jobsKpi = kpis.find((k) => k.metric_name === "unique_jobs_observed");
  const n =
    jobsKpi?.sample_size ??
    (typeof cooccur?.jobs_analyzed === "number" ? cooccur.jobs_analyzed : null) ??
    (trendItems.length
      ? trendItems.reduce((s, it) => s + (it.sample_size || 0), 0)
      : null);

  const compareBars = useMemo(() => {
    if (mode !== "compare" || techs.length < 2) return [];
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
  }, [mode, techs, trendItems]);

  const cooccurBars = useMemo(
    () => neighborsFromCooccur(cooccur, seed),
    [cooccur, seed],
  );

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

          {mode === "compare" && compareBars.length >= 2 ? (
            <RankBarsLazy
              items={compareBars}
              periodDays={periodDays}
              sampleSize={typeof n === "number" ? n : null}
              title={t("skillCompareTitle")}
              maxBars={Math.max(2, compareBars.length)}
              valueLabel={t("skillCompareValue")}
            />
          ) : null}

          {mode === "cooccur" ? (
            cooccurBars.length > 0 ? (
              <RankBarsLazy
                items={cooccurBars}
                periodDays={periodDays}
                sampleSize={typeof n === "number" ? n : null}
                title={t("skillCooccurTitle", { seed: seed || "…" })}
                maxBars={Math.min(15, Math.max(5, cooccurBars.length))}
                valueLabel={t("skillCooccurValue")}
              />
            ) : (
              <p className="text-sm text-[var(--muted)]">{t("skillCooccurEmpty")}</p>
            )
          ) : null}

          {mode === "trends" ? (
            <RiseCoolChartLazy
              items={trendItems}
              periodDays={periodDays}
              sampleSize={typeof n === "number" ? n : null}
              title={tCharts("riseCoolTitle")}
            />
          ) : null}
        </>
      ) : null}
    </section>
  );
}
