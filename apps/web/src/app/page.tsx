"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { createJob, createRoleOnlyJob, listJobs, archiveJob } from "@/lib/api-client";
import { FadeInStagger, FadeInItem } from "@/components/motion";
import { AuthGuard } from "@/components/auth-guard";
import { useToast } from "@/components/toast";

export default function HomePage() {
  const queryClient = useQueryClient();
  const { showToast } = useToast();
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

  const archiveMutation = useMutation({
    mutationFn: (jobId: string) => archiveJob(jobId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["jobs"] });
      showToast("Job archived.");
    },
  });

  const handleSubmit = () => {
    if (mode === "jd") jdMutation.mutate();
    else roleMutation.mutate();
  };

  const handleShare = (jobId: string) => {
    const url = `${window.location.origin}/jobs/${jobId}`;
    navigator.clipboard.writeText(url);
    showToast("Job link copied to clipboard.");
  };

  const isLoading = jdMutation.isPending || roleMutation.isPending;
  const hasJobs = jobs && jobs.length > 0;

  const createJobCard = (
    <div className="card">
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
  );

  return (
    <AuthGuard>
      <main className="page-wide">
        <h1 className="h1 mb-6">RecruitLens</h1>

        {!hasJobs && (
          <div className="max-w-xl mx-auto">{createJobCard}</div>
        )}

        {hasJobs && (
          <div className="grid md:grid-cols-2 gap-6">
            <div>{createJobCard}</div>

            <div>
              <h2 className="h2 mb-4">Existing Jobs</h2>
              <FadeInStagger>
                <div className="space-y-2">
                  {jobs?.map((job: any) => {
                    let hasRequirements = false;
                    try {
                      hasRequirements = !!job.parsed_requirements && job.parsed_requirements !== "null";
                    } catch {}

                    return (
                      <FadeInItem key={job.id}>
                        <div className="card">
                          <Link href={`/jobs/${job.id}`}>
                            <div className="flex items-center gap-2 mb-1">
                              <div className="font-medium">{job.title}</div>
                              <span className={`badge ${hasRequirements ? "badge-success" : "badge-warning"}`}>
                                {hasRequirements ? "Active" : "Draft"}
                              </span>
                            </div>
                            <div className="text-sm text-muted mb-3">
                              {job.is_role_only === "true" ? "Role-only" : "Full JD"} · {job.id}
                            </div>
                          </Link>

                          <div className="flex gap-4 text-sm pt-2 border-t" style={{ borderColor: "var(--paper-border)" }}>
                            <Link href={`/jobs/${job.id}/edit`} className="link-plain hover:underline">
  Edit
</Link>
                            <button
                              onClick={() => handleShare(job.id)}
                              className="link-plain hover:underline"
                            >
                              Share
                            </button>
                            <button
                              onClick={() => archiveMutation.mutate(job.id)}
                              disabled={archiveMutation.isPending}
                              className="hover:underline"
                              style={{ color: "var(--danger)" }}
                            >
                              Archive
                            </button>
                          </div>
                        </div>
                      </FadeInItem>
                    );
                  })}
                </div>
              </FadeInStagger>
            </div>
          </div>
        )}
      </main>
    </AuthGuard>
  );
}