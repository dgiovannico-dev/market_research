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

export type HeatCell = [xIndex: number, yIndex: number, value: number];

export type HeatMatrixProps = {
  xLabels: string[];
  yLabels: string[];
  values: HeatCell[];
  periodDays?: number | null;
  sampleSize?: number | null;
  title: string;
  emptyMessage?: string;
  xAxisLabel?: string;
  yAxisLabel?: string;
  valueLabel?: string;
  className?: string;
  /** When false, ChartFrame top-N control is hidden (parent already capped). */
  showTopN?: boolean;
  guideRepresents?: string;
  guideHowToRead?: string;
};

const THIN_N = 20;

function truncateHeat(
  xLabels: string[],
  yLabels: string[],
  values: HeatCell[],
  topN: number,
): { xLabels: string[]; yLabels: string[]; values: HeatCell[] } {
  const xCap = Math.min(topN, xLabels.length);
  const yCap = Math.min(topN, yLabels.length);
  if (xCap === xLabels.length && yCap === yLabels.length) {
    return { xLabels, yLabels, values };
  }
  const nextX = xLabels.slice(0, xCap);
  const nextY = yLabels.slice(0, yCap);
  const nextValues: HeatCell[] = [];
  for (const [xi, yi, v] of values) {
    if (xi < xCap && yi < yCap) nextValues.push([xi, yi, v]);
  }
  return { xLabels: nextX, yLabels: nextY, values: nextValues };
}

export function HeatMatrix({
  xLabels,
  yLabels,
  values,
  periodDays = null,
  sampleSize = null,
  title,
  emptyMessage,
  xAxisLabel,
  yAxisLabel,
  valueLabel,
  className,
  showTopN = true,
  guideRepresents,
  guideHowToRead,
}: HeatMatrixProps) {
  const t = useTranslations("charts");
  const [topN, setTopN] = useState<ChartTopN>(DEFAULT_CHART_TOP_N);
  const onTopNChange = (n: number) => {
    if (isChartTopN(n)) setTopN(n);
  };

  const sliced = useMemo(
    () =>
      showTopN
        ? truncateHeat(xLabels, yLabels, values, topN)
        : { xLabels, yLabels, values },
    [showTopN, topN, values, xLabels, yLabels],
  );

  const empty = sliced.xLabels.length === 0 || sliced.values.length === 0;
  const thin =
    !empty &&
    (sampleSize != null ? sampleSize < THIN_N : sliced.values.length < 4);
  const theme = chartTheme();
  const anim = chartAnimationMs();
  const resolvedValue = valueLabel ?? t("colJobs");

  const maxVal = useMemo(() => {
    let max = 0;
    for (const [, , v] of sliced.values) {
      if (v > max) max = v;
    }
    return max > 0 ? max : 1;
  }, [sliced.values]);

  const option = useMemo(() => {
    if (empty) return {};
    return {
      animationDuration: anim,
      tooltip: {
        position: "top",
        formatter: (p: { data?: HeatCell }) => {
          const cell = p.data;
          if (!cell) return "";
          const [xi, yi, v] = cell;
          return `${sliced.yLabels[yi] ?? "?"} × ${sliced.xLabels[xi] ?? "?"} · ${resolvedValue}: ${v}`;
        },
      },
      grid: {
        left: 4,
        right: 8,
        top: 8,
        bottom: sliced.xLabels.length > 8 ? 48 : 36,
        containLabel: true,
      },
      xAxis: {
        type: "category",
        data: sliced.xLabels,
        splitArea: { show: true },
        axisLabel: {
          color: theme.ink,
          fontSize: 10,
          rotate: sliced.xLabels.length > 6 ? 32 : 0,
          hideOverlap: true,
        },
        axisLine: { lineStyle: { color: theme.line } },
      },
      yAxis: {
        type: "category",
        data: sliced.yLabels,
        splitArea: { show: true },
        axisLabel: {
          color: theme.ink,
          fontSize: 10,
          width: 96,
          overflow: "truncate",
        },
        axisLine: { lineStyle: { color: theme.line } },
      },
      visualMap: {
        min: 0,
        max: maxVal,
        calculable: true,
        orient: "horizontal",
        left: "center",
        bottom: 0,
        itemWidth: 12,
        itemHeight: 80,
        textStyle: { color: theme.ink, fontSize: 10, fontFamily: theme.mono },
        inRange: {
          color: [theme.line, theme.cool, theme.signal],
        },
      },
      series: [
        {
          type: "heatmap",
          data: sliced.values,
          label: {
            show: sliced.values.length <= 120,
            color: theme.ink,
            fontSize: 9,
            fontFamily: theme.mono,
          },
          emphasis: {
            itemStyle: { shadowBlur: 6, shadowColor: "rgba(0,0,0,0.2)" },
          },
        },
      ],
    };
  }, [anim, empty, maxVal, resolvedValue, sliced, theme]);

  const height = Math.max(260, sliced.yLabels.length * 28 + 72);

  const table = useMemo(() => {
    if (empty) return null;
    const rows = sliced.values.map(([xi, yi, v]) => [
      sliced.yLabels[yi] ?? "",
      sliced.xLabels[xi] ?? "",
      v,
    ]);
    return {
      columns: [yAxisLabel ?? t("axisTechnology"), xAxisLabel ?? t("axisCountry"), resolvedValue],
      rows,
    };
  }, [empty, resolvedValue, sliced, t, xAxisLabel, yAxisLabel]);

  return (
    <ChartFrame
      title={title}
      periodDays={periodDays}
      sampleSize={sampleSize}
      empty={empty}
      thin={thin}
      emptyMessage={emptyMessage}
      table={table}
      topN={showTopN ? topN : undefined}
      onTopNChange={showTopN ? onTopNChange : undefined}
      xAxisLabel={xAxisLabel}
      yAxisLabel={yAxisLabel}
      guideRepresents={guideRepresents ?? t("guideHeatDefault")}
      guideHowToRead={guideHowToRead ?? t("guideHeatDefaultRead")}
      className={className}
    >
      <ReactECharts
        option={option}
        style={{ height, width: "100%" }}
        opts={{ renderer: "canvas" }}
        notMerge
      />
    </ChartFrame>
  );
}
