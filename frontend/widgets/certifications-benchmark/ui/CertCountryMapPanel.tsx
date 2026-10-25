"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { GeoWorldMapLazy, RankBarsLazy } from "@/shared/ui/charts";
import type { MarketCertificationsByCountry } from "@/entities/market";
import { useDashboardPrefs } from "@/features/dashboard-prefs";
import { useDashboardCountries } from "@/features/country-filter";
import { useDashboardLens } from "@/features/lens-toggle";
import { api } from "@/lib/api";

export function CertCountryMapPanel() {
  const t = useTranslations("certificationsPage");
  const tCharts = useTranslations("charts");
  const { prefs, hydrated } = useDashboardPrefs();
  const { lens, queryIds } = useDashboardLens();
  /** Chrome country filter scopes the API; map clicks stay local so the choropleth does not collapse to one ISO. */
  const { countries } = useDashboardCountries();
  const [data, setData] = useState<MarketCertificationsByCountry | null>(null);
  const [error, setError] = useState(false);
  const [selected, setSelected] = useState<string | null>(null);

  const selectCountry = (iso: string) => {
    const code = iso.trim().toUpperCase();
    if (!code) return;
    setSelected((prev) => (prev === code ? null : code));
  };

  useEffect(() => {
    if (!hydrated) return;
    let cancelled = false;
    setError(false);
    api
      .certificationsByCountry({
        days: Math.min(prefs.period_days, 365),
        lens,
        queryIds,
        countries,
        topNPerCountry: 5,
        topCountries: 40,
      })
      .then((res) => {
        if (cancelled) return;
        setData(res);
        const first = res.countries?.[0]?.country_code ?? null;
        setSelected((prev) => {
          if (prev && res.countries?.some((c) => c.country_code === prev)) {
            return prev;
          }
          return first;
        });
      })
      .catch(() => {
        if (!cancelled) {
          setData(null);
          setError(true);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [hydrated, prefs.period_days, lens, queryIds, countries]);

  const rows = data?.countries ?? [];
  // Selection drives highlight + local top bars only — table always lists all
  // countries returned by the API (filtering the table to `selected` made the
  // panel look like a single-country corpus, e.g. only SG).
  const activeCode =
    countries.length === 1
      ? countries[0]
      : selected && rows.some((r) => r.country_code === selected)
        ? selected
        : rows[0]?.country_code ?? null;
  const active =
    rows.find((c) => c.country_code === activeCode) ?? rows[0] ?? null;
  const countryRank = (active?.top ?? []).map((it) => ({
    label: it.certification,
    value: it.job_mentions,
  }));

  return (
    <section className="space-y-3" aria-labelledby="cert-by-country">
      <h2
        id="cert-by-country"
        className="text-sm font-semibold uppercase tracking-[0.1em] text-[var(--muted)]"
      >
        {t("byCountryTitle")}
      </h2>
      <p className="text-xs text-[var(--muted)]">{t("byCountryCaption")}</p>
      {error ? (
        <p className="text-sm text-[var(--danger)]">{t("byCountryLoadFailed")}</p>
      ) : null}
      {!error && rows.length === 0 ? (
        <p className="text-sm text-[var(--muted)]">{t("byCountryEmpty")}</p>
      ) : null}

      {rows.length > 0 ? (
        <>
          <GeoWorldMapLazy
            items={data?.map_items ?? []}
            unknownJobs={data?.unknown_jobs ?? 0}
            periodDays={data?.period_days ?? prefs.period_days}
            sampleSize={data?.sample_size ?? null}
            title={t("byCountryMapTitle")}
            onCountryClick={selectCountry}
          />

          <div className="grid gap-4 lg:grid-cols-2">
            <div className="overflow-x-auto">
              <table className="w-full min-w-[20rem] text-left text-sm">
                <caption className="sr-only">{t("byCountryTableCaption")}</caption>
                <thead>
                  <tr className="border-b border-[var(--line)] text-[0.65rem] uppercase tracking-[0.1em] text-[var(--muted)]">
                    <th className="py-2 pr-2 font-semibold">{t("colCountry")}</th>
                    <th className="py-2 pr-2 font-semibold">{t("colJobsWithCerts")}</th>
                    <th className="py-2 font-semibold">{t("colTopCert")}</th>
                  </tr>
                </thead>
                <tbody>
                  {rows.map((row) => {
                    const isActive = row.country_code === active?.country_code;
                    return (
                      <tr
                        key={row.country_code}
                        className={
                          isActive
                            ? "bg-[var(--signal)]/10 text-[var(--ink)]"
                            : "text-[var(--ink)]"
                        }
                      >
                        <td className="py-1.5 pr-2">
                          <button
                            type="button"
                            className="font-mono text-xs underline-offset-2 hover:underline"
                            aria-pressed={isActive}
                            onClick={() => selectCountry(row.country_code)}
                          >
                            {row.country_code}
                          </button>
                        </td>
                        <td className="py-1.5 pr-2 font-mono text-xs">
                          {row.jobs_with_certs}
                        </td>
                        <td className="py-1.5 text-xs">
                          {row.top_certification
                            ? `${row.top_certification} (${row.top_mentions})`
                            : "—"}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {countryRank.length > 0 && active ? (
              <RankBarsLazy
                items={countryRank}
                periodDays={data?.period_days ?? prefs.period_days}
                sampleSize={active.jobs_with_certs}
                title={t("byCountryBarsTitle", { country: active.country_code })}
                valueLabel={tCharts("colMentions")}
              />
            ) : null}
          </div>
        </>
      ) : null}
    </section>
  );
}
