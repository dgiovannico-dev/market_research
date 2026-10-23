export type QualityBySourceRow = {
  source_id?: number;
  name?: string | null;
  connector_type?: string | null;
  n: number;
  pct_known_country: number;
  pct_thin: number;
  pct_with_rate: number;
  last_seen_at?: string | null;
};

export type QualityPayload = {
  total_canonical_jobs?: number;
  disclaimer?: string;
  metrics?: Record<string, number>;
  by_source?: QualityBySourceRow[];
  sources?: Array<Record<string, unknown>>;
  market_n?: number;
  focus_n?: number;
  overlap_n?: number;
};
