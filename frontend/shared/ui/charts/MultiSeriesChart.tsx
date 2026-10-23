"use client";

import { useTranslations } from "next-intl";
import { useMemo, useState } from "react";
import ReactECharts from "echarts-for-react";
import { ChartFrame } from "./ChartFrame";
import { chartAnimationMs, chartTheme } from "./chartTheme";
import {
  DEFAULT_CHART_TOP_N,
  isChartTopN,
  type ChartTopN,
} from "./chartTopN";
export type MultiSeriesLine = {
  key: string;
  points: { bucket: string; count: number | null }[];
};

export type MultiSeriesChartProps = {
  series: MultiSeriesLine[];
  periodDays?: number | null;
  sampleSize?: number | null;
  title: string;
  emptyMessage?: string;
  xAxisLabel?: string;
  yAxisLabel?: string;
  className?: string;
  guideRepresents?: string;
  guideHowToRead?: string;
};

const THIN_N = 20;

function seriesPalette(theme: ReturnType<typeof chartTheme>): string[] {
  return [theme.signal, theme.rise, theme.cool, theme.ink, "#b45309", "#7c3aed"];
}

export function MultiSeriesChart({
  series,
  periodDays = null,
  sampleSize = null,
  title,
  emptyMessage,
  xAxisLabel,
  yAxisLabel,
  className,
  guideRepresents,
  guideHowToRead,
}: MultiSeriesChartProps) {
  const t = useTranslations("charts");
  const [topN, setTopN] = useState<ChartTopN>(DEFAULT_CHART_TOP_N);
  const onTopNChange = (n: number) => {
    if (isChartTopN(n)) setTopN(n);
  };

  const lines = series.length > topN ? series.slice(0, topN) : series;
  const empty = lines.length === 0 || lines.every((s) => s.points.length < 2);
  const thin =
    !empty &&
    (sampleSize != null ? sampleSize < THIN_N : lines.every((s) => s.points.length < 4));
  const theme = chartTheme();
  const anim = chartAnimationMs();
  const colors = seriesPalette(theme);

  const buckets = useMemo(() => {
    const seen = new Set<string>();
    const ordered: string[] = [];
    for (const line of lines) {
      for (const p of line.points) {
        if (!seen.has(p.bucket)) {
          seen.add(p.bucket);
          ordered.push(p.bucket);
        }
      }
    }
    return ordered;
  }, [lines]);

  const option = useMemo(() => {
    if (empty) return {};
    return {
      animationDuration: anim,
      legend: {
        type: "scroll",
        bottom: 0,
        textStyle: { color: theme.ink, fontSize: 11 },
      },
      grid: { left: 4, right: 8, top: 12, bottom: 36, containLabel: true },
      tooltip: { trigger: "axis" },
      xAxis: {
        type: "category",
        data: buckets,
        axisLabel: {
          color: theme.ink,
          fontSize: 10,
          rotate: buckets.length > 10 ? 28 : 0,
          hideOverlap: true,
        },
        axisLine: { lineStyle: { color: theme.line } },
      },
      yAxis: {
        type: "value",
        axisLabel: { color: theme.ink, fontFamily: theme.mono, fontSize: 10 },
        splitLine: { lineStyle: { color: theme.line, opacity: 0.5 } },
      },
      series: lines.map((line, i) => {
        const byBucket = new Map(line.points.map((p) => [p.bucket, p.count]));
        const color = colors[i % colors.length];
        return {
          name: line.key,
          type: "line",
          data: buckets.map((b) => byBucket.get(b) ?? null),
          smooth: anim > 0,
          symbol: "circle",
          symbolSize: 4,
          connectNulls: false,
          lineStyle: { color, width: 2 },
          itemStyle: { color },
        };
      }),
    };
  }, [anim, buckets, colors, empty, lines, theme]);

  const table = useMemo(() => {
    if (empty) return null;
    const columns = [xAxisLabel ?? t("axisDay"), ...lines.map((l) => l.key)];
    const rows = buckets.map((bucket) => {
      const cells: (string | number | null)[] = [bucket];
      for (const line of lines) {
        const hit = line.points.find((p) => p.bucket === bucket);
        cells.push(hit?.count ?? null);
      }
      return cells;
    });
    return { columns, rows };
  }, [buckets, empty, lines, t, xAxisLabel]);

  return (
    <ChartFrame
      title={title}
      periodDays={periodDays}
      sampleSize={sampleSize}
      empty={empty}
      thin={thin}
      emptyMessage={emptyMessage}
      table={table}
      topN={topN}
      onTopNChange={onTopNChange}
      xAxisLabel={xAxisLabel}
      yAxisLabel={yAxisLabel ?? t("axisJobs")}
      guideRepresents={guideRepresents ?? t("guideMultiSeries")}
      guideHowToRead={guideHowToRead ?? t("guideMultiSeriesRead")}
      className={className}
    >
      <ReactECharts
        option={option}
        style={{ height: 280, width: "100%" }}
        opts={{ renderer: "canvas" }}
        notMerge
      />
    </ChartFrame>
  );
}
