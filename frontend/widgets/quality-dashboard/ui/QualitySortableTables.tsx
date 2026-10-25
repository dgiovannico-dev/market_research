"use client";

import { useMemo, useState } from "react";
import { useTranslations } from "next-intl";
import { ScrollLoadFooter } from "@/shared/ui/ScrollLoadFooter";
import { SortableTh } from "@/shared/ui/SortableTh";
import { TableGuide } from "@/shared/ui/TableGuide";
import { TableSearch } from "@/shared/ui/TableSearch";
import { useClientPageWindow } from "@/shared/hooks/useClientPageWindow";
import { useClientTableFilter } from "@/shared/hooks/useClientTableFilter";
import { useClientTableSort } from "@/shared/hooks/useClientTableSort";
import { formatDateMinute } from "@/shared/lib/formatDateTime";
import { joinSearchParts } from "@/shared/lib/tableFilter";

/** Default: hide catalog refs / agencies / demoted stubs (connector_status=unsupported). */
type CatalogStatusFilter =
  | "connectors"
  | "enabled"
  | "requires_credentials"
  | "unsupported"
  | "disabled"
  | "all";

function matchesCatalogStatusFilter(
  status: string,
  filter: CatalogStatusFilter,
): boolean {
  if (filter === "all") return true;
  if (filter === "connectors") {
    return (
      status === "enabled" ||
      status === "requires_credentials" ||
      status === "manual_import"
    );
  }
  return status === filter;
}

type Tone = "pass" | "warn" | "neutral";

type BySourceRow = {
  source_id?: number | null;
  name?: string | null;
  connector_type?: string | null;
  n?: number | null;
  pct_known_country?: number | null;
  pct_thin?: number | null;
  pct_with_rate?: number | null;
  last_seen_at?: string | null;
};

type CatalogSource = {
  id?: number | string;
  name?: string | null;
  connector_status?: string | null;
  enabled?: boolean | null;
  last_success_at?: string | null;
  coverage_notes?: string | null;
};

type ToneBadgeProps = {
  tone: Tone;
  children: React.ReactNode;
  title?: string;
};

type Props = {
  bySource: BySourceRow[];
  sources: CatalogSource[];
  ToneBadge: (props: ToneBadgeProps) => React.ReactNode;
  sourceStatusTone: (status: string, enabled: boolean) => Tone;
};

export function QualityBySourceTable({ bySource }: { bySource: BySourceRow[] }) {
  const t = useTranslations("quality");
  const tCommon = useTranslations("common");
  const {
    query: tableQuery,
    setQuery: setTableQuery,
    filtered,
  } = useClientTableFilter(bySource, (r) =>
    joinSearchParts(
      r.name,
      r.connector_type,
      r.n,
      r.pct_known_country,
      r.pct_thin,
      r.pct_with_rate,
      r.last_seen_at,
    ),
  );
  const { sorted, sortKey, order, toggle } = useClientTableSort(
    filtered,
    {
      source: (r) => r.name ?? "",
      connector: (r) => r.connector_type ?? "",
      n: (r) => r.n ?? 0,
      pct_known: (r) => r.pct_known_country ?? 0,
      pct_thin: (r) => r.pct_thin ?? 0,
      pct_rate: (r) => r.pct_with_rate ?? 0,
      last_seen: (r) => r.last_seen_at ?? "",
    },
    "n",
    "desc",
  );
  const page = useClientPageWindow(
    sorted,
    30,
    `${tableQuery}|${sortKey}|${order}|${sorted.length}`,
  );

  return (
    <div className="space-y-3">
      <TableGuide
        represents={t("bySourceRepresents")}
        howToRead={t("bySourceHowToRead")}
      />
      <div className="border-b border-[var(--line)] px-3 py-2">
        <TableSearch value={tableQuery} onChange={setTableQuery} />
      </div>
      <table className="min-w-full text-sm">
        <thead className="border-b border-[var(--line)] text-xs uppercase text-[var(--muted)]">
          <tr>
            <SortableTh label={t("colSource")} sortKey="source" activeSort={sortKey} order={order} onSort={toggle} ariaLabel={tCommon("sortBy", { column: t("colSource") })} hint={t("hintSource")} className="px-3 py-2 text-left" />
            <SortableTh label={t("colConnector")} sortKey="connector" activeSort={sortKey} order={order} onSort={toggle} ariaLabel={tCommon("sortBy", { column: t("colConnector") })} hint={t("hintConnector")} className="px-3 py-2 text-left" />
            <SortableTh label={t("colN")} sortKey="n" activeSort={sortKey} order={order} onSort={toggle} ariaLabel={tCommon("sortBy", { column: t("colN") })} align="right" hint={t("hintN")} className="px-3 py-2" />
            <SortableTh label={t("colPctKnownCountry")} sortKey="pct_known" activeSort={sortKey} order={order} onSort={toggle} ariaLabel={tCommon("sortBy", { column: t("colPctKnownCountry") })} align="right" hint={t("hintPctKnownCountry")} className="px-3 py-2" />
            <SortableTh label={t("colPctThin")} sortKey="pct_thin" activeSort={sortKey} order={order} onSort={toggle} ariaLabel={tCommon("sortBy", { column: t("colPctThin") })} align="right" hint={t("hintPctThin")} className="px-3 py-2" />
            <SortableTh label={t("colPctRate")} sortKey="pct_rate" activeSort={sortKey} order={order} onSort={toggle} ariaLabel={tCommon("sortBy", { column: t("colPctRate") })} align="right" hint={t("hintPctRate")} className="px-3 py-2" />
            <SortableTh label={t("colLastSeen")} sortKey="last_seen" activeSort={sortKey} order={order} onSort={toggle} ariaLabel={tCommon("sortBy", { column: t("colLastSeen") })} hint={t("hintLastSeen")} className="px-3 py-2 text-left" />
          </tr>
        </thead>
        <tbody>
          {sorted.length === 0 ? (
            <tr>
              <td colSpan={7} className="px-3 py-4 text-sm text-[var(--muted)]">
                {tableQuery ? tCommon("tableFilterEmpty") : tCommon("empty")}
              </td>
            </tr>
          ) : (
            page.visible.map((row) => (
              <tr
                key={String(row.source_id ?? row.name)}
                className="border-b border-[var(--line)]"
              >
                <td className="px-3 py-2 font-medium">{row.name ?? "—"}</td>
                <td
                  className="px-3 py-2 text-[var(--muted)]"
                  style={{ fontFamily: "var(--mono)" }}
                >
                  {row.connector_type ?? "—"}
                </td>
                <td className="px-3 py-2 text-right" style={{ fontFamily: "var(--mono)" }}>
                  {row.n}
                </td>
                <td className="px-3 py-2 text-right" style={{ fontFamily: "var(--mono)" }}>
                  {Number(row.pct_known_country ?? 0).toFixed(1)}%
                </td>
                <td className="px-3 py-2 text-right" style={{ fontFamily: "var(--mono)" }}>
                  {Number(row.pct_thin ?? 0).toFixed(1)}%
                </td>
                <td className="px-3 py-2 text-right" style={{ fontFamily: "var(--mono)" }}>
                  {Number(row.pct_with_rate ?? 0).toFixed(1)}%
                </td>
                <td
                  className="px-3 py-2 text-[var(--muted)]"
                  style={{ fontFamily: "var(--mono)" }}
                >
                  {formatDateMinute(row.last_seen_at)}
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
      {sorted.length > 0 ? (
        <ScrollLoadFooter
          hasMore={page.hasMore}
          isExpanded={page.isExpanded}
          onLoadMore={page.loadMore}
          onExpandAll={page.expandAll}
          onCollapse={page.collapse}
          shown={page.shown}
          total={page.total}
        />
      ) : null}
    </div>
  );
}

export function QualityCatalogTable({
  sources,
  ToneBadge,
  sourceStatusTone,
}: Pick<Props, "sources" | "ToneBadge" | "sourceStatusTone">) {
  const t = useTranslations("quality");
  const tCommon = useTranslations("common");
  const [statusFilter, setStatusFilter] =
    useState<CatalogStatusFilter>("connectors");

  const statusFiltered = useMemo(
    () =>
      sources.filter((s) =>
        matchesCatalogStatusFilter(
          String(s.connector_status ?? ""),
          statusFilter,
        ),
      ),
    [sources, statusFilter],
  );

  const hiddenUnsupported = useMemo(
    () =>
      sources.filter((s) => String(s.connector_status ?? "") === "unsupported")
        .length,
    [sources],
  );

  const {
    query: tableQuery,
    setQuery: setTableQuery,
    filtered,
  } = useClientTableFilter(statusFiltered, (s) =>
    joinSearchParts(
      s.name,
      s.connector_status,
      s.enabled,
      s.last_success_at,
      s.coverage_notes,
    ),
  );

  const { sorted, sortKey, order, toggle } = useClientTableSort(
    filtered,
    {
      source: (s) => String(s.name ?? ""),
      status: (s) => String(s.connector_status ?? ""),
      enabled: (s) => (s.enabled ? 1 : 0),
      last_success: (s) =>
        typeof s.last_success_at === "string" ? s.last_success_at : "",
      notes: (s) => String(s.coverage_notes ?? ""),
    },
    "source",
    "asc",
  );
  const page = useClientPageWindow(
    sorted,
    30,
    `${statusFilter}|${tableQuery}|${sortKey}|${order}|${sorted.length}`,
  );

  return (
    <div className="space-y-2">
      <TableGuide
        represents={t("catalogRepresents")}
        howToRead={t("catalogHowToRead")}
      />
      <div className="flex flex-wrap items-end justify-between gap-2 border-b border-[var(--line)] px-3 py-2">
        <label className="text-xs text-[var(--muted)]">
          {t("filterConnectorStatus")}
          <select
            className="ml-1 rounded border border-[var(--line)] bg-transparent px-2 py-1 text-[var(--ink)]"
            value={statusFilter}
            onChange={(e) =>
              setStatusFilter(e.target.value as CatalogStatusFilter)
            }
          >
            <option value="connectors">{t("filterConnectors")}</option>
            <option value="enabled">{t("filterEnabledOnly")}</option>
            <option value="requires_credentials">
              {t("filterNeedsCredentials")}
            </option>
            <option value="unsupported">{t("filterUnsupported")}</option>
            <option value="disabled">{t("filterDisabled")}</option>
            <option value="all">{t("filterAllStatuses")}</option>
          </select>
        </label>
        <p className="text-xs text-[var(--muted)]">
          {t("catalogShown", {
            shown: filtered.length,
            total: sources.length,
          })}
          {statusFilter === "connectors" && hiddenUnsupported > 0
            ? ` · ${t("catalogUnsupportedHidden", { count: hiddenUnsupported })}`
            : null}
        </p>
      </div>
      <div className="px-3">
        <TableSearch value={tableQuery} onChange={setTableQuery} />
      </div>
      <p className="px-3 text-[0.7rem] leading-snug text-[var(--muted)]">
        {t("catalogUnsupportedHint")}
      </p>
      <table className="min-w-full text-sm">
        <thead className="border-b border-[var(--line)] text-xs uppercase text-[var(--muted)]">
          <tr>
            <SortableTh label={t("colSource")} sortKey="source" activeSort={sortKey} order={order} onSort={toggle} ariaLabel={tCommon("sortBy", { column: t("colSource") })} hint={t("hintSource")} className="px-3 py-2 text-left" />
            <SortableTh label={t("colStatus")} sortKey="status" activeSort={sortKey} order={order} onSort={toggle} ariaLabel={tCommon("sortBy", { column: t("colStatus") })} hint={t("hintStatus")} className="px-3 py-2 text-left" />
            <SortableTh label={t("colEnabled")} sortKey="enabled" activeSort={sortKey} order={order} onSort={toggle} ariaLabel={tCommon("sortBy", { column: t("colEnabled") })} hint={t("hintEnabled")} className="px-3 py-2 text-left" />
            <SortableTh label={t("colLastSuccess")} sortKey="last_success" activeSort={sortKey} order={order} onSort={toggle} ariaLabel={tCommon("sortBy", { column: t("colLastSuccess") })} hint={t("hintLastSuccess")} className="px-3 py-2 text-left" />
            <SortableTh label={t("colNotes")} sortKey="notes" activeSort={sortKey} order={order} onSort={toggle} ariaLabel={tCommon("sortBy", { column: t("colNotes") })} hint={t("hintNotes")} className="px-3 py-2 text-left" />
          </tr>
        </thead>
        <tbody>
          {sorted.length === 0 ? (
            <tr>
              <td colSpan={5} className="px-3 py-4 text-sm text-[var(--muted)]">
                {tableQuery ? tCommon("tableFilterEmpty") : tCommon("empty")}
              </td>
            </tr>
          ) : (
            page.visible.map((s) => {
              const status = String(s.connector_status ?? "");
              const enabled = Boolean(s.enabled);
              const tone = sourceStatusTone(status, enabled);
              return (
                <tr
                  key={String(s.id)}
                  className="border-b border-[var(--line)] align-top"
                >
                  <td className="px-3 py-2 font-medium">{String(s.name)}</td>
                  <td className="px-3 py-2">
                    <ToneBadge tone={tone}>{status || "—"}</ToneBadge>
                  </td>
                  <td className="px-3 py-2">
                    <ToneBadge tone={enabled ? "pass" : "warn"}>
                      {enabled ? t("badgeEnabled") : t("badgeDisabled")}
                    </ToneBadge>
                  </td>
                  <td
                    className="px-3 py-2 text-[var(--muted)]"
                    style={{ fontFamily: "var(--mono)" }}
                  >
                    {formatDateMinute(
                      typeof s.last_success_at === "string"
                        ? s.last_success_at
                        : null,
                    )}
                  </td>
                  <td className="px-3 py-2 text-xs text-[var(--muted)]">
                    {String(s.coverage_notes ?? "")}
                  </td>
                </tr>
              );
            })
          )}
        </tbody>
      </table>
      {sorted.length > 0 ? (
        <ScrollLoadFooter
          hasMore={page.hasMore}
          isExpanded={page.isExpanded}
          onLoadMore={page.loadMore}
          onExpandAll={page.expandAll}
          onCollapse={page.collapse}
          shown={page.shown}
          total={page.total}
        />
      ) : null}
    </div>
  );
}
