"use client";

import { useTranslations } from "next-intl";
import { useMemo, useState } from "react";
import ReactECharts from "echarts-for-react";
import { ChartFrame } from "./ChartFrame";
import { chartAnimationMs, chartTheme } from "./chartTheme";
import { formatPercent, formatPercentNumber } from "@/shared/lib/formatPercent";
import {
  DEFAULT_CHART_TOP_N,
  isChartTopN,
  type ChartTopN,
} from "./chartTopN";
import {
  pickRiseCoolRows,
  riseCoolCorpusSampleSize,
} from "@/lib/riseCoolPick";

const THIN_THRESHOLD = 3;

export type RiseCoolItem = {
  technology: string;
  category?: string;
  recent_mentions: number;
  previous_mentions: number;
  sample_size: number;
  growth_pct: number | null;
  status: string;
};

export type RiseCoolChartProps = {
  items: RiseCoolItem[];
  periodDays: number;
  /** Corpus-level n for the period footer (stable when Mostra changes). */
  sampleSize?: number | null;
  title?: string;
  className?: string;
};

export function RiseCoolChart({
  items,
  periodDays,
  sampleSize: sampleSizeProp = null,
  title,
  className,
}: RiseCoolChartProps) {
  const t = useTranslations("charts");
  const resolvedTitle = title ?? t("riseCoolTitle");
  const [topN, setTopN] = useState<ChartTopN>(DEFAULT_CHART_TOP_N);
  const onTopNChange = (n: number) => {
    if (isChartTopN(n)) setTopN(n);
  };
  const rows = useMemo(() => pickRiseCoolRows(items, topN), [items, topN]);
  const empty = rows.length === 0;
  const thin = !empty && rows.length < THIN_THRESHOLD;
  const corpusN = riseCoolCorpusSampleSize(items);
  const sampleSize =
    sampleSizeProp != null && sampleSizeProp > 0
      ? sampleSizeProp
      : corpusN > 0
        ? corpusN
        : null;
  const theme = chartTheme();
  const anim = chartAnimationMs();

  const option = useMemo(() => {
    if (empty) return {};
    const labels = rows.map((r) => r.technology);
    const values = rows.map((r) => r.growth_pct);
    const colors = rows.map((r) => (r.side === "rise" ? theme.rise : theme.cool));

    return {
      animationDuration: anim,
      // Extra side gutters so bar end-labels (e.g. +420%) are not clipped.
      grid: { left: 12, right: 96, top: 16, bottom: 28, containLabel: true },
      tooltip: {
        trigger: "axis",
        axisPointer: { type: "shadow" },
        valueFormatter: (v: number) => formatPercent(Number(v)),
      },
      xAxis: {
        type: "value",
        axisLabel: {
          formatter: (v: number) =>
            formatPercent(Number(v), Math.abs(Number(v)) >= 100 ? 0 : 2),
          color: theme.ink,
          fontFamily: theme.mono,
          fontSize: 11,
          hideOverlap: true,
        },
        splitLine: { lineStyle: { color: theme.line, opacity: 0.6 } },
        axisLine: { show: false },
      },
      yAxis: {
        type: "category",
        data: labels,
        axisLabel: {
          color: theme.ink,
          fontSize: 12,
          width: 140,
          overflow: "truncate",
          ellipsis: "…",
        },
        axisTick: { show: false },
        axisLine: { show: false },
      },
      series: [
        {
          type: "bar",
          data: values.map((v, i) => ({
            value: v,
            itemStyle: {
              color: colors[i],
              borderRadius: v >= 0 ? [0, 4, 4, 0] : [4, 0, 0, 4],
            },
            label: {
              show: true,
              position: v >= 0 ? "right" : "left",
              distance: 4,
              formatter: formatPercent(v, Math.abs(v) >= 100 ? 0 : 2),
              color: theme.ink,
              fontFamily: theme.mono,
              fontSize: 10,
            },
          })),
          barMaxWidth: 18,
        },
      ],
    };
  }, [anim, empty, rows, theme]);

  const height = Math.max(240, rows.length * 36 + 32);

  return (
    <ChartFrame
      title={resolvedTitle}
      periodDays={periodDays}
      sampleSize={empty ? null : sampleSize}
      empty={empty}
      thin={thin}
      topN={topN}
      onTopNChange={onTopNChange}
      xAxisLabel={t("axisGrowthPct")}
      guideRepresents={t("guideRiseCool")}
      guideHowToRead={t("guideRiseCoolRead")}
      legendItems={[
        { term: t("termRise"), definition: t("defRise") },
        { term: t("termCool"), definition: t("defCool") },
        { term: t("termGrowth"), definition: t("defGrowth") },
        { term: t("termN"), definition: t("defN") },
        ...(thin ? [{ term: t("termThin"), definition: t("defThin") }] : []),
      ]}
      table={{
        columns: [
          t("legendRise") + "/" + t("legendCool"),
          t("colGrowth"),
          t("colRecent"),
          t("colPrevious"),
          t("colSample"),
        ],
        rows: rows.map((r) => [
          r.technology,
          formatPercentNumber(r.growth_pct),
          r.recent_mentions,
          r.previous_mentions,
          r.sample_size,
        ]),
      }}
      className={className}
    >
      {!empty ? (
        <ReactECharts
          option={option}
          style={{ height, width: "100%" }}
          opts={{ renderer: "svg" }}
        />
      ) : null}
    </ChartFrame>
  );
}
