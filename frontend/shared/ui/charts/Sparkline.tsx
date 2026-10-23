"use client";

import { useTranslations } from "next-intl";
import { useMemo } from "react";
import ReactECharts from "echarts-for-react";
import { ChartFrame } from "./ChartFrame";
import { chartAnimationMs, chartTheme } from "./chartTheme";

export type SparkPoint = {
  label: string;
  value: number;
};

export type SparklineProps = {
  points: SparkPoint[];
  periodDays?: number | null;
  sampleSize?: number | null;
  title?: string;
  emptyMessage?: string;
  className?: string;
};

export function Sparkline({
  points,
  periodDays = null,
  sampleSize = null,
  title,
  emptyMessage,
  className,
}: SparklineProps) {
  const t = useTranslations("charts");
  const resolvedTitle = title ?? t("sparklineTitle");
  const empty = points.length < 2;
  const thin = !empty && (points.length < 5 || (sampleSize != null && sampleSize < 20));
  const theme = chartTheme();
  const anim = chartAnimationMs();

  const option = useMemo(() => {
    if (empty) return {};
    return {
      animationDuration: anim,
      grid: { left: 4, right: 8, top: 8, bottom: 4, containLabel: true },
      xAxis: {
        type: "category",
        data: points.map((p) => p.label),
        axisLabel: {
          color: theme.ink,
          fontFamily: theme.mono,
          fontSize: 9,
          hideOverlap: true,
          rotate: points.length > 14 ? 32 : 0,
        },
        axisTick: { show: false },
        axisLine: { lineStyle: { color: theme.line } },
      },
      yAxis: {
        type: "value",
        scale: true,
        axisLabel: { color: theme.ink, fontFamily: theme.mono, fontSize: 10 },
        splitLine: { lineStyle: { color: theme.line, opacity: 0.5 } },
      },
      tooltip: {
        trigger: "axis",
        valueFormatter: (v: number) => String(v),
      },
      series: [
        {
          type: "line",
          data: points.map((p) => p.value),
          smooth: anim > 0,
          symbol: "none",
          lineStyle: { color: theme.signal, width: 2 },
          areaStyle: {
            color: {
              type: "linear",
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                { offset: 0, color: `${theme.signal}33` },
                { offset: 1, color: `${theme.signal}00` },
              ],
            },
          },
        },
      ],
    };
  }, [anim, empty, points, theme]);

  return (
    <ChartFrame
      title={resolvedTitle}
      periodDays={periodDays}
      sampleSize={sampleSize}
      empty={empty}
      thin={thin}
      emptyMessage={emptyMessage}
      yAxisLabel={t("axisJobs")}
      xAxisLabel={t("axisDay")}
      guideRepresents={t("guideSparkline")}
      guideHowToRead={t("guideSparklineRead")}
      legendItems={[
        { term: t("termN"), definition: t("defN") },
        ...(thin
          ? [{ term: t("termThin"), definition: t("defThin") }]
          : []),
      ]}
      table={{
        columns: [t("axisDay"), t("axisJobs")],
        rows: points.map((p) => [p.label, p.value]),
      }}
      className={className}
    >
      {!empty ? (
        <ReactECharts option={option} style={{ height: 200, width: "100%" }} opts={{ renderer: "svg" }} />
      ) : null}
    </ChartFrame>
  );
}
