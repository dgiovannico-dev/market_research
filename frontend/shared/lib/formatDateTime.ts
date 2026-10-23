/**
 * Format timestamps for UI display — minute precision, no fractional seconds.
 *
 * Output: ``2026-10-20 23:42 UTC`` (UTC). Date-only ``YYYY-MM-DD`` stays a date.
 */

export function formatDateMinute(
  value: string | Date | null | undefined,
  fallback = "—",
): string {
  if (value == null || value === "") return fallback;
  if (typeof value === "string") {
    const trimmed = value.trim();
    if (/^\d{4}-\d{2}-\d{2}$/.test(trimmed)) return trimmed;
  }
  const d = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(d.getTime())) {
    return typeof value === "string" && value.trim() ? value.trim() : fallback;
  }
  const y = d.getUTCFullYear();
  const mo = String(d.getUTCMonth() + 1).padStart(2, "0");
  const da = String(d.getUTCDate()).padStart(2, "0");
  const h = String(d.getUTCHours()).padStart(2, "0");
  const mi = String(d.getUTCMinutes()).padStart(2, "0");
  return `${y}-${mo}-${da} ${h}:${mi} UTC`;
}
