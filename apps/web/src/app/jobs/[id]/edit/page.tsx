"use client";

import { useState, useEffect } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import { getJob, updateJob } from "@/lib/api-client";
import { AuthGuard } from "@/components/auth-guard";
import { useToast } from "@/components/toast";

export default function EditJobPage() {
  const params = useParams();
  const router = useRouter();
  const jobId = params.id as string;
  const { showToast } = useToast();

  const { data: job } = useQuery({
    queryKey: ["job", jobId],
    queryFn: () => getJob(jobId),
  });

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");

  useEffect(() => {
    if (job) {
      setTitle(job.title || "");
      setDescription(job.description || "");
    }
  }, [job]);

  const mutation = useMutation({
    mutationFn: () => updateJob(jobId, { title, description }),
    onSuccess: () => {
      showToast("Job updated successfully.");
      router.push(`/jobs/${jobId}`);
    },
  });

  return (
    <AuthGuard>
      <main className="page">
        <a href={`/jobs/${jobId}`} className="link text-sm mb-4 inline-block">
          Back to job
        </a>

        <h1 className="h1 mb-6">Edit Job</h1>

        <div className="card">
          <label className="text-sm text-muted block mb-1">Title</label>
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="input mb-4"
          />

          <label className="text-sm text-muted block mb-1">Description</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={8}
            className="input mb-2"
          />
          <p className="text-xs text-faint mb-4">
            Changing the description will clear previously extracted requirements — you&apos;ll
            need to re-extract them.
          </p>

          <button
            onClick={() => mutation.mutate()}
            disabled={!title || mutation.isPending}
            className="btn-primary"
          >
            {mutation.isPending ? "Saving..." : "Save Changes"}
          </button>
        </div>
      </main>
    </AuthGuard>
  );
}