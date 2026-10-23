export type RateExplorerItem = {
  country_code: string;
  currency: string;
  unit: string;
  sample_size: number;
  median: number | null;
  p25: number | null;
  p75: number | null;
  status: string;
};

export type RateExplorer = {
  period_days?: number;
  min_sample?: number;
  jobs_with_rates?: number;
  disclaimer?: string;
  items?: RateExplorerItem[];
  lens?: string;
  query_ids?: number[] | null;
  market_n?: number;
  focus_n?: number;
  overlap_n?: number;
  min_evidence?: string;
  excluded_thin_n?: number;
};
