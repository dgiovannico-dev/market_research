"use client";

import { useTranslations } from "next-intl";

/**
 * Site-wide credit footer — sits below main content in AppChrome.
 */
export function SiteFooter() {
  const t = useTranslations("nav");
  const year = new Date().getFullYear();

  return (
    <footer
      className="mt-auto border-t border-[var(--line)] bg-[color-mix(in_srgb,var(--card)_70%,transparent)]"
      role="contentinfo"
    >
      <div className="mx-auto flex max-w-7xl flex-col items-center gap-2 px-4 py-8 text-center sm:flex-row sm:justify-between sm:text-left">
        <div className="space-y-1">
          <p className="font-display text-[0.65rem] uppercase tracking-[0.28em] signal-text">
            {t("brand")}
          </p>
          <p className="text-xs text-[var(--muted)]">{t("tagline")}</p>
        </div>

        <p className="font-display text-sm tracking-tight text-[var(--ink)]">
          <span className="text-[var(--muted)]">{t("createdByPrefix")}</span>{" "}
          <span className="font-semibold signal-text">{t("createdByName")}</span>
          <span className="mx-2 select-none text-[var(--muted)]" aria-hidden>
            ·
          </span>
          <time
            className="text-xs text-[var(--muted)] tabular-nums"
            dateTime={String(year)}
          >
            {year}
          </time>
        </p>
      </div>
    </footer>
  );
}
