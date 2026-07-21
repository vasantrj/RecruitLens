"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import { getJob, uploadCandidate, extractCandidateData, extractJobRequirements, matchCandidateToJob } from "@/lib/api-client";
import { FadeInStagger, FadeInItem } from "@/components/motion";
import { AuthGuard } from "@/components/auth-guard";

export default function JobDetailPage() {
  const params = useParams();
  const jobId = params.id as string;
  const queryClient = useQueryClient();

  const [file, setFile] = useState<File | null>(null);
  const [statusMessage, setStatusMessage] = useState<string>("");

  const { data: job } = useQuery({
    queryKey: ["job", jobId],
    queryFn: () => getJob(jobId),
  });

  const extractJdMutation = useMutation({
    mutationFn: () => extractJobRequirements(jobId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["job", jobId] }),
  });

  const uploadMutation = useMutation({
    mutationFn: async () => {
      if (!file) throw new Error("No file selected");
      setStatusMessage("Uploading resume...");
      const candidate = await uploadCandidate(file, jobId);

      setStatusMessage("Extracting structured data...");
      await extractCandidateData(candidate.id);

      setStatusMessage("Computing match score...");
      const match = await matchCandidateToJob(candidate.id, jobId);

      setStatusMessage("Done!");
      return { candidate, match };
    },
    onSuccess: () => {
      setFile(null);
    },
  });

  let parsedRequirements = null;
  if (job?.parsed_requirements) {
    try {
      parsedRequirements = JSON.parse(job.parsed_requirements);
    } catch {}
  }

  return (
    <AuthGuard>
      <main className="page">
        <a href="/" className="link text-sm mb-4 inline-block">
          Back to jobs
        </a>

        <h1 className="h1 mb-2">{job?.title}</h1>
        <p className="text-sm text-muted mb-2">
          {job?.is_role_only === "true" ? "Role-only" : "Full JD"}
        </p>

        <a href={`/jobs/${jobId}/rankings`} className="link text-sm mb-6 inline-block">
          View Rankings
        </a>

        <FadeInStagger>
          <FadeInItem>
            <div className="card mb-6">
              <h2 className="h2 mb-3">Requirements</h2>

              {!parsedRequirements && job?.description && (
                <button
                  onClick={() => extractJdMutation.mutate()}
                  disabled={extractJdMutation.isPending}
                  className="btn-primary text-sm"
                >
                  {extractJdMutation.isPending ? "Extracting..." : "Extract Requirements from JD"}
                </button>
              )}

              {parsedRequirements && (
                <div className="text-sm space-y-2">
                  <div>
                    <span className="text-muted">Required skills:</span>{" "}
                    {parsedRequirements.required_skills?.join(", ")}
                  </div>
                  <div>
                    <span className="text-muted">Nice to have:</span>{" "}
                    {parsedRequirements.nice_to_have_skills?.join(", ") || "-"}
                  </div>
                  <div>
                    <span className="text-muted">Min experience:</span>{" "}
                    {parsedRequirements.min_years_experience} years
                  </div>
                  <div>
                    <span className="text-muted">Seniority:</span>{" "}
                    {parsedRequirements.seniority}
                  </div>
                </div>
              )}
            </div>
          </FadeInItem>

          <FadeInItem>
            <div className="card">
              <h2 className="h2 mb-3">Upload a Resume</h2>

              <input
                type="file"
                accept=".pdf,.docx"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                className="mb-3 text-sm"
              />

              <button
                onClick={() => uploadMutation.mutate()}
                disabled={!file || uploadMutation.isPending}
                className="btn-primary block"
              >
                {uploadMutation.isPending ? "Processing..." : "Upload & Match"}
              </button>

              {statusMessage && <p className="text-sm text-muted mt-3">{statusMessage}</p>}

              {uploadMutation.data && (
                <div className="card-alt mt-4">
                  <div className="score-display">{uploadMutation.data.match.final_score}/100</div>
                  <div className="text-sm text-muted mt-1">Match Score</div>
                  <a
                    href={`/candidates/${uploadMutation.data.candidate.id}?jobId=${jobId}&matchId=${uploadMutation.data.match.id}`}
                    className="link text-sm mt-2 inline-block"
                  >
                    View full breakdown
                  </a>
                </div>
              )}
            </div>
          </FadeInItem>
        </FadeInStagger>
      </main>
    </AuthGuard>
  );
}