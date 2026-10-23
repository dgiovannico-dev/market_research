"use client";

import { useMemo, useState } from "react";
import { useTranslations } from "next-intl";
import { ConnectorKindBadge } from "@/entities/source";
import { RunSourceButton } from "./RunSourceButton";
import { SourceStatusBadge } from "@/entities/source";
import { formatDateMinute } from "@/shared/lib/formatDateTime";

export type RunnableSource = {
  id: number;
  name: string;
  connector_type: string;
  category?: string;
  coverage_notes?: string;
  verification_status?: string;
  is_credentialed_scaffold?: boolean;
  has_insert_evidence?: boolean;
  insert_runs_count?: number;
  last_insert_at?: string | null;
  last_success_at?: string | null;
  last_error?: string | null;
};

type KindFilter = "all" | "free" | "credentialed";

function hasInsertEvidence(s: RunnableSource): boolean {
  if (typeof s.has_insert_evidence === "boolean") return s.has_insert_evidence;
  return Number(s.insert_runs_count ?? 0) > 0;
}

export function RunnableConnectorsPanel({ sources }: { sources: RunnableSource[] }) {
  const t = useTranslations("sources");
  const [kind, setKind] = useState<KindFilter>("all");

  const filtered = useMemo(() => {
    if (kind === "free") {
      return sources.filter((s) => !s.is_credentialed_scaffold);
    }
    if (kind === "credentialed") {
      return sources.filter((s) => s.is_credentialed_scaffold);
    }
    return sources;
  }, [kind, sources]);

  const freeCount = sources.filter((s) => !s.is_credentialed_scaffold).length;
  const credCount = sources.length - freeCount;

  function statusLabel(status: string): string {
    if (!status) return "—";
    const key = `status.${status}` as Parameters<typeof t>[0];
    return t.has(key) ? t(key) : status;
  }

  const filterBtn = (value: KindFilter, label: string, count: number) => (
    <button
      key={value}
      type="button"
      aria-pressed={kind === value}
      onClick={() => setKind(value)}
      className={`rounded border px-2 py-1 text-xs ${
        kind === value
          ? "border-teal-700 bg-teal-700/10 font-medium"
          : "border-[var(--line)] opacity-80 hover:opacity-100"
      }`}
    >
      {label} ({count})
    </button>
  );

  return (
    <section className="space-y-3">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <h3 className="font-semibold">{t("runnableHeading")}</h3>
        <div
          className="flex flex-wrap gap-2"
          role="group"
          aria-label={t("filterKindAria")}
        >
          {filterBtn("all", t("kindFilterAll"), sources.length)}
          {filterBtn("free", t("kindFreePublic"), freeCount)}
          {filterBtn("credentialed", t("kindCredentialed"), credCount)}
        </div>
      </div>

      {filtered.length === 0 ? (
        <div className="card p-6 text-sm opacity-80">
          <p className="font-medium">{t("emptyRunnableFilterTitle")}</p>
          <p className="mt-1 text-xs opacity-70">{t("emptyRunnableFilterBody")}</p>
        </div>
      ) : (
        <div className="grid gap-3">
          {filtered.map((s) => {
            const inserts = hasInsertEvidence(s);
            const insertRuns = Number(s.insert_runs_count ?? 0);
            const lastInsert = s.last_insert_at
              ? formatDateMinute(s.last_insert_at)
              : null;
            const lastSuccess = s.last_success_at
              ? formatDateMinute(s.last_success_at)
              : null;
            const lastRunAt = lastSuccess ?? lastInsert;
            const vStatus = String(s.verification_status ?? "");
            const isActive = vStatus === "ACTIVE";
            const needsCreds = vStatus === "NEEDS_CREDENTIALS";
            const lastError = s.last_error ? String(s.last_error) : null;
            const credentialed = Boolean(s.is_credentialed_scaffold);

            return (
              <article key={s.id} className="card p-4">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <h3 className="font-semibold">{s.name}</h3>
                      <ConnectorKindBadge credentialed={credentialed} />
                      <SourceStatusBadge
                        status={vStatus || "—"}
                        label={statusLabel(vStatus)}
                        title={
                          isActive
                            ? t("statusActiveHint")
                            : needsCreds
                              ? t("statusNeedsCredsHint")
                              : undefined
                        }
                      />
                      {inserts ? (
                        <span className="badge rise-text" title={lastInsert ?? undefined}>
                          {t("badgeHasInserts", { count: insertRuns })}
                        </span>
                      ) : (
                        <span className={`badge ${isActive ? "cool-text" : ""}`}>
                          {isActive ? t("badgeNeedsRun") : t("badgeNoInserts")}
                        </span>
                      )}
                    </div>
                    <p className="text-xs opacity-60">
                      {s.connector_type} · cat={String(s.category ?? "—")}
                    </p>
                    <p className="mt-1 text-xs opacity-70">
                      {lastRunAt ? t("lastRun", { at: lastRunAt }) : t("lastRunNever")}
                    </p>
                    {lastInsert && lastInsert !== lastRunAt ? (
                      <p className="mt-0.5 text-xs opacity-60">
                        {t("lastInsert", { at: lastInsert })}
                      </p>
                    ) : null}
                    {lastError ? (
                      <p className="mt-1 text-xs text-red-700 opacity-90" title={lastError}>
                        {t("lastError", {
                          msg:
                            lastError.length > 120
                              ? `${lastError.slice(0, 120)}…`
                              : lastError,
                        })}
                      </p>
                    ) : null}
                    <p className="mt-2 text-sm opacity-80">{String(s.coverage_notes ?? "")}</p>
                  </div>
                  <RunSourceButton sourceId={s.id} />
                </div>
              </article>
            );
          })}
        </div>
      )}
    </section>
  );
}
