"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useMutation } from "@tanstack/react-query";
import { loginUser } from "@/lib/api-client";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const loginMutation = useMutation({
    mutationFn: () => loginUser({ email, password }),
    onSuccess: (data) => {
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("account_type", data.account_type);
      router.push("/");
    },
    onError: () => {
      setError("Invalid email or password.");
    },
  });

  return (
    <main className="page">
      <h1 className="h1 mb-6">Log in to RecruitLens</h1>

      <div className="card max-w-sm">
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="input mb-3"
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="input mb-3"
        />

        {error && <p className="text-sm status-danger mb-3">{error}</p>}

        <button
          onClick={() => loginMutation.mutate()}
          disabled={!email || !password || loginMutation.isPending}
          className="btn-primary w-full"
        >
          {loginMutation.isPending ? "Logging in..." : "Log In"}
        </button>

        <p className="text-sm text-muted mt-4">
          Don&apos;t have an account?{" "}
          <a href="/register" className="link">
            Register
          </a>
        </p>
      </div>
    </main>
  );
}