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

export type CompareSeriesPoint = {
  label: string;
  market: number | null;
  focus: number | null;
};

export type CompareDualProps = {
  points: CompareSeriesPoint[];
  periodDays?: number | null;
  sampleSize?: number | null;
  title?: string;
  emptyMessage?: string;
  className?: string;
};

/** Dual-line market vs focus. Honest empty when either series is missing. */
export function CompareDual({
  points,
  periodDays = null,
  sampleSize = null,
  title,
  emptyMessage,
  className,
}: CompareDualProps) {
  const t = useTranslations("charts");
  const resolvedTitle = title ?? t("compareTitle");
  const marketLabel = t("legendMarket");
  const focusLabel = t("legendFocus");
  const [topN, setTopN] = useState<ChartTopN>(DEFAULT_CHART_TOP_N);
  const onTopNChange = (n: number) => {
    if (isChartTopN(n)) setTopN(n);
  };
  const chartPoints = points.length > topN ? points.slice(0, topN) : points;
  const hasMarket = chartPoints.some((p) => p.market != null);
  const hasFocus = chartPoints.some((p) => p.focus != null);
  const empty = chartPoints.length < 2 || !hasMarket || !hasFocus;
  const thin = !empty && (chartPoints.length < 5 || (sampleSize != null && sampleSize < 20));
  const theme = chartTheme();
  const anim = chartAnimationMs();

  const option = useMemo(() => {
    if (empty) return {};
    return {
      animationDuration: anim,
      legend: {
        data: [marketLabel, focusLabel],
        bottom: 0,
        textStyle: { color: theme.ink, fontSize: 11 },
      },
      grid: { left: 4, right: 8, top: 12, bottom: 28, containLabel: true },
      tooltip: { trigger: "axis" },
      xAxis: {
        type: "category",
        data: chartPoints.map((p) => p.label),
        axisLabel: {
          color: theme.ink,
          fontSize: 10,
          rotate: chartPoints.length > 8 ? 28 : 0,
          hideOverlap: true,
        },
        axisLine: { lineStyle: { color: theme.line } },
      },
      yAxis: {
        type: "value",
        axisLabel: { color: theme.ink, fontFamily: theme.mono, fontSize: 10 },
        splitLine: { lineStyle: { color: theme.line, opacity: 0.5 } },
      },
      series: [
        {
          name: marketLabel,
          type: "line",
          data: chartPoints.map((p) => p.market),
          smooth: anim > 0,
          symbol: "circle",
          symbolSize: 5,
          lineStyle: { color: theme.signal, width: 2 },
          itemStyle: { color: theme.signal },
        },
        {
          name: focusLabel,
          type: "line",
          data: chartPoints.map((p) => p.focus),
          smooth: anim > 0,
          symbol: "circle",
          symbolSize: 5,
          lineStyle: { color: theme.rise, width: 2 },
          itemStyle: { color: theme.rise },
        },
      ],
    };
  }, [anim, chartPoints, empty, focusLabel, marketLabel, theme]);

  return (
    <ChartFrame
      title={resolvedTitle}
      periodDays={periodDays}
      sampleSize={sampleSize}
      empty={empty}
      thin={thin}
      emptyMessage={emptyMessage}
      topN={topN}
      onTopNChange={onTopNChange}
      yAxisLabel={t("axisMentions")}
      guideRepresents={t("guideCompareDual")}
      guideHowToRead={t("guideCompareDualRead")}
      legendItems={[
        { term: t("termMarket"), definition: t("defMarket") },
        { term: t("termFocus"), definition: t("defFocus") },
        { term: t("termN"), definition: t("defN") },
        ...(thin
          ? [{ term: t("termThin"), definition: t("defThin") }]
          : []),
      ]}
      table={{
        columns: [t("colLabel"), marketLabel, focusLabel],
        rows: chartPoints.map((p) => [p.label, p.market, p.focus]),
      }}
      className={className}
    >
      {!empty ? (
        <ReactECharts option={option} style={{ height: 240, width: "100%" }} opts={{ renderer: "svg" }} />
      ) : null}
    </ChartFrame>
  );
}
