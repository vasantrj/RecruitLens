"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import { getJob, uploadCandidate, extractCandidateData, extractJobRequirements, matchCandidateToJob } from "@/lib/api-client";
import { FadeInStagger, FadeInItem } from "@/components/motion";
import { AuthGuard } from "@/components/auth-guard";
import { useToast } from "@/components/toast";
import { AnimatedScore } from "@/components/animated-score";
import { getAccountType } from "@/lib/auth-helpers";

export default function JobDetailPage() {
  const params = useParams();
  const jobId = params.id as string;
  const queryClient = useQueryClient();
  const { showToast } = useToast();
  const accountType = getAccountType();

  const [screeningMode, setScreeningMode] = useState<"single" | "bulk" | null>(
    accountType === "personal" ? "single" : null
  );

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
      showToast("Candidate scored successfully.");
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
      <div className="home-bg" />
      <main className="page">
        <a href="/" className="link text-sm mb-4 inline-block">
          Back to jobs
        </a>

        <h1 className="h1 mb-2">{job?.title}</h1>
        <p className="text-sm text-muted mb-6">
          {job?.is_role_only === "true" ? "Role-only" : "Full JD"}
        </p>

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

          {/* Company fork: choose single vs bulk */}
          {accountType === "company" && screeningMode === null && (
            <FadeInItem>
              <div className="card">
                <h2 className="h2 mb-4">How would you like to screen candidates?</h2>
                <div className="grid grid-cols-2 gap-4">
                  <button
                    onClick={() => setScreeningMode("single")}
                    className="card card-interactive text-left"
                  >
                    <div className="font-medium mb-1">Single Resume</div>
                    <div className="text-sm text-muted">
                      Upload and score one candidate at a time.
                    </div>
                  </button>
                  <a href={`/jobs/${jobId}/bulk-upload`} className="card card-interactive text-left block">
                    <div className="font-medium mb-1">Bulk Resumes</div>
                    <div className="text-sm text-muted">
                      Upload multiple resumes, rank them, and shortlist top candidates.
                    </div>
                  </a>
                </div>
              </div>
            </FadeInItem>
          )}

          {/* Single resume upload flow */}
          {screeningMode === "single" && (
            <FadeInItem>
              <div className="card">
                {accountType === "company" && (
                  <button
                    onClick={() => setScreeningMode(null)}
                    className="link text-sm mb-3 inline-block"
                  >
                    ← Change screening mode
                  </button>
                )}

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
                    <div className="score-display">
                      <AnimatedScore value={uploadMutation.data.match.final_score} />/100
                    </div>
                    <div className="text-sm text-muted mt-1">Match Score</div>
                    <a
                      href={`/candidates/${uploadMutation.data.candidate.id}?jobId=${jobId}&matchId=${uploadMutation.data.match.id}&score=${uploadMutation.data.match.final_score}`}
                      className="link text-sm mt-2 inline-block"
                    >
                      View full breakdown
                    </a>
                  </div>
                )}
              </div>
            </FadeInItem>
          )}

          {accountType === "company" && (
            <FadeInItem>
              <a href={`/jobs/${jobId}/rankings`} className="link text-sm mt-4 inline-block">
                View Rankings
              </a>
            </FadeInItem>
          )}
        </FadeInStagger>
      </main>
    </AuthGuard>
  );
}