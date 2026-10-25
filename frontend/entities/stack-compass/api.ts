import { requestJSON, withLensQuery, type DashboardLensParams } from "@/shared/api";
import type { LearningCandidatesPayload } from "./model";

export const stackCompassApi = {
  learningCandidates: async (
    body: {
      skills: string[];
      certifications?: string[];
      country_code?: string;
      days?: number;
      top_n?: number;
      include_rates?: boolean;
    },
    opts: DashboardLensParams = {},
  ) => {
    const path = withLensQuery(
      "/api/v1/profile/learning-candidates",
      {},
      opts.lens,
      opts.queryIds,
      opts.countries,
    );
    return requestJSON<LearningCandidatesPayload>(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        skills: body.skills,
        certifications: body.certifications,
        country_code: body.country_code,
        days: body.days ?? opts.days ?? 90,
        top_n: body.top_n ?? 15,
        include_rates: body.include_rates ?? true,
      }),
    });
  },
};
