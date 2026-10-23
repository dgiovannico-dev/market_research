import type { SparkPoint } from "@/shared/ui/charts";

function asNumber(value: unknown): number | null {
  if (value == null) return null;
  const n = typeof value === "number" ? value : Number(value);
  return Number.isFinite(n) ? n : null;
}

function pointsFromRows(rows: unknown): SparkPoint[] {
  if (!Array.isArray(rows)) return [];
  const points: SparkPoint[] = [];
  for (const row of rows) {
    if (!row || typeof row !== "object") continue;
    const r = row as Record<string, unknown>;
    const label = String(r.day ?? r.label ?? r.date ?? "").trim();
    const value = asNumber(r.jobs ?? r.value ?? r.count);
    if (!label || value == null) continue;
    points.push({ label, value });
  }
  return points;
}

/**
 * Extract jobs/day sparkline points from `/dashboard/summary`.
 * Compare lens nests series under `market` / `focus` — prefer market for the strip.
 */
export function extractJobsPerDayPoints(summary: unknown): SparkPoint[] {
  if (!summary || typeof summary !== "object") return [];
  const s = summary as Record<string, unknown>;
  const direct = pointsFromRows(s.jobs_per_day);
  if (direct.length) return direct;

  for (const key of ["market", "focus"] as const) {
    const nest = s[key];
    if (!nest || typeof nest !== "object") continue;
    const nested = pointsFromRows((nest as Record<string, unknown>).jobs_per_day);
    if (nested.length) return nested;
  }
  return [];
}
