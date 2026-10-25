import type { CoverageNote } from "@/entities/coverage-note";

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

export type JobsPerDayPoint = {
  day: string;
  jobs: number;
};

export type DashboardSummary = {
  /** Optional on partial compare wrappers before backend lifts. */
  period_days?: number;
  generated_at?: string;
  disclaimer?: string;
  growth_status?: string;
  kpis?: Kpi[];
  /** Observed canonical jobs by published_at calendar day (UTC). Empty when n=0. */
  jobs_per_day?: JobsPerDayPoint[];
  top_technologies?: { technology: string; job_skill_mentions: number }[];
  top_countries?: { country_code: string; jobs: number }[];
  /** Absent on older payloads / partial compare wrappers — treat as optional. */
  data_quality?: {
    sources_total: number;
    sources_enabled: number;
    sources_with_errors: number;
    last_source_success_at: string | null;
  };
  /** DSS footnotes (thin evidence, capped/snapshot sources). */
  coverage_notes?: CoverageNote[];
  lens?: string;
  market_n?: number;
  focus_n?: number;
  overlap_n?: number;
  overlap?: unknown;
  compare_series?: unknown;
  dual_series?: unknown;
  series?: unknown;
  market_series?: unknown;
  focus_series?: unknown;
  /** Present when `lens=compare`. */
  market?: DashboardSummary;
  focus?: DashboardSummary;
};

export type TechnologyTrendItem = {
  technology: string;
  category: string;
  recent_mentions: number;
  previous_mentions: number;
  sample_size: number;
  growth_pct: number | null;
  status: string;
  evidence_kind: string;
  limits: string;
};

export type TechnologyTrends = {
  period_days?: number;
  min_support?: number;
  items?: TechnologyTrendItem[];
  lens?: string;
  query_ids?: number[] | null;
  market_n?: number;
  focus_n?: number;
  overlap_n?: number;
  min_evidence?: string;
  excluded_thin_n?: number;
  /** Present when `lens=compare` — paired half-period trend bundles. */
  market?: TechnologyTrends;
  focus?: TechnologyTrends;
  overlap?: unknown;
  compare_series?: unknown;
  dual_series?: unknown;
  series?: unknown;
  market_series?: unknown;
  focus_series?: unknown;
};

export type CountryComparisonItem = {
  country_code: string;
  jobs_observed: number;
  remote_share: number;
  b2b_freelance_share: number;
  explicitly_allowed_residence: number;
  explicitly_restricted_residence: number;
  top_technologies?: { name: string; mentions: number }[];
};

export type CountryComparison = {
  period_days?: number;
  disclaimer?: string;
  items?: CountryComparisonItem[];
  /** Present when `for_map=1` — choropleth series (unknown excluded). */
  map_items?: { country_code: string; jobs: number }[];
  unknown_jobs?: number;
  for_map?: boolean;
  /** DSS footnotes (thin evidence, capped/snapshot sources). */
  coverage_notes?: CoverageNote[];
  lens?: string;
  query_ids?: number[] | null;
  market_n?: number;
  focus_n?: number;
  overlap_n?: number;
  market?: CountryComparison;
  focus?: CountryComparison;
};

export type MarketFacetBucket = { key: string; jobs: number };

export type MarketFacets = {
  period_days?: number;
  sample_size?: number;
  facets?: {
    remote?: MarketFacetBucket[];
    contract?: MarketFacetBucket[];
    seniority?: MarketFacetBucket[];
    status?: MarketFacetBucket[];
  };
  lens?: string;
  query_ids?: number[] | null;
  market_n?: number;
  focus_n?: number;
  overlap_n?: number;
  disclaimer?: string;
  market?: MarketFacets;
  focus?: MarketFacets;
};

export type MarketLanguageItem = {
  language: string;
  jobs: number;
  share?: number;
};

export type MarketLanguages = {
  period_days?: number;
  sample_size?: number;
  jobs_with_language_requirements?: number;
  coverage_pct?: number;
  items?: MarketLanguageItem[];
  by_country_top?: Record<string, { language: string; jobs: number }[]>;
  lens?: string;
  query_ids?: number[] | null;
  market_n?: number;
  focus_n?: number;
  overlap_n?: number;
  disclaimer?: string;
  market?: MarketLanguages;
  focus?: MarketLanguages;
};

export type MarketCertificationItem = {
  certification: string;
  slug?: string;
  job_mentions: number;
  evidence_kind?: string;
};

export type MarketCertifications = {
  period_days?: number;
  sample_size?: number;
  items?: MarketCertificationItem[];
  lens?: string;
  query_ids?: number[] | null;
  market_n?: number;
  focus_n?: number;
  overlap_n?: number;
  disclaimer?: string;
  market?: MarketCertifications;
  focus?: MarketCertifications;
};

export type CertCountryMapItem = {
  country_code: string;
  jobs: number;
};

export type CertCountryRow = {
  country_code: string;
  jobs_with_certs: number;
  top_certification: string | null;
  top_mentions: number;
  top: MarketCertificationItem[];
};

export type MarketCertificationsByCountry = {
  period_days?: number;
  sample_size?: number;
  map_items?: CertCountryMapItem[];
  unknown_jobs?: number;
  countries?: CertCountryRow[];
  disclaimer?: string;
  lens?: string;
};

export type CooccurrencePayload = {
  seed?: string | null;
  neighbor_limit?: number | null;
  jobs_analyzed: number;
  period_days: number;
  items: Record<string, unknown>[];
  lens?: string;
  query_ids?: number[] | null;
  market_n?: number;
  focus_n?: number;
  overlap_n?: number;
  min_evidence?: string;
  excluded_thin_n?: number;
};

export type EscoSearchResult = {
  items: { title?: string; uri?: string; code?: string; class_name?: string }[];
  total?: number;
  disclaimer?: string;
  error?: string;
};
