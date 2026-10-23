import { defineRouting } from "next-intl/routing";

export const locales = ["en", "it"] as const;
export type AppLocale = (typeof locales)[number];

export const routing = defineRouting({
  locales,
  defaultLocale: "en",
  localePrefix: "always",
});

export function isAppLocale(value: string): value is AppLocale {
  return (locales as readonly string[]).includes(value);
}

/** Browser Accept-Language / navigator: it* → it, else en. */
export function localeFromBrowserTag(tag: string | null | undefined): AppLocale {
  if (!tag) return "en";
  const primary = tag.trim().split(",")[0]?.split("-")[0]?.toLowerCase() ?? "";
  return primary === "it" ? "it" : "en";
}
