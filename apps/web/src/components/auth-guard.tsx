"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { getCurrentUser } from "@/lib/api-client";

const IDLE_TIMEOUT_MS = 5 * 60 * 1000;   // 5 minutes of inactivity
const WARNING_BEFORE_MS = 60 * 1000;      // show warning 1 minute before logout

const ACTIVITY_EVENTS = ["mousemove", "keydown", "click", "scroll", "touchstart"];

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [checked, setChecked] = useState(false);
  const [showWarning, setShowWarning] = useState(false);

  const warningTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const logoutTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const { data: user, isError, isFetched } = useQuery({
    queryKey: ["currentUser"],
    queryFn: getCurrentUser,
    retry: false,
  });

  const handleLogout = useCallback(() => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("account_type");
    router.push("/login");
  }, [router]);

  const resetIdleTimers = useCallback(() => {
    setShowWarning(false);
    if (warningTimer.current) clearTimeout(warningTimer.current);
    if (logoutTimer.current) clearTimeout(logoutTimer.current);

    warningTimer.current = setTimeout(() => {
      setShowWarning(true);
    }, IDLE_TIMEOUT_MS - WARNING_BEFORE_MS);

    logoutTimer.current = setTimeout(() => {
      handleLogout();
    }, IDLE_TIMEOUT_MS);
  }, [handleLogout]);

  useEffect(() => {
    const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
    if (!token) {
      router.push("/login");
      return;
    }
    if (isFetched) {
      if (isError) {
        router.push("/login");
      } else {
        setChecked(true);
      }
    }
  }, [isFetched, isError, router]);

  useEffect(() => {
    if (!checked) return;

    resetIdleTimers();

    ACTIVITY_EVENTS.forEach((event) => window.addEventListener(event, resetIdleTimers));

    return () => {
      ACTIVITY_EVENTS.forEach((event) => window.removeEventListener(event, resetIdleTimers));
      if (warningTimer.current) clearTimeout(warningTimer.current);
      if (logoutTimer.current) clearTimeout(logoutTimer.current);
    };
  }, [checked, resetIdleTimers]);

  if (!checked) {
    return (
      <main className="page">
        <p className="text-muted">Loading...</p>
      </main>
    );
  }

  return (
    <>
      {showWarning && (
        <div
          className="fixed top-4 right-4 z-50 rounded-lg border p-4 text-sm shadow-lg max-w-xs"
          style={{ background: "var(--paper-card)", borderColor: "var(--warning)" }}
        >
          <p className="status-warning font-medium mb-1">You've been inactive.</p>
          <p className="text-muted">You'll be logged out in about a minute unless you interact with the page.</p>
        </div>
      )}
      {children}
    </>
  );
}