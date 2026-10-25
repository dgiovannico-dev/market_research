export type LearningCandidate = {
  technology: string;
  anchor_skill?: string | null;
  support?: number;
  lift?: number | null;
  gap_priority?: number;
  rise_cool_status?: string | null;
  growth_pct?: number | null;
  irreplaceability_score?: number;
  score?: number;
  complement?: number;
  rarity_proxy?: number;
  generic_penalty?: number;
  evidence_kind?: string;
  limits?: string | string[];
  drilldown?: {
    relations_seed?: string;
    relations_href?: string;
    certifications_href?: string;
  };
  rate_check?: {
    sample_size?: number;
    status?: string;
    rate?: { median?: number | null; p25?: number | null; p75?: number | null } | null;
    limits?: string;
  } | null;
};

export type RelatedCert = {
  slug?: string;
  display_name?: string;
  mentions?: number;
};

export type LearningCandidatesPayload = {
  owned_skills?: string[];
  candidates?: LearningCandidate[];
  related_certifications?: RelatedCert[];
  sample_size?: number | null;
  jobs_analyzed?: number | null;
  score_version?: number;
  methodology_version?: string;
  disclaimer?: string;
  lens?: string;
  market?: LearningCandidatesPayload;
  focus?: LearningCandidatesPayload;
  error?: string;
};
