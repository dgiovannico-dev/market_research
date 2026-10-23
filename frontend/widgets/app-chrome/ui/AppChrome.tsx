"use client";

import { useLocale, useTranslations } from "next-intl";
import { Suspense, useEffect, useState, type ReactNode } from "react";
import { NAV_ZONES } from "@/lib/navZones";
import {
  PrefsPanel,
  useDashboardPrefs,
  type AppLocale,
} from "@/features/dashboard-prefs";
import {
  ANALYTICS_COUNTRY_PATHS,
  CountryFilter,
} from "@/features/country-filter";
import { PrimaryNav } from "./PrimaryNav";
import { Link, usePathname, useRouter } from "@/i18n/navigation";

export function AppChrome({ children }: { children: ReactNode }) {
  const t = useTranslations("nav");
  const locale = useLocale() as AppLocale;
  const pathname = usePathname();
  const router = useRouter();
  const { prefs, setViewMode, setLocale, hydrated } = useDashboardPrefs();
  const [panelOpen, setPanelOpen] = useState(false);
  const hidden = new Set(prefs.nav_hidden);
  const showCountryFilter = ANALYTICS_COUNTRY_PATHS.has(pathname);

  const zones = NAV_ZONES.map((zone) => ({
    ...zone,
    items: zone.items.filter((item) => !hidden.has(item.href)),
  })).filter((zone) => zone.items.length > 0);

  useEffect(() => {
    if (!hydrated) return;
    if (prefs.locale !== locale) {
      router.replace(pathname, { locale: prefs.locale });
    }
  }, [hydrated, prefs.locale, locale, pathname, router]);

  const switchLocale = (next: AppLocale) => {
    setLocale(next);
    if (next !== locale) {
      router.replace(pathname, { locale: next });
    }
  };

  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-30 border-b border-[var(--line)] bg-[color-mix(in_srgb,var(--card)_82%,transparent)] backdrop-blur-md">
        <div className="mx-auto flex max-w-7xl flex-col gap-2.5 px-4 py-3">
          {/* Row 1: brand + chrome controls (never share a wrap line with nav). */}
          <div className="flex flex-wrap items-center justify-between gap-x-4 gap-y-2">
            <Link href="/" className="group min-w-0 shrink">
              <p className="font-display text-[0.65rem] uppercase tracking-[0.22em] signal-text">
                {t("brand")}
              </p>
              <p className="truncate font-display text-sm font-semibold tracking-tight text-[var(--ink)] group-hover:text-[var(--signal)] sm:text-base">
                {t("tagline")}
              </p>
            </Link>

            <div className="flex flex-wrap items-center justify-end gap-2">
              {showCountryFilter ? (
                <Suspense fallback={null}>
                  <CountryFilter.Control />
                </Suspense>
              ) : null}
              <div
                className="inline-flex rounded-full border border-[var(--line)] p-0.5 text-xs"
                role="group"
                aria-label={t("locale")}
              >
                <button
                  type="button"
                  className={`rounded-full px-3 py-1.5 ${
                    prefs.locale === "en" ? "bg-[var(--signal)] text-white" : "opacity-70"
                  }`}
                  onClick={() => switchLocale("en")}
                >
                  {t("localeEn")}
                </button>
                <button
                  type="button"
                  className={`rounded-full px-3 py-1.5 ${
                    prefs.locale === "it" ? "bg-[var(--signal)] text-white" : "opacity-70"
                  }`}
                  onClick={() => switchLocale("it")}
                >
                  {t("localeIt")}
                </button>
              </div>
              <div
                className="inline-flex rounded-full border border-[var(--line)] p-0.5 text-xs"
                role="group"
                aria-label={t("viewMode")}
              >
                <button
                  type="button"
                  className={`rounded-full px-3 py-1.5 ${
                    prefs.view_mode === "guided" ? "bg-[var(--signal)] text-white" : "opacity-70"
                  }`}
                  onClick={() => setViewMode("guided")}
                >
                  {t("guided")}
                </button>
                <button
                  type="button"
                  className={`rounded-full px-3 py-1.5 ${
                    prefs.view_mode === "trends_only"
                      ? "bg-[var(--signal)] text-white"
                      : "opacity-70"
                  }`}
                  onClick={() => setViewMode("trends_only")}
                >
                  {t("trendsOnly")}
                </button>
              </div>
              <button
                type="button"
                className="rounded-full border border-[var(--line)] px-3 py-1.5 text-xs hover:border-[var(--signal)]"
                onClick={() => setPanelOpen((o) => !o)}
              >
                {t("prefs")}
              </button>
              {!hydrated && (
                <span className="text-xs opacity-50" suppressHydrationWarning>
                  …
                </span>
              )}
            </div>
          </div>

          {/* Row 2: primary zones — full width, clear from chrome controls. */}
          <div className="border-t border-[var(--line)] pt-2">
            <PrimaryNav zones={zones} />
          </div>

          {panelOpen ? <PrefsPanel onClose={() => setPanelOpen(false)} /> : null}
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-4 py-6">{children}</main>
    </div>
  );
}
