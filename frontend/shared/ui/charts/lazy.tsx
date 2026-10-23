"use client";

import dynamic from "next/dynamic";
import type { ComponentType } from "react";
import type { RiseCoolChartProps } from "./RiseCoolChart";
import type { SparklineProps } from "./Sparkline";
import type { GeoStripProps } from "./GeoStrip";
import type { CompareDualProps } from "./CompareDual";
import type { DonutMixProps } from "./DonutMix";
import type { RankBarsProps } from "./RankBars";
import type { RatesBoxProps } from "./RatesBox";
import type { GeoWorldMapProps } from "./GeoWorldMap";
import type { HeatMatrixProps } from "./HeatMatrix";
import type { MultiSeriesChartProps } from "./MultiSeriesChart";

function ChartSkeleton({ height = 220 }: { height?: number }) {
  return (
    <div
      className="card flex items-center justify-center text-xs opacity-50"
      style={{ height }}
      aria-hidden
    >
      …
    </div>
  );
}

export const RiseCoolChartLazy: ComponentType<RiseCoolChartProps> = dynamic(
  () => import("./RiseCoolChart").then((m) => m.RiseCoolChart),
  { ssr: false, loading: () => <ChartSkeleton height={280} /> },
);

export const SparklineLazy: ComponentType<SparklineProps> = dynamic(
  () => import("./Sparkline").then((m) => m.Sparkline),
  { ssr: false, loading: () => <ChartSkeleton height={140} /> },
);

export const GeoStripLazy: ComponentType<GeoStripProps> = dynamic(
  () => import("./GeoStrip").then((m) => m.GeoStrip),
  { ssr: false, loading: () => <ChartSkeleton height={180} /> },
);

export const CompareDualLazy: ComponentType<CompareDualProps> = dynamic(
  () => import("./CompareDual").then((m) => m.CompareDual),
  { ssr: false, loading: () => <ChartSkeleton height={240} /> },
);

export const DonutMixLazy: ComponentType<DonutMixProps> = dynamic(
  () => import("./DonutMix").then((m) => m.DonutMix),
  { ssr: false, loading: () => <ChartSkeleton height={220} /> },
);

export const RankBarsLazy: ComponentType<RankBarsProps> = dynamic(
  () => import("./RankBars").then((m) => m.RankBars),
  { ssr: false, loading: () => <ChartSkeleton height={220} /> },
);

export const RatesBoxLazy: ComponentType<RatesBoxProps> = dynamic(
  () => import("./RatesBox").then((m) => m.RatesBox),
  { ssr: false, loading: () => <ChartSkeleton height={260} /> },
);

export const GeoWorldMapLazy: ComponentType<GeoWorldMapProps> = dynamic(
  () => import("./GeoWorldMap").then((m) => m.GeoWorldMap),
  { ssr: false, loading: () => <ChartSkeleton height={360} /> },
);

export const HeatMatrixLazy: ComponentType<HeatMatrixProps> = dynamic(
  () => import("./HeatMatrix").then((m) => m.HeatMatrix),
  { ssr: false, loading: () => <ChartSkeleton height={320} /> },
);

export const MultiSeriesChartLazy: ComponentType<MultiSeriesChartProps> = dynamic(
  () => import("./MultiSeriesChart").then((m) => m.MultiSeriesChart),
  { ssr: false, loading: () => <ChartSkeleton height={280} /> },
);
