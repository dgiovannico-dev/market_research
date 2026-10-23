"use client";

import { FormEvent, useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";

type Props = {
  value: string;
  onApply: (next: string) => void;
};

/** Local filter for discovery probes on Market scan. */
export function DiscoveryProbeSearch({ value, onApply }: Props) {
  const t = useTranslations("research");
  const [draft, setDraft] = useState(value);

  useEffect(() => {
    setDraft(value);
  }, [value]);

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    onApply(draft.trim());
  }

  return (
    <div className="card space-y-3 p-4">
      <form
        onSubmit={onSubmit}
        className="flex flex-col gap-2 sm:flex-row sm:items-end"
        role="search"
        aria-label={t("probeSearchAria")}
      >
        <label className="flex min-w-0 flex-1 flex-col gap-1 text-xs font-medium text-[var(--muted)]">
          {t("probeSearchLabel")}
          <input
            type="search"
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            placeholder={t("probeSearchPlaceholder")}
            className="w-full rounded border border-[var(--line)] bg-transparent px-3 py-2.5 text-sm text-[var(--ink)]"
            autoComplete="off"
            enterKeyHint="search"
          />
        </label>
        <button
          type="submit"
          className="shrink-0 rounded bg-[var(--signal)] px-4 py-2.5 text-sm font-medium text-white hover:opacity-90"
        >
          {t("probeSearchSubmit")}
        </button>
      </form>
      <p className="text-xs text-[var(--muted)]">
        {t("probeSearchJobsHint")}{" "}
        <Link href="/explorer" className="underline signal-text">
          {t("openExplorer")}
        </Link>
      </p>
    </div>
  );
}
