"use client";

import { useCallback, useEffect, useState } from "react";
import {
  DEFAULT_LOCAL_PROFILE,
  loadLocalProfile,
  saveLocalProfile,
  type LocalUserProfile,
} from "./model";

/**
 * Reactive localStorage profile (ADR-009). Single source for My Stack skills/certs.
 */
export function useLocalProfile() {
  const [profile, setProfileState] = useState<LocalUserProfile>(DEFAULT_LOCAL_PROFILE);
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    setProfileState(loadLocalProfile());
    setHydrated(true);
  }, []);

  const setProfile = useCallback((next: LocalUserProfile | ((prev: LocalUserProfile) => LocalUserProfile)) => {
    setProfileState((prev) => {
      const resolved = typeof next === "function" ? next(prev) : next;
      saveLocalProfile(resolved);
      return resolved;
    });
  }, []);

  const refresh = useCallback(() => {
    setProfileState(loadLocalProfile());
  }, []);

  return { profile, setProfile, hydrated, refresh };
}
