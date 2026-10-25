"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { ApiNotReadyState } from "@/features/research-intents";
import { DiscoveryCoverageWarn } from "@/features/research-intents";
import { DiscoveryIntentCard } from "./DiscoveryIntentCard";
import { DiscoveryProbeSearch } from "./DiscoveryProbeSearch";
import { useResearchIntents } from "@/features/research-intents";
import { ScrollLoadFooter } from "@/shared/ui/ScrollLoadFooter";
import { useClientPageWindow } from "@/shared/hooks/useClientPageWindow";

function matchesProbeFilter(
  intent: { name: string; label?: string | null; query_text: string },
  filter: string,
): boolean {
  if (!filter) return true;
  const hay = `${intent.name} ${intent.label ?? ""} ${intent.query_text}`.toLowerCase();
  return hay.includes(filter.toLowerCase());
}

export function MarketScanPanel() {
  const t = useTranslations("research");
  const tCommon = useTranslations("common");
  const { state, actionError, busyIds, reload, patch, sync } = useResearchIntents("discovery");
  const [probeFilter, setProbeFilter] = useState("");

  const readyItems = state.phase === "ready" ? state.items : [];
  const filtered = readyItems.filter((it) => matchesProbeFilter(it, probeFilter));
  const {
    visible,
    hasMore,
    isExpanded,
    loadMore,
    expandAll,
    collapse,
    shown,
    total: listTotal,
  } = useClientPageWindow(filtered, 20, `${probeFilter}|${filtered.length}`);

  if (state.phase === "loading") {
    return (
      <div className="card p-6 text-sm text-[var(--muted)]" aria-busy="true" aria-live="polite">
        {tCommon("loading")}
      </div>
    );
  }

  if (state.phase === "not_ready") {
    return <ApiNotReadyState />;
  }

  if (state.phase === "error") {
    return (
      <section className="card space-y-3 p-6" role="alert">
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

  const enabledCount = readyItems.filter((it) => it.enabled).length;

  return (
    <div className="space-y-4">
      <header className="space-y-1">
        <p className="font-display text-xs uppercase tracking-[0.2em] signal-text">
          {t("marketScanEyebrow")}
        </p>
        <h2 className="font-display text-2xl font-semibold tracking-tight text-[var(--ink)]">
          {t("marketScanTitle")}
        </h2>
        <p className="max-w-2xl text-sm text-[var(--muted)]">{t("marketScanSubtitle")}</p>
      </header>

      <DiscoveryProbeSearch value={probeFilter} onApply={setProbeFilter} />

      <DiscoveryCoverageWarn enabledCount={enabledCount} />

      {actionError ? (
        <p className="text-sm text-[var(--warn)]" role="alert">
          {actionError}
        </p>
      ) : null}

      {readyItems.length === 0 ? (
        <section className="card p-6 text-sm text-[var(--muted)]" role="status">
          {t("emptyDiscovery")}
        </section>
      ) : filtered.length === 0 ? (
        <section className="card space-y-2 p-6 text-sm text-[var(--muted)]" role="status">
          <p className="font-display font-medium text-[var(--ink)]">{t("probeFilterEmpty")}</p>
          <p>{t("probeFilterEmptyHint")}</p>
        </section>
      ) : (
        <div className="space-y-3">
          {visible.map((intent) => (
            <DiscoveryIntentCard
              key={intent.id}
              intent={intent}
              busy={busyIds.has(intent.id)}
              onToggle={(enabled) => void patch(intent.id, { enabled })}
              onSave={(fields) => void patch(intent.id, fields)}
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
            total={listTotal}
          />
        </div>
      )}
    </div>
  );
}
