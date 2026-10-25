import { getJSON, withLensQuery, type DashboardLensParams } from "@/shared/api";
import type { QualityPayload } from "@/entities/quality";
import type { RateExplorer } from "@/entities/rate";
import type {
  CooccurrencePayload,
  CountryComparison,
  DashboardSummary,
  EscoSearchResult,
  MarketCertifications,
  MarketCertificationsByCountry,
  MarketFacets,
  MarketLanguages,
  TechnologyTrends,
} from "./model";

export const marketApi = {
  summary: (daysOrOpts: number | DashboardLensParams = 30) => {
    const opts: DashboardLensParams =
      typeof daysOrOpts === "number" ? { days: daysOrOpts } : daysOrOpts;
    const days = opts.days ?? 30;
    const topN = opts.topN ?? 100;
    return getJSON<DashboardSummary>(
      withLensQuery(
        "/api/v1/dashboard/summary",
        { days, top_n: topN },
        opts.lens,
        opts.queryIds,
        opts.countries,
      ),
    );
  },
  quality: (opts: DashboardLensParams = {}) =>
    getJSON<QualityPayload>(
      withLensQuery(
        "/api/v1/market/quality",
        {},
        opts.lens,
        opts.queryIds,
        opts.countries,
      ),
    ),
  trends: (daysOrOpts: number | DashboardLensParams = 90, minSupport = 3) => {
    const opts: DashboardLensParams =
      typeof daysOrOpts === "number"
        ? { days: daysOrOpts, minSupport }
        : { minSupport, ...daysOrOpts };
    const days = opts.days ?? 90;
    const support = opts.minSupport ?? minSupport;
    return getJSON<TechnologyTrends>(
      withLensQuery(
        "/api/v1/market/trends",
        { days, min_support: support },
        opts.lens,
        opts.queryIds,
        opts.countries,
      ),
    );
  },
  countries: (opts: DashboardLensParams & { forMap?: boolean } = {}) => {
    const days = opts.days ?? 90;
    return getJSON<CountryComparison>(
      withLensQuery(
        "/api/v1/market/countries",
        { days, for_map: opts.forMap ? "true" : undefined },
        opts.lens,
        opts.queryIds,
        opts.countries,
      ),
    );
  },
  facets: (opts: DashboardLensParams = {}) => {
    const days = opts.days ?? 30;
    return getJSON<MarketFacets>(
      withLensQuery(
        "/api/v1/market/facets",
        { days },
        opts.lens,
        opts.queryIds,
        opts.countries,
      ),
    );
  },
  languages: (opts: DashboardLensParams & { limit?: number } = {}) => {
    const days = opts.days ?? 90;
    return getJSON<MarketLanguages>(
      withLensQuery(
        "/api/v1/market/languages",
        { days, limit: opts.limit },
        opts.lens,
        opts.queryIds,
        opts.countries,
      ),
    );
  },
  certificationsTop: (
    opts: DashboardLensParams & { topN?: number } = {},
  ) => {
    const days = opts.days ?? 90;
    const topN = opts.topN ?? 20;
    return getJSON<MarketCertifications>(
      withLensQuery(
        "/api/v1/market/certifications/top",
        { days, top_n: topN },
        opts.lens,
        opts.queryIds,
        opts.countries,
      ),
    );
  },
  certificationsByCountry: (
    opts: DashboardLensParams & {
      topNPerCountry?: number;
      topCountries?: number;
    } = {},
  ) => {
    const days = opts.days ?? 90;
    return getJSON<MarketCertificationsByCountry>(
      withLensQuery(
        "/api/v1/market/certifications/by-country",
        {
          days,
          top_n_per_country: opts.topNPerCountry ?? 5,
          top_countries: opts.topCountries ?? 40,
        },
        opts.lens,
        opts.queryIds,
        opts.countries,
      ),
    );
  },
  rates: (opts: DashboardLensParams = {}) => {
    const days = opts.days ?? 180;
    const minSample = opts.minSample ?? 3;
    return getJSON<RateExplorer>(
      withLensQuery(
        "/api/v1/market/rates",
        { days, min_sample: minSample },
        opts.lens,
        opts.queryIds,
        opts.countries,
      ),
    );
  },
  cooccurrence: (
    daysOrOpts: number | DashboardLensParams = 90,
    minSupport = 2,
  ) => {
    const opts: DashboardLensParams =
      typeof daysOrOpts === "number"
        ? { days: daysOrOpts, minSupport }
        : { minSupport, ...daysOrOpts };
    const days = opts.days ?? 90;
    const support = opts.minSupport ?? minSupport;
    return getJSON<CooccurrencePayload>(
      withLensQuery(
        "/api/v1/market/skills/cooccurrence",
        {
          days,
          min_support: support,
          min_evidence: opts.minEvidence,
          seed: opts.seed,
          neighbor_limit: opts.neighborLimit,
        },
        opts.lens,
        opts.queryIds,
        opts.countries,
      ),
    );
  },
  escoSearch: (
    q: string,
    type: "occupation" | "skill" | "concept" = "occupation",
    limit = 8,
  ) => {
    const qs = new URLSearchParams({
      q,
      type,
      limit: String(limit),
      language: "en",
    });
    return getJSON<EscoSearchResult>(`/api/v1/taxonomy/esco/search?${qs}`);
  },
};
