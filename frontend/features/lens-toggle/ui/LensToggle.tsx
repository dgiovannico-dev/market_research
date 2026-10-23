"use client";

import {
  createContext,
  startTransition,
  use,
  useEffect,
  useMemo,
  useRef,
  type ReactNode,
} from "react";
import { useSearchParams } from "next/navigation";
import { useTranslations } from "next-intl";
import { usePathname, useRouter } from "@/i18n/navigation";
import type { DashboardLens } from "@/shared/api";
import { parsePrefsLens, useDashboardPrefs } from "@/features/dashboard-prefs";

export type { DashboardLens };
export const DASHBOARD_LENSES: readonly DashboardLens[] = [
  "market",
  "focus",
  "compare",
];

const DEFAULT_LENS: DashboardLens = "market";

type LensState = {
  lens: DashboardLens;
  /** Optional focus intent ids from `query_ids` (comma-separated). */
  queryIds: number[];
};

type LensActions = {
  setLens: (lens: DashboardLens) => void;
};

type LensMeta = {
  options: readonly DashboardLens[];
};

type LensContextValue = {
  state: LensState;
  actions: LensActions;
  meta: LensMeta;
};

const LensContext = createContext<LensContextValue | null>(null);

export function parseDashboardLens(raw: string | null | undefined): DashboardLens {
  return parsePrefsLens(raw);
}

export function parseQueryIds(raw: string | null | undefined): number[] {
  if (!raw?.trim()) return [];
  return raw
    .split(",")
    .map((part) => Number.parseInt(part.trim(), 10))
    .filter((n) => Number.isFinite(n) && n > 0);
}

function lensQueryValue(lens: DashboardLens): string | null {
  return lens === DEFAULT_LENS ? null : lens;
}

function writeLensToUrl(
  pathname: string,
  searchParams: URLSearchParams,
  router: ReturnType<typeof useRouter>,
  next: DashboardLens,
) {
  const params = new URLSearchParams(searchParams.toString());
  const desired = lensQueryValue(next);
  if (desired === null) params.delete("lens");
  else params.set("lens", desired);
  const qs = params.toString();
  startTransition(() => {
    router.replace(qs ? `${pathname}?${qs}` : pathname, { scroll: false });
  });
}

function useLensFromUrl(): LensContextValue {
  const searchParams = useSearchParams();
  const pathname = usePathname();
  const router = useRouter();
  const { prefs, hydrated, setPrefs } = useDashboardPrefs();
  /** One-shot: URL `?lens=` seeds prefs before prefs may rewrite the URL. */
  const urlSeedDone = useRef(false);

  const hasLensParam = searchParams.has("lens");
  const lensParam = searchParams.get("lens");
  // Prefer `query_ids`; accept legacy Explore singular `query_id`.
  const queryIdsParam =
    searchParams.get("query_ids") ?? searchParams.get("query_id") ?? "";
  const queryIds = useMemo(() => parseQueryIds(queryIdsParam), [queryIdsParam]);

  // URL wins when present; otherwise sticky prefs (after hydrate).
  const lens = hasLensParam
    ? parseDashboardLens(lensParam)
    : hydrated
      ? prefs.lens
      : DEFAULT_LENS;

  useEffect(() => {
    if (!hydrated) return;

    if (!urlSeedDone.current) {
      urlSeedDone.current = true;
      if (hasLensParam) {
        const fromUrl = parseDashboardLens(lensParam);
        setPrefs((p) => (p.lens === fromUrl ? p : { ...p, lens: fromUrl }));
        return;
      }
    }

    // No URL on entry, or later prefs changes (toggle / preset / profile): align URL.
    const desired = lensQueryValue(prefs.lens);
    const current = searchParams.get("lens");
    if (desired === current) return;
    writeLensToUrl(pathname, searchParams, router, prefs.lens);
  }, [
    hydrated,
    hasLensParam,
    lensParam,
    prefs.lens,
    pathname,
    router,
    searchParams,
    setPrefs,
  ]);

  return useMemo(() => {
    const setLens = (next: DashboardLens) => {
      setPrefs((p) => (p.lens === next ? p : { ...p, lens: next }));
      writeLensToUrl(pathname, searchParams, router, next);
    };
    return {
      state: { lens, queryIds },
      actions: { setLens },
      meta: { options: DASHBOARD_LENSES },
    };
  }, [lens, queryIds, pathname, router, searchParams, setPrefs]);
}

function LensToggleProvider({ children }: { children: ReactNode }) {
  const value = useLensFromUrl();
  return <LensContext value={value}>{children}</LensContext>;
}

function useLensContext(): LensContextValue {
  const ctx = use(LensContext);
  if (!ctx) {
    throw new Error("LensToggle components require LensToggle.Provider");
  }
  return ctx;
}

/** Hook for dashboards that fetch with the active lens. */
export function useDashboardLens(): LensState & { setLens: (lens: DashboardLens) => void } {
  const { state, actions } = useLensContext();
  return { ...state, setLens: actions.setLens };
}

function LensToggleRoot({
  children,
  className = "",
}: {
  children?: ReactNode;
  className?: string;
}) {
  const t = useTranslations("compass");
  const { meta } = useLensContext();
  return (
    <div
      className={`inline-flex rounded-full border border-[var(--line)] p-0.5 text-xs ${className}`}
      role="group"
      aria-label={t("lensAria")}
    >
      {children ??
        meta.options.map((value) => <LensToggleOption key={value} value={value} />)}
    </div>
  );
}

function LensToggleOption({ value }: { value: DashboardLens }) {
  const t = useTranslations("compass");
  const { state, actions } = useLensContext();
  const active = state.lens === value;
  const label =
    value === "market"
      ? t("lensMarket")
      : value === "focus"
        ? t("lensFocus")
        : t("lensCompare");
  const hint =
    value === "market"
      ? t("lensDefMarket")
      : value === "focus"
        ? t("lensDefFocus")
        : t("lensDefCompare");

  return (
    <button
      type="button"
      className={`rounded-full px-3 py-1.5 transition-colors duration-200 ${
        active ? "bg-[var(--signal)] text-white" : "opacity-70 hover:opacity-100"
      }`}
      aria-pressed={active}
      aria-label={`${label}. ${hint}`}
      title={hint}
      onClick={() => actions.setLens(value)}
    >
      {label}
    </button>
  );
}

/** Composed default: market / focus / compare. */
function LensToggleControl({ className }: { className?: string }) {
  return <LensToggleRoot className={className} />;
}

export const LensToggle = {
  Provider: LensToggleProvider,
  Root: LensToggleRoot,
  Option: LensToggleOption,
  Control: LensToggleControl,
};
