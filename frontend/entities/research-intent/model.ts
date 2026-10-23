export type ResearchIntentKind = "discovery" | "focus";

export type ResearchIntent = {
  id: number;
  name: string;
  label?: string;
  query_text: string;
  kind: ResearchIntentKind;
  countries: string[];
  role_families: string[];
  contract_types: string[];
  filters_extra: Record<string, unknown> | null;
  enabled: boolean;
  schedule_hint: "daily" | "manual_only";
  origin: string;
  version: number;
  deleted_at: string | null;
  created_at: string | null;
  updated_at: string | null;
};

export type ResearchIntentCreate = {
  name: string;
  query_text: string;
  kind: ResearchIntentKind;
  countries?: string[];
  enabled?: boolean;
  schedule_hint?: "daily" | "manual_only";
  origin?: string;
};

export type ResearchIntentPatch = {
  name?: string;
  query_text?: string;
  enabled?: boolean;
  schedule_hint?: "daily" | "manual_only";
  countries?: string[];
};

export type ResearchJobFacets = {
  countries: string[];
  sources: { id: number; name: string }[];
  contracts: string[];
  remotes: string[];
  lens?: string | null;
  query_id?: number | null;
};

export type ResearchJobsParams = {
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
