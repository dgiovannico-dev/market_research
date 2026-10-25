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

export type RankBarsItem = {
  label: string;
  value: number;
};

export type RankBarsProps = {
  items: RankBarsItem[];
  periodDays?: number | null;
  sampleSize?: number | null;
  title: string;
  className?: string;
  maxBars?: number;
  valueLabel?: string;
  /** When set, bar click reports the category label (for deep-links). */
  onBarClick?: (label: string) => void;
};

export function RankBars({
  items,
  periodDays = null,
  sampleSize = null,
  title,
  className,
  maxBars,
  valueLabel,
  onBarClick,
}: RankBarsProps) {
  const t = useTranslations("charts");
  const initialTopN: ChartTopN =
    maxBars != null && isChartTopN(maxBars) ? maxBars : DEFAULT_CHART_TOP_N;
  const [topN, setTopN] = useState<ChartTopN>(initialTopN);
  const onTopNChange = (n: number) => {
    if (isChartTopN(n)) setTopN(n);
  };
  const rows = useMemo(
    () =>
      items
        .filter((it) => it.value > 0 && it.label)
        .slice()
        .sort((a, b) => b.value - a.value)
        .slice(0, topN),
    [items, topN],
  );
  const empty = rows.length === 0;
  const thin = !empty && rows.length < 3;
  const n = sampleSize ?? rows.reduce((s, r) => s + r.value, 0);
  const theme = chartTheme();
  const anim = chartAnimationMs();
  const colValue = valueLabel ?? t("colJobs");

  const option = useMemo(() => {
    if (empty) return {};
    const labels = rows.map((r) => r.label).reverse();
    const values = rows.map((r) => r.value).reverse();
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
        axisLabel: {
          color: theme.ink,
          fontSize: 12,
          fontFamily: theme.mono,
          width: 96,
          overflow: "truncate",
        },
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
  }, [anim, colValue, empty, rows, theme]);

  const height = Math.max(160, rows.length * 28 + 24);

  const onEvents = useMemo(() => {
    if (!onBarClick) return undefined;
    return {
      click: (params: {
        name?: string;
        componentType?: string;
        dataIndex?: number;
      }) => {
        if (params.componentType !== "series") return;
        let label = params.name ? String(params.name) : "";
        if (!label && typeof params.dataIndex === "number") {
          // Category axis is reversed for display; map dataIndex back.
          const labels = rows.map((r) => r.label).reverse();
          label = labels[params.dataIndex] ?? "";
        }
        if (label) onBarClick(label);
      },
    };
  }, [onBarClick, rows]);

  return (
    <ChartFrame
      title={title}
      periodDays={periodDays}
      sampleSize={empty ? null : n}
      empty={empty}
      thin={thin}
      topN={topN}
      onTopNChange={onTopNChange}
      xAxisLabel={colValue}
      guideRepresents={t("guideRankBars")}
      guideHowToRead={t("guideRankBarsRead")}
      legendItems={[
        { term: t("termRankLabel"), definition: t("defRankLabel") },
        { term: t("termJobs"), definition: t("defJobs") },
        { term: t("termN"), definition: t("defN") },
      ]}
      table={{
        columns: [t("colLabel"), colValue],
        rows: rows.map((r) => [r.label, r.value]),
      }}
      className={className}
    >
      {!empty ? (
        <ReactECharts
          option={option}
          style={{
            height,
            width: "100%",
            cursor: onBarClick ? "pointer" : undefined,
          }}
          opts={{ renderer: "svg" }}
          onEvents={onEvents}
        />
      ) : null}
    </ChartFrame>
  );
}
