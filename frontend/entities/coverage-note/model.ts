/** Structured coverage footnote (preferred) or legacy plain string. */
export type CoverageNote =
  | string
  | {
      code?: string;
      message?: string;
      thin_n?: number;
      pct?: number;
      sources?: string;
    };

export type CoverageNotesSource = {
  coverage_notes?: CoverageNote[];
  market?: { coverage_notes?: CoverageNote[] };
  focus?: { coverage_notes?: CoverageNote[] };
};
