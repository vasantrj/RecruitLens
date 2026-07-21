"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { getCurrentUser } from "@/lib/api-client";

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [checked, setChecked] = useState(false);

  const { data: user, isError, isFetched } = useQuery({
    queryKey: ["currentUser"],
    queryFn: getCurrentUser,
    retry: false,
  });

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

  if (!checked) {
    return (
      <main className="page">
        <p className="text-muted">Loading...</p>
      </main>
    );
  }

  return <>{children}</>;
}