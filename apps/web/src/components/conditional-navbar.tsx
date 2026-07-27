"use client";

import { usePathname } from "next/navigation";
import { Navbar } from "@/components/navbar";

const HIDDEN_ON = ["/login", "/register", "/forgot-password", "/reset-password"];

export function ConditionalNavbar() {
  const pathname = usePathname();

  if (HIDDEN_ON.includes(pathname)) {
    return null;
  }

  return <Navbar />;
}