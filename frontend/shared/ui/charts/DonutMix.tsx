"use client";

import { useTranslations } from "next-intl";
import { useMemo } from "react";
import ReactECharts from "echarts-for-react";
import { ChartFrame } from "./ChartFrame";
import { chartAnimationMs, chartTheme } from "./chartTheme";
import { formatPercent, formatPercentNumber } from "@/shared/lib/formatPercent";

export type DonutMixItem = {
  key: string;
  jobs: number;
};

export type DonutMixProps = {
  items: DonutMixItem[];
  periodDays?: number | null;
  sampleSize?: number | null;
  title: string;
  className?: string;
};

export function DonutMix({
  items,
  periodDays = null,
  sampleSize = null,
  title,
  className,
}: DonutMixProps) {
  const t = useTranslations("charts");
  const rows = useMemo(
    () =>
      items
        .filter((it) => it.jobs > 0)
        .slice()
        .sort((a, b) => b.jobs - a.jobs),
    [items],
  );
  const empty = rows.length === 0;
  const thin = !empty && (sampleSize ?? rows.reduce((s, r) => s + r.jobs, 0)) < 10;
  const n = sampleSize ?? rows.reduce((s, r) => s + r.jobs, 0);
  const theme = chartTheme();
  const anim = chartAnimationMs();
  const palette = [
    theme.signal,
    theme.rise,
    theme.cool,
    "#0f766e",
    "#0369a1",
    "#57534e",
    "#a8a29e",
  ];

  const option = useMemo(() => {
    if (empty) return {};
    return {
      animationDuration: anim,
      tooltip: {
        trigger: "item",
        formatter: (p: { name?: string; value?: number; percent?: number }) => {
          const pct =
            typeof p.percent === "number" ? formatPercent(p.percent) : "";
          return `${p.name ?? ""}: ${p.value ?? ""} (${pct})`;
        },
      },
      legend: {
        type: "scroll",
        orient: "vertical",
        right: 0,
        top: "middle",
        itemWidth: 10,
        itemHeight: 10,
        textStyle: {
          color: theme.ink,
          fontFamily: theme.mono,
          fontSize: 10,
        },
        formatter: (name: string) => {
          const row = rows.find((r) => r.key === name);
          if (!row || n <= 0) return name;
          return `${name}  ${formatPercent((row.jobs / n) * 100)}`;
        },
      },
      series: [
        {
          type: "pie",
          radius: ["42%", "68%"],
          center: ["36%", "50%"],
          avoidLabelOverlap: true,
          minShowLabelAngle: 12,
          itemStyle: { borderRadius: 4, borderColor: theme.card, borderWidth: 2 },
          label: {
            color: theme.ink,
            fontFamily: theme.mono,
            fontSize: 10,
            formatter: (p: { percent?: number }) =>
              typeof p.percent === "number" ? formatPercent(p.percent) : "",
          },
          labelLayout: { hideOverlap: true },
          labelLine: { length: 12, length2: 10, maxSurfaceAngle: 80 },
          data: rows.map((r, i) => ({
            name: r.key,
            value: r.jobs,
            itemStyle: {
              color: palette[i % palette.length],
            },
          })),
        },
      ],
    };
  }, [anim, empty, n, palette, rows, theme.card, theme.ink, theme.mono]);

  return (
    <ChartFrame
      title={title}
      periodDays={periodDays}
      sampleSize={empty ? null : n}
      empty={empty}
      thin={thin}
      guideRepresents={t("guideDonutMix")}
      guideHowToRead={t("guideDonutMixRead")}
      legendItems={[
        { term: t("termMixKey"), definition: t("defMixKey") },
        { term: t("termJobs"), definition: t("defJobs") },
        { term: t("termN"), definition: t("defN") },
      ]}
      table={{
        columns: [t("colKey"), t("colJobs"), t("colPct")],
        rows: rows.map((r) => {
          const pct = n > 0 ? formatPercentNumber((r.jobs / n) * 100) : "0.00";
          return [r.key, r.jobs, `${pct}%`];
        }),
      }}
      className={className}
    >
      {!empty ? (
        <ReactECharts option={option} style={{ height: 260, width: "100%" }} opts={{ renderer: "svg" }} />
      ) : null}
    </ChartFrame>
  );
}
