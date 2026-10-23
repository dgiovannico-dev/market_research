"use client";

import type { SortOrder } from "@/shared/lib/tableSort";

type Props = {
  label: string;
  sortKey: string;
  activeSort: string;
  order: SortOrder;
  onSort: (key: string) => void;
  ariaLabel: string;
  /** Plain-language tip for the column (native tooltip + title). */
  hint?: string;
  align?: "left" | "right";
  className?: string;
};

export function SortableTh({
  label,
  sortKey,
  activeSort,
  order,
  onSort,
  ariaLabel,
  hint,
  align = "left",
  className = "px-3 py-2.5",
}: Props) {
  const active = activeSort === sortKey;
  const indicator = active ? (order === "asc" ? " ↑" : " ↓") : "";
  const alignClass = align === "right" ? " text-right" : "";
  return (
    <th className={`${className}${alignClass}`.trim()} aria-sort={active ? (order === "asc" ? "ascending" : "descending") : "none"}>
      <button
        type="button"
        className={`inline-flex items-center gap-0.5 uppercase tracking-[0.12em] hover:text-[var(--ink)]${
          align === "right" ? " w-full justify-end" : ""
        }`}
        onClick={() => onSort(sortKey)}
        aria-label={hint ? `${ariaLabel}. ${hint}` : ariaLabel}
        title={hint}
      >
        {label}
        <span aria-hidden>{indicator}</span>
      </button>
    </th>
  );
}
