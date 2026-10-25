"use client";

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

export type ApplicationRow = {
  id: string | number;
  applied_at?: string | null;
  job_id?: string | number | null;
  channel?: string | null;
  response?: string | null;
  outcome?: string | null;
};

type Props = {
  items: ApplicationRow[];
};

export function ApplicationsTable({ items }: Props) {
  const t = useTranslations("applications");
  const tCommon = useTranslations("common");
  const {
    query: tableQuery,
    setQuery: setTableQuery,
    filtered,
  } = useClientTableFilter(items, (r) =>
    joinSearchParts(
      r.applied_at,
      r.job_id,
      r.channel,
      r.response,
      r.outcome,
    ),
  );
  const { sorted, sortKey, order, toggle } = useClientTableSort(
    filtered,
    {
      date: (r) => r.applied_at ?? "",
      job: (r) => String(r.job_id ?? ""),
      channel: (r) => String(r.channel ?? ""),
      response: (r) => String(r.response ?? ""),
      outcome: (r) => String(r.outcome ?? ""),
    },
    "date",
    "desc",
  );
  const {
    visible: visibleRows,
    hasMore,
    isExpanded,
    loadMore,
    expandAll,
    collapse,
    shown,
    total: listTotal,
  } = useClientPageWindow(
    sorted,
    30,
    `${tableQuery}|${sortKey}|${order}|${sorted.length}`,
  );

  if (items.length === 0) {
    return (
      <p className="p-6 text-sm text-[var(--muted)]">{t("empty")}</p>
    );
  }

  return (
    <div className="space-y-3 overflow-hidden">
      <TableGuide
        represents={t("tableRepresents")}
        howToRead={t("tableHowToRead")}
      />
      <div className="border-b border-[var(--line)] px-3 py-2">
        <TableSearch value={tableQuery} onChange={setTableQuery} />
      </div>
      <table className="min-w-full text-sm">
        <thead className="border-b border-[var(--line)] text-xs uppercase tracking-wide text-[var(--muted)]">
          <tr>
            <SortableTh
              label={t("colDate")}
              sortKey="date"
              activeSort={sortKey}
              order={order}
              onSort={toggle}
              ariaLabel={tCommon("sortBy", { column: t("colDate") })}
              className="px-3 py-2 text-left font-medium"
            />
            <SortableTh
              label={t("colJob")}
              sortKey="job"
              activeSort={sortKey}
              order={order}
              onSort={toggle}
              ariaLabel={tCommon("sortBy", { column: t("colJob") })}
              className="px-3 py-2 text-left font-medium"
            />
            <SortableTh
              label={t("colChannel")}
              sortKey="channel"
              activeSort={sortKey}
              order={order}
              onSort={toggle}
              ariaLabel={tCommon("sortBy", { column: t("colChannel") })}
              className="px-3 py-2 text-left font-medium"
            />
            <SortableTh
              label={t("colResponse")}
              sortKey="response"
              activeSort={sortKey}
              order={order}
              onSort={toggle}
              ariaLabel={tCommon("sortBy", { column: t("colResponse") })}
              className="px-3 py-2 text-left font-medium"
            />
            <SortableTh
              label={t("colOutcome")}
              sortKey="outcome"
              activeSort={sortKey}
              order={order}
              onSort={toggle}
              ariaLabel={tCommon("sortBy", { column: t("colOutcome") })}
              className="px-3 py-2 text-left font-medium"
            />
          </tr>
        </thead>
        <tbody>
          {sorted.length === 0 ? (
            <tr>
              <td
                colSpan={5}
                className="px-3 py-6 text-sm text-[var(--muted)]"
              >
                {tCommon("tableFilterEmpty")}
              </td>
            </tr>
          ) : (
            visibleRows.map((row) => (
              <tr
                key={String(row.id)}
                className="border-b border-[var(--line)] last:border-b-0"
              >
                <td
                  className="px-3 py-2 text-[var(--muted)]"
                  style={{ fontFamily: "var(--mono)" }}
                >
                  {formatDateMinute(
                    typeof row.applied_at === "string" ? row.applied_at : null,
                  )}
                </td>
                <td className="px-3 py-2 text-[var(--ink)]">
                  {String(row.job_id ?? "—")}
                </td>
                <td className="px-3 py-2 text-[var(--ink)]">
                  {String(row.channel ?? "—")}
                </td>
                <td className="px-3 py-2 text-[var(--ink)]">
                  {String(row.response ?? "—")}
                </td>
                <td className="px-3 py-2 text-[var(--ink)]">
                  {String(row.outcome ?? "—")}
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
      {sorted.length > 0 ? (
        <ScrollLoadFooter
          hasMore={hasMore}
          isExpanded={isExpanded}
          onLoadMore={loadMore}
          onExpandAll={expandAll}
          onCollapse={collapse}
          shown={shown}
          total={listTotal}
        />
      ) : null}
    </div>
  );
}
