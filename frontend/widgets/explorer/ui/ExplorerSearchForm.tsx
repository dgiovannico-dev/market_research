"use client";

import { FormEvent, startTransition, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { useTranslations } from "next-intl";
import { MultiSelectFacet } from "@/shared/ui/MultiSelectFacet";
import { usePathname, useRouter } from "@/i18n/navigation";
import { api } from "@/lib/api";
import type { DashboardLens } from "@/lib/api";
import type { ResearchIntent } from "@/entities/research-intent";

type Props = {
  q?: string;
  country?: string;
  lens: DashboardLens;
  queryId?: number;
  intents: ResearchIntent[];
};

function parseLens(raw: string | null | undefined): DashboardLens {
  if (raw === "focus" || raw === "compare" || raw === "market") return raw;
  return "market";
}

function parseCountriesCsv(raw: string | null | undefined): string[] {
  if (!raw?.trim()) return [];
  const out: string[] = [];
  const seen = new Set<string>();
  for (const part of raw.split(",")) {
    const code = part.trim().toUpperCase();
    if (!code || code === "ALL" || seen.has(code)) continue;
    seen.add(code);
    out.push(code);
  }
  return out;
}

/**
 * Client GET→URL filters for Explore.
 * URL uses chrome keys (`countries`, `query_ids`); page maps to research API
 * (`country_code`, `query_id`) — same pattern as JobsFilters / jobsListParams.
 */
export function ExplorerSearchForm({
  q: initialQ,
  country: initialCountry,
  lens: initialLens,
  queryId: initialQueryId,
  intents,
}: Props) {
  const t = useTranslations("explorer");
  const searchParams = useSearchParams();
  const pathname = usePathname();
  const router = useRouter();

  const [q, setQ] = useState(initialQ ?? "");
  const [countries, setCountries] = useState<string[]>(() =>
    parseCountriesCsv(initialCountry),
  );
  const [countryOptions, setCountryOptions] = useState<string[]>([]);
  const [lens, setLens] = useState<DashboardLens>(initialLens);
  const [queryId, setQueryId] = useState(
    initialQueryId != null ? String(initialQueryId) : "",
  );

  useEffect(() => {
    let cancelled = false;
    api
      .researchJobFacets({})
      .then((data) => {
        if (!cancelled) setCountryOptions(data.countries ?? []);
      })
      .catch(() => {
        if (!cancelled) setCountryOptions([]);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  // Soft URL updates (back/forward, shared chrome lens) must refresh drafts.
  useEffect(() => {
    const nextQ = (searchParams.get("q") || searchParams.get("technology") || "").trim();
    const nextCountries = parseCountriesCsv(
      searchParams.get("countries") ||
        searchParams.get("country_code") ||
        searchParams.get("country"),
    );
    const nextLens = parseLens(searchParams.get("lens"));
    const rawQid =
      (searchParams.get("query_ids") || "").split(",")[0]?.trim() ||
      searchParams.get("query_id") ||
      "";
    const n = Number(rawQid);
    const nextQid =
      Number.isFinite(n) && n > 0 ? String(Math.trunc(n)) : "";

    setQ(nextQ);
    setCountries(nextCountries);
    setLens(nextLens);
    setQueryId(nextQid);
  }, [searchParams]);

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    const params = new URLSearchParams(searchParams.toString());
    params.delete("technology");
    params.delete("country_code");
    params.delete("country");
    params.delete("query_id");

    const nextQ = q.trim();
    if (nextQ) params.set("q", nextQ);
    else params.delete("q");

    if (countries.length) params.set("countries", countries.join(","));
    else params.delete("countries");

    if (lens !== "market") params.set("lens", lens);
    else params.delete("lens");

    if (queryId) params.set("query_ids", queryId);
    else params.delete("query_ids");

    const qs = params.toString();
    startTransition(() => {
      router.replace(qs ? `${pathname}?${qs}` : pathname, { scroll: false });
    });
  }

  const facetCountryOptions = (
    countryOptions.length ? countryOptions : countries
  ).map((c) => ({ value: c, label: c }));

  return (
    <form
      onSubmit={onSubmit}
      className="space-y-3"
      role="search"
      aria-label={t("searchAria")}
    >
      <div className="flex flex-col gap-2 sm:flex-row sm:items-end">
        <label className="flex min-w-0 flex-1 flex-col gap-1 text-xs font-medium text-[var(--muted)]">
          {t("labelQ")}
          <input
            type="search"
            name="q"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder={t("placeholderKeyword")}
            className="w-full rounded border border-[var(--line)] bg-transparent px-3 py-2.5 text-sm text-[var(--ink)]"
            autoComplete="off"
            enterKeyHint="search"
          />
        </label>
        <button
          type="submit"
          className="shrink-0 rounded bg-[var(--signal)] px-4 py-2.5 text-sm font-medium text-white hover:opacity-90"
        >
          {t("filter")}
        </button>
      </div>

      <fieldset className="space-y-2 border-0 p-0">
        <legend className="font-display mb-1 text-xs uppercase tracking-[0.2em] text-[var(--muted)]">
          {t("filtersHeading")}
        </legend>
        <div className="flex flex-wrap items-end gap-2">
          <MultiSelectFacet
            label={t("labelCountry")}
            options={facetCountryOptions}
            selected={countries}
            onChange={setCountries}
            emptyLabel={t("filterNone")}
            selectedCountLabel={t("filterSelectedCount")}
            clearLabel={t("filterClear")}
          />

          <label className="flex flex-col gap-1 text-xs text-[var(--muted)]">
            {t("lensLabel")}
            <select
              name="lens"
              value={lens}
              onChange={(e) => setLens(parseLens(e.target.value))}
              className="rounded border border-[var(--line)] bg-transparent px-2 py-2 text-sm text-[var(--ink)]"
            >
              <option value="market">{t("lensMarket")}</option>
              <option value="focus">{t("lensFocus")}</option>
              <option value="compare">{t("lensCompare")}</option>
            </select>
          </label>

          <label className="flex flex-col gap-1 text-xs text-[var(--muted)]">
            {t("intentLabel")}
            <select
              name="query_ids"
              value={queryId}
              onChange={(e) => setQueryId(e.target.value)}
              className="min-w-[12rem] rounded border border-[var(--line)] bg-transparent px-2 py-2 text-sm text-[var(--ink)]"
            >
              <option value="">{t("intentAny")}</option>
              {intents.map((intent) => (
                <option key={intent.id} value={intent.id}>
                  [{intent.kind}] {intent.name}
                </option>
              ))}
            </select>
          </label>
        </div>
      </fieldset>
    </form>
  );
}
