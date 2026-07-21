"use client";

import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { createJob, createRoleOnlyJob, listJobs } from "@/lib/api-client";
import { FadeInStagger, FadeInItem } from "@/components/motion";
import { AuthGuard } from "@/components/auth-guard";

export default function HomePage() {
  const [mode, setMode] = useState<"jd" | "role">("jd");
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");

  const { data: jobs, refetch } = useQuery({
    queryKey: ["jobs"],
    queryFn: listJobs,
  });

  const jdMutation = useMutation({
    mutationFn: () => createJob({ title, description, is_role_only: false }),
    onSuccess: () => {
      setTitle("");
      setDescription("");
      refetch();
    },
  });

  const roleMutation = useMutation({
    mutationFn: () => createRoleOnlyJob(title),
    onSuccess: () => {
      setTitle("");
      refetch();
    },
  });

  const handleSubmit = () => {
    if (mode === "jd") jdMutation.mutate();
    else roleMutation.mutate();
  };

  const isLoading = jdMutation.isPending || roleMutation.isPending;

  return (
    <AuthGuard>
      <main className="page">
        <h1 className="h1 mb-6">RecruitLens</h1>

        <div className="card mb-8">
          <h2 className="h2 mb-4">Create a Job</h2>

          <div className="flex gap-2 mb-4">
            <button
              onClick={() => setMode("jd")}
              className={`btn-toggle ${mode === "jd" ? "btn-toggle-active" : "btn-toggle-inactive"}`}
            >
              Full Job Description
            </button>
            <button
              onClick={() => setMode("role")}
              className={`btn-toggle ${mode === "role" ? "btn-toggle-active" : "btn-toggle-inactive"}`}
            >
              Role Title Only
            </button>
          </div>

          <input
            type="text"
            placeholder={mode === "jd" ? "Job title (e.g. Data Science Intern)" : "Role title (e.g. Data Science Intern)"}
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="input mb-3"
          />

          {mode === "jd" && (
            <textarea
              placeholder="Paste the full job description here..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={6}
              className="input mb-3"
            />
          )}

          <button onClick={handleSubmit} disabled={!title || isLoading} className="btn-primary">
            {isLoading ? "Creating..." : "Create Job"}
          </button>
        </div>

        <div>
          <h2 className="h2 mb-4">Existing Jobs</h2>
          <FadeInStagger>
            <div className="space-y-2">
              {jobs?.map((job: any) => (
                <FadeInItem key={job.id}>
                  <Link href={`/jobs/${job.id}`}>
                    <div className="card card-interactive cursor-pointer">
                      <div className="font-medium">{job.title}</div>
                      <div className="text-sm text-muted">
                        {job.is_role_only === "true" ? "Role-only" : "Full JD"} · {job.id}
                      </div>
                    </div>
                  </Link>
                </FadeInItem>
              ))}
            </div>
          </FadeInStagger>
        </div>
      </main>
    </AuthGuard>
  );
}