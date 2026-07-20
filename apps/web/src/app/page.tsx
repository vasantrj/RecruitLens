"use client";

import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { createJob, createRoleOnlyJob, listJobs } from "@/lib/api-client";

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
    <main className="max-w-2xl mx-auto p-8">
      <h1 className="text-2xl font-semibold mb-6">RecruitLens</h1>

      <div className="bg-gray-900 rounded-lg p-6 mb-8 border border-gray-800">
        <h2 className="text-lg font-medium mb-4">Create a Job</h2>

        <div className="flex gap-2 mb-4">
          <button
            onClick={() => setMode("jd")}
            className={`px-4 py-2 rounded ${mode === "jd" ? "bg-blue-600" : "bg-gray-800"}`}
          >
            Full Job Description
          </button>
          <button
            onClick={() => setMode("role")}
            className={`px-4 py-2 rounded ${mode === "role" ? "bg-blue-600" : "bg-gray-800"}`}
          >
            Role Title Only
          </button>
        </div>

        <input
          type="text"
          placeholder={mode === "jd" ? "Job title (e.g. Data Science Intern)" : "Role title (e.g. Data Science Intern)"}
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="w-full p-2 rounded bg-gray-800 border border-gray-700 mb-3"
        />

        {mode === "jd" && (
          <textarea
            placeholder="Paste the full job description here..."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={6}
            className="w-full p-2 rounded bg-gray-800 border border-gray-700 mb-3"
          />
        )}

        <button
          onClick={handleSubmit}
          disabled={!title || isLoading}
          className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 px-4 py-2 rounded"
        >
          {isLoading ? "Creating..." : "Create Job"}
        </button>
      </div>

      <div>
        <h2 className="text-lg font-medium mb-4">Existing Jobs</h2>
        <div className="space-y-2">
          {jobs?.map((job: any) => (
            <Link key={job.id} href={`/jobs/${job.id}`}>
              <div className="bg-gray-900 border border-gray-800 rounded p-4 hover:border-blue-600 cursor-pointer transition-colors">
                <div className="font-medium">{job.title}</div>
                <div className="text-sm text-gray-400">
                  {job.is_role_only === "true" ? "Role-only" : "Full JD"} · {job.id}
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </main>
  );
}