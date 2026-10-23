"use client";

import { useTranslations } from "next-intl";

const SOFT_THRESHOLD = 3;

export function DiscoveryCoverageWarn({ enabledCount }: { enabledCount: number }) {
  const t = useTranslations("research");
  if (enabledCount >= SOFT_THRESHOLD) return null;

  return (
    <p
      className="rounded-lg border border-[var(--warn)]/40 bg-[color-mix(in_srgb,var(--warn)_12%,transparent)] px-3 py-2 text-sm text-[var(--warn)]"
      role="status"
    >
      {t("discoveryWarn", { count: enabledCount, min: SOFT_THRESHOLD })}
    </p>
  );
}
