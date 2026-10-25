"use client";

import { useMemo, useRef, useState } from "react";
import { useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";
import {
  CHART_TOP_N_OPTIONS,
  DEFAULT_CHART_TOP_N,
  isChartTopN,
  type ChartTopN,
} from "@/shared/ui/charts/chartTopN";
import { useClientPageWindow } from "@/shared/hooks/useClientPageWindow";
import { ScrollLoadFooter } from "@/shared/ui/ScrollLoadFooter";

export type TechListItem = {
  technology: string;
  job_skill_mentions: number;
};

export type CountryListItem = {
  country_code: string;
  jobs: number;
};

type Props = {
  techs: TechListItem[];
  countries: CountryListItem[];
  loading: boolean;
  /** Click ISO2 → CountryFilter (same as GeoStrip). */
  onCountryClick?: (iso2: string) => void;
};

const LIST_PAGE = 15;

function TopNSelect({
  value,
  onChange,
  ariaLabel,
}: {
  value: ChartTopN;
  onChange: (n: ChartTopN) => void;
  ariaLabel: string;
}) {
  const tCharts = useTranslations("charts");
  return (
    <label className="flex items-center gap-1.5 text-xs text-[var(--muted)]">
      <span>{tCharts("topNLabel")}</span>
      <select
        className="rounded border border-[var(--line)] bg-transparent px-1.5 py-1 text-[var(--ink)]"
        value={value}
        aria-label={ariaLabel}
        onChange={(e) => {
          const n = Number(e.target.value);
          if (isChartTopN(n)) onChange(n);
        }}
      >
        {CHART_TOP_N_OPTIONS.map((n) => (
          <option key={n} value={n}>
            {n}
          </option>
        ))}
      </select>
    </label>
  );
}

export function ExecutiveTopLists({
  techs,
  countries,
  loading,
  onCountryClick,
}: Props) {
  const t = useTranslations("executive");
  const tCharts = useTranslations("charts");
  const [techTopN, setTechTopN] = useState<ChartTopN>(DEFAULT_CHART_TOP_N);
  const [countryTopN, setCountryTopN] =
    useState<ChartTopN>(DEFAULT_CHART_TOP_N);
  const techScrollRef = useRef<HTMLDivElement | null>(null);
  const countryScrollRef = useRef<HTMLDivElement | null>(null);

  const cappedTechs = useMemo(
    () => techs.slice(0, techTopN),
    [techs, techTopN],
  );
  const cappedCountries = useMemo(
    () => countries.slice(0, countryTopN),
    [countries, countryTopN],
  );

  const techPage = useClientPageWindow(
    cappedTechs,
    LIST_PAGE,
    `${techTopN}|${cappedTechs.length}|${cappedTechs[0]?.technology ?? ""}`,
  );
  const countryPage = useClientPageWindow(
    cappedCountries,
    LIST_PAGE,
    `${countryTopN}|${cappedCountries.length}|${cappedCountries[0]?.country_code ?? ""}`,
  );

  return (
    <section className="grid gap-4 md:grid-cols-2">
      <article className="rounded-xl border border-[var(--line)] bg-[var(--card)] p-4">
        <header className="flex flex-wrap items-center justify-between gap-2">
          <h2 className="font-display text-base font-semibold tracking-tight text-[var(--ink)]">
            {t("topTechnologies")}
          </h2>
          <TopNSelect
            value={techTopN}
            onChange={setTechTopN}
            ariaLabel={tCharts("topNAria")}
          />
        </header>
        <div
          ref={techScrollRef}
          className="mt-3 max-h-80 overflow-y-auto overscroll-contain"
        >
          <ul className="space-y-0 text-sm">
            {loading && techs.length === 0 ? (
              <li className="text-[var(--muted)]">{t("summaryLoading")}</li>
            ) : cappedTechs.length === 0 ? (
              <li className="text-[var(--muted)]">{t("noTechnologies")}</li>
            ) : (
              techPage.visible.map((item) => (
                <li
                  key={item.technology}
                  className="flex justify-between border-b border-[var(--line)] py-2 last:border-b-0"
                >
                  <Link
                    href={`/explorer?technology=${encodeURIComponent(item.technology)}`}
                    className="text-[var(--ink)] hover:text-[var(--signal)]"
                  >
                    {item.technology}
                  </Link>
                  <span
                    className="text-[var(--muted)]"
                    style={{ fontFamily: "var(--mono)" }}
                  >
                    {item.job_skill_mentions}
                  </span>
                </li>
              ))
            )}
          </ul>
          {cappedTechs.length > 0 ? (
            <ScrollLoadFooter
              hasMore={techPage.hasMore}
              isExpanded={techPage.isExpanded}
              onLoadMore={techPage.loadMore}
              onExpandAll={techPage.expandAll}
              onCollapse={techPage.collapse}
              shown={techPage.shown}
              total={techPage.total}
              scrollRootRef={techScrollRef}
            />
          ) : null}
        </div>
      </article>
      <article className="rounded-xl border border-[var(--line)] bg-[var(--card)] p-4">
        <header className="flex flex-wrap items-center justify-between gap-2">
          <h2 className="font-display text-base font-semibold tracking-tight text-[var(--ink)]">
            {t("topCountries")}
          </h2>
          <TopNSelect
            value={countryTopN}
            onChange={setCountryTopN}
            ariaLabel={tCharts("topNAria")}
          />
        </header>
        <div
          ref={countryScrollRef}
          className="mt-3 max-h-80 overflow-y-auto overscroll-contain"
        >
          <ul className="space-y-0 text-sm">
            {loading && countries.length === 0 ? (
              <li className="text-[var(--muted)]">{t("summaryLoading")}</li>
            ) : cappedCountries.length === 0 ? (
              <li className="text-[var(--muted)]">{t("noCountries")}</li>
            ) : (
              countryPage.visible.map((c) => (
                <li
                  key={c.country_code}
                  className="flex justify-between border-b border-[var(--line)] py-2 last:border-b-0"
                >
                  {onCountryClick ? (
                    <button
                      type="button"
                      className="font-mono text-[var(--ink)] underline-offset-2 hover:text-[var(--signal)] hover:underline"
                      onClick={() => onCountryClick(c.country_code)}
                    >
                      {c.country_code}
                    </button>
                  ) : (
                    <span
                      className="text-[var(--ink)]"
                      style={{ fontFamily: "var(--mono)" }}
                    >
                      {c.country_code}
                    </span>
                  )}
                  <span
                    className="text-[var(--muted)]"
                    style={{ fontFamily: "var(--mono)" }}
                  >
                    {c.jobs}
                  </span>
                </li>
              ))
            )}
          </ul>
          {cappedCountries.length > 0 ? (
            <ScrollLoadFooter
              hasMore={countryPage.hasMore}
              isExpanded={countryPage.isExpanded}
              onLoadMore={countryPage.loadMore}
              onExpandAll={countryPage.expandAll}
              onCollapse={countryPage.collapse}
              shown={countryPage.shown}
              total={countryPage.total}
              scrollRootRef={countryScrollRef}
            />
          ) : null}
        </div>
      </article>
    </section>
  );
}
