"use client";

import { useEffect, useState } from "react";

const DEFAULT_PAGE = 30;

/**
 * Progressive reveal for already-fetched arrays (skills, catalog, table rows).
 * Resets when `items` identity or length changes meaningfully via resetKey.
 */
export function useClientPageWindow<T>(
  items: readonly T[],
  pageSize = DEFAULT_PAGE,
  resetKey?: string | number,
) {
  const [visibleCount, setVisibleCount] = useState(pageSize);

  useEffect(() => {
    setVisibleCount(pageSize);
  }, [pageSize, resetKey, items.length]);

  const visible = items.slice(0, visibleCount);
  const hasMore = visibleCount < items.length;
  const loadMore = () =>
    setVisibleCount((n) => Math.min(n + pageSize, items.length));

  return {
    visible,
    hasMore,
    loadMore,
    shown: visible.length,
    total: items.length,
  };
}
