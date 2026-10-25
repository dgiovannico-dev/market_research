import { API_URL } from "@/shared/api";
import type { StudyModality, StudyPlan, StudyPlanResponse } from "./model";

export type StudyAdviceInput = {
  skills: string[];
  certifications?: string[];
  hours_per_week: number;
  modality: StudyModality;
  horizon_weeks: number;
  country_code?: string;
  days?: number;
};

async function postJson<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    cache: "no-store",
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(
      String((data as { detail?: string }).detail || res.statusText),
    );
  }
  return data as T;
}

export const studyAdvisorApi = {
  evidence: (body: StudyAdviceInput) =>
    postJson<Record<string, unknown>>("/api/v1/profile/study-advice/evidence", body),
  plan: (body: StudyAdviceInput) =>
    postJson<StudyPlanResponse>("/api/v1/profile/study-advice/plan", body),
  refine: (body: {
    plan: StudyPlan;
    evidence: Record<string, unknown>;
    message: string;
  }) => postJson<StudyPlanResponse>("/api/v1/profile/study-advice/refine", body),
};
