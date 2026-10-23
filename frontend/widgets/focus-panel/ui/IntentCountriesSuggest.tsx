"use client";

import { useMemo } from "react";
import { useTranslations } from "next-intl";
import { useDashboardCountries } from "@/features/country-filter";
import {
  missingSuggestedCountries,
  suggestedCountriesFromIntents,
} from "@/lib/intentCountries";
import type { ResearchIntent } from "@/entities/research-intent";

type Props = {
  intents: ResearchIntent[];
};

/** Suggest CountryFilter codes from focus intents — never auto-applies. */
export function IntentCountriesSuggest({ intents }: Props) {
  const t = useTranslations("research");
  const { countries, setCountries } = useDashboardCountries();

  const suggested = useMemo(
    () => suggestedCountriesFromIntents(intents),
    [intents],
  );

  const missing = useMemo(
    () => missingSuggestedCountries(countries, suggested),
    [countries, suggested],
  );

  if (missing.length === 0) return null;

  return (
    <div className="rounded-lg border border-[var(--line)] bg-[var(--surface)] px-4 py-3 text-sm">
      <p className="text-[var(--ink)]">
        {t("suggestCountries", { codes: missing.join(", ") })}
      </p>
      <button
        type="button"
        className="mt-2 rounded-full border border-[var(--line)] px-3 py-1 text-xs hover:border-[var(--signal)]"
        onClick={() => setCountries([...countries, ...missing])}
      >
        {t("applySuggestedCountries")}
      </button>
    </div>
  );
}
