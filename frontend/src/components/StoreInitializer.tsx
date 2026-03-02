"use client";

import { useEffect, useRef } from "react";
import { useSession } from "next-auth/react";
import { useZipsaStore } from "@/store/zipsa";
import { getZipsaToken } from "@/lib/api";

export function StoreInitializer() {
  const { status } = useSession();
  const initialized = useRef(false);
  const { loadProfile, loadSessions } = useZipsaStore();

  useEffect(() => {
    if (status !== "authenticated") return;
    if (initialized.current) return;
    initialized.current = true;

    const token = getZipsaToken();
    if (!token) return;

    loadProfile(token).catch(() => {});
    loadSessions(token).catch(() => {});
  }, [status, loadProfile, loadSessions]);

  return null;
}
