export type JobItem = {
  id: number;
  title: string;
  company: string | null;
  source: string | null;
  country_code: string;
  published_at: string | null;
  contract_type: string;
  contract_evidence_kind: string;
  remote_type: string;
  seniority: string | null;
  status: string;
  canonical_url: string;
  technologies: { name: string; importance: string; evidence_kind: string }[];
  rates: {
    amount_min: number | null;
    amount_max: number | null;
    currency: string | null;
    unit: string;
    evidence_kind: string;
  }[];
};
