"use client";

import { usePathname } from "next/navigation";

const HIDDEN_ON = ["/login", "/register", "/forgot-password", "/reset-password"];

export function ConditionalPageBackground() {
  const pathname = usePathname();

  if (HIDDEN_ON.includes(pathname)) {
    return null;
  }

  return (
    <div
      className="fixed inset-0 z-[-1] pointer-events-none"
      style={{
        backgroundImage: "url('/page-bg.png')",
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundAttachment: "fixed",
        opacity: 0.35,
      }}
    />
  );
}