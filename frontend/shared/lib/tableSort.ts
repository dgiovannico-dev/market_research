/** Client-side table sorting helpers (stable, nulls last). */

export type SortOrder = "asc" | "desc";

export type SortValue = string | number | boolean | null | undefined;

export function compareSortValues(a: SortValue, b: SortValue, order: SortOrder): number {
  const aNull = a == null || a === "";
  const bNull = b == null || b === "";
  if (aNull && bNull) return 0;
  if (aNull) return 1;
  if (bNull) return -1;

  let cmp = 0;
  if (typeof a === "number" && typeof b === "number") {
    cmp = a - b;
  } else if (typeof a === "boolean" && typeof b === "boolean") {
    cmp = Number(a) - Number(b);
  } else {
    cmp = String(a).localeCompare(String(b), undefined, {
      numeric: true,
      sensitivity: "base",
    });
  }
  return order === "asc" ? cmp : -cmp;
}

export function sortRows<T>(
  rows: readonly T[],
  getValue: (row: T) => SortValue,
  order: SortOrder,
): T[] {
  return rows
    .map((row, index) => ({ row, index }))
    .sort((a, b) => {
      const cmp = compareSortValues(getValue(a.row), getValue(b.row), order);
      return cmp !== 0 ? cmp : a.index - b.index;
    })
    .map((x) => x.row);
}
