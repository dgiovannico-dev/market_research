"use client";

import { useMemo, useRef, useState } from "react";
import { filterRows } from "@/shared/lib/tableFilter";

export function useClientTableFilter<T>(
  rows: readonly T[],
  getHaystack: (row: T) => string,
) {
  const [query, setQuery] = useState("");
  const getHaystackRef = useRef(getHaystack);
  getHaystackRef.current = getHaystack;

  const filtered = useMemo(
    () => filterRows(rows, query, (row) => getHaystackRef.current(row)),
    [rows, query],
  );

  return { query, setQuery, filtered };
}
