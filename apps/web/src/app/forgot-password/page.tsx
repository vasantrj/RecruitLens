"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { forgotPassword } from "@/lib/api-client";
import { AuthBrandingPanel } from "@/components/auth-branding-panel";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");

  const mutation = useMutation({
    mutationFn: () => forgotPassword(email),
    onError: (err: any) => {
      setError(err?.response?.data?.detail || "Something went wrong. Please try again.");
    },
    onSuccess: () => {
      setError("");
    },
  });

  return (
    <div className="flex min-h-screen">
      <AuthBrandingPanel />

      <div
        className="w-full md:w-1/2 flex items-center justify-center p-8"
        style={{ background: "#e9edeb" }}
      >
        <div className="w-full max-w-sm">
          <h1 className="h1 mb-6" style={{ color: "#ffffff" }}>
            Reset your password
          </h1>

          <div className="card-holo">
            <p className="text-sm text-muted mb-4">
              Enter your account email. We&apos;ll generate a reset link for you.
            </p>

            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => {
                setEmail(e.target.value);
                setError("");
              }}
              className="input mb-3"
            />

            {error && <p className="text-sm status-danger mb-3">{error}</p>}

            <button
              onClick={() => mutation.mutate()}
              disabled={!email || mutation.isPending}
              className="btn-primary w-full"
            >
              {mutation.isPending ? "Sending..." : "Send Reset Link"}
            </button>

            {mutation.isSuccess && (
              <div className="card-alt mt-4 text-sm">
                <p className="status-success mb-2">Reset link generated.</p>
                {mutation.data?.dev_reset_token && (
                  <>
                    <p className="text-xs text-faint mb-2">
                      (Demo mode — normally this would be emailed. Use this link now:)
                    </p>
                    <a
                      href={`/reset-password?token=${mutation.data.dev_reset_token}`}
                      className="link break-all"
                    >
                      Reset your password
                    </a>
                  </>
                )}
              </div>
            )}

            <p className="text-sm text-muted mt-4">
              <a href="/login" className="link">
                Back to login
              </a>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}