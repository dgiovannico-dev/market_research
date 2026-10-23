"use client";

import {
  createContext,
  use,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import {
  DEFAULT_PREFS,
  applyNamedPreset,
  loadDashboardPrefs,
  prefsFromDashboardSpec,
  saveDashboardPrefs,
  saveNamedPreset,
  type AppLocale,
  type DashboardPrefs,
  type ViewMode,
} from "../model/prefs";

type PrefsContextValue = {
  prefs: DashboardPrefs;
  hydrated: boolean;
  setPrefs: (updater: (prev: DashboardPrefs) => DashboardPrefs) => void;
  setViewMode: (mode: ViewMode) => void;
  setPeriodDays: (days: number) => void;
  setLocale: (locale: AppLocale) => void;
  applyPreset: (name: string) => void;
  savePreset: (name: string) => void;
  applyDashboardSpec: (spec: Parameters<typeof prefsFromDashboardSpec>[1]) => void;
};

const PrefsContext = createContext<PrefsContextValue | null>(null);

export function DashboardPrefsProvider({ children }: { children: ReactNode }) {
  const [prefs, setPrefsState] = useState<DashboardPrefs>(DEFAULT_PREFS);
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    setPrefsState(loadDashboardPrefs());
    setHydrated(true);
  }, []);

  useEffect(() => {
    if (!hydrated) return;
    saveDashboardPrefs(prefs);
  }, [prefs, hydrated]);

  const setPrefs = (updater: (prev: DashboardPrefs) => DashboardPrefs) => {
    setPrefsState((prev) => updater(prev));
  };

  const value: PrefsContextValue = {
    prefs,
    hydrated,
    setPrefs,
    setViewMode: (mode) => setPrefs((p) => ({ ...p, view_mode: mode })),
    setPeriodDays: (days) =>
      setPrefs((p) => ({ ...p, period_days: Math.max(1, Math.min(days, 3660)) })),
    setLocale: (locale) => setPrefs((p) => ({ ...p, locale })),
    applyPreset: (name) => setPrefs((p) => applyNamedPreset(p, name)),
    savePreset: (name) => setPrefs((p) => saveNamedPreset(p, name)),
    applyDashboardSpec: (spec) => setPrefs((p) => prefsFromDashboardSpec(p, spec)),
  };

  return <PrefsContext.Provider value={value}>{children}</PrefsContext.Provider>;
}

export function useDashboardPrefs(): PrefsContextValue {
  const ctx = use(PrefsContext);
  if (!ctx) {
    throw new Error("useDashboardPrefs must be used within DashboardPrefsProvider");
  }
  return ctx;
}
