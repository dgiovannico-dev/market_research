"use client";

import { useEffect, useRef } from "react";

type Options = {
  rootMargin?: string;
  /** Change when list grows so a still-visible sentinel can fire again. */
  observeKey?: string | number;
};

/**
 * Fires `onHit` when the sentinel enters the viewport (with rootMargin slack).
 * Disable while a fetch is in flight or when there is nothing more to load.
 */
export function useInfiniteSentinel(
  enabled: boolean,
  onHit: () => void,
  options: Options = {},
) {
  const { rootMargin = "280px", observeKey = 0 } = options;
  const ref = useRef<HTMLDivElement | null>(null);
  // Keep latest handler without re-subscribing (useEffectEvent not in all React runtimes).
  const onHitRef = useRef(onHit);
  onHitRef.current = onHit;

  useEffect(() => {
    const node = ref.current;
    if (!enabled || !node) return;
    const io = new IntersectionObserver(
      (entries) => {
        if (entries.some((e) => e.isIntersecting)) onHitRef.current();
      },
      { root: null, rootMargin, threshold: 0 },
    );
    io.observe(node);
    return () => io.disconnect();
  }, [enabled, rootMargin, observeKey]);

  return ref;
}
