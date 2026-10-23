import { getJSON, withLensQuery } from "@/shared/api";
import type {
  LanguageCountryMatrix,
  MarketSeriesOpts,
  MarketSeriesPayload,
  MatrixLanguageCountryOpts,
  MatrixRoleTechOpts,
  MatrixSeniorityTechOpts,
  MatrixTechCountryOpts,
  RoleTechMatrix,
  SeniorityTechMatrix,
  TechCountryMatrix,
} from "./model";

export const relationsApi = {
  matrixTechCountry: (opts: MatrixTechCountryOpts = {}) => {
    const days = opts.days ?? 90;
    return getJSON<TechCountryMatrix>(
      withLensQuery(
        "/api/v1/market/matrix/tech-country",
        {
          days,
          top_tech: opts.topTech,
          top_country: opts.topCountry,
          min_cell: opts.minCell,
          min_evidence: opts.minEvidence,
        },
        opts.lens,
        opts.queryIds,
        opts.countries,
      ),
    );
  },
  matrixLanguageCountry: (opts: MatrixLanguageCountryOpts = {}) => {
    const days = opts.days ?? 90;
    return getJSON<LanguageCountryMatrix>(
      withLensQuery(
        "/api/v1/market/matrix/language-country",
        {
          days,
          top_language: opts.topLang,
          top_country: opts.topCountry,
          min_cell: opts.minCell,
          min_evidence: opts.minEvidence,
        },
        opts.lens,
        opts.queryIds,
        opts.countries,
      ),
    );
  },
  matrixRoleTech: (opts: MatrixRoleTechOpts = {}) => {
    const days = opts.days ?? 90;
    return getJSON<RoleTechMatrix>(
      withLensQuery(
        "/api/v1/market/matrix/role-tech",
        {
          days,
          top_role: opts.topRole,
          top_tech: opts.topTech,
          min_cell: opts.minCell,
          min_evidence: opts.minEvidence,
        },
        opts.lens,
        opts.queryIds,
        opts.countries,
      ),
    );
  },
  matrixSeniorityTech: (opts: MatrixSeniorityTechOpts = {}) => {
    const days = opts.days ?? 90;
    return getJSON<SeniorityTechMatrix>(
      withLensQuery(
        "/api/v1/market/matrix/seniority-tech",
        {
          days,
          top_seniority: opts.topSeniority,
          top_tech: opts.topTech,
          min_cell: opts.minCell,
          min_evidence: opts.minEvidence,
        },
        opts.lens,
        opts.queryIds,
        opts.countries,
      ),
    );
  },
  seriesTechnologies: (opts: MarketSeriesOpts = {}) => {
    const days = opts.days ?? 90;
    return getJSON<MarketSeriesPayload>(
      withLensQuery(
        "/api/v1/market/series/technologies",
        {
          days,
          top: opts.top,
          grain: opts.grain,
          min_evidence: opts.minEvidence,
        },
        opts.lens,
        opts.queryIds,
        opts.countries,
      ),
    );
  },
  seriesCountries: (opts: MarketSeriesOpts = {}) => {
    const days = opts.days ?? 90;
    return getJSON<MarketSeriesPayload>(
      withLensQuery(
        "/api/v1/market/series/countries",
        {
          days,
          top: opts.top,
          grain: opts.grain,
          min_evidence: opts.minEvidence,
        },
        opts.lens,
        opts.queryIds,
        opts.countries,
      ),
    );
  },
  seriesRates: (opts: MarketSeriesOpts = {}) => {
    const days = opts.days ?? 90;
    return getJSON<MarketSeriesPayload>(
      withLensQuery(
        "/api/v1/market/series/rates",
        {
          days,
          top: opts.top,
          grain: opts.grain,
          min_evidence: opts.minEvidence,
        },
        opts.lens,
        opts.queryIds,
        opts.countries,
      ),
    );
  },
};
