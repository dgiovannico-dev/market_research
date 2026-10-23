"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import type { ResearchIntent } from "@/entities/research-intent";
import { IntentEditFields } from "@/features/research-intents";
import { IntentEnableToggle } from "@/features/research-intents";
import { IntentSyncButton } from "@/features/research-intents";

type Props = {
  intent: ResearchIntent;
  busy?: boolean;
  onToggle: (enabled: boolean) => void;
  onSave: (fields: { name: string; query_text: string }) => void;
  onSync: () => void;
};

export function DiscoveryIntentCard({ intent, busy, onToggle, onSave, onSync }: Props) {
  const t = useTranslations("research");
  const [editing, setEditing] = useState(false);
  const [name, setName] = useState(intent.name);
  const [queryText, setQueryText] = useState(intent.query_text);

  const label = intent.label || intent.name;

  const startEdit = () => {
    setName(intent.name);
    setQueryText(intent.query_text);
    setEditing(true);
  };

  return (
    <article className="card space-y-3 p-4">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0 space-y-1">
          <h3 className="font-display text-base font-semibold tracking-tight text-[var(--ink)]">
            {label}
          </h3>
          <p
            className="truncate text-xs text-[var(--muted)]"
            style={{ fontFamily: "var(--mono)" }}
          >
            {intent.query_text}
          </p>
          <p className="text-xs text-[var(--muted)]">
            {t("origin")}: {intent.origin} · {intent.schedule_hint}
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <IntentEnableToggle enabled={intent.enabled} busy={busy} onChange={onToggle} />
          <IntentSyncButton busy={busy} onSync={onSync} />
          {!editing ? (
            <button
              type="button"
              disabled={busy}
              className="rounded-full border border-[var(--line)] px-3 py-1.5 text-xs hover:border-[var(--signal)] disabled:opacity-50"
              onClick={startEdit}
            >
              {t("edit")}
            </button>
          ) : null}
        </div>
      </div>
      {editing ? (
        <IntentEditFields
          name={name}
          queryText={queryText}
          busy={busy}
          onNameChange={setName}
          onQueryChange={setQueryText}
          onSave={() => {
            onSave({ name: name.trim(), query_text: queryText.trim() });
            setEditing(false);
          }}
          onCancel={() => setEditing(false)}
        />
      ) : null}
    </article>
  );
}
