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

export type GeoStripItem = {
  country_code: string;
  jobs: number;
};

export type GeoStripProps = {
  items: GeoStripItem[];
  periodDays?: number | null;
  title?: string;
  className?: string;
  /** Initial / override max bars; user can change via ChartFrame top-N control. */
  maxBars?: number;
};

export function GeoStrip({
  items,
  periodDays = null,
  title,
  className,
  maxBars,
}: GeoStripProps) {
  const t = useTranslations("charts");
  const resolvedTitle = title ?? t("geoTitle");
  const initialTopN: ChartTopN =
    maxBars != null && isChartTopN(maxBars) ? maxBars : DEFAULT_CHART_TOP_N;
  const [topN, setTopN] = useState<ChartTopN>(initialTopN);
  const onTopNChange = (n: number) => {
    if (isChartTopN(n)) setTopN(n);
  };
  const rows = useMemo(
    () =>
      items
        .filter((it) => it.jobs > 0 && it.country_code && it.country_code !== "unknown")
        .slice()
        .sort((a, b) => b.jobs - a.jobs)
        .slice(0, topN),
    [items, topN],
  );
  const empty = rows.length === 0;
  const thin = !empty && rows.length < 3;
  const sampleSize = rows.reduce((s, r) => s + r.jobs, 0);
  const theme = chartTheme();
  const anim = chartAnimationMs();

  const option = useMemo(() => {
    if (empty) return {};
    const labels = rows.map((r) => r.country_code).reverse();
    const values = rows.map((r) => r.jobs).reverse();
    return {
      animationDuration: anim,
      grid: { left: 4, right: 44, top: 8, bottom: 4, containLabel: true },
      tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
      xAxis: {
        type: "value",
        axisLabel: { color: theme.ink, fontFamily: theme.mono, fontSize: 10 },
        splitLine: { lineStyle: { color: theme.line, opacity: 0.5 } },
        axisLine: { show: false },
      },
      yAxis: {
        type: "category",
        data: labels,
        axisLabel: { color: theme.ink, fontSize: 12, fontFamily: theme.mono },
        axisTick: { show: false },
        axisLine: { show: false },
      },
      series: [
        {
          type: "bar",
          data: values,
          barMaxWidth: 14,
          itemStyle: { color: theme.signal, borderRadius: [0, 4, 4, 0] },
          label: {
            show: true,
            position: "right",
            distance: 6,
            color: theme.ink,
            fontFamily: theme.mono,
            fontSize: 10,
          },
        },
      ],
    };
  }, [anim, empty, rows, theme]);

  const height = Math.max(160, rows.length * 28 + 24);

  return (
    <ChartFrame
      title={resolvedTitle}
      periodDays={periodDays}
      sampleSize={empty ? null : sampleSize}
      empty={empty}
      thin={thin}
      topN={topN}
      onTopNChange={onTopNChange}
      xAxisLabel={t("axisJobs")}
      guideRepresents={t("guideWorldMap")}
      guideHowToRead={t("guideWorldMapRead")}
      legendItems={[
        { term: t("termCountry"), definition: t("defCountry") },
        { term: t("termJobs"), definition: t("defJobs") },
        { term: t("termN"), definition: t("defN") },
      ]}
      table={{
        columns: [t("colCountry"), t("colJobs")],
        rows: rows.map((r) => [r.country_code, r.jobs]),
      }}
      className={className}
    >
      {!empty ? (
        <ReactECharts option={option} style={{ height, width: "100%" }} opts={{ renderer: "svg" }} />
      ) : null}
    </ChartFrame>
  );
}
