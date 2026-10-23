import type { CompareSeriesPoint } from "@/shared/ui/charts";

function asNumber(value: unknown): number | null {
  if (value == null) return null;
  const n = typeof value === "number" ? value : Number(value);
  return Number.isFinite(n) ? n : null;
}

function pointFromUnknown(row: unknown): CompareSeriesPoint | null {
  if (!row || typeof row !== "object") return null;
  const r = row as Record<string, unknown>;
  const label = String(r.label ?? r.period ?? r.bucket ?? r.technology ?? "").trim();
  if (!label) return null;
  const market = asNumber(r.market ?? r.market_value ?? r.market_count);
  const focus = asNumber(r.focus ?? r.focus_value ?? r.focus_count);
  if (market == null && focus == null) return null;
  return { label, market, focus };
}

function fromArray(value: unknown): CompareSeriesPoint[] {
  if (!Array.isArray(value)) return [];
  return value.flatMap((row) => {
    const p = pointFromUnknown(row);
    return p ? [p] : [];
  });
}

function trendItemValue(r: Record<string, unknown>): number | null {
  return asNumber(
    r.recent_mentions ?? r.value ?? r.count ?? r.mentions ?? r.jobs ?? r.growth_pct,
  );
}

function ingestSeriesRows(
  rows: unknown,
  key: "market" | "focus",
  byLabel: Map<string, CompareSeriesPoint>,
) {
  if (!Array.isArray(rows)) return;
  for (const row of rows) {
    if (!row || typeof row !== "object") continue;
    const r = row as Record<string, unknown>;
    const label = String(r.label ?? r.period ?? r.bucket ?? r.technology ?? "").trim();
    if (!label) continue;
    const value = trendItemValue(r);
    const prev = byLabel.get(label) ?? { label, market: null, focus: null };
    byLabel.set(label, { ...prev, [key]: value });
  }
}

function sortComparePoints(points: CompareSeriesPoint[]): CompareSeriesPoint[] {
  return [...points].sort(
    (a, b) => (b.market ?? 0) + (b.focus ?? 0) - ((a.market ?? 0) + (a.focus ?? 0)),
  );
}

function zipPairedSeries(payload: Record<string, unknown>): CompareSeriesPoint[] {
  const marketRaw = payload.market_series ?? payload.marketSeries;
  const focusRaw = payload.focus_series ?? payload.focusSeries;
  if (!Array.isArray(marketRaw) && !Array.isArray(focusRaw)) return [];

  const byLabel = new Map<string, CompareSeriesPoint>();
  ingestSeriesRows(marketRaw, "market", byLabel);
  ingestSeriesRows(focusRaw, "focus", byLabel);
  return sortComparePoints([...byLabel.values()]);
}

/** `/market/trends?lens=compare` → `{ market: { items }, focus: { items } }`. */
function zipTrendBundles(payload: Record<string, unknown>): CompareSeriesPoint[] {
  const market = payload.market;
  const focus = payload.focus;
  if (!market || !focus || typeof market !== "object" || typeof focus !== "object") {
    return [];
  }
  const m = market as Record<string, unknown>;
  const f = focus as Record<string, unknown>;
  if (!Array.isArray(m.items) && !Array.isArray(f.items)) return [];

  const byLabel = new Map<string, CompareSeriesPoint>();
  ingestSeriesRows(m.items, "market", byLabel);
  ingestSeriesRows(f.items, "focus", byLabel);
  return sortComparePoints([...byLabel.values()]);
}

function firstNonEmpty(...candidates: CompareSeriesPoint[][]): CompareSeriesPoint[] {
  for (const c of candidates) {
    if (c.length) return c;
  }
  return [];
}

/**
 * Best-effort extract of dual market/focus series from summary or trends payloads.
 * Backend shapes may vary while lenses land in parallel.
 */
export function extractComparePoints(payload: unknown): CompareSeriesPoint[] {
  if (!payload || typeof payload !== "object") return [];
  const p = payload as Record<string, unknown>;

  const direct = firstNonEmpty(
    fromArray(p.compare_series),
    fromArray(p.dual_series),
    fromArray(p.series),
    fromArray(p.compareSeries),
    fromArray(p.dualSeries),
  );
  if (direct.length) return direct;

  if (p.overlap && typeof p.overlap === "object") {
    const overlap = p.overlap as Record<string, unknown>;
    const fromOverlap = firstNonEmpty(
      fromArray(overlap.compare_series),
      fromArray(overlap.dual_series),
      fromArray(overlap.series),
      fromArray(overlap.points),
    );
    if (fromOverlap.length) return fromOverlap;
  }

  return firstNonEmpty(zipTrendBundles(p), zipPairedSeries(p));
}

export function hasComparePayload(payload: unknown): boolean {
  if (!payload || typeof payload !== "object") return false;
  const p = payload as Record<string, unknown>;
  if (p.overlap != null) return true;
  return extractComparePoints(payload).length > 0;
}
