"use client";

import { useTranslations } from "next-intl";
import type { Ref } from "react";
import { useInfiniteSentinel } from "@/shared/hooks/useInfiniteSentinel";

type Props = {
  hasMore: boolean;
  loading?: boolean;
  onLoadMore: () => void;
  shown?: number;
  total?: number;
  /** Optional external ref if parent already owns the sentinel. */
  sentinelRef?: Ref<HTMLDivElement>;
};

/**
 * Bottom-of-list footer: intersection sentinel + status line for infinite scroll.
 */
export function ScrollLoadFooter({
  hasMore,
  loading = false,
  onLoadMore,
  shown,
  total,
  sentinelRef,
}: Props) {
  const t = useTranslations("common");
  const internalRef = useInfiniteSentinel(hasMore && !loading, onLoadMore, {
    observeKey: shown ?? 0,
  });
  const ref = sentinelRef ?? internalRef;

  if (!hasMore && !loading && (shown == null || total == null)) {
    return null;
  }

  return (
    <div className="space-y-2 py-3 text-center text-xs text-[var(--muted)]">
      {shown != null && total != null ? (
        <p style={{ fontFamily: "var(--mono)" }}>
          {t("scrollShown", { shown, total })}
        </p>
      ) : null}
      {loading ? <p>{t("scrollLoading")}</p> : null}
      {!loading && !hasMore && total != null && total > 0 ? (
        <p>{t("scrollEnd")}</p>
      ) : null}
      {hasMore ? <div ref={ref} className="h-4 w-full" aria-hidden /> : null}
    </div>
  );
}
