/** Compact percent for UI (e.g. 748.3516… → "748.35%"). */
export function formatPercent(value: number, digits = 2): string {
  if (!Number.isFinite(value)) return "—";
  return `${value.toFixed(digits)}%`;
}

/** Same rounding without the `%` suffix (tables that add it elsewhere). */
export function formatPercentNumber(value: number, digits = 2): string {
  if (!Number.isFinite(value)) return "—";
  return value.toFixed(digits);
}
