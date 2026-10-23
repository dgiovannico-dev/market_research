"use client";

import { useTranslations } from "next-intl";
import { ApiNotReadyState } from "@/features/research-intents";
import { CreateFocusForm } from "./CreateFocusForm";
import { FocusIntentCard } from "./FocusIntentCard";
import { IntentCountriesSuggest } from "./IntentCountriesSuggest";
import { useResearchIntents } from "@/features/research-intents";

export function FocusPanel() {
  const t = useTranslations("research");
  const tCommon = useTranslations("common");
  const { state, actionError, busyIds, reload, patch, sync, create } = useResearchIntents("focus");

  if (state.phase === "loading") {
    return <div className="card p-6 text-sm text-[var(--muted)]">{tCommon("loading")}</div>;
  }

  if (state.phase === "not_ready") {
    return <ApiNotReadyState />;
  }

  if (state.phase === "error") {
    return (
      <section className="card space-y-3 p-6">
        <h2 className="font-display text-lg font-semibold tracking-tight text-[var(--ink)]">
          {tCommon("error")}
        </h2>
        <p className="text-sm text-[var(--muted)]">{state.message}</p>
        <button
          type="button"
          className="rounded-full border border-[var(--line)] px-3 py-1.5 text-sm hover:border-[var(--signal)]"
          onClick={() => void reload()}
        >
          {tCommon("retry")}
        </button>
      </section>
    );
  }

  return (
    <div className="space-y-4">
      <header className="space-y-1">
        <p className="font-display text-xs uppercase tracking-[0.2em] signal-text">
          {t("focusEyebrow")}
        </p>
        <h2 className="font-display text-2xl font-semibold tracking-tight text-[var(--ink)]">
          {t("focusTitle")}
        </h2>
        <p className="max-w-2xl text-sm text-[var(--muted)]">{t("focusSubtitle")}</p>
      </header>

      <CreateFocusForm
        onCreate={async (fields) => {
          const row = await create({ ...fields, enabled: true, origin: "user" });
          return row != null;
        }}
      />

      {actionError ? <p className="text-sm text-[var(--warn)]">{actionError}</p> : null}

      <IntentCountriesSuggest intents={state.items} />

      {state.items.length === 0 ? (
        <section className="card p-6 text-sm text-[var(--muted)]">{t("emptyFocus")}</section>
      ) : (
        <div className="space-y-3">
          {state.items.map((intent) => (
            <FocusIntentCard
              key={intent.id}
              intent={intent}
              busy={busyIds.has(intent.id)}
              onToggle={(enabled) => void patch(intent.id, { enabled })}
              onSync={() => void sync(intent.id)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
