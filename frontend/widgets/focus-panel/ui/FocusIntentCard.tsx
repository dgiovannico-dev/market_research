"use client";

import { useTranslations } from "next-intl";
import type { ResearchIntent } from "@/entities/research-intent";
import { IntentEnableToggle } from "@/features/research-intents";
import { IntentSyncButton } from "@/features/research-intents";

type Props = {
  intent: ResearchIntent;
  busy?: boolean;
  onToggle: (enabled: boolean) => void;
  onSync: () => void;
};

export function FocusIntentCard({ intent, busy, onToggle, onSync }: Props) {
  const t = useTranslations("research");
  const label = intent.label || intent.name;

  return (
    <article className="card space-y-2 p-4">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0 space-y-1">
          <h3 className="font-display text-base font-semibold tracking-tight text-[var(--ink)]">
            {label}
          </h3>
          <p className="text-sm text-[var(--muted)]" style={{ fontFamily: "var(--mono)" }}>
            {intent.query_text}
          </p>
          <p className="text-xs text-[var(--muted)]">
            {t("origin")}: {intent.origin} · {intent.schedule_hint}
          </p>
          {intent.countries?.length ? (
            <p className="text-xs text-[var(--muted)]">
              {t("intentCountries")}:{" "}
              <span style={{ fontFamily: "var(--mono)" }}>
                {intent.countries.join(", ")}
              </span>
            </p>
          ) : null}
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <IntentEnableToggle enabled={intent.enabled} busy={busy} onChange={onToggle} />
          <IntentSyncButton busy={busy} onSync={onSync} />
        </div>
      </div>
    </article>
  );
}
