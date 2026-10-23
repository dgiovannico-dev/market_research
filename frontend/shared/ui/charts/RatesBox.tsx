"use client";

import { useTranslations } from "next-intl";
import { useMemo } from "react";
import ReactECharts from "echarts-for-react";
import { ChartFrame } from "./ChartFrame";
import { chartAnimationMs, chartTheme } from "./chartTheme";
export type RatesBoxItem = {
  country_code: string;
  currency: string;
  unit: string;
  sample_size: number;
  median: number | null;
  p25: number | null;
  p75: number | null;
  status: string;
};

export type RatesBoxProps = {
  items: RatesBoxItem[];
  periodDays?: number | null;
  sampleSize?: number | null;
  title?: string;
  className?: string;
  maxBoxes?: number;
};

export function RatesBox({
  items,
  periodDays = null,
  sampleSize = null,
  title,
  className,
  maxBoxes = 8,
}: RatesBoxProps) {
  const t = useTranslations("charts");
  const resolvedTitle = title ?? t("ratesBoxTitle");
  const rows = useMemo(
    () =>
      items
        .filter((it) => it.median != null && it.sample_size > 0)
        .slice()
        .sort((a, b) => (b.sample_size || 0) - (a.sample_size || 0))
        .slice(0, maxBoxes),
    [items, maxBoxes],
  );
  const empty = rows.length === 0;
  const thin = !empty && rows.every((r) => r.sample_size < 5);
  const n = sampleSize ?? rows.reduce((s, r) => s + r.sample_size, 0);
  const theme = chartTheme();
  const anim = chartAnimationMs();

  const option = useMemo(() => {
    if (empty) return {};
    const cats = rows.map(
      (r) => `${r.country_code} · ${r.currency}/${r.unit}`,
    );
    return {
      animationDuration: anim,
      grid: { left: 4, right: 8, top: 12, bottom: 4, containLabel: true },
      tooltip: {
        trigger: "axis",
        formatter: (params: { dataIndex: number }[]) => {
          const idx = params[0]?.dataIndex ?? 0;
          const r = rows[idx];
          if (!r) return "";
          return [
            cats[idx],
            `${t("termMedian")}: ${r.median}`,
            `${t("colP25")}: ${r.p25 ?? "—"}`,
            `${t("colP75")}: ${r.p75 ?? "—"}`,
            `n=${r.sample_size}`,
          ].join("<br/>");
        },
      },
      xAxis: {
        type: "category",
        data: cats,
        axisLabel: {
          color: theme.ink,
          fontFamily: theme.mono,
          fontSize: 9,
          rotate: 30,
          interval: 0,
          hideOverlap: true,
        },
        axisTick: { show: false },
        axisLine: { lineStyle: { color: theme.line } },
      },
      yAxis: {
        type: "value",
        axisLabel: { color: theme.ink, fontFamily: theme.mono, fontSize: 10 },
        splitLine: { lineStyle: { color: theme.line, opacity: 0.5 } },
      },
      series: [
        {
          name: t("termMedian"),
          type: "bar",
          data: rows.map((r) => r.median),
          barMaxWidth: 28,
          itemStyle: { color: theme.signal, borderRadius: [4, 4, 0, 0] },
        },
      ],
    };
  }, [anim, empty, rows, t, theme]);

  return (
    <ChartFrame
      title={resolvedTitle}
      periodDays={periodDays}
      sampleSize={empty ? null : n}
      empty={empty}
      thin={thin}
      yAxisLabel={t("axisMedian")}
      guideRepresents={t("guideRatesBox")}
      guideHowToRead={t("guideRatesBoxRead")}
      legendItems={[
        { term: t("termMedian"), definition: t("defMedian") },
        { term: t("termIqr"), definition: t("defIqr") },
        { term: t("termN"), definition: t("defN") },
      ]}
      table={{
        columns: [
          t("colCountry"),
          t("colCurrency"),
          t("colUnit"),
          t("colMedian"),
          t("colP25"),
          t("colP75"),
          t("colSample"),
        ],
        rows: rows.map((r) => [
          r.country_code,
          r.currency,
          r.unit,
          r.median,
          r.p25,
          r.p75,
          r.sample_size,
        ]),
      }}
      className={className}
    >
      {!empty ? (
        <ReactECharts option={option} style={{ height: 260, width: "100%" }} opts={{ renderer: "svg" }} />
      ) : null}
    </ChartFrame>
  );
}
