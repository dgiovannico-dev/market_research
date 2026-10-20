const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function getJSON<T>(path: string): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`API ${path} failed: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export type Kpi = {
  metric_name: string;
  metric_value: number;
  sample_size: number;
  unit: string;
  definition: string;
  limits: string;
  evidence_kind: string;
  source_coverage: string;
};

export type DashboardSummary = {
  period_days: number;
  generated_at: string;
  disclaimer: string;
  growth_status: string;
  kpis: Kpi[];
  top_technologies: { technology: string; job_skill_mentions: number }[];
  top_countries: { country_code: string; jobs: number }[];
  data_quality: {
    sources_total: number;
    sources_enabled: number;
    sources_with_errors: number;
    last_source_success_at: string | null;
  };
};

export type JobItem = {
  id: number;
  title: string;
  company: string | null;
  source: string | null;
  country_code: string;
  published_at: string | null;
  contract_type: string;
  contract_evidence_kind: string;
  remote_type: string;
  seniority: string | null;
  status: string;
  canonical_url: string;
  technologies: { name: string; importance: string; evidence_kind: string }[];
  rates: {
    amount_min: number | null;
    amount_max: number | null;
    currency: string | null;
    unit: string;
    evidence_kind: string;
  }[];
};

export const api = {
  summary: (days = 30) => getJSON<DashboardSummary>(`/api/v1/dashboard/summary?days=${days}`),
  jobs: (params = "") => getJSON<{ total: number; items: JobItem[] }>(`/api/v1/market/jobs?${params}`),
  quality: () => getJSON<Record<string, unknown>>("/api/v1/market/quality"),
  trends: (days = 90) => getJSON<{ items: Record<string, unknown>[] }>(`/api/v1/market/trends?days=${days}`),
  sources: () => getJSON<{ items: Record<string, unknown>[] }>("/api/v1/sources"),
  llmStatus: () => getJSON<Record<string, unknown>>("/api/v1/llm/status"),
  cooccurrence: (days = 90, minSupport = 2) =>
    getJSON<{
      jobs_analyzed: number;
      period_days: number;
      items: Record<string, unknown>[];
    }>(`/api/v1/market/skills/cooccurrence?days=${days}&min_support=${minSupport}`),
  runSource: async (sourceId: number, query?: string) => {
    const q = query ? `?query=${encodeURIComponent(query)}` : "";
    const res = await fetch(`${API_URL}/api/v1/sources/${sourceId}/run${q}`, { method: "POST" });
    if (!res.ok) throw new Error(`Run failed: ${res.status}`);
    return res.json();
  },
};
