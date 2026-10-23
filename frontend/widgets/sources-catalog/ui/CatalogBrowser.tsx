"use client";

import { Suspense, startTransition, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { useTranslations } from "next-intl";
import { usePathname, useRouter } from "@/i18n/navigation";
import { api } from "@/lib/api";
import { ConnectorKindBadge } from "@/entities/source";
import { SourceStatusBadge } from "@/entities/source";
import {
  catalogFiltersEqual,
  parseCatalogUrlFilters,
  writeCatalogFiltersToSearchParams,
  type CatalogUrlFilterState,
} from "@/lib/catalogFilters";
import { formatDateMinute } from "@/shared/lib/formatDateTime";
import { useClientPageWindow } from "@/shared/hooks/useClientPageWindow";
import { ScrollLoadFooter } from "@/shared/ui/ScrollLoadFooter";

const STATUSES = [
  "",
  "ACTIVE",
  "NEEDS_CREDENTIALS",
  "UNDER_REVIEW",
  "VALIDATED",
  "REJECTED",
  "DISCOVERED",
];
const CATEGORIES = ["", "A", "B", "C", "D", "E", "F", "G", "H", "I"];

type SourceItem = Record<string, unknown>;

type InsertEvidence = {
  has_insert_evidence: boolean;
  insert_runs_count: number;
  last_insert_at: string | null;
  verification_status: string;
};

function hasInsertEvidence(s: SourceItem): boolean {
  if (typeof s.has_insert_evidence === "boolean") return s.has_insert_evidence;
  return Number(s.insert_runs_count ?? 0) > 0;
}

function evidenceFromSource(s: SourceItem): InsertEvidence {
  return {
    has_insert_evidence: hasInsertEvidence(s),
    insert_runs_count: Number(s.insert_runs_count ?? 0),
    last_insert_at: s.last_insert_at
      ? formatDateMinute(String(s.last_insert_at))
      : null,
    verification_status: String(s.verification_status ?? ""),
  };
}

function InsertBadge({ evidence }: { evidence: InsertEvidence }) {
  const t = useTranslations("sources");
  const isActive = evidence.verification_status === "ACTIVE";
  if (evidence.has_insert_evidence) {
    return (
      <span
        className="badge rise-text"
        title={evidence.last_insert_at ?? undefined}
      >
        {t("badgeHasInserts", { count: evidence.insert_runs_count })}
      </span>
    );
  }
  return (
    <span className={`badge ${isActive ? "cool-text" : ""}`}>
      {isActive ? t("badgeNeedsRun") : t("badgeNoInserts")}
    </span>
  );
}

function CatalogBrowserInner() {
  const t = useTranslations("sources");
  const searchParams = useSearchParams();
  const pathname = usePathname();
  const router = useRouter();

  const [filters, setFilters] = useState<CatalogUrlFilterState>(() =>
    parseCatalogUrlFilters((k) => searchParams.get(k)),
  );
  const [items, setItems] = useState<SourceItem[]>([]);
  const [loaded, setLoaded] = useState(false);
  const [evidenceByKey, setEvidenceByKey] = useState<
    Record<string, InsertEvidence>
  >({});
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fromUrl = parseCatalogUrlFilters((k) => searchParams.get(k));
    setFilters((prev) => (catalogFiltersEqual(prev, fromUrl) ? prev : fromUrl));
  }, [searchParams]);

  useEffect(() => {
    let cancelled = false;
    api
      .sources()
      .then((data) => {
        if (cancelled) return;
        const map: Record<string, InsertEvidence> = {};
        for (const s of data.items) {
          const key = String(s.connector_type ?? "").trim();
          if (key) map[key] = evidenceFromSource(s);
        }
        setEvidenceByKey(map);
      })
      .catch(() => {
        /* catalog still useful without DB evidence */
      });
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    let cancelled = false;
    setLoaded(false);
    setError(null);
    api
      .catalog({
        status: filters.status || undefined,
        category: filters.category || undefined,
        kind: filters.kind || undefined,
      })
      .then((data) => {
        if (!cancelled) {
          setItems(data.items ?? []);
          setLoaded(true);
        }
      })
      .catch((e: unknown) => {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : t("loadFailed"));
          setItems([]);
          setLoaded(true);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [filters.status, filters.category, filters.kind, t]);

  const {
    visible,
    hasMore,
    loadMore,
    shown,
    total: listTotal,
  } = useClientPageWindow(
    items,
    24,
    `${filters.status}|${filters.category}|${filters.kind}|${items.length}`,
  );

  const commit = (next: CatalogUrlFilterState) => {
    setFilters(next);
    const params = new URLSearchParams(searchParams.toString());
    writeCatalogFiltersToSearchParams(params, next);
    const qs = params.toString();
    startTransition(() => {
      router.replace(qs ? `${pathname}?${qs}` : pathname, { scroll: false });
    });
  };

  return (
    <section className="space-y-3">
      <p className="max-w-3xl text-xs text-[var(--muted)]">{t("partnerBoardsNote")}</p>
      <div className="flex flex-wrap items-end gap-3">
        <h3 className="font-semibold">{t("catalogHeading")}</h3>
        <label className="text-xs">
          {t("filterStatus")}
          <select
            className="ml-1 rounded border border-[var(--line)] bg-transparent px-2 py-1"
            value={filters.status}
            onChange={(e) => commit({ ...filters, status: e.target.value })}
          >
            {STATUSES.map((s) => (
              <option key={s || "all"} value={s}>
                {s || t("filterAll")}
              </option>
            ))}
          </select>
        </label>
        <label className="text-xs">
          {t("filterCategory")}
          <select
            className="ml-1 rounded border border-[var(--line)] bg-transparent px-2 py-1"
            value={filters.category}
            onChange={(e) => commit({ ...filters, category: e.target.value })}
          >
            {CATEGORIES.map((c) => (
              <option key={c || "all"} value={c}>
                {c || t("filterAll")}
              </option>
            ))}
          </select>
        </label>
        <label className="text-xs">
          {t("filterKind")}
          <select
            className="ml-1 rounded border border-[var(--line)] bg-transparent px-2 py-1"
            value={filters.kind}
            onChange={(e) =>
              commit({
                ...filters,
                kind: e.target.value === "free" || e.target.value === "credentialed"
                  ? e.target.value
                  : "",
              })
            }
          >
            <option value="">{t("kindFilterAll")}</option>
            <option value="free">{t("kindFreePublic")}</option>
            <option value="credentialed">{t("kindCredentialed")}</option>
          </select>
        </label>
        <span className="text-xs opacity-60">
          {t("catalogShown", { count: listTotal })}
        </span>
      </div>
      {error ? <p className="text-sm text-red-700">{error}</p> : null}
      {loaded && !error && items.length === 0 ? (
        <p className="text-sm opacity-70">{t("emptyCatalog")}</p>
      ) : null}
      <div className="grid gap-2">
        {visible.map((s) => {
          const key = String(s.connector_key ?? s.key ?? "");
          const evidence = key ? evidenceByKey[key] : undefined;
          const vStatus = String(s.verification_status ?? "");
          const statusKey = `status.${vStatus}`;
          const statusLabel =
            vStatus && t.has(statusKey) ? t(statusKey) : vStatus || "—";
          const credentialed = Boolean(s.is_credentialed_scaffold);
          return (
            <article
              key={String(s.catalog_id ?? s.key ?? s.name)}
              className="card px-4 py-3 text-sm"
            >
              <div className="flex flex-wrap justify-between gap-2">
                <span className="font-medium">{String(s.name)}</span>
                <div className="flex flex-wrap items-center gap-2">
                  <ConnectorKindBadge credentialed={credentialed} />
                  {evidence ? <InsertBadge evidence={evidence} /> : null}
                  <SourceStatusBadge status={vStatus || "—"} label={statusLabel} />
                </div>
              </div>
              <p className="mt-1 text-xs opacity-60">
                cat={String(s.category ?? "—")} · {key}
              </p>
              {evidence?.last_insert_at ? (
                <p className="mt-1 text-xs opacity-60">
                  {t("lastInsert", { at: evidence.last_insert_at })}
                </p>
              ) : null}
              {!evidence?.last_insert_at && evidence ? (
                <p className="mt-1 text-xs opacity-60">{t("lastRunNever")}</p>
              ) : null}
              <p className="mt-1 text-xs opacity-60">
                {String(s.notes ?? s.coverage_notes ?? "")}
              </p>
            </article>
          );
        })}
      </div>
      {items.length > 0 ? (
        <ScrollLoadFooter
          hasMore={hasMore}
          onLoadMore={loadMore}
          shown={shown}
          total={listTotal}
        />
      ) : null}
    </section>
  );
}

export function CatalogBrowser() {
  const t = useTranslations("common");
  return (
    <Suspense
      fallback={
        <section className="space-y-3">
          <p className="text-sm text-[var(--muted)]">{t("loading")}</p>
        </section>
      }
    >
      <CatalogBrowserInner />
    </Suspense>
  );
}
