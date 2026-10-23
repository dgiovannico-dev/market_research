import { getJSON } from "@/shared/api";
import type { JobItem } from "./model";

export const jobApi = {
  list: (params = "") =>
    getJSON<{ total: number; items: JobItem[] }>(`/api/v1/market/jobs?${params}`),
};
