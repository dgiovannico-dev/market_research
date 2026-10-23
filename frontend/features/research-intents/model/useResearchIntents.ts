"use client";

import { useCallback, useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { ApiRequestError } from "@/shared/api";
import {
  researchApi,
  type ResearchIntent,
  type ResearchIntentCreate,
  type ResearchIntentKind,
  type ResearchIntentPatch,
} from "@/entities/research-intent";

export type ResearchLoadState =
  | { phase: "loading" }
  | { phase: "not_ready" }
  | { phase: "error"; message: string }
  | { phase: "ready"; items: ResearchIntent[] };

function isNotReady(err: unknown): boolean {
  return err instanceof ApiRequestError && (err.status === 404 || err.status === 501);
}

export function useResearchIntents(kind: ResearchIntentKind) {
  const t = useTranslations("research");
  const [state, setState] = useState<ResearchLoadState>({ phase: "loading" });
  const [actionError, setActionError] = useState<string | null>(null);
  const [busyIds, setBusyIds] = useState<Set<number>>(() => new Set());

  const markBusy = (id: number, busy: boolean) => {
    setBusyIds((prev) => {
      const next = new Set(prev);
      if (busy) next.add(id);
      else next.delete(id);
      return next;
    });
  };

  const reload = useCallback(async () => {
    setState({ phase: "loading" });
    setActionError(null);
    try {
      const data = await researchApi.list(kind);
      setState({ phase: "ready", items: data.items });
    } catch (err) {
      if (isNotReady(err)) {
        setState({ phase: "not_ready" });
        return;
      }
      setState({
        phase: "error",
        message: err instanceof Error ? err.message : t("loadIntentsFailed"),
      });
    }
  }, [kind, t]);

  useEffect(() => {
    void reload();
  }, [reload]);

  const patch = async (id: number, body: ResearchIntentPatch) => {
    setActionError(null);
    markBusy(id, true);
    try {
      const updated = await researchApi.patch(id, body);
      setState((prev) =>
        prev.phase === "ready"
          ? { phase: "ready", items: prev.items.map((it) => (it.id === id ? updated : it)) }
          : prev,
      );
      return updated;
    } catch (err) {
      if (isNotReady(err)) {
        setState({ phase: "not_ready" });
        return null;
      }
      setActionError(err instanceof Error ? err.message : t("updateFailed"));
      return null;
    } finally {
      markBusy(id, false);
    }
  };

  const sync = async (id: number) => {
    setActionError(null);
    markBusy(id, true);
    try {
      await researchApi.sync(id);
      return true;
    } catch (err) {
      if (isNotReady(err)) {
        setState({ phase: "not_ready" });
        return false;
      }
      setActionError(err instanceof Error ? err.message : t("syncFailed"));
      return false;
    } finally {
      markBusy(id, false);
    }
  };

  const create = async (body: Omit<ResearchIntentCreate, "kind">) => {
    setActionError(null);
    try {
      const created = await researchApi.create({ ...body, kind });
      setState((prev) =>
        prev.phase === "ready"
          ? { phase: "ready", items: [...prev.items, created] }
          : { phase: "ready", items: [created] },
      );
      return created;
    } catch (err) {
      if (isNotReady(err)) {
        setState({ phase: "not_ready" });
        return null;
      }
      setActionError(err instanceof Error ? err.message : t("createFailed"));
      return null;
    }
  };

  return { state, actionError, busyIds, reload, patch, sync, create };
}
