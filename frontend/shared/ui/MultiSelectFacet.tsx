"use client";

import { useEffect, useId, useRef, useState } from "react";

type Option = { value: string; label: string };

type Props = {
  label: string;
  options: Option[];
  selected: string[];
  onChange: (next: string[]) => void;
  /** Shown when nothing selected */
  emptyLabel?: string;
  /** e.g. "{count} selected" — `{count}` replaced */
  selectedCountLabel?: string;
  clearLabel?: string;
  className?: string;
};

/**
 * Checkbox multi-select dropdown (click to toggle; no Ctrl/Cmd required).
 */
export function MultiSelectFacet({
  label,
  options,
  selected,
  onChange,
  emptyLabel = "—",
  selectedCountLabel = "{count} selected",
  clearLabel = "Clear",
  className = "",
}: Props) {
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);
  const listId = useId();
  const selectedSet = new Set(selected);

  useEffect(() => {
    if (!open) return;
    const onDoc = (e: MouseEvent) => {
      if (!rootRef.current?.contains(e.target as Node)) setOpen(false);
    };
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    document.addEventListener("mousedown", onDoc);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onDoc);
      document.removeEventListener("keydown", onKey);
    };
  }, [open]);

  const toggle = (value: string) => {
    if (selectedSet.has(value)) {
      onChange(selected.filter((v) => v !== value));
    } else {
      onChange([...selected, value]);
    }
  };

  const summary =
    selected.length === 0
      ? emptyLabel
      : selected.length <= 2
        ? selected
            .map((v) => options.find((o) => o.value === v)?.label ?? v)
            .join(", ")
        : selectedCountLabel.replace("{count}", String(selected.length));

  return (
    <div ref={rootRef} className={`relative flex flex-col gap-1 text-xs text-[var(--muted)] ${className}`}>
      <span id={`${listId}-label`}>{label}</span>
      <button
        type="button"
        className="min-w-[9rem] rounded-md border border-[var(--line)] bg-[var(--card)] px-2 py-1.5 text-left text-xs text-[var(--ink)] focus:border-[var(--signal)] focus:outline-none"
        aria-expanded={open}
        aria-haspopup="listbox"
        aria-labelledby={`${listId}-label`}
        onClick={() => setOpen((o) => !o)}
      >
        {summary}
      </button>
      {open ? (
        <div
          id={listId}
          role="listbox"
          aria-multiselectable
          aria-labelledby={`${listId}-label`}
          className="absolute left-0 top-full z-20 mt-1 max-h-56 min-w-[12rem] overflow-y-auto rounded-md border border-[var(--line)] bg-[var(--card)] p-2 shadow-sm"
        >
          {selected.length > 0 ? (
            <button
              type="button"
              className="mb-1 block w-full text-left text-[0.65rem] underline signal-text"
              onClick={() => onChange([])}
            >
              {clearLabel}
            </button>
          ) : null}
          {options.length === 0 ? (
            <p className="px-1 py-0.5 text-[var(--muted)]">—</p>
          ) : (
            options.map((opt) => (
              <label
                key={opt.value}
                className="flex cursor-pointer items-center gap-2 px-1 py-0.5 text-xs text-[var(--ink)]"
              >
                <input
                  type="checkbox"
                  checked={selectedSet.has(opt.value)}
                  onChange={() => toggle(opt.value)}
                />
                <span className="truncate">{opt.label}</span>
              </label>
            ))
          )}
        </div>
      ) : null}
    </div>
  );
}
