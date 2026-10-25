"use client";

import { useEffect, useState } from "react";
import { finishLogin } from "@/features/auth/keycloak";

export default function AuthCallbackPage() {
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const code = params.get("code");
    const err = params.get("error");
    if (err) {
      setError(err);
      return;
    }
    if (!code) {
      setError("missing_code");
      return;
    }
    finishLogin(code)
      .then(() => {
        window.location.replace("/");
      })
      .catch((e: unknown) => {
        setError(e instanceof Error ? e.message : "login_failed");
      });
  }, []);

  if (error) {
    return (
      <main className="mx-auto max-w-lg p-8">
        <h1 className="text-lg font-semibold">Sign-in failed</h1>
        <p className="mt-2 text-sm text-neutral-600">{error}</p>
      </main>
    );
  }
  return (
    <main className="mx-auto max-w-lg p-8">
      <p className="text-sm text-neutral-600">Completing sign-in…</p>
    </main>
  );
}
