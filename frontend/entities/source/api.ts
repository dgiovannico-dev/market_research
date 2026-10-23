import { getJSON } from "@/shared/api";

export const sourceApi = {
  list: () => getJSON<{ items: Record<string, unknown>[] }>("/api/v1/sources"),
  catalogSummary: () =>
    getJSON<{
      total: number;
      by_status: Record<string, number>;
      active_connector_keys: string[];
    }>("/api/v1/sources/catalog/summary"),
  catalog: (params?: { status?: string; category?: string; kind?: string }) => {
    const qs = new URLSearchParams();
    if (params?.status) qs.set("status", params.status);
    if (params?.category) qs.set("category", params.category);
    if (params?.kind) qs.set("kind", params.kind);
    const q = qs.toString();
    return getJSON<{
      summary: Record<string, unknown>;
      items: Record<string, unknown>[];
    }>(`/api/v1/sources/catalog${q ? `?${q}` : ""}`);
  },
  opsMetrics: () => getJSON<Record<string, unknown>>("/api/v1/ops/metrics"),
  llmStatus: () => getJSON<Record<string, unknown>>("/api/v1/llm/status"),
};
