import { API_URL } from "@/shared/api";

export type RunSourceResult = {
  records_received?: number;
  inserted?: number;
  updated?: number;
  duplicates?: number;
  detail?: string;
  [key: string]: unknown;
};

export async function runSource(
  sourceId: number,
  query?: string,
): Promise<RunSourceResult> {
  const q = query ? `?query=${encodeURIComponent(query)}` : "";
  const res = await fetch(`${API_URL}/api/v1/sources/${sourceId}/run${q}`, {
    method: "POST",
  });
  const data = (await res.json()) as RunSourceResult;
  if (!res.ok) {
    throw new Error(
      typeof data.detail === "string" ? data.detail : `Run failed: ${res.status}`,
    );
  }
  return data;
}
