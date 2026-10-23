"use client";

import { useTranslations } from "next-intl";
import { useState } from "react";
import {
  DEFAULT_PREFS,
  NAV_ITEMS,
  parsePrefsLens,
  type AppLocale,
  type DashboardPrefs,
} from "../model/prefs";
import { useDashboardPrefs } from "./DashboardPrefsProvider";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function mergeServerPrefs(local: DashboardPrefs, remote: unknown): DashboardPrefs {
  if (!remote || typeof remote !== "object") return local;
  const r = remote as Partial<DashboardPrefs>;
  return {
    ...DEFAULT_PREFS,
    ...local,
    ...r,
    presets: { ...local.presets, ...(r.presets ?? {}) },
    locale: r.locale === "it" || r.locale === "en" ? r.locale : local.locale,
    view_mode:
      r.view_mode === "trends_only"
        ? "trends_only"
        : r.view_mode === "guided"
          ? "guided"
          : local.view_mode,
    period_days: Number(r.period_days) > 0 ? Number(r.period_days) : local.period_days,
    lens: r.lens !== undefined ? parsePrefsLens(r.lens) : local.lens,
    visible_widgets: Array.isArray(r.visible_widgets) ? r.visible_widgets : local.visible_widgets,
    focus_technologies: Array.isArray(r.focus_technologies)
      ? r.focus_technologies
      : local.focus_technologies,
    focus_countries: Array.isArray(r.focus_countries) ? r.focus_countries : local.focus_countries,
    nav_hidden: Array.isArray(r.nav_hidden) ? r.nav_hidden : local.nav_hidden,
  };
}

export function PrefsPanel({ onClose }: { onClose: () => void }) {
  const t = useTranslations("prefs");
  const tNav = useTranslations("nav");
  const tCommon = useTranslations("common");
  const { prefs, setPrefs, setPeriodDays, setLocale, savePreset, applyPreset } =
    useDashboardPrefs();
  const [presetName, setPresetName] = useState(() => t("defaultPresetName"));
  const [techInput, setTechInput] = useState(prefs.focus_technologies.join(", "));
  const [countryInput, setCountryInput] = useState(prefs.focus_countries.join(", "));
  const [syncMsg, setSyncMsg] = useState("");
  const [syncing, setSyncing] = useState<"pull" | "push" | null>(null);

  const toggleNav = (href: string) => {
    setPrefs((p) => {
      const set = new Set(p.nav_hidden);
      if (set.has(href)) set.delete(href);
      else set.add(href);
      return { ...p, nav_hidden: [...set] };
    });
  };

  const applyFilters = () => {
    setPrefs((p) => ({
      ...p,
      focus_technologies: techInput
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean),
      focus_countries: countryInput
        .split(",")
        .map((s) => s.trim().toUpperCase())
        .filter(Boolean),
    }));
  };

  const pullServer = async () => {
    setSyncing("pull");
    setSyncMsg("");
    try {
      const res = await fetch(`${API_URL}/api/v1/profile/dashboard-prefs`, { cache: "no-store" });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || res.statusText);
      const next = mergeServerPrefs(prefs, data.prefs);
      setPrefs(() => next);
      setTechInput(next.focus_technologies.join(", "));
      setCountryInput(next.focus_countries.join(", "));
      setSyncMsg(
        Object.keys(data.prefs || {}).length ? t("loadedFromProfile") : t("noServerPrefs"),
      );
    } catch (e) {
      setSyncMsg(e instanceof Error ? e.message : t("pullFailed"));
    } finally {
      setSyncing(null);
    }
  };

  const pushServer = async () => {
    const next: DashboardPrefs = {
      ...prefs,
      focus_technologies: techInput
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean),
      focus_countries: countryInput
        .split(",")
        .map((s) => s.trim().toUpperCase())
        .filter(Boolean),
    };
    setPrefs(() => next);
    setSyncing("push");
    setSyncMsg("");
    try {
      const res = await fetch(`${API_URL}/api/v1/profile/dashboard-prefs`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prefs: next }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || res.statusText);
      setSyncMsg(t("savedToProfile"));
    } catch (e) {
      setSyncMsg(e instanceof Error ? e.message : t("pushFailed"));
    } finally {
      setSyncing(null);
    }
  };

  return (
    <section className="card mt-2 space-y-3 p-4 text-sm">
      <div className="flex items-center justify-between">
        <h2 className="font-semibold">{t("title")}</h2>
        <button type="button" className="text-xs opacity-70" onClick={onClose}>
          {tCommon("close")}
        </button>
      </div>

      <label className="flex flex-wrap items-center gap-2">
        <span className="opacity-70">{t("localeLabel")}</span>
        <select
          className="rounded border border-[var(--line)] bg-transparent px-2 py-1"
          value={prefs.locale}
          onChange={(e) => setLocale(e.target.value as AppLocale)}
        >
          <option value="en">{tNav("localeEn")}</option>
          <option value="it">{tNav("localeIt")}</option>
        </select>
      </label>
      <p className="text-xs opacity-60">{t("localeHint")}</p>

      <label className="flex flex-wrap items-center gap-2">
        <span className="opacity-70">{t("periodDays")}</span>
        <input
          type="number"
          min={1}
          max={3660}
          className="w-24 rounded border border-[var(--line)] bg-transparent px-2 py-1"
          value={prefs.period_days}
          onChange={(e) => setPeriodDays(Number(e.target.value) || 30)}
        />
      </label>

      <label className="block space-y-1">
        <span className="opacity-70">{t("focusTech")}</span>
        <input
          className="w-full rounded border border-[var(--line)] bg-transparent px-2 py-1"
          value={techInput}
          onChange={(e) => setTechInput(e.target.value)}
          onBlur={applyFilters}
        />
      </label>

      <label className="block space-y-1">
        <span className="opacity-70">{t("focusCountries")}</span>
        <input
          className="w-full rounded border border-[var(--line)] bg-transparent px-2 py-1"
          value={countryInput}
          onChange={(e) => setCountryInput(e.target.value)}
          onBlur={applyFilters}
        />
      </label>

      <div>
        <p className="mb-1 opacity-70">{t("hideNav")}</p>
        <div className="flex flex-wrap gap-2">
          {NAV_ITEMS.map((item) => (
            <label key={item.href} className="inline-flex items-center gap-1 text-xs">
              <input
                type="checkbox"
                checked={prefs.nav_hidden.includes(item.href)}
                onChange={() => toggleNav(item.href)}
              />
              {tNav(item.key)}
            </label>
          ))}
        </div>
      </div>

      <div className="flex flex-wrap items-end gap-2 border-t border-[var(--line)] pt-3">
        <label className="space-y-1">
          <span className="opacity-70">{t("presetName")}</span>
          <input
            className="block rounded border border-[var(--line)] bg-transparent px-2 py-1"
            value={presetName}
            onChange={(e) => setPresetName(e.target.value)}
          />
        </label>
        <button
          type="button"
          className="rounded border border-[var(--line)] px-3 py-1.5 hover:border-[var(--signal)]"
          onClick={() => {
            applyFilters();
            savePreset(presetName);
          }}
        >
          {t("savePreset")}
        </button>
        {Object.keys(prefs.presets).map((name) => (
          <button
            key={name}
            type="button"
            className="rounded border border-[color-mix(in_srgb,var(--signal)_40%,transparent)] px-3 py-1.5 signal-text"
            onClick={() => applyPreset(name)}
          >
            {t("loadPreset", { name })}
          </button>
        ))}
      </div>

      <div className="flex flex-wrap items-center gap-2 border-t border-[var(--line)] pt-3">
        <button
          type="button"
          disabled={syncing !== null}
          className="rounded border border-[var(--line)] px-3 py-1.5 hover:border-[var(--signal)] disabled:opacity-50"
          onClick={() => void pullServer()}
        >
          {syncing === "pull" ? t("loadingProfile") : t("loadFromProfile")}
        </button>
        <button
          type="button"
          disabled={syncing !== null}
          className="rounded border border-[var(--line)] px-3 py-1.5 hover:border-[var(--signal)] disabled:opacity-50"
          onClick={() => void pushServer()}
        >
          {syncing === "push" ? t("savingProfile") : t("saveToProfile")}
        </button>
        {syncMsg ? <span className="text-xs opacity-70">{syncMsg}</span> : null}
      </div>
    </section>
  );
}
