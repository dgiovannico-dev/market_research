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
import {
  buildTechGraph,
  type TechGraphPair,
} from "@/shared/lib/buildTechGraph";

export type TechCooccurGraphProps = {
  pairs: TechGraphPair[];
  periodDays: number;
  sampleSize?: number | null;
  seed?: string | null;
  title?: string;
  className?: string;
  onNodeClick?: (tech: string) => void;
};

export function TechCooccurGraph({
  pairs,
  periodDays,
  sampleSize = null,
  seed = null,
  title,
  className,
  onNodeClick,
}: TechCooccurGraphProps) {
  const t = useTranslations("charts");
  const resolvedTitle = title ?? t("techGraphTitle");
  const [topN, setTopN] = useState<ChartTopN>(DEFAULT_CHART_TOP_N);
  const onTopNChange = (n: number) => {
    if (isChartTopN(n)) setTopN(n);
  };

  const graph = useMemo(
    () => buildTechGraph(pairs, topN, seed),
    [pairs, seed, topN],
  );
  const empty = graph.nodes.length === 0;
  const thin = !empty && graph.nodes.length < 3;
  const theme = chartTheme();
  const anim = chartAnimationMs();

  const option = useMemo(() => {
    if (empty) return {};
    const categories = [
      { name: t("techGraphSeedCategory") },
      { name: t("techGraphNeighborCategory") },
    ];
    return {
      animationDuration: anim,
      tooltip: {
        formatter: (params: {
          dataType?: string;
          name?: string;
          data?: {
            name?: string;
            value?: number;
            support?: number;
            lift?: number | null;
          };
        }) => {
          if (params.dataType === "edge") {
            const d = params.data ?? {};
            const lift =
              d.lift != null ? ` · lift ${d.lift}` : "";
            return `${params.name ?? ""}<br/>support=${d.support ?? "—"}${lift}`;
          }
          const d = params.data ?? {};
          return `${d.name ?? params.name}<br/>n≈${d.value ?? "—"}`;
        },
      },
      series: [
        {
          type: "graph",
          layout: "force",
          roam: true,
          draggable: true,
          categories,
          label: {
            show: true,
            position: "right",
            fontSize: 11,
            color: theme.ink,
          },
          force: {
            repulsion: 180,
            edgeLength: [40, 120],
            gravity: 0.08,
          },
          data: graph.nodes.map((n) => ({
            id: n.id,
            name: n.name,
            value: n.value,
            category: n.category ?? 1,
            symbolSize: Math.max(12, Math.min(40, 10 + Math.sqrt(n.value))),
            itemStyle: {
              color:
                seed &&
                n.id.toLowerCase() === String(seed).trim().toLowerCase()
                  ? theme.signal
                  : theme.rise,
            },
          })),
          links: graph.links.map((l) => ({
            source: l.source,
            target: l.target,
            support: l.support,
            lift: l.lift,
            name: `${l.source} — ${l.target}`,
            lineStyle: {
              width: l.lineWidth,
              color: theme.line,
              opacity: 0.75,
              curveness: 0.1,
            },
          })),
          lineStyle: { opacity: 0.7 },
          emphasis: { focus: "adjacency" },
        },
      ],
    };
  }, [anim, empty, graph, seed, t, theme]);

  const onEvents = useMemo(() => {
    if (!onNodeClick) return undefined;
    return {
      click: (params: { dataType?: string; data?: { id?: string; name?: string } }) => {
        if (params.dataType !== "node") return;
        const id = params.data?.id ?? params.data?.name;
        if (id) onNodeClick(String(id));
      },
    };
  }, [onNodeClick]);

  return (
    <ChartFrame
      title={resolvedTitle}
      periodDays={periodDays}
      sampleSize={empty ? null : sampleSize}
      empty={empty}
      thin={thin}
      topN={topN}
      onTopNChange={onTopNChange}
      guideRepresents={t("guideTechGraph")}
      guideHowToRead={t("guideTechGraphRead")}
      legendItems={[
        { term: t("termTechGraphEdge"), definition: t("defTechGraphEdge") },
        { term: t("termTechGraphSupport"), definition: t("defTechGraphSupport") },
        { term: t("termN"), definition: t("defN") },
      ]}
      table={{
        columns: [
          t("colTechA"),
          t("colTechB"),
          t("colSupport"),
          t("colLift"),
        ],
        rows: graph.links.map((l) => [
          l.source,
          l.target,
          l.support,
          l.lift ?? "—",
        ]),
      }}
      className={className}
    >
      {!empty ? (
        <ReactECharts
          option={option}
          style={{ height: 420, width: "100%" }}
          opts={{ renderer: "svg" }}
          onEvents={onEvents}
        />
      ) : null}
    </ChartFrame>
  );
}
