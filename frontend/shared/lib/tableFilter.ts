/** Client-side table text filter (case-insensitive substring). */

export function normalizeFilterQuery(query: string): string {
  return query.trim().toLowerCase();
}

export function rowMatchesFilter(
  haystack: string,
  normalizedQuery: string,
): boolean {
  if (!normalizedQuery) return true;
  return haystack.toLowerCase().includes(normalizedQuery);
}

export function filterRows<T>(
  rows: readonly T[],
  query: string,
  getHaystack: (row: T) => string,
): T[] {
  const q = normalizeFilterQuery(query);
  if (!q) return [...rows];
  return rows.filter((row) => rowMatchesFilter(getHaystack(row), q));
}

/** Join display fields into one searchable string. */
export function joinSearchParts(
  ...parts: Array<string | number | boolean | null | undefined>
): string {
  return parts
    .map((p) => (p == null || p === "" ? "" : String(p)))
    .filter(Boolean)
    .join(" ");
}
