/**
 * Curated external certification-demand snapshots for the Certifications page.
 * Values are taken from published reports (not live APIs). Keep as-of dates honest.
 */

export type CertBenchmarkItem = {
  label: string;
  value: number;
  /** Optional role / context for Adzuna-style rows */
  context?: string;
};

export type CertBenchmarkSeries = {
  id: "skillsoft_pursued" | "adzuna_us_share" | "pearson_specialty";
  unit: "count" | "share_pct";
  asOf: string;
  sourceUrl: string;
  items: CertBenchmarkItem[];
};

/** Skillsoft / Global Knowledge IT Skills & Salary Report 2024–2025 — most pursued. */
export const SKILLSOFT_MOST_PURSUED: CertBenchmarkSeries = {
  id: "skillsoft_pursued",
  unit: "count",
  asOf: "2024-09",
  sourceUrl:
    "https://www.globalknowledge.com/en/resources/it-skills-and-salary-report",
  items: [
    { label: "CompTIA Security+", value: 532 },
    { label: "CISSP", value: 435 },
    { label: "AWS Cloud Practitioner", value: 429 },
    { label: "CompTIA Network+", value: 402 },
    { label: "CompTIA CySA+", value: 397 },
    { label: "Cisco CCNA", value: 308 },
    { label: "AWS Solutions Architect Associate", value: 295 },
    { label: "CompTIA PenTest+", value: 290 },
    { label: "CompTIA A+", value: 271 },
    { label: "ISC2 Certified in Cybersecurity", value: 262 },
  ],
};

/**
 * CertWorthIT / Adzuna US — share of role ads naming the cert (Oct 2026 snapshot).
 * Value is percent share within that role.
 */
export const ADZUNA_US_ROLE_SHARE: CertBenchmarkSeries = {
  id: "adzuna_us_share",
  unit: "share_pct",
  asOf: "2026-10",
  sourceUrl: "https://www.certworthit.com/rankings/united-states/",
  items: [
    { label: "OSCP", value: 73, context: "Penetration tester" },
    { label: "CEH", value: 30, context: "Penetration tester" },
    { label: "PMP", value: 24, context: "Project manager" },
    { label: "SAFe", value: 22, context: "Scrum Master" },
    { label: "CSM", value: 22, context: "Scrum Master" },
    { label: "CompTIA A+", value: 20, context: "IT support" },
    { label: "Cisco CCNP", value: 20, context: "Network engineer" },
    { label: "Cisco CCNA", value: 16, context: "Network engineer" },
    { label: "ITIL", value: 7.5, context: "IT support" },
    { label: "CompTIA Network+", value: 5.9, context: "IT support" },
  ],
};

/** Pearson VUE Value of Certification 2025 — specialty areas of interest (%). */
export const PEARSON_SPECIALTY_INTEREST: CertBenchmarkSeries = {
  id: "pearson_specialty",
  unit: "share_pct",
  asOf: "2025",
  sourceUrl:
    "https://www.pearsonvue.com/content/dam/VUE/vue/en/documents/voc/pearson-vue-2025-value-of-certification-report.pdf",
  items: [
    { label: "Cloud computing", value: 49 },
    { label: "AI / machine learning", value: 35 },
    { label: "Cybersecurity / info security", value: 35 },
    { label: "DevOps", value: 23 },
    { label: "Security (broader)", value: 23 },
    { label: "Analytics / big data", value: 18 },
    { label: "Application development", value: 17 },
    { label: "Virtualization", value: 15 },
    { label: "Servers", value: 14 },
    { label: "Networking & wireless", value: 14 },
  ],
};

export const CERT_BENCHMARK_SERIES: CertBenchmarkSeries[] = [
  SKILLSOFT_MOST_PURSUED,
  ADZUNA_US_ROLE_SHARE,
  PEARSON_SPECIALTY_INTEREST,
];

export function seriesToRankItems(
  series: CertBenchmarkSeries,
): { label: string; value: number }[] {
  return series.items.map((it) => ({
    label: it.context ? `${it.label} (${it.context})` : it.label,
    value: it.value,
  }));
}
