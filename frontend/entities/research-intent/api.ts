import { requestJSON } from "@/shared/api";
import type {
  ResearchIntent,
  ResearchIntentCreate,
  ResearchIntentKind,
  ResearchIntentPatch,
  ResearchJobFacets,
  ResearchJobsParams,
} from "./model";

export const researchApi = {
  list: (kind?: ResearchIntentKind) => {
    const qs = kind ? `?kind=${kind}` : "";
    return requestJSON<{ items: ResearchIntent[]; total: number }>(
      `/api/v1/research/intents${qs}`,
    );
  },
  create: (body: ResearchIntentCreate) =>
    requestJSON<ResearchIntent>("/api/v1/research/intents", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }),
  patch: (id: number, body: ResearchIntentPatch) =>
    requestJSON<ResearchIntent>(`/api/v1/research/intents/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }),
  remove: (id: number) =>
    requestJSON<{ status: string; id: number }>(`/api/v1/research/intents/${id}`, {
      method: "DELETE",
    }),
  sync: (id: number) =>
    requestJSON<Record<string, unknown>>(`/api/v1/research/intents/${id}/sync`, {
      method: "POST",
    }),
  acceptWatch: (body: Omit<ResearchIntentCreate, "origin">) =>
    requestJSON<ResearchIntent>("/api/v1/research/watches/accept", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }),
  jobFacets: (params: {
    lens?: "market" | "focus" | "compare";
    query_id?: number;
  } = {}) => {
    const qs = new URLSearchParams();
    if (params.lens) qs.set("lens", params.lens);
    if (params.query_id != null) qs.set("query_id", String(params.query_id));
    const suffix = qs.toString() ? `?${qs}` : "";
    return requestJSON<ResearchJobFacets>(`/api/v1/research/jobs/facets${suffix}`);
  },
  jobs: (params: ResearchJobsParams = {}) => {
    const qs = new URLSearchParams();
    if (params.q) qs.set("q", params.q);
    if (params.lens) qs.set("lens", params.lens);
    if (params.query_id != null) qs.set("query_id", String(params.query_id));
    if (params.country_code) qs.set("country_code", params.country_code);
    if (params.source_id) qs.set("source_id", params.source_id);
    if (params.contract_type) qs.set("contract_type", params.contract_type);
    if (params.remote_type) qs.set("remote_type", params.remote_type);
    if (params.sort) qs.set("sort", params.sort);
    if (params.order) qs.set("order", params.order);
    if (params.skip != null) qs.set("skip", String(params.skip));
    if (params.limit != null) qs.set("limit", String(params.limit));
    const suffix = qs.toString() ? `?${qs}` : "";
    return requestJSON<{
      total: number;
      skip: number;
      limit: number;
      sort?: string;
      order?: string;
      items: Record<string, unknown>[];
    }>(`/api/v1/research/jobs${suffix}`);
  },
};
