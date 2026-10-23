/**
 * Pure URL ↔ research jobs API param mapping for the Jobs table.
 * URL uses UI keys (countries, sources, …); API expects country_code, source_id, ….
 */

export type JobsUrlFilterState = {
  q: string;
  countries: string[];
  sources: string[];
  contracts: string[];
  remotes: string[];
};

export type ResearchJobsListParams = {
  q?: string;
  lens?: "market" | "focus" | "compare";
  query_id?: number;
  country_code?: string;
  source_id?: string;
  contract_type?: string;
  remote_type?: string;
  sort?: string;
  order?: "asc" | "desc";
  skip?: number;
  limit?: number;
};

export function parseCsvList(raw: string | null | undefined): string[] {
  if (!raw?.trim()) return [];
  return raw
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
}

export function parseJobsUrlFilters(
  get: (key: string) => string | null,
): JobsUrlFilterState {
  return {
    q: (get("q") || get("technology") || "").trim(),
    countries: parseCsvList(get("countries") || get("country_code")),
    sources: parseCsvList(get("sources") || get("source_id")),
    contracts: parseCsvList(get("contracts") || get("contract_type")),
    remotes: parseCsvList(get("remotes") || get("remote_type")),
  };
}

export function jobsUrlFiltersEqual(
  a: JobsUrlFilterState,
  b: JobsUrlFilterState,
): boolean {
  const same = (x: string[], y: string[]) =>
    x.length === y.length && x.every((v, i) => v === y[i]);
  return (
    a.q === b.q &&
    same(a.countries, b.countries) &&
    same(a.sources, b.sources) &&
    same(a.contracts, b.contracts) &&
    same(a.remotes, b.remotes)
  );
}

/** Write Jobs filter UI state onto URLSearchParams (clears page + legacy aliases). */
export function writeJobsFiltersToSearchParams(
  params: URLSearchParams,
  state: JobsUrlFilterState,
  opts: { lens: "market" | "focus" | "compare"; queryIds: number[] },
): void {
  params.delete("page");
  params.delete("country_code");
  params.delete("technology");
  params.delete("source_id");
  params.delete("contract_type");
  params.delete("remote_type");

  const setOrDelete = (key: string, values: string[]) => {
    if (values.length) params.set(key, values.join(","));
    else params.delete(key);
  };

  const nextQ = state.q.trim();
  if (nextQ) params.set("q", nextQ);
  else params.delete("q");

  setOrDelete(
    "countries",
    state.countries.map((c) => c.toUpperCase()),
  );
  setOrDelete("sources", state.sources);
  setOrDelete("contracts", state.contracts);
  setOrDelete("remotes", state.remotes);

  if (opts.lens !== "market") params.set("lens", opts.lens);
  else params.delete("lens");
  if (opts.queryIds.length > 0) params.set("query_ids", opts.queryIds.join(","));
  else params.delete("query_ids");
}

/** Map URL filter CSV strings + lens into researchApi.jobs() args. */
export function toResearchJobsParams(input: {
  q: string;
  countriesCsv: string;
  sourcesCsv: string;
  contractsCsv: string;
  remotesCsv: string;
  lens: "market" | "focus" | "compare";
  queryIds: number[];
  sort: string;
  order: "asc" | "desc";
  skip: number;
  limit: number;
}): ResearchJobsListParams {
  return {
    q: input.q || undefined,
    lens: input.lens,
    query_id: input.queryIds[0],
    country_code: input.countriesCsv || undefined,
    source_id: input.sourcesCsv || undefined,
    contract_type: input.contractsCsv || undefined,
    remote_type: input.remotesCsv || undefined,
    sort: input.sort,
    order: input.order,
    skip: input.skip,
    limit: input.limit,
  };
}
