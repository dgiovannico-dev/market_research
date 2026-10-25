/**
 * Shared lens query params for market analytics endpoints.
 *
 * Naming: request query uses `days=`; prefs / response body use `period_days`.
 */

export type DashboardLens = "market" | "focus" | "compare";

export type DashboardLensParams = {
  days?: number;
  lens?: DashboardLens;
  /** Focus intent ids — forwarded as `query_ids=1,2`. */
  queryIds?: number[];
  /** ISO country codes — forwarded as `country_code=IT,CH`. */
  countries?: string[];
  minSupport?: number;
  /** Rates explorer — forwarded as `min_sample`. */
  minSample?: number;
  /** Evidence gate — forwarded as `min_evidence` when set. */
  minEvidence?: string;
  /** Dashboard summary top_technologies / top_countries cap (1–100). */
  topN?: number;
  /** Co-occurrence ego seed technology (canonical name). */
  seed?: string;
  /** Co-occurrence neighbors when seed is set. */
  neighborLimit?: number;
};

export function withLensQuery(
  path: string,
  params: Record<string, string | number | undefined | null>,
  lens?: DashboardLens,
  queryIds?: number[],
  countries?: string[],
): string {
  const qs = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value == null || value === "") continue;
    qs.set(key, String(value));
  }
  if (lens) qs.set("lens", lens);
  if (queryIds?.length) qs.set("query_ids", queryIds.join(","));
  if (countries?.length) qs.set("country_code", countries.join(","));
  const q = qs.toString();
  return q ? `${path}?${q}` : path;
}
