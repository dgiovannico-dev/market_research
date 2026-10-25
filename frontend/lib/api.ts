/**
 * @deprecated Prefer `@/entities/*` and `@/shared/api`.
 * Thin barrel kept for existing imports during FSD Wave 1.
 */
import { assistantApi } from "@/entities/assistant";
import { jobApi } from "@/entities/job";
import { marketApi } from "@/entities/market";
import { relationsApi } from "@/entities/relation";
import { researchApi } from "@/entities/research-intent";
import { sourceApi } from "@/entities/source";
import { runSource } from "@/features/run-source";

export { ApiRequestError } from "@/shared/api";
export type { DashboardLens, DashboardLensParams } from "@/shared/api";
export type { CoverageNote } from "@/entities/coverage-note";
export type {
  CooccurrencePayload,
  CountryComparison,
  CountryComparisonItem,
  DashboardSummary,
  JobsPerDayPoint,
  Kpi,
  MarketFacetBucket,
  MarketFacets,
  MarketCertificationItem,
  MarketCertifications,
  MarketLanguageItem,
  MarketLanguages,
  TechnologyTrendItem,
  TechnologyTrends,
} from "@/entities/market";
export type { JobItem } from "@/entities/job";
export type {
  LanguageCountryMatrix,
  LanguageCountryMatrixCell,
  MarketSeriesLine,
  MarketSeriesOpts,
  MarketSeriesPayload,
  MarketSeriesPoint,
  MatrixLanguageCountryOpts,
  MatrixRoleTechOpts,
  MatrixSeniorityTechOpts,
  MatrixTechCountryOpts,
  RoleTechMatrix,
  RoleTechMatrixCell,
  SeniorityTechMatrix,
  SeniorityTechMatrixCell,
  TechCountryMatrix,
  TechCountryMatrixCell,
} from "@/entities/relation";
export type {
  QualityBySourceRow,
  QualityPayload,
} from "@/entities/quality";
export type { RateExplorer, RateExplorerItem } from "@/entities/rate";
export type {
  ResearchIntent,
  ResearchIntentCreate,
  ResearchIntentKind,
  ResearchIntentPatch,
} from "@/entities/research-intent";
export type {
  AssistantBriefType,
  AssistantLocale,
  AssistantLocaleMeta,
  EvidenceBrief,
  ProposedWatchCandidate,
} from "@/entities/assistant";

export const api = {
  summary: marketApi.summary,
  jobs: jobApi.list,
  quality: marketApi.quality,
  trends: marketApi.trends,
  countries: marketApi.countries,
  facets: marketApi.facets,
  languages: marketApi.languages,
  certificationsTop: marketApi.certificationsTop,
  certificationsByCountry: marketApi.certificationsByCountry,
  rates: marketApi.rates,
  sources: sourceApi.list,
  catalogSummary: sourceApi.catalogSummary,
  catalog: sourceApi.catalog,
  opsMetrics: sourceApi.opsMetrics,
  llmStatus: sourceApi.llmStatus,
  cooccurrence: marketApi.cooccurrence,
  matrixTechCountry: relationsApi.matrixTechCountry,
  matrixLanguageCountry: relationsApi.matrixLanguageCountry,
  matrixRoleTech: relationsApi.matrixRoleTech,
  matrixSeniorityTech: relationsApi.matrixSeniorityTech,
  seriesTechnologies: relationsApi.seriesTechnologies,
  seriesCountries: relationsApi.seriesCountries,
  seriesRates: relationsApi.seriesRates,
  escoSearch: marketApi.escoSearch,
  runSource,
  assistantPropose: assistantApi.propose,
  assistantBrief: assistantApi.brief,
  researchJobs: researchApi.jobs,
  researchJobFacets: researchApi.jobFacets,
  listResearchIntents: researchApi.list,
  createResearchIntent: researchApi.create,
  patchResearchIntent: researchApi.patch,
  deleteResearchIntent: researchApi.remove,
  syncResearchIntent: researchApi.sync,
  acceptResearchWatch: researchApi.acceptWatch,
};
