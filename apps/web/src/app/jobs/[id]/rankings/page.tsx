"use client";

import { useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import { getJob, getJobRankings } from "@/lib/api-client";
import { FadeInStagger, FadeInItem } from "@/components/motion";
import { AuthGuard } from "@/components/auth-guard";

export default function RankingsPage() {
  const params = useParams();
  const jobId = params.id as string;

  const { data: job } = useQuery({
    queryKey: ["job", jobId],
    queryFn: () => getJob(jobId),
  });

  const { data: rankings } = useQuery({
    queryKey: ["rankings", jobId],
    queryFn: () => getJobRankings(jobId),
  });

  return (
    <AuthGuard>
      <main className="page">
        <a href={`/jobs/${jobId}`} className="link text-sm mb-4 inline-block">
          Back to job
        </a>

        <h1 className="h1 mb-1">Rankings</h1>
        <p className="text-sm text-muted mb-6">{job?.title}</p>

        <FadeInStagger>
          <div className="space-y-3">
            {rankings?.length === 0 && (
              <p className="text-faint text-sm">No candidates matched against this job yet.</p>
            )}

            {rankings?.map((r: any, i: number) => (
              <FadeInItem key={r.match_id}>
                <a href={`/candidates/${r.candidate_id}?jobId=${jobId}&matchId=${r.match_id}`}>
                  <div className="card card-interactive">
                    <div className="flex justify-between items-center">
                      <div>
                        <div className="font-medium">
                          #{i + 1} - {r.candidate_name || "Unnamed Candidate"}
                        </div>
                        <div className="text-sm text-muted">{r.candidate_email}</div>
                      </div>
                      <div className="score-display">{r.final_score}</div>
                    </div>
                  </div>
                </a>
              </FadeInItem>
            ))}
          </div>
        </FadeInStagger>
      </main>
    </AuthGuard>
  );
}