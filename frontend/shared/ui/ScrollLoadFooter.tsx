"use client";

import { useTranslations } from "next-intl";
import {
  useCallback,
  type Ref,
  type RefObject,
} from "react";
import { useInfiniteSentinel } from "@/shared/hooks/useInfiniteSentinel";

type Props = {
  hasMore: boolean;
  loading?: boolean;
  onLoadMore: () => void;
  /** Reveal the full client-side window (long lists). */
  onExpandAll?: () => void;
  /** Reset to the initial page size after expand-all. */
  onCollapse?: () => void;
  /** True when the list is fully expanded past the first page. */
  isExpanded?: boolean;
  shown?: number;
  total?: number;
  /**
   * Optional external ref. When set, it is merged with the IO sentinel so
   * parents can observe the same node without breaking infinite scroll.
   */
  sentinelRef?: Ref<HTMLDivElement>;
  /**
   * Scroll parent for nested max-height lists (IntersectionObserver root).
   * When set, viewport-safe infinite scroll stays on. Without it, only
   * explicit buttons are used so page-level scroll (docs videos) cannot
   * inflate the document height.
   */
  scrollRootRef?: RefObject<Element | null>;
};

function assignRef<T>(ref: Ref<T> | undefined, value: T | null) {
  if (!ref) return;
  if (typeof ref === "function") ref(value);
  else ref.current = value;
}

const btnClass =
  "rounded border border-[var(--line)] px-2.5 py-1 text-xs text-[var(--ink)] hover:border-[var(--signal)] disabled:opacity-50";

/**
 * Bottom-of-list footer: status + Show more / Expand all (and optional
 * nested infinite scroll when `scrollRootRef` is set).
 */
export function ScrollLoadFooter({
  hasMore,
  loading = false,
  onLoadMore,
  onExpandAll,
  onCollapse,
  isExpanded = false,
  shown,
  total,
  sentinelRef,
  scrollRootRef,
}: Props) {
  const t = useTranslations("common");
  const useInfinite = Boolean(scrollRootRef) && hasMore && !loading;
  const internalRef = useInfiniteSentinel(useInfinite, onLoadMore, {
    observeKey: shown ?? 0,
    rootRef: scrollRootRef,
  });

  const setSentinelNode = useCallback(
    (node: HTMLDivElement | null) => {
      internalRef.current = node;
      assignRef(sentinelRef, node);
    },
    [internalRef, sentinelRef],
  );

  const showStatus = shown != null && total != null;
  const showCollapse = Boolean(onCollapse) && isExpanded && !loading;
  const showButtons =
    !loading && (hasMore || showCollapse) && !useInfinite;

  if (!hasMore && !loading && !showStatus && !showCollapse) {
    return null;
  }

  return (
    <div className="space-y-2 py-3 text-center text-xs text-[var(--muted)]">
      {showStatus ? (
        <p style={{ fontFamily: "var(--mono)" }}>
          {t("scrollShown", { shown: shown!, total: total! })}
        </p>
      ) : null}
      {loading ? <p>{t("scrollLoading")}</p> : null}
      {!loading && !hasMore && !isExpanded && total != null && total > 0 ? (
        <p>{t("scrollEnd")}</p>
      ) : null}
      {showButtons ? (
        <div className="flex flex-wrap items-center justify-center gap-2">
          {hasMore ? (
            <button
              type="button"
              className={btnClass}
              onClick={onLoadMore}
            >
              {t("scrollShowMore")}
            </button>
          ) : null}
          {hasMore && onExpandAll ? (
            <button
              type="button"
              className={btnClass}
              onClick={onExpandAll}
            >
              {t("scrollExpandAll")}
            </button>
          ) : null}
          {showCollapse ? (
            <button type="button" className={btnClass} onClick={onCollapse}>
              {t("scrollCollapse")}
            </button>
          ) : null}
        </div>
      ) : null}
      {useInfinite ? (
        <div ref={setSentinelNode} className="h-4 w-full" aria-hidden />
      ) : null}
      {useInfinite && hasMore && onExpandAll ? (
        <div className="flex justify-center">
          <button type="button" className={btnClass} onClick={onExpandAll}>
            {t("scrollExpandAll")}
          </button>
        </div>
      ) : null}
    </div>
  );
}
