"use client";

import { Suspense, useCallback, useEffect, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import { useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";
import { api } from "@/lib/api";
import {
  LensToggle,
  useDashboardLens,
} from "@/features/lens-toggle";
import { MarketCoverageBanner } from "@/features/dashboard-chrome";
import { JobsFilters } from "./JobsFilters";
import { JobsTable, asJobRow, type JobRow } from "./JobsTable";
import {
  parseJobsUrlFilters,
  toResearchJobsParams,
} from "@/lib/jobsListParams";

const PAGE_SIZE = 25;

function JobsListInner() {
  const t = useTranslations("jobs");
  const tCommon = useTranslations("common");
  const searchParams = useSearchParams();
  const { lens, queryIds } = useDashboardLens();

  const filters = parseJobsUrlFilters((k) => searchParams.get(k));
  const countriesCsv = filters.countries.join(",");
  const sourcesCsv = filters.sources.join(",");
  const contractsCsv = filters.contracts.join(",");
  const remotesCsv = filters.remotes.join(",");
  const sort = searchParams.get("sort") || "published_at";
  const order = searchParams.get("order") === "asc" ? "asc" : "desc";

  const filterKey = [
    filters.q,
    countriesCsv,
    sourcesCsv,
    contractsCsv,
    remotesCsv,
    sort,
    order,
    lens,
    queryIds.join(","),
  ].join("|");

  const [total, setTotal] = useState(0);
  const [items, setItems] = useState<JobRow[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const skipRef = useRef(0);
  const busyRef = useRef(false);

  const fetchPage = useCallback(
    async (skip: number, append: boolean) => {
      if (busyRef.current) return;
      busyRef.current = true;
      if (append) setLoadingMore(true);
      else setLoading(true);
      try {
        const res = await api.researchJobs(
          toResearchJobsParams({
            q: filters.q,
            countriesCsv,
            sourcesCsv,
            contractsCsv,
            remotesCsv,
            lens,
            queryIds,
            sort,
            order,
            skip,
            limit: PAGE_SIZE,
          }),
        );
        const rows = (res.items ?? []).flatMap((raw) => {
          if (!raw || typeof raw !== "object") return [];
          const row = asJobRow(raw as Record<string, unknown>);
          return row ? [row] : [];
        });
        setTotal(res.total ?? (append ? skip + rows.length : rows.length));
        setItems((prev) => (append ? [...prev, ...rows] : rows));
        skipRef.current = skip + rows.length;
        setError(null);
      } catch (e: unknown) {
        if (!append) {
          setItems([]);
          setTotal(0);
          skipRef.current = 0;
        }
        const detail = e instanceof Error ? e.message : String(e);
        setError(detail ? `${t("loadFailed")}: ${detail}` : t("loadFailed"));
      } finally {
        busyRef.current = false;
        setLoading(false);
        setLoadingMore(false);
      }
    },
    [
      filters.q,
      countriesCsv,
      sourcesCsv,
      contractsCsv,
      remotesCsv,
      lens,
      queryIds,
      sort,
      order,
      t,
    ],
  );

  useEffect(() => {
    skipRef.current = 0;
    void fetchPage(0, false);
  }, [filterKey, fetchPage]);

  const hasMore = items.length < total;

  const onLoadMore = () => {
    if (!hasMore || busyRef.current) return;
    void fetchPage(skipRef.current, true);
  };

  return (
    <div className="space-y-5">
      <header className="flex flex-wrap items-end justify-between gap-3">
        <div className="space-y-1">
          <h2 className="font-display text-2xl font-semibold tracking-tight text-[var(--ink)]">
            {t("title")}
          </h2>
          <p className="max-w-2xl text-sm text-[var(--muted)]">{t("subtitle")}</p>
          {!loading && !error ? (
            <p className="text-xs text-[var(--muted)]" style={{ fontFamily: "var(--mono)" }}>
              {t("sampleN", { n: total })}
            </p>
          ) : null}
        </div>
        <LensToggle.Control />
      </header>

      <MarketCoverageBanner sampleSize={loading || error ? null : total} />

      <JobsFilters lens={lens} queryIds={queryIds} />

      {error ? (
        <div
          className="space-y-1 rounded-xl border border-[var(--warn)]/40 bg-[var(--card)] p-4 text-sm text-[var(--warn)]"
          role="alert"
        >
          <p className="font-medium">{error}</p>
          <p className="text-xs text-[var(--muted)]">{t("loadFailedHint")}</p>
        </div>
      ) : null}

      {loading ? (
        <div className="rounded-xl border border-[var(--line)] bg-[var(--card)] p-4 text-sm text-[var(--muted)]">
          {tCommon("loading")}
        </div>
      ) : error ? null : items.length === 0 ? (
        <section className="space-y-2 rounded-xl border border-[var(--line)] bg-[var(--card)] p-5 text-sm text-[var(--muted)]">
          <p className="font-medium text-[var(--ink)]" style={{ fontFamily: "var(--mono)" }}>
            {t("sampleN", { n: total })}
          </p>
          <p>{t("empty")}</p>
          <p>
            {t("emptyHint")}{" "}
            <Link href="/market-scan" className="font-medium underline signal-text">
              {t("openScan")}
            </Link>{" "}
            /{" "}
            <Link href="/focus" className="font-medium underline signal-text">
              {t("openFocus")}
            </Link>
          </p>
        </section>
      ) : (
        <JobsTable
          items={items}
          total={total}
          hasMore={hasMore}
          loadingMore={loadingMore}
          onLoadMore={onLoadMore}
        />
      )}
    </div>
  );
}

export function JobsListDashboard() {
  const t = useTranslations("common");
  return (
    <Suspense
      fallback={
        <div className="rounded-xl border border-[var(--line)] bg-[var(--card)] p-6 text-sm text-[var(--muted)]">
          {t("loading")}
        </div>
      }
    >
      <LensToggle.Provider>
        <JobsListInner />
      </LensToggle.Provider>
    </Suspense>
  );
}
