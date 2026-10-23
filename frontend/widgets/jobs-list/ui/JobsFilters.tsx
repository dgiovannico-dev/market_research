"use client";

import { startTransition, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { useTranslations } from "next-intl";
import { usePathname, useRouter } from "@/i18n/navigation";
import { MultiSelectFacet } from "@/shared/ui/MultiSelectFacet";
import { api } from "@/lib/api";
import {
  jobsUrlFiltersEqual,
  parseJobsUrlFilters,
  writeJobsFiltersToSearchParams,
  type JobsUrlFilterState,
} from "@/lib/jobsListParams";
import type { ResearchJobFacets } from "@/entities/research-intent";

type Props = {
  lens: "market" | "focus" | "compare";
  queryIds: number[];
};

const fieldClass =
  "rounded-md border border-[var(--line)] bg-[var(--card)] px-3 py-2 text-sm text-[var(--ink)] placeholder:text-[var(--muted)] focus:border-[var(--signal)] focus:outline-none";

const EMPTY: JobsUrlFilterState = {
  q: "",
  countries: [],
  sources: [],
  contracts: [],
  remotes: [],
};

export function JobsFilters({ lens, queryIds }: Props) {
  const t = useTranslations("jobs");
  const searchParams = useSearchParams();
  const pathname = usePathname();
  const router = useRouter();

  const [draft, setDraft] = useState<JobsUrlFilterState>(() =>
    parseJobsUrlFilters((k) => searchParams.get(k)),
  );
  const [facets, setFacets] = useState<ResearchJobFacets | null>(null);

  // Sync from URL when filter keys change — not on page/sort (would wipe draft).
  const filterUrlKey = [
    searchParams.get("q"),
    searchParams.get("technology"),
    searchParams.get("countries"),
    searchParams.get("country_code"),
    searchParams.get("sources"),
    searchParams.get("source_id"),
    searchParams.get("contracts"),
    searchParams.get("contract_type"),
    searchParams.get("remotes"),
    searchParams.get("remote_type"),
  ].join("\0");

  useEffect(() => {
    const fromUrl = parseJobsUrlFilters((k) => searchParams.get(k));
    setDraft((prev) => (jobsUrlFiltersEqual(prev, fromUrl) ? prev : fromUrl));
    // eslint-disable-next-line react-hooks/exhaustive-deps -- intentional: filterUrlKey only
  }, [filterUrlKey]);

  useEffect(() => {
    let cancelled = false;
    api
      .researchJobFacets({
        lens,
        query_id: queryIds[0],
      })
      .then((data) => {
        if (!cancelled) setFacets(data);
      })
      .catch(() => {
        if (!cancelled) {
          setFacets({ countries: [], sources: [], contracts: [], remotes: [] });
        }
      });
    return () => {
      cancelled = true;
    };
  }, [lens, queryIds]);

  const commit = (next: JobsUrlFilterState) => {
    const params = new URLSearchParams(searchParams.toString());
    writeJobsFiltersToSearchParams(params, next, { lens, queryIds });
    const qs = params.toString();
    startTransition(() => {
      router.replace(qs ? `${pathname}?${qs}` : pathname, { scroll: false });
    });
  };

  const facetProps = {
    emptyLabel: t("filterNone"),
    selectedCountLabel: t("filterSelectedCount"),
    clearLabel: t("filterClear"),
  };

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-end gap-2">
        <label className="flex min-w-[12rem] flex-1 flex-col gap-1 text-xs text-[var(--muted)]">
          {t("filterSearch")}
          <input
            value={draft.q}
            onChange={(e) => setDraft((d) => ({ ...d, q: e.target.value }))}
            placeholder={t("placeholderSearch")}
            className={fieldClass}
            autoComplete="off"
          />
        </label>
        <button
          type="button"
          onClick={() => commit(draft)}
          className="rounded-md bg-[var(--signal)] px-4 py-2 text-sm font-medium text-white transition-opacity hover:opacity-90"
        >
          {t("apply")}
        </button>
        <button
          type="button"
          onClick={() => {
            setDraft(EMPTY);
            commit(EMPTY);
          }}
          className="rounded-md border border-[var(--line)] px-4 py-2 text-sm text-[var(--ink)] transition-opacity hover:opacity-90"
        >
          {t("reset")}
        </button>
      </div>
      <div className="flex flex-wrap gap-3">
        <MultiSelectFacet
          label={t("filterCountries")}
          options={(facets?.countries ?? []).map((c) => ({ value: c, label: c }))}
          selected={draft.countries}
          onChange={(countries) => setDraft((d) => ({ ...d, countries }))}
          {...facetProps}
        />
        <MultiSelectFacet
          label={t("filterSources")}
          options={(facets?.sources ?? []).map((s) => ({
            value: String(s.id),
            label: s.name,
          }))}
          selected={draft.sources}
          onChange={(sources) => setDraft((d) => ({ ...d, sources }))}
          {...facetProps}
        />
        <MultiSelectFacet
          label={t("filterContracts")}
          options={(facets?.contracts ?? []).map((c) => ({ value: c, label: c }))}
          selected={draft.contracts}
          onChange={(contracts) => setDraft((d) => ({ ...d, contracts }))}
          {...facetProps}
        />
        <MultiSelectFacet
          label={t("filterRemotes")}
          options={(facets?.remotes ?? []).map((r) => ({ value: r, label: r }))}
          selected={draft.remotes}
          onChange={(remotes) => setDraft((d) => ({ ...d, remotes }))}
          {...facetProps}
        />
      </div>
    </div>
  );
}
