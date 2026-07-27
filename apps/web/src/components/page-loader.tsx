"use client";

import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";

export function PageLoader() {
  const pathname = usePathname();
  const [visible, setVisible] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    // Skip the loader on the very first mount (avoids double-flash on initial load)
    if (!mounted) {
      setMounted(true);
      return;
    }
    setVisible(true);
    const timer = setTimeout(() => setVisible(false), 500);
    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pathname]);

  if (!visible) return null;

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center"
      style={{ background: "var(--paper)" }}
    >
      <div className="flex flex-col items-center gap-3">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" className="animate-pulse">
          <circle cx="12" cy="12" r="9" stroke="var(--accent)" strokeWidth="1.5" />
          <circle cx="12" cy="12" r="5.5" stroke="var(--accent-soft)" strokeWidth="1.5" />
          <circle cx="12" cy="12" r="2" fill="var(--accent)" />
        </svg>
        <p className="text-sm font-medium" style={{ color: "var(--ink)" }}>
          Loading RecruitLens<span style={{ color: "var(--accent)" }}>AI</span>
        </p>
      </div>
    </div>
  );
}