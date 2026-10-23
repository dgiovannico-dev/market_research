"use client";

import { useTranslations } from "next-intl";

export type JobsPaginationProps = {
  page: number;
  pageSize: number;
  total: number;
  onPageChange: (page: number) => void;
};

export function JobsPagination({
  page,
  pageSize,
  total,
  onPageChange,
}: JobsPaginationProps) {
  const t = useTranslations("jobs");
  const totalPages = Math.max(1, Math.ceil(total / pageSize) || 1);
  const from = total === 0 ? 0 : (page - 1) * pageSize + 1;
  const to = Math.min(page * pageSize, total);
  const hasPrev = page > 1;
  const hasNext = total > 0 && page < totalPages;

  const pageBtn =
    "rounded-md border border-[var(--line)] bg-[var(--card)] px-3 py-1.5 text-sm text-[var(--ink)] transition-colors hover:border-[var(--signal)] hover:text-[var(--signal)] disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:border-[var(--line)] disabled:hover:text-[var(--ink)]";

  return (
    <nav
      aria-label={t("paginationLabel")}
      className="flex flex-wrap items-center justify-between gap-3 border-t border-[var(--line)] px-3 py-3 text-sm"
      style={{
        background: "color-mix(in srgb, var(--paper) 72%, var(--card))",
      }}
    >
      <p className="text-xs text-[var(--muted)]" style={{ fontFamily: "var(--mono)" }}>
        {t("showingRange", { from, to, total })}
      </p>
      <div className="flex items-center gap-2">
        <button
          type="button"
          className={pageBtn}
          disabled={!hasPrev}
          aria-label={t("prevPage")}
          onClick={() => onPageChange(page - 1)}
        >
          {t("previous")}
        </button>
        <span
          className="min-w-[4.5rem] text-center text-xs text-[var(--muted)]"
          style={{ fontFamily: "var(--mono)" }}
          aria-current="page"
        >
          {t("pageOf", { page, totalPages })}
        </span>
        <button
          type="button"
          className={pageBtn}
          disabled={!hasNext}
          aria-label={t("nextPage")}
          onClick={() => onPageChange(page + 1)}
        >
          {t("next")}
        </button>
      </div>
    </nav>
  );
}
