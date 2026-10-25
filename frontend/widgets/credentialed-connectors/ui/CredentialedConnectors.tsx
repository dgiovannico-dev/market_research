"use client";

import { useCallback, useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { canSeeAdminConfig, useAuth } from "@/features/auth";
import { ConnectorKindBadge } from "@/entities/source";
import { useClientPageWindow } from "@/shared/hooks/useClientPageWindow";
import { ScrollLoadFooter } from "@/shared/ui/ScrollLoadFooter";
import { CredentialEditor } from "./CredentialEditor";
import { SourceStatusBadge } from "@/entities/source";
import { formatDateMinute } from "@/shared/lib/formatDateTime";

type ConnectorRow = {
  connector_key: string;
  credentials_present: boolean;
  credentials_source?: string;
};

type FreeActiveRow = {
  connector_key: string;
  verification_status: string;
  last_run_at: string | null;
  last_success_at: string | null;
  last_run_status: string | null;
  enabled: boolean;
  seeded_in_db?: boolean;
};

export function CredentialedConnectors() {
  const t = useTranslations("sources");
  const { isAdmin, enabled: oidcOn } = useAuth();
  const showCredAdmin = canSeeAdminConfig({ enabled: oidcOn, isAdmin });
  const [items, setItems] = useState<ConnectorRow[] | null>(null);
  const [activeFree, setActiveFree] = useState<FreeActiveRow[] | null>(null);
  const [error, setError] = useState("");
  const [showCred, setShowCred] = useState(true);
  const [editing, setEditing] = useState<string | null>(null);
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const reload = useCallback(() => {
    let cancelled = false;
    fetch(`${apiUrl}/api/v1/ops/connectors`, { cache: "no-store" })
      .then(async (res) => {
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || res.statusText);
        if (!cancelled) {
          setItems(data.items || []);
          setActiveFree(data.active_free || []);
          setError("");
        }
      })
      .catch((e) => {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : t("credLoadFailed"));
          setItems([]);
          setActiveFree([]);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [apiUrl]);

  useEffect(() => {
    return reload();
  }, [reload]);

  function sourceLabel(src?: string) {
    if (src === "db") return t("credSourceDb");
    if (src === "env") return t("credSourceEnv");
    return t("credSourceNone");
  }

  const freeRows = activeFree ?? [];
  const freePage = useClientPageWindow(
    freeRows,
    16,
    freeRows.length,
  );
  const credRows = items ?? [];
  const credPage = useClientPageWindow(
    credRows,
    16,
    `${credRows.length}|${showCred}`,
  );

  return (
    <>
      <section className="card mt-4 p-4 text-sm">
        <h3 className="font-semibold">{t("freeActiveHeading")}</h3>
        <p className="mt-1 text-xs opacity-70">{t("freeActiveSubtitle")}</p>
        {error ? (
          <p className="mt-2 text-xs text-red-700">
            {error}
          </p>
        ) : null}
        {activeFree === null ? (
          <p className="mt-3 text-xs opacity-60">{t("credLoading")}</p>
        ) : activeFree.length === 0 ? (
          <p className="mt-3 text-xs opacity-70">{t("freeActiveEmpty")}</p>
        ) : (
          <>
            <ul className="mt-3 grid gap-1 sm:grid-cols-2">
              {freePage.visible.map((row) => {
                const when = formatDateMinute(
                  row.last_success_at ?? row.last_run_at,
                  "",
                );
                return (
                  <li
                    key={row.connector_key}
                    className="flex items-center justify-between gap-2 border-b border-[var(--line)] py-1.5"
                  >
                    <div className="min-w-0">
                      <div className="flex flex-wrap items-center gap-2">
                        <code className="text-xs">{row.connector_key}</code>
                        <ConnectorKindBadge credentialed={false} />
                      </div>
                      <p className="text-[11px] opacity-60">
                        {when
                          ? t("lastRun", { at: when })
                          : t("lastRunNever")}
                        {row.last_run_status ? ` · ${row.last_run_status}` : ""}
                        {row.seeded_in_db === false
                          ? ` · ${t("catalogOnlyHint")}`
                          : ""}
                      </p>
                    </div>
                    <SourceStatusBadge
                      status="ACTIVE"
                      label={t("status.ACTIVE")}
                      title={t("statusActiveHint")}
                    />
                  </li>
                );
              })}
            </ul>
            <ScrollLoadFooter
              hasMore={freePage.hasMore}
              isExpanded={freePage.isExpanded}
              onLoadMore={freePage.loadMore}
              onExpandAll={freePage.expandAll}
              onCollapse={freePage.collapse}
              shown={freePage.shown}
              total={freePage.total}
            />
          </>
        )}
      </section>

      {showCredAdmin ? (
        <section className="card mt-4 p-4 text-sm">
          <div className="flex flex-wrap items-start justify-between gap-2">
            <div>
              <h3 className="font-semibold">{t("credHeading")}</h3>
              <p className="mt-1 text-xs opacity-70">{t("credSubtitle")}</p>
            </div>
            <button
              type="button"
              className="rounded border border-[var(--line)] px-2 py-1 text-xs opacity-80 hover:opacity-100"
              aria-expanded={showCred}
              onClick={() => setShowCred((v) => !v)}
            >
              {showCred ? t("credToggleHide") : t("credToggleShow")}
            </button>
          </div>
          {error ? (
            <p className="mt-2 text-xs text-red-700">
              {error}
            </p>
          ) : null}
          {showCred ? (
            items === null ? (
              <p className="mt-3 text-xs opacity-60">{t("credLoading")}</p>
            ) : items.length === 0 ? (
              <p className="mt-3 text-xs opacity-70">{t("credEmpty")}</p>
            ) : (
              <>
                <ul className="mt-3 space-y-1">
                  {credPage.visible.map((row) => (
                    <li
                      key={row.connector_key}
                      className="border-b border-[var(--line)] py-1.5"
                    >
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <div className="flex min-w-0 flex-wrap items-center gap-2">
                          <code className="text-xs">{row.connector_key}</code>
                          <ConnectorKindBadge credentialed />
                          <span className="text-[11px] opacity-60">
                            {sourceLabel(row.credentials_source)}
                          </span>
                        </div>
                        <div className="flex items-center gap-2">
                          {row.credentials_present ? (
                            <span
                              className="badge signal-text"
                              title={t("credKeysSetHint")}
                            >
                              {t("credKeysSet")}
                            </span>
                          ) : (
                            <SourceStatusBadge
                              status="NEEDS_CREDENTIALS"
                              label={t("status.NEEDS_CREDENTIALS")}
                              title={t("credNoKeysHint")}
                            />
                          )}
                          <button
                            type="button"
                            className="rounded border border-[var(--line)] px-2 py-0.5 text-[11px]"
                            aria-expanded={editing === row.connector_key}
                            onClick={() =>
                              setEditing((cur) =>
                                cur === row.connector_key
                                  ? null
                                  : row.connector_key,
                              )
                            }
                          >
                            {editing === row.connector_key
                              ? t("credEditorClose")
                              : t("credSetKeys")}
                          </button>
                        </div>
                      </div>
                      {editing === row.connector_key ? (
                        <CredentialEditor
                          connectorKey={row.connector_key}
                          apiUrl={apiUrl}
                          onClose={() => setEditing(null)}
                          onSaved={() => reload()}
                        />
                      ) : null}
                    </li>
                  ))}
                </ul>
                <ScrollLoadFooter
                  hasMore={credPage.hasMore}
                  isExpanded={credPage.isExpanded}
                  onLoadMore={credPage.loadMore}
                  onExpandAll={credPage.expandAll}
                  onCollapse={credPage.collapse}
                  shown={credPage.shown}
                  total={credPage.total}
                />
              </>
            )
          ) : null}
        </section>
      ) : null}
    </>
  );
}
