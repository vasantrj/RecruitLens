"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useMutation } from "@tanstack/react-query";
import { registerUser } from "@/lib/api-client";

export default function RegisterPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [accountType, setAccountType] = useState<"personal" | "company">("personal");
  const [companyName, setCompanyName] = useState("");
  const [error, setError] = useState("");

  const registerMutation = useMutation({
    mutationFn: () =>
      registerUser({
        email,
        password,
        account_type: accountType,
        company_name: accountType === "company" ? companyName : undefined,
      }),
    onSuccess: (data) => {
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("account_type", data.account_type);
      router.push("/");
    },
    onError: (err: any) => {
      setError(err?.response?.data?.detail || "Registration failed.");
    },
  });

  return (
    <main className="page">
      <h1 className="h1 mb-6">Create your RecruitLens account</h1>

      <div className="card max-w-sm">
        <div className="flex gap-2 mb-4">
          <button
            onClick={() => setAccountType("personal")}
            className={`btn-toggle ${accountType === "personal" ? "btn-toggle-active" : "btn-toggle-inactive"}`}
          >
            Personal
          </button>
          <button
            onClick={() => setAccountType("company")}
            className={`btn-toggle ${accountType === "company" ? "btn-toggle-active" : "btn-toggle-inactive"}`}
          >
            Company
          </button>
        </div>

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

        {accountType === "company" && (
          <input
            type="text"
            placeholder="Company name"
            value={companyName}
            onChange={(e) => setCompanyName(e.target.value)}
            className="input mb-3"
          />
        )}

        {error && <p className="text-sm status-danger mb-3">{error}</p>}

        <button
          onClick={() => registerMutation.mutate()}
          disabled={!email || !password || registerMutation.isPending}
          className="btn-primary w-full"
        >
          {registerMutation.isPending ? "Creating account..." : "Create Account"}
        </button>

        <p className="text-sm text-muted mt-4">
          Already have an account?{" "}
          <a href="/login" className="link">
            Log in
          </a>
        </p>
      </div>
    </main>
  );
}