import type { AssistantBriefType } from "@/lib/api";

export const ASSISTANT_BRIEF_TYPES: readonly AssistantBriefType[] = [
  "rising_cooling",
  "where_demand",
  "adjacent",
  "focus_vs_market",
  "suggest_watches",
] as const;

export function briefChipKey(
  briefType: AssistantBriefType,
):
  | "briefRisingCooling"
  | "briefWhereDemand"
  | "briefAdjacent"
  | "briefFocusVsMarket"
  | "briefSuggestWatches" {
  switch (briefType) {
    case "rising_cooling":
      return "briefRisingCooling";
    case "where_demand":
      return "briefWhereDemand";
    case "adjacent":
      return "briefAdjacent";
    case "focus_vs_market":
      return "briefFocusVsMarket";
    case "suggest_watches":
      return "briefSuggestWatches";
  }
}
