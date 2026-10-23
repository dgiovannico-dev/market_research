"use client";

import { Suspense, type ReactNode } from "react";
import { CountryFilter } from "./CountryFilter";

/** Suspense for useSearchParams inside CountryFilter.Provider. */
export function CountryFilterBoundary({ children }: { children: ReactNode }) {
  return (
    <Suspense
      fallback={
        <CountryFilter.PrefsFallbackProvider>
          {children}
        </CountryFilter.PrefsFallbackProvider>
      }
    >
      <CountryFilter.Provider>{children}</CountryFilter.Provider>
    </Suspense>
  );
}
