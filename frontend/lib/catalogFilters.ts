/** URL ↔ catalog API filter keys for Sources CatalogBrowser. */

export type CatalogKindFilter = "" | "free" | "credentialed";

export type CatalogUrlFilterState = {
  status: string;
  category: string;
  kind: CatalogKindFilter;
};

export function parseCatalogKind(raw: string | null | undefined): CatalogKindFilter {
  if (raw === "free" || raw === "credentialed") return raw;
  return "";
}

export function parseCatalogUrlFilters(
  get: (key: string) => string | null,
): CatalogUrlFilterState {
  return {
    status: (get("status") || "").trim(),
    category: (get("category") || "").trim(),
    kind: parseCatalogKind(get("kind")),
  };
}

export function writeCatalogFiltersToSearchParams(
  params: URLSearchParams,
  state: CatalogUrlFilterState,
): void {
  if (state.status) params.set("status", state.status);
  else params.delete("status");
  if (state.category) params.set("category", state.category);
  else params.delete("category");
  if (state.kind) params.set("kind", state.kind);
  else params.delete("kind");
}

export function catalogFiltersEqual(
  a: CatalogUrlFilterState,
  b: CatalogUrlFilterState,
): boolean {
  return a.status === b.status && a.category === b.category && a.kind === b.kind;
}
