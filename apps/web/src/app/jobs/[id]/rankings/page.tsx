"use client";

import { useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import { getJob, getJobRankings } from "@/lib/api-client";

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
    <main className="max-w-2xl mx-auto p-8">
      <a href={`/jobs/${jobId}`} className="text-blue-400 text-sm mb-4 inline-block">
        Back to job
      </a>

      <h1 className="text-2xl font-semibold mb-1">Rankings</h1>
      <p className="text-sm text-gray-400 mb-6">{job?.title}</p>

      <div className="space-y-3">
        {rankings?.length === 0 && (
          <p className="text-gray-500 text-sm">No candidates matched against this job yet.</p>
        )}

        {rankings?.map((r: any, i: number) => (
          <a
            key={r.match_id}
            href={`/candidates/${r.candidate_id}?jobId=${jobId}&matchId=${r.match_id}`}
            className="block bg-gray-900 border border-gray-800 rounded p-4 hover:border-blue-600 transition-colors"
          >
            <div className="flex justify-between items-center">
              <div>
                <div className="font-medium">
                  #{i + 1} - {r.candidate_name || "Unnamed Candidate"}
                </div>
                <div className="text-sm text-gray-400">{r.candidate_email}</div>
              </div>
              <div className="text-xl font-semibold text-blue-400">{r.final_score}</div>
            </div>
          </a>
        ))}
      </div>
    </main>
  );
}