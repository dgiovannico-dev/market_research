"use client";

/**
 * World choropleth for observed job counts by ISO2.
 * GeoJSON: Apache ECharts examples world.json (BSD-3 / Apache-2.0 project assets).
 * Pin: echarts website examples data asset (fetched once client-side).
 */

import { useTranslations } from "next-intl";
import { useEffect, useMemo, useState } from "react";
import ReactECharts from "echarts-for-react";
import * as echarts from "echarts";
import { ChartFrame } from "./ChartFrame";
import { chartAnimationMs, chartTheme } from "./chartTheme";
import { echartsNameForIso2 } from "./iso2Names";
import { useRouter } from "@/i18n/navigation";

/** Pinned CDN path for ECharts demo world geoJSON (name-keyed features). */
const WORLD_GEO_URL =
  "https://cdn.jsdelivr.net/gh/apache/echarts-website@asf-site/examples/data/asset/geo/world.json";

export type GeoWorldMapItem = {
  country_code: string;
  jobs: number;
};

export type GeoWorldMapProps = {
  items: GeoWorldMapItem[];
  unknownJobs?: number;
  periodDays?: number | null;
  sampleSize?: number | null;
  title?: string;
  className?: string;
  /**
   * Analytics pages: filter in-place (CountryFilter / local selection).
   * When omitted, click drills to Jobs for that ISO2.
   */
  onCountryClick?: (iso2: string) => void;
};

let worldRegistered = false;

async function ensureWorldMap(): Promise<boolean> {
  if (worldRegistered) return true;
  try {
    const res = await fetch(WORLD_GEO_URL);
    if (!res.ok) return false;
    const geo = await res.json();
    echarts.registerMap("world", geo);
    worldRegistered = true;
    return true;
  } catch {
    return false;
  }
}

export function GeoWorldMap({
  items,
  unknownJobs = 0,
  periodDays = null,
  sampleSize = null,
  title,
  className,
  onCountryClick,
}: GeoWorldMapProps) {
  const t = useTranslations("charts");
  const router = useRouter();
  const resolvedTitle = title ?? t("worldMapTitle");
  const [ready, setReady] = useState(worldRegistered);

  useEffect(() => {
    let cancelled = false;
    ensureWorldMap().then((ok) => {
      if (!cancelled) setReady(ok);
    });
    return () => {
      cancelled = true;
    };
  }, []);

  const rows = useMemo(
    () =>
      items
        .filter((it) => it.jobs > 0 && it.country_code && it.country_code !== "unknown")
        .slice()
        .sort((a, b) => b.jobs - a.jobs),
    [items],
  );
  const empty = rows.length === 0;
  const thin = !empty && rows.length < 3;
  const n = sampleSize ?? rows.reduce((s, r) => s + r.jobs, 0);
  const theme = chartTheme();
  const anim = chartAnimationMs();

  const seriesData = useMemo(() => {
    const out: { name: string; value: number; iso2: string }[] = [];
    for (const row of rows) {
      const name = echartsNameForIso2(row.country_code);
      if (!name) continue;
      out.push({ name, value: row.jobs, iso2: row.country_code.toUpperCase() });
    }
    return out;
  }, [rows]);

  const option = useMemo(() => {
    if (empty || !ready) return {};
    const maxVal = Math.max(...seriesData.map((d) => d.value), 1);
    return {
      animationDuration: anim,
      tooltip: {
        trigger: "item",
        formatter: (p: { name?: string; value?: number; data?: { iso2?: string } }) => {
          const iso = p.data?.iso2 ?? "";
          const val = typeof p.value === "number" ? p.value : 0;
          return `${iso || p.name}: ${val}`;
        },
      },
      visualMap: {
        min: 0,
        max: maxVal,
        left: "left",
        bottom: 8,
        text: [t("mapHigh"), t("mapLow")],
        textStyle: { color: theme.ink, fontFamily: theme.mono, fontSize: 10 },
        inRange: { color: ["#e8f2f0", theme.signal] },
        calculable: true,
      },
      series: [
        {
          type: "map",
          map: "world",
          roam: true,
          emphasis: {
            label: { show: false },
            itemStyle: { areaColor: theme.rise },
          },
          data: seriesData,
        },
      ],
    };
  }, [anim, empty, ready, seriesData, t, theme.ink, theme.mono, theme.rise, theme.signal]);

  const onEvents = useMemo(
    () => ({
      click: (params: { data?: { iso2?: string } }) => {
        const iso = params.data?.iso2;
        if (!iso) return;
        if (onCountryClick) {
          onCountryClick(iso);
          return;
        }
        router.push(`/jobs?countries=${encodeURIComponent(iso)}`);
      },
    }),
    [onCountryClick, router],
  );

  return (
    <ChartFrame
      title={resolvedTitle}
      periodDays={periodDays}
      sampleSize={empty ? null : n}
      empty={empty}
      thin={thin}
      guideRepresents={t("guideWorldMap")}
      guideHowToRead={t("guideWorldMapRead")}
      legendItems={[
        { term: t("termCountry"), definition: t("defCountry") },
        { term: t("termJobs"), definition: t("defJobs") },
        { term: t("termN"), definition: t("defN") },
      ]}
      table={{
        columns: [t("colCountry"), t("colJobs")],
        rows: [
          ...rows.map((r) => [r.country_code, r.jobs]),
          ...(unknownJobs > 0 ? [["unknown", unknownJobs]] : []),
        ],
      }}
      className={className}
    >
      {!empty && ready ? (
        <ReactECharts
          option={option}
          style={{ height: 360, width: "100%", cursor: "pointer" }}
          opts={{ renderer: "canvas" }}
          onEvents={onEvents}
        />
      ) : !empty && !ready ? (
        <p className="py-8 text-center text-sm text-[var(--muted)]">{t("mapLoading")}</p>
      ) : null}
      {unknownJobs > 0 ? (
        <p className="mt-2 text-xs text-[var(--muted)]" style={{ fontFamily: "var(--mono)" }}>
          {t("unknownExcluded", { n: unknownJobs })}
        </p>
      ) : null}
    </ChartFrame>
  );
}
