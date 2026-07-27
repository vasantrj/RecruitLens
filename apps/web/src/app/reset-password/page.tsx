"use client";

import { Suspense, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useMutation } from "@tanstack/react-query";
import { resetPassword } from "@/lib/api-client";
import { AuthBrandingPanel } from "@/components/auth-branding-panel";

function ResetPasswordForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get("token") || "";

  const [newPassword, setNewPassword] = useState("");
  const [error, setError] = useState("");

  const mutation = useMutation({
    mutationFn: () => resetPassword({ token, new_password: newPassword }),
    onError: (err: any) => {
      setError(err?.response?.data?.detail || "Failed to reset password.");
    },
  });

  if (mutation.isSuccess) {
    return (
      <div className="card-holo">
        <p className="text-sm status-success mb-4">Password reset successfully.</p>
        <button onClick={() => router.push("/login")} className="btn-primary w-full">
          Go to Login
        </button>
      </div>
    );
  }

  return (
    <div className="card-holo">
      {!token && (
        <p className="text-sm status-danger mb-3">
          No reset token found. Use the link from your reset request.
        </p>
      )}

      <input
        type="password"
        placeholder="New password"
        value={newPassword}
        onChange={(e) => setNewPassword(e.target.value)}
        className="input mb-3"
      />

      {error && <p className="text-sm status-danger mb-3">{error}</p>}

      <button
        onClick={() => mutation.mutate()}
        disabled={!token || !newPassword || mutation.isPending}
        className="btn-primary w-full"
      >
        {mutation.isPending ? "Resetting..." : "Reset Password"}
      </button>
    </div>
  );
}

export default function ResetPasswordPage() {
  return (
    <div className="flex min-h-screen">
      <AuthBrandingPanel />

      <div
        className="w-full md:w-1/2 flex items-center justify-center p-8"
        style={{ background: "#e9edeb" }}
      >
        <div className="w-full max-w-sm">
          <h1 className="h1 mb-6" style={{ color: "#ffffff" }}>
            Set a new password
          </h1>
          <Suspense fallback={<p className="text-muted">Loading...</p>}>
            <ResetPasswordForm />
          </Suspense>
        </div>
      </div>
    </div>
  );
}