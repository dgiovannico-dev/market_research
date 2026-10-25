"use client";

import { useEffect, useMemo, useState } from "react";
import { useTranslations } from "next-intl";
import { RankBarsLazy, TechCooccurGraphLazy } from "@/shared/ui/charts";
import { api, type DashboardLens } from "@/lib/api";
import {
  egoNeighbors,
  type TechGraphPair,
} from "@/shared/lib/buildTechGraph";

export type RelationsGraphPanelProps = {
  periodDays: number;
  lens: DashboardLens;
  queryIds?: number[];
  countries?: string[];
  /** Global pairs (overview) from parent fetch. */
  overviewPairs: TechGraphPair[];
  jobsAnalyzed: number | null;
  seed: string | null;
  onSeedChange: (seed: string | null) => void;
};

function pairFromUnknown(row: Record<string, unknown>): TechGraphPair | null {
  const tech_a = String(row.tech_a ?? "").trim();
  const tech_b = String(row.tech_b ?? "").trim();
  const support = Number(row.support) || 0;
  if (!tech_a || !tech_b || support <= 0) return null;
  const liftRaw = row.lift;
  const lift =
    typeof liftRaw === "number" && Number.isFinite(liftRaw) ? liftRaw : null;
  return { tech_a, tech_b, support, lift };
}

function resolveCanonical(
  raw: string,
  options: readonly string[],
): string | null {
  const trimmed = raw.trim();
  if (!trimmed) return null;
  const exact = options.find((o) => o === trimmed);
  if (exact) return exact;
  const lower = trimmed.toLowerCase();
  return options.find((o) => o.toLowerCase() === lower) ?? trimmed;
}

export function RelationsGraphPanel({
  periodDays,
  lens,
  queryIds,
  countries,
  overviewPairs,
  jobsAnalyzed,
  seed,
  onSeedChange,
}: RelationsGraphPanelProps) {
  const t = useTranslations("relations");
  const [seedInput, setSeedInput] = useState(seed ?? "");
  const [egoPairs, setEgoPairs] = useState<TechGraphPair[] | null>(null);
  const [egoLoading, setEgoLoading] = useState(false);
  const [egoError, setEgoError] = useState(false);

  useEffect(() => {
    setSeedInput(seed ?? "");
  }, [seed]);

  useEffect(() => {
    if (!seed) {
      setEgoPairs(null);
      setEgoError(false);
      setEgoLoading(false);
      return;
    }
    let cancelled = false;
    setEgoPairs(null);
    setEgoError(false);
    setEgoLoading(true);
    api
      .cooccurrence({
        days: periodDays,
        lens,
        queryIds,
        countries,
        minSupport: 2,
        seed,
        neighborLimit: 50,
      })
      .then((res) => {
        if (cancelled) return;
        const items = (res.items ?? [])
          .map((row) => pairFromUnknown(row as Record<string, unknown>))
          .filter((p): p is TechGraphPair => p != null);
        setEgoPairs(items);
      })
      .catch(() => {
        if (!cancelled) {
          setEgoPairs(null);
          setEgoError(true);
        }
      })
      .finally(() => {
        if (!cancelled) setEgoLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [seed, periodDays, lens, queryIds, countries]);

  const techOptions = useMemo(() => {
    const names = new Set<string>();
    for (const p of overviewPairs) {
      names.add(p.tech_a);
      names.add(p.tech_b);
    }
    return [...names].sort((a, b) => a.localeCompare(b));
  }, [overviewPairs]);

  const activePairs = !seed
    ? overviewPairs
    : egoLoading || egoPairs == null
      ? null
      : egoPairs;

  const neighborRows = useMemo(
    () =>
      seed && activePairs
        ? egoNeighbors(activePairs, seed, 50)
        : [],
    [activePairs, seed],
  );

  const commitSeed = (raw: string) => {
    const next = resolveCanonical(raw, techOptions);
    onSeedChange(next);
    if (next) setSeedInput(next);
  };

  return (
    <div
      id="relations-panel-graph"
      role="tabpanel"
      aria-labelledby="relations-tab-graph"
      className="space-y-5"
    >
      <div className="flex flex-wrap items-end gap-3 rounded-xl border border-[var(--line)] bg-[var(--card)] px-4 py-3">
        <label className="flex min-w-[14rem] flex-1 flex-col gap-1 text-xs text-[var(--muted)]">
          <span>{t("graphSeedLabel")}</span>
          <input
            list="relations-graph-tech-options"
            className="rounded border border-[var(--line)] bg-transparent px-2 py-1.5 text-sm text-[var(--ink)]"
            placeholder={t("graphSeedPlaceholder")}
            value={seedInput}
            onChange={(e) => setSeedInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") commitSeed(seedInput);
            }}
            onBlur={() => commitSeed(seedInput)}
          />
          <datalist id="relations-graph-tech-options">
            {techOptions.map((name) => (
              <option key={name} value={name} />
            ))}
          </datalist>
        </label>
        {seed ? (
          <button
            type="button"
            className="rounded border border-[var(--line)] px-2.5 py-1.5 text-xs text-[var(--ink)] hover:border-[var(--signal)]"
            onClick={() => {
              setSeedInput("");
              onSeedChange(null);
            }}
          >
            {t("graphSeedClear")}
          </button>
        ) : null}
        <p className="w-full text-xs text-[var(--muted)]">{t("graphPickHint")}</p>
      </div>

      {seed && egoLoading ? (
        <p className="text-sm text-[var(--muted)]">{t("graphLoading")}</p>
      ) : null}

      {seed && egoError ? (
        <p className="text-sm text-[var(--warn)]" role="alert">
          {t("loadFailed")}
        </p>
      ) : null}

      {seed && !egoLoading && !egoError && neighborRows.length > 0 ? (
        <RankBarsLazy
          items={neighborRows.map((r) => ({
            label: r.label,
            value: r.value,
          }))}
          periodDays={periodDays}
          sampleSize={jobsAnalyzed}
          title={t("graphEgoTitle", { seed })}
          valueLabel={t("colSupport")}
          maxBars={30}
          onBarClick={(tech) => {
            setSeedInput(tech);
            onSeedChange(tech);
          }}
        />
      ) : null}

      {seed && !egoLoading && !egoError && egoPairs != null && neighborRows.length === 0 ? (
        <p className="text-sm text-[var(--muted)]">{t("graphEmptySeed")}</p>
      ) : null}

      {activePairs != null ? (
        <TechCooccurGraphLazy
          key={seed ?? "overview"}
          pairs={activePairs}
          periodDays={periodDays}
          sampleSize={jobsAnalyzed}
          seed={seed}
          title={
            seed ? t("graphEgoTitle", { seed }) : t("graphOverviewTitle")
          }
          onNodeClick={(tech) => {
            setSeedInput(tech);
            onSeedChange(tech);
          }}
        />
      ) : null}
    </div>
  );
}
