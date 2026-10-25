import { ISO2_TO_ECHARTS_NAME } from "@/shared/ui/charts/iso2Names";

/** Common freelance / EU markets first in the country select. */
const PRIORITY_COUNTRY_CODES = [
  "IT",
  "CH",
  "DE",
  "AT",
  "FR",
  "ES",
  "PT",
  "NL",
  "BE",
  "LU",
  "GB",
  "IE",
  "SE",
  "NO",
  "DK",
  "FI",
  "PL",
  "CZ",
  "RO",
  "HU",
  "GR",
  "US",
  "CA",
  "AU",
  "NZ",
  "SG",
  "AE",
  "IN",
] as const;

export type CountryOption = { code: string; label: string };

export const PROFILE_CURRENCIES = [
  "EUR",
  "CHF",
  "USD",
  "GBP",
  "PLN",
  "CZK",
  "SEK",
  "NOK",
  "DKK",
  "RON",
  "HUF",
  "CAD",
  "AUD",
] as const;

export const PROFILE_RATE_UNITS = ["hour", "day", "week", "month", "project"] as const;

export type ProfileRateUnit = (typeof PROFILE_RATE_UNITS)[number];
export type ProfileCurrency = (typeof PROFILE_CURRENCIES)[number];

export function profileCountryOptions(): CountryOption[] {
  const priority = new Set<string>(PRIORITY_COUNTRY_CODES);
  const rest = Object.entries(ISO2_TO_ECHARTS_NAME)
    .filter(([code]) => !priority.has(code))
    .map(([code, name]) => ({ code, label: `${name} (${code})` }))
    .sort((a, b) => a.label.localeCompare(b.label, "en"));
  const head = PRIORITY_COUNTRY_CODES.filter((code) => ISO2_TO_ECHARTS_NAME[code]).map(
    (code) => ({
      code,
      label: `${ISO2_TO_ECHARTS_NAME[code]} (${code})`,
    }),
  );
  return [...head, ...rest];
}

export function normalizeCountryCode(raw: string): string {
  const code = raw.trim().toUpperCase();
  if (!code) return "";
  if (ISO2_TO_ECHARTS_NAME[code]) return code;
  return "";
}

export function normalizeCurrency(raw: string): ProfileCurrency {
  const c = raw.trim().toUpperCase();
  return (PROFILE_CURRENCIES as readonly string[]).includes(c)
    ? (c as ProfileCurrency)
    : "EUR";
}

export function normalizeRateUnit(raw: string): ProfileRateUnit {
  const u = raw.trim().toLowerCase();
  return (PROFILE_RATE_UNITS as readonly string[]).includes(u)
    ? (u as ProfileRateUnit)
    : "day";
}
