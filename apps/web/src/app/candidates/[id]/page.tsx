"use client";

import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useParams, useSearchParams } from "next/navigation";
import {
  getCandidate,
  generateFeedback,
  extractPortfolioLinks,
  getPortfolioLinks,
  analyzeGithub,
  previewEmail,
  sendEmail,
  getGmailStatus,
} from "@/lib/api-client";

export default function CandidateDetailPage() {
  const params = useParams();
  const searchParams = useSearchParams();
  const candidateId = params.id as string;
  const matchId = searchParams.get("matchId");

  const [emailTemplate, setEmailTemplate] = useState("invite_interview");
  const [emailPreview, setEmailPreview] = useState<any>(null);
  const [sendResult, setSendResult] = useState<any>(null);

  const { data: candidate } = useQuery({
    queryKey: ["candidate", candidateId],
    queryFn: () => getCandidate(candidateId),
  });

  const { data: gmailStatus } = useQuery({
    queryKey: ["gmailStatus"],
    queryFn: getGmailStatus,
  });

  const { data: links, refetch: refetchLinks } = useQuery({
    queryKey: ["links", candidateId],
    queryFn: () => getPortfolioLinks(candidateId),
  });

  const feedbackMutation = useMutation({
    mutationFn: () => generateFeedback(matchId as string),
  });

  const extractLinksMutation = useMutation({
    mutationFn: () => extractPortfolioLinks(candidateId),
    onSuccess: () => refetchLinks(),
  });

  const githubMutation = useMutation({
    mutationFn: () => analyzeGithub(candidateId),
  });

  const previewMutation = useMutation({
    mutationFn: () => previewEmail(candidateId, emailTemplate, "the role"),
    onSuccess: (data) => setEmailPreview(data),
  });

  const sendMutation = useMutation({
    mutationFn: () =>
      sendEmail({
        candidate_id: candidateId,
        to_email: emailPreview.to_email,
        subject: emailPreview.subject,
        body: emailPreview.body,
        template_key: emailTemplate,
      }),
    onSuccess: (data) => setSendResult(data),
  });

  let parsedData: any = null;
  if (candidate?.parsed_data) {
    try {
      parsedData = JSON.parse(candidate.parsed_data);
    } catch {}
  }

  const feedback = feedbackMutation.data?.feedback;
  const githubData = githubMutation.data;

  return (
    <main className="max-w-3xl mx-auto p-8">
      <a href="/" className="text-blue-400 text-sm mb-4 inline-block">
        Back to jobs
      </a>

      <h1 className="text-2xl font-semibold mb-1">{candidate?.full_name || "Candidate"}</h1>
      <p className="text-sm text-gray-400 mb-6">{candidate?.email}</p>

      {/* Structured resume data */}
      {parsedData && (
        <section className="bg-gray-900 rounded-lg p-6 mb-6 border border-gray-800">
          <h2 className="text-lg font-medium mb-3">Profile</h2>
          <div className="text-sm space-y-2">
            <div><span className="text-gray-400">Skills:</span> {parsedData.skills?.join(", ")}</div>
            <div><span className="text-gray-400">Experience:</span> {parsedData.years_experience} years</div>
            <div><span className="text-gray-400">Titles held:</span> {parsedData.titles_held?.join(", ")}</div>
            <div><span className="text-gray-400">Summary:</span> {parsedData.summary}</div>
          </div>
        </section>
      )}

      {/* AI Feedback */}
      <section className="bg-gray-900 rounded-lg p-6 mb-6 border border-gray-800">
        <h2 className="text-lg font-medium mb-3">AI Recruiter Feedback</h2>

        {!feedback && (
          <button
            onClick={() => feedbackMutation.mutate()}
            disabled={!matchId || feedbackMutation.isPending}
            className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 px-4 py-2 rounded text-sm"
          >
            {feedbackMutation.isPending ? "Generating..." : "Generate AI Feedback"}
          </button>
        )}

        {!matchId && (
          <p className="text-sm text-gray-500 mt-2">
            No match ID found — feedback requires visiting this page via a job match.
          </p>
        )}

        {feedback && (
          <div className="text-sm space-y-4">
            <div>
              <div className="text-gray-400 mb-1">Recommendation</div>
              <div className="font-medium text-blue-400">{feedback.recommendation}</div>
              <div className="text-gray-300 mt-1">{feedback.recommendation_reason}</div>
            </div>
            <div>
              <div className="text-gray-400 mb-1">Strengths</div>
              <ul className="list-disc list-inside space-y-1">
                {feedback.strengths?.map((s: string, i: number) => <li key={i}>{s}</li>)}
              </ul>
            </div>
            <div>
              <div className="text-gray-400 mb-1">Gaps</div>
              <ul className="list-disc list-inside space-y-1">
                {feedback.gaps?.map((g: string, i: number) => <li key={i}>{g}</li>)}
              </ul>
            </div>
            <div>
              <div className="text-gray-400 mb-1">Suggested Interview Questions</div>
              <ul className="list-disc list-inside space-y-1">
                {feedback.interview_questions?.map((q: string, i: number) => <li key={i}>{q}</li>)}
              </ul>
            </div>
          </div>
        )}
      </section>

      {/* Portfolio + GitHub */}
      <section className="bg-gray-900 rounded-lg p-6 mb-6 border border-gray-800">
        <h2 className="text-lg font-medium mb-3">Portfolio &amp; GitHub</h2>

        {(!links || links.length === 0) && (
          <button
            onClick={() => extractLinksMutation.mutate()}
            disabled={extractLinksMutation.isPending}
            className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 px-4 py-2 rounded text-sm mb-3"
          >
            {extractLinksMutation.isPending ? "Extracting..." : "Extract Links from Resume"}
          </button>
        )}

        {links && links.length > 0 && (
          <div className="text-sm space-y-2 mb-4">
            {links.map((link: any, i: number) => (
              <div key={i} className="flex items-center gap-2">
                <span className="px-2 py-0.5 bg-gray-800 rounded text-xs">{link.type}</span>
                <a href={link.url} target="_blank" className="text-blue-400 underline break-all">
                  {link.url}
                </a>
              </div>
            ))}
          </div>
        )}

        {links && links.some((l: any) => l.type === "github") && !githubData && (
          <button
            onClick={() => githubMutation.mutate()}
            disabled={githubMutation.isPending}
            className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 px-4 py-2 rounded text-sm"
          >
            {githubMutation.isPending ? "Analyzing..." : "Run GitHub Analysis"}
          </button>
        )}

        {githubData && (
          <div className="text-sm space-y-2 mt-3">
            <div className="text-xl font-semibold text-blue-400">
              {githubData.technical_signal_score}/100
            </div>
            <div className="text-gray-400">Technical Signal Score</div>
            {githubData.profile && (
              <div>
                <span className="text-gray-400">Public repos:</span> {githubData.profile.public_repos} ·{" "}
                <span className="text-gray-400">Followers:</span> {githubData.profile.followers} ·{" "}
                <span className="text-gray-400">Top languages:</span> {githubData.profile.top_languages?.join(", ")}
              </div>
            )}
            <div className="space-y-2 mt-2">
              {githubData.repositories?.map((repo: any, i: number) => (
                <div key={i} className="bg-gray-800 rounded p-3">
                  <div className="font-medium">{repo.repo_name}</div>
                  <div className="text-gray-400 text-xs">{repo.description}</div>
                  <div className="text-xs mt-1">
                    ⭐ {repo.stars} · {repo.languages?.join(", ")} · {repo.has_readme ? "Has README" : "No README"}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </section>

      {/* Email Outreach */}
      <section className="bg-gray-900 rounded-lg p-6 border border-gray-800">
        <h2 className="text-lg font-medium mb-3">Email Outreach</h2>

        {!gmailStatus?.connected && (
          <p className="text-sm text-yellow-500 mb-3">
            Gmail not connected. Visit{" "}
            <a href="http://localhost:8000/integrations/gmail/connect" target="_blank" className="underline">
              this link
            </a>{" "}
            to connect first.
          </p>
        )}

        <select
          value={emailTemplate}
          onChange={(e) => {
            setEmailTemplate(e.target.value);
            setEmailPreview(null);
          }}
          className="bg-gray-800 border border-gray-700 rounded p-2 text-sm mb-3 w-full"
        >
          <option value="invite_interview">Invite to Interview</option>
          <option value="next_round">Move to Next Round</option>
          <option value="reject">Reject</option>
        </select>

        <button
          onClick={() => previewMutation.mutate()}
          disabled={previewMutation.isPending}
          className="bg-gray-700 hover:bg-gray-600 disabled:opacity-50 px-4 py-2 rounded text-sm mr-2"
        >
          {previewMutation.isPending ? "Loading..." : "Preview Email"}
        </button>

        {emailPreview && (
          <div className="mt-4 bg-gray-800 rounded p-4 text-sm">
            <div className="text-gray-400 mb-1">To: {emailPreview.to_email}</div>
            <div className="font-medium mb-2">{emailPreview.subject}</div>
            <div className="whitespace-pre-wrap text-gray-300 mb-4">{emailPreview.body}</div>

            <button
              onClick={() => sendMutation.mutate()}
              disabled={sendMutation.isPending || !gmailStatus?.connected}
              className="bg-green-600 hover:bg-green-700 disabled:opacity-50 px-4 py-2 rounded text-sm"
            >
              {sendMutation.isPending ? "Sending..." : "Confirm & Send"}
            </button>
          </div>
        )}

        {sendResult && (
          <p className={`text-sm mt-3 ${sendResult.status === "sent" ? "text-green-400" : "text-red-400"}`}>
            Status: {sendResult.status}
          </p>
        )}
      </section>
    </main>
  );
}