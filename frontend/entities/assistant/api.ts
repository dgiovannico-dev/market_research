import {
  requestJSON,
  type DashboardLens,
} from "@/shared/api";
import type {
  AssistantBriefType,
  AssistantLocale,
  AssistantLocaleMeta,
  EvidenceBrief,
} from "./model";

export const assistantApi = {
  propose: async (
    prompt: string,
    kind: "dashboard" | "report" = "dashboard",
    materialize = false,
    locale: AssistantLocale = "en",
  ) => {
    return requestJSON<{
      kind: string;
      spec: Record<string, unknown>;
      validation: { ok: boolean; errors: string[]; warnings: string[] };
      materialized: Record<string, unknown> | null;
      meta: AssistantLocaleMeta;
    }>("/api/v1/assistant/propose", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt, kind, materialize, locale }),
    });
  },
  brief: async (body: {
    brief_type: AssistantBriefType;
    lens?: DashboardLens;
    query_ids?: number[];
    period_days?: number;
    /** CSV ISO codes — same contract as market/summary. */
    country_code?: string;
    prompt?: string;
    locale?: AssistantLocale;
    /** LocalStorage profile skills (ADR-009) for adjacent / suggest_watches. */
    owned_skills?: string[];
  }) => {
    return requestJSON<{
      kind: "brief";
      brief: EvidenceBrief;
      meta: AssistantLocaleMeta;
    }>("/api/v1/assistant/brief", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  },
};
