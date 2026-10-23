"use client";

import { useId } from "react";
import { useTranslations } from "next-intl";

type Props = {
  value: string;
  onChange: (next: string) => void;
  /** Optional override; defaults to common.tableSearchPlaceholder */
  placeholder?: string;
  className?: string;
};

export function TableSearch({
  value,
  onChange,
  placeholder,
  className = "",
}: Props) {
  const t = useTranslations("common");
  const inputId = useId();
  const resolvedPlaceholder = placeholder ?? t("tableSearchPlaceholder");

  return (
    <div
      className={`flex flex-wrap items-center gap-2 ${className}`.trim()}
    >
      <label className="sr-only" htmlFor={inputId}>
        {t("tableSearchAria")}
      </label>
      <input
        id={inputId}
        type="search"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={resolvedPlaceholder}
        aria-label={t("tableSearchAria")}
        className="min-w-[12rem] flex-1 rounded-md border border-[var(--line)] bg-transparent px-3 py-1.5 text-sm text-[var(--ink)] placeholder:text-[var(--muted)] focus:border-[var(--signal)] focus:outline-none"
      />
      {value ? (
        <button
          type="button"
          className="rounded-md border border-[var(--line)] px-2.5 py-1.5 text-xs text-[var(--muted)] hover:border-[var(--signal)] hover:text-[var(--ink)]"
          onClick={() => onChange("")}
        >
          {t("tableSearchClear")}
        </button>
      ) : null}
    </div>
  );
}
