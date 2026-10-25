"use client";

import { useState } from "react";

type Props = {
  label: string;
  hint?: string;
  values: string[];
  onChange: (next: string[]) => void;
  placeholder?: string;
  addLabel: string;
};

export function ProfileTagField({
  label,
  hint,
  values,
  onChange,
  placeholder,
  addLabel,
}: Props) {
  const [draft, setDraft] = useState("");

  function addFromDraft() {
    const parts = draft
      .split(/[,;\n]/)
      .map((s) => s.trim())
      .filter(Boolean);
    if (parts.length === 0) return;
    const seen = new Set(values.map((v) => v.toLowerCase()));
    const next = [...values];
    for (const part of parts) {
      if (seen.has(part.toLowerCase())) continue;
      seen.add(part.toLowerCase());
      next.push(part);
    }
    onChange(next);
    setDraft("");
  }

  return (
    <div className="space-y-2 text-sm">
      <div>
        <span className="text-[var(--muted)]">{label}</span>
        {hint ? <p className="mt-0.5 text-xs text-[var(--muted)]">{hint}</p> : null}
      </div>
      {values.length > 0 ? (
        <ul className="flex flex-wrap gap-1.5">
          {values.map((value) => (
            <li
              key={value}
              className="inline-flex items-center gap-1 rounded-md border border-[var(--line)] bg-[var(--card)] px-2 py-1 text-xs text-[var(--ink)]"
            >
              <span>{value}</span>
              <button
                type="button"
                className="text-[var(--muted)] hover:text-[var(--warn)]"
                aria-label={`Remove ${value}`}
                onClick={() => onChange(values.filter((v) => v !== value))}
              >
                ×
              </button>
            </li>
          ))}
        </ul>
      ) : null}
      <div className="flex flex-wrap gap-2">
        <input
          className="min-w-[12rem] flex-1 rounded-md border border-[var(--line)] bg-transparent px-2 py-1.5 text-sm text-[var(--ink)] placeholder:text-[var(--muted)] focus:border-[var(--signal)] focus:outline-none"
          value={draft}
          placeholder={placeholder}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              addFromDraft();
            }
          }}
        />
        <button
          type="button"
          className="rounded-md border border-[var(--line)] px-3 py-1.5 text-sm text-[var(--ink)] hover:border-[var(--signal)] hover:text-[var(--signal)]"
          onClick={addFromDraft}
        >
          {addLabel}
        </button>
      </div>
    </div>
  );
}
