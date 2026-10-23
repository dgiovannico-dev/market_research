import { localeFromBrowserTag, type AppLocale } from "@/i18n/routing";
import type { DashboardLens } from "@/shared/api";
import { NAV_ITEMS, type NavKey } from "@/lib/navZones";

export type ViewMode = "guided" | "trends_only";
export type { AppLocale, DashboardLens };
export type { NavKey };
export { NAV_ITEMS };

export type DashboardPrefs = {
  view_mode: ViewMode;
  period_days: number;
  /** Sticky analytics lens. URL `?lens=` wins when present; else hydrate from here. */
  lens: DashboardLens;
  locale: AppLocale;
  visible_widgets: string[];
  focus_technologies: string[];
  focus_countries: string[];
  nav_hidden: string[];
  presets: Record<string, Omit<DashboardPrefs, "presets">>;
};

export const PREFS_STORAGE_KEY = "fmi:dashboardPrefs:v2";
const LEGACY_PREFS_STORAGE_KEY = "fmi:dashboardPrefs:v1";

export const DEFAULT_PREFS: DashboardPrefs = {
  view_mode: "guided",
  period_days: 30,
  lens: "market",
  locale: "en",
  visible_widgets: [],
  focus_technologies: [],
  focus_countries: [],
  nav_hidden: [],
  presets: {},
};

function parseLocale(value: unknown, fallback: AppLocale): AppLocale {
  return value === "it" || value === "en" ? value : fallback;
}

export function parsePrefsLens(value: unknown): DashboardLens {
  return value === "focus" || value === "compare" || value === "market" ? value : "market";
}

function normalizePrefs(
  parsed: Partial<DashboardPrefs>,
  fallbackLocale: AppLocale,
): DashboardPrefs {
  return {
    ...DEFAULT_PREFS,
    ...parsed,
    locale: parseLocale(parsed.locale, fallbackLocale),
    presets: parsed.presets ?? {},
    view_mode: parsed.view_mode === "trends_only" ? "trends_only" : "guided",
    period_days: Number(parsed.period_days) > 0 ? Number(parsed.period_days) : 30,
    lens: parsePrefsLens(parsed.lens),
    visible_widgets: Array.isArray(parsed.visible_widgets) ? parsed.visible_widgets : [],
    focus_technologies: Array.isArray(parsed.focus_technologies)
      ? parsed.focus_technologies
      : [],
    focus_countries: Array.isArray(parsed.focus_countries) ? parsed.focus_countries : [],
    nav_hidden: Array.isArray(parsed.nav_hidden) ? parsed.nav_hidden : [],
  };
}

function browserDefaultLocale(): AppLocale {
  // Prefer html lang already negotiated by middleware on first visit.
  if (typeof document !== "undefined") {
    const lang = document.documentElement.lang;
    if (lang === "it" || lang === "en") return lang;
  }
  if (typeof navigator === "undefined") return "en";
  return localeFromBrowserTag(navigator.language || navigator.languages?.[0]);
}

function stripPresets(p: DashboardPrefs): Omit<DashboardPrefs, "presets"> {
  const { presets: _p, ...rest } = p;
  return rest;
}

export function loadDashboardPrefs(): DashboardPrefs {
  if (typeof window === "undefined") return { ...DEFAULT_PREFS, presets: {} };
  const fallbackLocale = browserDefaultLocale();
  try {
    const raw =
      localStorage.getItem(PREFS_STORAGE_KEY) ??
      localStorage.getItem(LEGACY_PREFS_STORAGE_KEY);
    if (!raw) {
      return normalizePrefs({}, fallbackLocale);
    }
    const parsed = JSON.parse(raw) as Partial<DashboardPrefs>;
    const prefs = normalizePrefs(parsed, fallbackLocale);
    // Migrate v1 → v2 on first read after upgrade.
    if (!localStorage.getItem(PREFS_STORAGE_KEY)) {
      saveDashboardPrefs(prefs);
    }
    return prefs;
  } catch {
    return normalizePrefs({}, fallbackLocale);
  }
}

export function saveDashboardPrefs(prefs: DashboardPrefs): void {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem(PREFS_STORAGE_KEY, JSON.stringify(prefs));
  } catch {
    // private mode / quota — soft-fail
  }
}

/** Apply MCP / API DashboardSpec fields onto prefs (presentation only). */
export function prefsFromDashboardSpec(
  current: DashboardPrefs,
  spec: {
    title?: string;
    period_days?: number;
    view_mode?: ViewMode;
    filters?: {
      technologies?: string[];
      countries?: string[];
      source_keys?: string[];
    };
  },
): DashboardPrefs {
  return {
    ...current,
    period_days: spec.period_days && spec.period_days > 0 ? spec.period_days : current.period_days,
    view_mode:
      spec.view_mode === "trends_only"
        ? "trends_only"
        : spec.view_mode === "guided"
          ? "guided"
          : current.view_mode,
    focus_technologies: spec.filters?.technologies?.length
      ? [...spec.filters.technologies]
      : current.focus_technologies,
    focus_countries: spec.filters?.countries?.length
      ? [...spec.filters.countries]
      : current.focus_countries,
  };
}

export function saveNamedPreset(prefs: DashboardPrefs, name: string): DashboardPrefs {
  const key = name.trim() || "preset";
  return {
    ...prefs,
    presets: {
      ...prefs.presets,
      [key]: stripPresets(prefs),
    },
  };
}

export function applyNamedPreset(prefs: DashboardPrefs, name: string): DashboardPrefs {
  const snap = prefs.presets[name];
  if (!snap) return prefs;
  return {
    ...DEFAULT_PREFS,
    ...snap,
    locale: parseLocale(snap.locale, prefs.locale),
    lens: parsePrefsLens(snap.lens),
    view_mode: snap.view_mode === "trends_only" ? "trends_only" : "guided",
    period_days: Number(snap.period_days) > 0 ? Number(snap.period_days) : DEFAULT_PREFS.period_days,
    presets: prefs.presets,
  };
}
