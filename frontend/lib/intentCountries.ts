/** Collect unique ISO country codes from enabled research intents. */

export type IntentCountriesSource = {
  enabled?: boolean;
  countries?: string[] | null;
};

export function suggestedCountriesFromIntents(
  intents: IntentCountriesSource[],
): string[] {
  const seen = new Set<string>();
  const out: string[] = [];
  for (const intent of intents) {
    if (intent.enabled === false) continue;
    for (const raw of intent.countries || []) {
      const code = String(raw).trim().toUpperCase();
      if (!code || code === "ALL" || seen.has(code)) continue;
      seen.add(code);
      out.push(code);
    }
  }
  return out;
}

export function missingSuggestedCountries(
  current: string[],
  suggested: string[],
): string[] {
  const have = new Set(current.map((c) => c.trim().toUpperCase()));
  return suggested.filter((c) => !have.has(c));
}
