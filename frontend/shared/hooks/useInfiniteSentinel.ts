"use client";

import { useEffect, useRef, type RefObject } from "react";

type Options = {
  rootMargin?: string;
  /** Change when list grows so a still-visible sentinel can fire again. */
  observeKey?: string | number;
  /**
   * Scroll container for nested infinite lists (max-height panels).
   * Defaults to the browser viewport when omitted.
   */
  rootRef?: RefObject<Element | null>;
};

/**
 * Fires `onHit` when the sentinel enters the root (viewport or scroll parent).
 * Disable while a fetch is in flight or when there is nothing more to load.
 */
export function useInfiniteSentinel(
  enabled: boolean,
  onHit: () => void,
  options: Options = {},
) {
  const { rootMargin = "280px", observeKey = 0, rootRef } = options;
  const ref = useRef<HTMLDivElement | null>(null);
  // Keep latest handler without re-subscribing (useEffectEvent not in all React runtimes).
  const onHitRef = useRef(onHit);
  onHitRef.current = onHit;

  useEffect(() => {
    const node = ref.current;
    if (!enabled || !node) return;
    const root = rootRef?.current ?? null;
    const io = new IntersectionObserver(
      (entries) => {
        if (entries.some((e) => e.isIntersecting)) onHitRef.current();
      },
      { root, rootMargin, threshold: 0 },
    );
    io.observe(node);
    return () => io.disconnect();
  }, [enabled, rootMargin, observeKey, rootRef]);

  return ref;
}
