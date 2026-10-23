/** Shared top-N options for ranked charts (not time-series sparklines). */

export const CHART_TOP_N_OPTIONS = [5, 10, 15, 20, 30] as const;

export type ChartTopN = (typeof CHART_TOP_N_OPTIONS)[number];

export const DEFAULT_CHART_TOP_N: ChartTopN = 10;

export function isChartTopN(value: number): value is ChartTopN {
  return (CHART_TOP_N_OPTIONS as readonly number[]).includes(value);
}
