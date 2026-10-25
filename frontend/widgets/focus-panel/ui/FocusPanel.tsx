"use client";

import { useTranslations } from "next-intl";
import { type ResearchIntent } from "@/entities/research-intent";
import { ApiNotReadyState, useResearchIntents } from "@/features/research-intents";
import { useClientPageWindow } from "@/shared/hooks/useClientPageWindow";
import { ScrollLoadFooter } from "@/shared/ui/ScrollLoadFooter";
import { CreateFocusForm } from "./CreateFocusForm";
import { FocusIntentCard } from "./FocusIntentCard";
import { IntentCountriesSuggest } from "./IntentCountriesSuggest";

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
    <FocusPanelReady
      items={state.items}
      actionError={actionError}
      busyIds={busyIds}
      create={create}
      patch={patch}
      sync={sync}
    />
  );
}

function FocusPanelReady({
  items,
  actionError,
  busyIds,
  create,
  patch,
  sync,
}: {
  items: ResearchIntent[];
  actionError: string | null;
  busyIds: Set<number>;
  create: ReturnType<typeof useResearchIntents>["create"];
  patch: ReturnType<typeof useResearchIntents>["patch"];
  sync: ReturnType<typeof useResearchIntents>["sync"];
}) {
  const t = useTranslations("research");
  const {
    visible,
    hasMore,
    isExpanded,
    loadMore,
    expandAll,
    collapse,
    shown,
    total,
  } = useClientPageWindow(items, 8, items.length);

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

      <IntentCountriesSuggest intents={items} />

      {items.length === 0 ? (
        <section className="card p-6 text-sm text-[var(--muted)]">{t("emptyFocus")}</section>
      ) : (
        <div className="space-y-3">
          {visible.map((intent) => (
            <FocusIntentCard
              key={intent.id}
              intent={intent}
              busy={busyIds.has(intent.id)}
              onToggle={(enabled) => void patch(intent.id, { enabled })}
              onSync={() => void sync(intent.id)}
            />
          ))}
          <ScrollLoadFooter
            hasMore={hasMore}
            isExpanded={isExpanded}
            onLoadMore={loadMore}
            onExpandAll={expandAll}
            onCollapse={collapse}
            shown={shown}
            total={total}
          />
        </div>
      )}
    </div>
  );
}
