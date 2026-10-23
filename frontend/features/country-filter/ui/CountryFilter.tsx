"use client";

import {
  createContext,
  startTransition,
  use,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { useSearchParams } from "next/navigation";
import { useTranslations } from "next-intl";
import { usePathname, useRouter } from "@/i18n/navigation";
import { api } from "@/lib/api";
import { useDashboardPrefs } from "@/features/dashboard-prefs";

type CountryState = {
  countries: string[];
};

type CountryActions = {
  setCountries: (codes: string[]) => void;
};

type CountryContextValue = {
  state: CountryState;
  actions: CountryActions;
};

const CountryContext = createContext<CountryContextValue | null>(null);

/**
 * Paths where the chrome country control is shown and prefs may sync to `?countries=`.
 * Exclude Jobs / Sources / Explorer — those pages own country filters in-page
 * (JobsFilters / CatalogBrowser / ExplorerSearchForm) and must not fight prefs.
 */
export const ANALYTICS_COUNTRY_PATHS = new Set([
  "/",
  "/market-scan",
  "/trends",
  "/skills",
  "/relations",
  "/rates",
  "/countries",
  "/languages",
  "/quality",
  "/assistant",
  "/focus",
]);

export function parseCountryCodes(raw: string | null | undefined): string[] {
  if (!raw?.trim()) return [];
  const out: string[] = [];
  const seen = new Set<string>();
  for (const part of raw.split(",")) {
    const code = part.trim().toUpperCase();
    if (!code || code === "ALL" || seen.has(code)) continue;
    seen.add(code);
    out.push(code);
  }
  return out;
}

function codesEqual(a: string[], b: string[]): boolean {
  if (a.length !== b.length) return false;
  return a.every((c, i) => c === b[i]);
}

function writeCountriesToUrl(
  pathname: string,
  searchParams: URLSearchParams,
  router: ReturnType<typeof useRouter>,
  codes: string[],
) {
  const params = new URLSearchParams(searchParams.toString());
  if (codes.length) params.set("countries", codes.join(","));
  else params.delete("countries");
  const qs = params.toString();
  startTransition(() => {
    router.replace(qs ? `${pathname}?${qs}` : pathname, { scroll: false });
  });
}

function useCountriesFromUrl(): CountryContextValue {
  const searchParams = useSearchParams();
  const pathname = usePathname();
  const router = useRouter();
  const { prefs, hydrated, setPrefs } = useDashboardPrefs();
  const urlSeedDone = useRef(false);
  const seededPath = useRef<string | null>(null);

  /** Jobs / Sources own `?countries=` for table filters — do not rewrite from prefs. */
  const syncCountriesToUrl = ANALYTICS_COUNTRY_PATHS.has(pathname);

  const hasCountriesParam = searchParams.has("countries");
  const countriesParam = searchParams.get("countries");
  const fromUrl = useMemo(
    () => parseCountryCodes(countriesParam),
    [countriesParam],
  );
  const fromPrefs = useMemo(
    () =>
      prefs.focus_countries
        .map((c) => c.trim().toUpperCase())
        .filter((c) => c && c !== "ALL"),
    [prefs.focus_countries],
  );

  // On Jobs-like pages, URL is authoritative when present; otherwise no geo filter.
  const countries = syncCountriesToUrl
    ? hasCountriesParam
      ? fromUrl
      : hydrated
        ? fromPrefs
        : []
    : fromUrl;

  useEffect(() => {
    if (!hydrated || !syncCountriesToUrl) return;

    // Provider wraps the whole app — re-seed when entering an analytics path.
    if (seededPath.current !== pathname) {
      seededPath.current = pathname;
      urlSeedDone.current = false;
    }

    if (!urlSeedDone.current) {
      urlSeedDone.current = true;
      if (hasCountriesParam) {
        setPrefs((p) =>
          codesEqual(
            p.focus_countries.map((c) => c.toUpperCase()),
            fromUrl,
          )
            ? p
            : { ...p, focus_countries: fromUrl },
        );
        return;
      }
    }

    const desired = fromPrefs.length ? fromPrefs.join(",") : null;
    const current = searchParams.get("countries");
    if (desired === current) return;
    if (!desired && !current) return;
    writeCountriesToUrl(pathname, searchParams, router, fromPrefs);
  }, [
    hydrated,
    syncCountriesToUrl,
    hasCountriesParam,
    fromUrl,
    fromPrefs,
    pathname,
    router,
    searchParams,
    setPrefs,
  ]);

  return useMemo(() => {
    const setCountries = (next: string[]) => {
      const normalized = parseCountryCodes(next.join(","));
      setPrefs((p) =>
        codesEqual(
          p.focus_countries.map((c) => c.toUpperCase()),
          normalized,
        )
          ? p
          : { ...p, focus_countries: normalized },
      );
      if (syncCountriesToUrl) {
        writeCountriesToUrl(pathname, searchParams, router, normalized);
      }
    };
    return {
      state: { countries },
      actions: { setCountries },
    };
  }, [countries, pathname, router, searchParams, setPrefs, syncCountriesToUrl]);
}

function CountryFilterProvider({ children }: { children: ReactNode }) {
  const value = useCountriesFromUrl();
  return <CountryContext value={value}>{children}</CountryContext>;
}

/** Prefs-only context while `useSearchParams` suspends (no URL sync yet). */
function CountryFilterPrefsFallbackProvider({
  children,
}: {
  children: ReactNode;
}) {
  const { prefs, setPrefs } = useDashboardPrefs();
  const value = useMemo(() => {
    const countries = prefs.focus_countries
      .map((c) => c.trim().toUpperCase())
      .filter((c) => c && c !== "ALL");
    return {
      state: { countries },
      actions: {
        setCountries: (next: string[]) => {
          const normalized = parseCountryCodes(next.join(","));
          setPrefs((p) =>
            codesEqual(
              p.focus_countries.map((c) => c.toUpperCase()),
              normalized,
            )
              ? p
              : { ...p, focus_countries: normalized },
          );
        },
      },
    };
  }, [prefs.focus_countries, setPrefs]);
  return <CountryContext value={value}>{children}</CountryContext>;
}

export function useDashboardCountries(): CountryState & {
  setCountries: (codes: string[]) => void;
} {
  const ctx = use(CountryContext);
  const { prefs } = useDashboardPrefs();
  if (!ctx) {
    const countries = prefs.focus_countries
      .map((c) => c.trim().toUpperCase())
      .filter((c) => c && c !== "ALL");
    return { countries, setCountries: () => {} };
  }
  return { ...ctx.state, setCountries: ctx.actions.setCountries };
}

function CountryFilterControl({ className = "" }: { className?: string }) {
  const t = useTranslations("nav");
  const ctx = use(CountryContext);
  const [options, setOptions] = useState<string[]>([]);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (!ctx) return;
    let cancelled = false;
    api
      .researchJobFacets({})
      .then((data) => {
        if (!cancelled) setOptions(data.countries ?? []);
      })
      .catch(() => {
        if (!cancelled) setOptions([]);
      });
    return () => {
      cancelled = true;
    };
  }, [ctx]);

  if (!ctx) return null;
  const { state, actions } = ctx;
  const selected = new Set(state.countries);
  const label =
    state.countries.length === 0
      ? t("countriesAll")
      : state.countries.length <= 3
        ? state.countries.join(", ")
        : t("countriesSelected", { count: state.countries.length });

  const toggle = (code: string) => {
    const next = selected.has(code)
      ? state.countries.filter((c) => c !== code)
      : [...state.countries, code];
    actions.setCountries(next);
  };

  return (
    <div className={`relative ${className}`}>
      <button
        type="button"
        className="rounded-full border border-[var(--line)] px-3 py-1.5 text-xs hover:border-[var(--signal)]"
        aria-expanded={open}
        aria-haspopup="listbox"
        aria-label={t("countriesAria")}
        onClick={() => setOpen((o) => !o)}
      >
        {t("countriesLabel")}: {label}
      </button>
      {open ? (
        <div
          className="absolute right-0 z-20 mt-1 max-h-64 min-w-[10rem] overflow-y-auto rounded-md border border-[var(--line)] bg-[var(--card)] p-2 shadow-sm"
          role="listbox"
          aria-multiselectable
        >
          <button
            type="button"
            className="mb-1 block w-full text-left text-[0.65rem] underline signal-text"
            onClick={() => {
              actions.setCountries([]);
              setOpen(false);
            }}
          >
            {t("countriesClear")}
          </button>
          {(options.length ? options : state.countries).map((code) => (
            <label
              key={code}
              className="flex cursor-pointer items-center gap-2 px-1 py-0.5 text-xs text-[var(--ink)]"
            >
              <input
                type="checkbox"
                checked={selected.has(code)}
                onChange={() => toggle(code)}
              />
              {code}
            </label>
          ))}
        </div>
      ) : null}
    </div>
  );
}

export const CountryFilter = {
  Provider: CountryFilterProvider,
  PrefsFallbackProvider: CountryFilterPrefsFallbackProvider,
  Control: CountryFilterControl,
};
