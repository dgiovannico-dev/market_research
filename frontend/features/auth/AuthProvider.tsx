"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { oidcEnabled } from "./config";
import { beginLogin, logout as kcLogout } from "./keycloak";
import {
  getAccessToken,
  isAdminFromToken,
  rolesFromAccessToken,
} from "./tokenStore";

type AuthState = {
  enabled: boolean;
  authenticated: boolean;
  isAdmin: boolean;
  roles: string[];
  login: () => Promise<void>;
  logout: () => Promise<void>;
  refresh: () => void;
};

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const enabled = oidcEnabled();
  const [token, setToken] = useState<string | null>(null);

  const refresh = useCallback(() => {
    setToken(getAccessToken());
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const value = useMemo<AuthState>(
    () => ({
      enabled,
      authenticated: Boolean(token),
      isAdmin: isAdminFromToken(token),
      roles: rolesFromAccessToken(token),
      login: beginLogin,
      logout: kcLogout,
      refresh,
    }),
    [enabled, token, refresh],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    return {
      enabled: false,
      authenticated: false,
      isAdmin: false,
      roles: [],
      login: async () => undefined,
      logout: async () => undefined,
      refresh: () => undefined,
    };
  }
  return ctx;
}
