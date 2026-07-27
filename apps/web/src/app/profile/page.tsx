"use client";

import { useState, useEffect } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { getCurrentUser, updateProfile, changePassword } from "@/lib/api-client";
import { AuthGuard } from "@/components/auth-guard";

export default function ProfilePage() {
  const queryClient = useQueryClient();

  const { data: user } = useQuery({
    queryKey: ["currentUser"],
    queryFn: getCurrentUser,
  });

  const [fullName, setFullName] = useState("");
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [nameSaved, setNameSaved] = useState(false);
  const [passwordError, setPasswordError] = useState("");
  const [passwordSaved, setPasswordSaved] = useState(false);

  useEffect(() => {
    if (user?.full_name) setFullName(user.full_name);
  }, [user]);

  const nameMutation = useMutation({
    mutationFn: () => updateProfile({ full_name: fullName }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["currentUser"] });
      setNameSaved(true);
      setTimeout(() => setNameSaved(false), 2500);
    },
  });

  const passwordMutation = useMutation({
    mutationFn: () => changePassword({ current_password: currentPassword, new_password: newPassword }),
    onSuccess: () => {
      setPasswordSaved(true);
      setPasswordError("");
      setCurrentPassword("");
      setNewPassword("");
      setTimeout(() => setPasswordSaved(false), 2500);
    },
    onError: (err: any) => {
      setPasswordError(err?.response?.data?.detail || "Failed to change password.");
    },
  });

  return (
    <AuthGuard>
      <main className="page">
        <a href="/" className="link text-sm mb-4 inline-block">
          Back to jobs
        </a>

        <h1 className="h1 mb-6">Edit Profile</h1>

        <div className="card mb-6">
          <h2 className="h2 mb-3">Account Info</h2>
          <div className="text-sm space-y-1 text-muted">
            <div>Email: {user?.email}</div>
            <div>Account type: {user?.account_type}</div>
            {user?.company_name && <div>Company: {user.company_name}</div>}
          </div>
        </div>

        <div className="card mb-6">
          <h2 className="h2 mb-3">Display Name</h2>
          <input
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            placeholder="Your name"
            className="input mb-3"
          />
          <button
            onClick={() => nameMutation.mutate()}
            disabled={nameMutation.isPending}
            className="btn-primary"
          >
            {nameMutation.isPending ? "Saving..." : "Save Name"}
          </button>
          {nameSaved && <p className="text-sm status-success mt-2">Name updated.</p>}
        </div>

        <div className="card">
          <h2 className="h2 mb-3">Change Password</h2>
          <input
            type="password"
            value={currentPassword}
            onChange={(e) => setCurrentPassword(e.target.value)}
            placeholder="Current password"
            className="input mb-3"
          />
          <input
            type="password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            placeholder="New password"
            className="input mb-3"
          />

          {passwordError && <p className="text-sm status-danger mb-3">{passwordError}</p>}

          <button
            onClick={() => passwordMutation.mutate()}
            disabled={!currentPassword || !newPassword || passwordMutation.isPending}
            className="btn-primary"
          >
            {passwordMutation.isPending ? "Updating..." : "Change Password"}
          </button>
          {passwordSaved && <p className="text-sm status-success mt-2">Password changed.</p>}
        </div>
      </main>
    </AuthGuard>
  );
}