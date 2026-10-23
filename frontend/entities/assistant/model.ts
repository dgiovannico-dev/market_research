import type { ResearchIntentKind } from "@/entities/research-intent";

/** Requested UI locale for assistant propose/briefs (en|it). */
export type AssistantLocale = "en" | "it";

/** Echoed by API; narrative_locale stays en for MVP English evidence prose. */
export type AssistantLocaleMeta = {
  locale: AssistantLocale;
  narrative_locale: AssistantLocale;
};

export type AssistantBriefType =
  | "rising_cooling"
  | "where_demand"
  | "adjacent"
  | "focus_vs_market"
  | "suggest_watches";

export type ProposedWatchCandidate = {
  name: string;
  query_text: string;
  kind: ResearchIntentKind;
  rationale?: string;
  support?: number;
  anchor_skill?: string | null;
  origin_hint?: string;
};

export type EvidenceBrief = {
  brief_type: string;
  lens: string;
  sample_size: number;
  evidence: Record<string, unknown>[];
  narrative: string;
  limits: string;
  methodology_version?: string;
  status: string;
  countries?: string[] | null;
  proposed_intents?: ProposedWatchCandidate[];
};
