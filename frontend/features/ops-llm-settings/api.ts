import { authHeaders, getAccessToken, isAdminFromToken } from "@/features/auth";
import { API_URL } from "@/shared/api";

function adminHeaders(opsToken: string, json = false): HeadersInit {
  const h: Record<string, string> = { ...authHeaders() };
  const t = opsToken.trim();
  if (t) h["X-Ops-Token"] = t;
  if (json) h["Content-Type"] = "application/json";
  return h;
}

export function canEditLlm(opsToken: string): boolean {
  if (isAdminFromToken(getAccessToken())) return true;
  return Boolean(opsToken.trim());
}

export type LlmSettings = {
  provider: string;
  base_url: string;
  model: string;
  temperature: number;
  timeout_s: number;
  max_tokens: number | null;
  api_key_set: boolean;
  enable_classify: boolean;
  enable_weekly_report: boolean;
  enable_study_advisor: boolean;
  enable_brief_narrative: boolean;
  source: string;
  updated_by?: string | null;
  updated_at?: string | null;
};

export type PromptVersion = {
  id: number;
  template_id: number;
  version: number;
  system_text: string;
  user_text: string;
  status: string;
  notes?: string | null;
  created_by?: string | null;
  created_at?: string | null;
};

export type PromptTemplate = {
  id: number;
  slug: string;
  purpose: string;
  description?: string | null;
  active_version_id?: number | null;
  versions: PromptVersion[];
};

export async function fetchLlmSettings(opsToken: string) {
  const res = await fetch(`${API_URL}/api/v1/ops/llm/settings`, {
    cache: "no-store",
    headers: adminHeaders(opsToken),
  });
  const data = await res.json().catch(() => ({}));
  return { res, data: data as LlmSettings & { detail?: string } };
}

export async function putLlmSettings(
  opsToken: string,
  body: Record<string, unknown>,
) {
  const res = await fetch(`${API_URL}/api/v1/ops/llm/settings`, {
    method: "PUT",
    headers: adminHeaders(opsToken, true),
    body: JSON.stringify(body),
  });
  const data = await res.json().catch(() => ({}));
  return { res, data };
}

export async function testLlm(opsToken: string) {
  const res = await fetch(`${API_URL}/api/v1/ops/llm/test`, {
    method: "POST",
    headers: adminHeaders(opsToken),
  });
  const data = await res.json().catch(() => ({}));
  return { res, data };
}

export async function fetchPrompts(opsToken: string) {
  const res = await fetch(`${API_URL}/api/v1/ops/llm/prompts`, {
    cache: "no-store",
    headers: adminHeaders(opsToken),
  });
  const data = await res.json().catch(() => ({}));
  return { res, data: data as { items?: PromptTemplate[]; detail?: string } };
}

export async function createPromptVersion(
  opsToken: string,
  slug: string,
  body: {
    system_text: string;
    user_text: string;
    notes?: string;
    activate?: boolean;
  },
) {
  const res = await fetch(
    `${API_URL}/api/v1/ops/llm/prompts/${encodeURIComponent(slug)}/versions`,
    {
      method: "POST",
      headers: adminHeaders(opsToken, true),
      body: JSON.stringify(body),
    },
  );
  const data = await res.json().catch(() => ({}));
  return { res, data };
}

export async function activatePromptVersion(
  opsToken: string,
  versionId: number,
) {
  const res = await fetch(
    `${API_URL}/api/v1/ops/llm/prompts/versions/${versionId}/activate`,
    { method: "POST", headers: adminHeaders(opsToken) },
  );
  const data = await res.json().catch(() => ({}));
  return { res, data };
}

export async function archivePromptVersion(
  opsToken: string,
  versionId: number,
) {
  const res = await fetch(
    `${API_URL}/api/v1/ops/llm/prompts/versions/${versionId}/archive`,
    { method: "POST", headers: adminHeaders(opsToken) },
  );
  const data = await res.json().catch(() => ({}));
  return { res, data };
}
