export {
  DashboardPrefsProvider,
  useDashboardPrefs,
} from "./ui/DashboardPrefsProvider";
export { PrefsPanel } from "./ui/PrefsPanel";
export {
  DEFAULT_PREFS,
  NAV_ITEMS,
  PREFS_STORAGE_KEY,
  applyNamedPreset,
  loadDashboardPrefs,
  parsePrefsLens,
  prefsFromDashboardSpec,
  saveDashboardPrefs,
  saveNamedPreset,
  type AppLocale,
  type DashboardPrefs,
  type DashboardLens,
  type NavKey,
  type ViewMode,
} from "./model/prefs";
