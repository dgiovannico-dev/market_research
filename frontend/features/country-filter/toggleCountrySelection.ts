/**
 * Map / bar country click → next CountryFilter selection.
 * Same sole country again clears the filter (toggle).
 */
export function nextCountriesOnClick(
  current: string[],
  iso: string,
): string[] {
  const code = iso.trim().toUpperCase();
  if (!code || code === "UNKNOWN" || code === "ALL") return current;
  if (current.length === 1 && current[0] === code) return [];
  return [code];
}
