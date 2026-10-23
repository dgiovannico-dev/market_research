"use client";

import { useMemo, useRef, useState } from "react";
import { sortRows, type SortOrder, type SortValue } from "@/shared/lib/tableSort";

export function useClientTableSort<
  T,
  A extends Record<string, (row: T) => SortValue>,
>(
  rows: readonly T[],
  accessors: A,
  defaultKey: keyof A & string,
  defaultOrder: SortOrder = "asc",
) {
  const [sortKey, setSortKey] = useState<keyof A & string>(defaultKey);
  const [order, setOrder] = useState<SortOrder>(defaultOrder);
  const accessorsRef = useRef(accessors);
  accessorsRef.current = accessors;

  const toggle = (key: string) => {
    if (!(key in accessorsRef.current)) return;
    const next = key as keyof A & string;
    if (next === sortKey) {
      setOrder((o) => (o === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(next);
      setOrder("asc");
    }
  };

  const sorted = useMemo(() => {
    const getValue = accessorsRef.current[sortKey] ?? (() => null);
    return sortRows(rows, getValue, order);
  }, [rows, sortKey, order]);

  return { sorted, sortKey: sortKey as string, order, toggle };
}
