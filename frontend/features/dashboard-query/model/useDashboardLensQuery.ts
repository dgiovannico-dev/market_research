"use client";

import { useEffect, useRef, useState } from "react";
import type { DashboardLens } from "@/shared/api";

export type DashboardQueryStatus = "idle" | "loading" | "success" | "error";

export type DashboardLensQueryContext = {
  days: number;
  lens: DashboardLens;
  queryIds: number[];
  countries: string[];
};

export type UseDashboardLensQueryOptions<T> = {
  hydrated: boolean;
  days: number;
  lens: DashboardLens;
  queryIds: number[];
  countries: string[];
  /** Stable enough via ref — identity changes do not re-fetch. */
  fetcher: (ctx: DashboardLensQueryContext) => Promise<T>;
  fallbackError: string;
  /** Keep showing previous data while a new request is in flight. Default true. */
  keepPreviousData?: boolean;
};

export type UseDashboardLensQueryResult<T> = {
  data: T | null;
  error: string | null;
  status: DashboardQueryStatus;
  /** True when showing previous data after lens/period/country change. */
  isStale: boolean;
  /** True until first success/error for this mount, or while refreshing. */
  loading: boolean;
};

/**
 * Shared hydrated → fetch lifecycle for analytics dashboards.
 * Clears error on each new request; optional keepPreviousData + isStale.
 */
export function useDashboardLensQuery<T>(
  opts: UseDashboardLensQueryOptions<T>,
): UseDashboardLensQueryResult<T> {
  const {
    hydrated,
    days,
    lens,
    queryIds,
    countries,
    fetcher,
    fallbackError,
    keepPreviousData = true,
  } = opts;

  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<DashboardQueryStatus>("idle");
  const [isStale, setIsStale] = useState(false);

  const fetcherRef = useRef(fetcher);
  fetcherRef.current = fetcher;
  const dataRef = useRef(data);
  dataRef.current = data;

  const queryIdsKey = queryIds.join(",");
  const countriesKey = countries.join(",");

  useEffect(() => {
    if (!hydrated) return;
    let cancelled = false;
    setError(null);
    setStatus("loading");
    if (keepPreviousData) {
      // Dim only when we already have something to keep; first paint stays crisp.
      setIsStale(dataRef.current !== null);
    } else {
      setData(null);
      setIsStale(false);
    }

    const ids = queryIdsKey
      ? queryIdsKey.split(",").map((x) => Number(x)).filter((n) => Number.isFinite(n))
      : [];
    const codes = countriesKey ? countriesKey.split(",").filter(Boolean) : [];

    fetcherRef
      .current({ days, lens, queryIds: ids, countries: codes })
      .then((res) => {
        if (cancelled) return;
        setData(res);
        setError(null);
        setIsStale(false);
        setStatus("success");
      })
      .catch((e: unknown) => {
        if (cancelled) return;
        setError(e instanceof Error ? e.message : fallbackError);
        setStatus("error");
        setIsStale(false);
      });

    return () => {
      cancelled = true;
    };
  }, [
    hydrated,
    days,
    lens,
    queryIdsKey,
    countriesKey,
    fallbackError,
    keepPreviousData,
  ]);

  const loading =
    status === "loading" || (hydrated && data === null && error === null);

  return { data, error, status, isStale, loading };
}
