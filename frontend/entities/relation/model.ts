import type { DashboardLensParams } from "@/shared/api";

export type TechCountryMatrixCell = {
  technology: string;
  country_code: string;
  jobs: number;
};

export type TechCountryMatrix = {
  period_days: number;
  sample_size: number;
  technologies: string[];
  countries: string[];
  cells: TechCountryMatrixCell[];
  excluded_thin_n?: number;
  limits?: string;
  lens?: string;
  query_ids?: number[] | null;
};

export type LanguageCountryMatrixCell = {
  language: string;
  country_code: string;
  jobs: number;
};

export type LanguageCountryMatrix = {
  period_days: number;
  sample_size: number;
  languages: string[];
  countries: string[];
  cells: LanguageCountryMatrixCell[];
  excluded_thin_n?: number;
  limits?: string;
  lens?: string;
  query_ids?: number[] | null;
};

export type RoleTechMatrixCell = {
  role_family: string;
  technology: string;
  jobs: number;
};

export type RoleTechMatrix = {
  period_days: number;
  sample_size: number;
  role_families: string[];
  technologies: string[];
  cells: RoleTechMatrixCell[];
  excluded_thin_n?: number;
  limits?: string;
  lens?: string;
  query_ids?: number[] | null;
};

export type SeniorityTechMatrixCell = {
  seniority: string;
  technology: string;
  jobs: number;
};

export type SeniorityTechMatrix = {
  period_days: number;
  sample_size: number;
  seniorities: string[];
  technologies: string[];
  cells: SeniorityTechMatrixCell[];
  excluded_thin_n?: number;
  limits?: string;
  lens?: string;
  query_ids?: number[] | null;
};

export type MarketSeriesPoint = {
  bucket: string;
  /** Sparse buckets (esp. rates medians) may be null. */
  count: number | null;
};

export type MarketSeriesLine = {
  key: string;
  points: MarketSeriesPoint[];
};

export type MarketSeriesPayload = {
  period_days: number;
  grain: string;
  sample_size: number;
  series: MarketSeriesLine[];
  limits?: string;
  lens?: string;
  query_ids?: number[] | null;
};

export type MatrixTechCountryOpts = DashboardLensParams & {
  topTech?: number;
  topCountry?: number;
  minCell?: number;
};

export type MatrixLanguageCountryOpts = DashboardLensParams & {
  topLang?: number;
  topCountry?: number;
  minCell?: number;
};

export type MatrixRoleTechOpts = DashboardLensParams & {
  topRole?: number;
  topTech?: number;
  minCell?: number;
};

export type MatrixSeniorityTechOpts = DashboardLensParams & {
  topSeniority?: number;
  topTech?: number;
  minCell?: number;
};

export type MarketSeriesOpts = DashboardLensParams & {
  top?: number;
  grain?: "day" | "week" | "month";
};
