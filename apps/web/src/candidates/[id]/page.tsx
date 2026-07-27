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
  getInterviewPrep,
  checkDuplicates,
} from "@/lib/api-client";
import { FadeInStagger, FadeInItem } from "@/components/motion";
import { AuthGuard } from "@/components/auth-guard";
import { getAccountType } from "@/lib/auth-helpers";
import { useToast } from "@/components/toast";
import { ScoreRing } from "@/components/score-ring";

export default function CandidateDetailPage() {
  const params = useParams();
  const searchParams = useSearchParams();
  const candidateId = params.id as string;
  const matchId = searchParams.get("matchId");
  const scoreParam = searchParams.get("score");
  const accountType = getAccountType();
  const { showToast } = useToast();

  const [emailTemplate, setEmailTemplate] = useState("invite_interview");
  const [toEmail, setToEmail] = useState("");
  const [subject, setSubject] = useState("");
  const [body, setBody] = useState("");
  const [previewed, setPreviewed] = useState(false);
  const [sendResult, setSendResult] = useState<any>(null);

  const { data: candidate } = useQuery({
    queryKey: ["candidate", candidateId],
    queryFn: () => getCandidate(candidateId),
  });

  const { data: gmailStatus } = useQuery({
    queryKey: ["gmailStatus"],
    queryFn: getGmailStatus,
    enabled: accountType === "company",
  });

  const { data: links, refetch: refetchLinks } = useQuery({
    queryKey: ["links", candidateId],
    queryFn: () => getPortfolioLinks(candidateId),
  });

  const { data: duplicatesData } = useQuery({
    queryKey: ["duplicates", candidateId],
    queryFn: () => checkDuplicates(candidateId),
  });

  const duplicates = duplicatesData?.duplicate_applications || [];

  const feedbackMutation = useMutation({
    mutationFn: () => generateFeedback(matchId as string),
  });

  const interviewPrepMutation = useMutation({
    mutationFn: () => getInterviewPrep(matchId as string),
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
    onSuccess: (data) => {
      setToEmail(data.to_email || "");
      setSubject(data.subject);
      setBody(data.body);
      setPreviewed(true);
    },
  });

  const sendMutation = useMutation({
    mutationFn: () =>
      sendEmail({
        candidate_id: candidateId,
        to_email: toEmail,
        subject,
        body,
        template_key: emailTemplate,
      }),
    onSuccess: (data) => {
      setSendResult(data);
      showToast(
        data.status === "sent" ? "Email sent successfully." : "Email failed to send.",
        data.status === "sent" ? "success" : "error"
      );
    },
  });

  let parsedData: any = null;
  if (candidate?.parsed_data) {
    try {
      parsedData = JSON.parse(candidate.parsed_data);
    } catch {}
  }

  const feedback = feedbackMutation.data?.feedback;
  const githubData = githubMutation.data;
  const interviewPrep = interviewPrepMutation.data?.interview_prep;

  const getGmailConnectUrl = () => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : "";
    return `${apiUrl}/integrations/gmail/connect?token=${token}`;
  };

  return (
    <AuthGuard>
      <main className="page-wide">
        <a href="/" className="link text-sm mb-4 inline-block">
          Back to jobs
        </a>

        <h1 className="h1 mb-1">{candidate?.full_name || "Candidate"}</h1>
        <p className="text-sm text-muted mb-6">{candidate?.email}</p>

        {scoreParam && (
          <div className="flex justify-center mb-6">
            <ScoreRing value={parseFloat(scoreParam)} />
          </div>
        )}

        {duplicates.length > 0 && (
          <div className="card-alt mb-6 text-sm status-warning">
            ⚠ This candidate has applied to {duplicates.length} other job{duplicates.length > 1 ? "s" : ""} you're
            tracking.
          </div>
        )}

        <FadeInStagger>
          {/* Structured resume data */}
          {parsedData && (
            <FadeInItem>
              <section className="card mb-6">
                <h2 className="h2 mb-3">Profile</h2>
                <div className="text-sm space-y-2">
                  <div><span className="text-muted">Skills:</span> {parsedData.skills?.join(", ")}</div>
                  <div><span className="text-muted">Experience:</span> {parsedData.years_experience} years</div>
                  <div><span className="text-muted">Titles held:</span> {parsedData.titles_held?.join(", ")}</div>
                  <div><span className="text-muted">Summary:</span> {parsedData.summary}</div>
                </div>
              </section>
            </FadeInItem>
          )}

          {/* AI Feedback */}
          <FadeInItem>
            <section className="card mb-6">
              <h2 className="h2 mb-3">AI Recruiter Feedback</h2>

              {!feedback && (
                <button
                  onClick={() => feedbackMutation.mutate()}
                  disabled={!matchId || feedbackMutation.isPending}
                  className="btn-primary text-sm"
                >
                  {feedbackMutation.isPending ? "Generating..." : "Generate AI Feedback"}
                </button>
              )}

              {!matchId && (
                <p className="text-sm text-faint mt-2">
                  No match ID found — feedback requires visiting this page via a job match.
                </p>
              )}

              {feedback && (
                <div className="text-sm space-y-4">
                  <div>
                    <div className="text-muted mb-1">Recommendation</div>
                    <div className="font-medium accent-text">{feedback.recommendation}</div>
                    <div className="mt-1">{feedback.recommendation_reason}</div>
                  </div>
                  <div>
                    <div className="text-muted mb-1">Strengths</div>
                    <ul className="list-disc list-inside space-y-1">
                      {feedback.strengths?.map((s: string, i: number) => <li key={i}>{s}</li>)}
                    </ul>
                  </div>
                  <div>
                    <div className="text-muted mb-1">Gaps</div>
                    <ul className="list-disc list-inside space-y-1">
                      {feedback.gaps?.map((g: string, i: number) => <li key={i}>{g}</li>)}
                    </ul>
                  </div>
                  <div>
                    <div className="text-muted mb-1">Suggested Interview Questions</div>
                    <ul className="list-disc list-inside space-y-1">
                      {feedback.interview_questions?.map((q: string, i: number) => <li key={i}>{q}</li>)}
                    </ul>
                  </div>
                </div>
              )}
            </section>
          </FadeInItem>

          {/* Interview Prep */}
          <FadeInItem>
            <section className="card mb-6">
              <h2 className="h2 mb-3">Interview Preparation</h2>

              {!interviewPrep && (
                <button
                  onClick={() => interviewPrepMutation.mutate()}
                  disabled={!matchId || interviewPrepMutation.isPending}
                  className="btn-primary text-sm"
                >
                  {interviewPrepMutation.isPending ? "Generating..." : "Generate Interview Questions"}
                </button>
              )}

              {interviewPrep && (
                <div className="text-sm space-y-4">
                  <div>
                    <div className="text-muted mb-1">Technical Questions</div>
                    <ul className="list-disc list-inside space-y-1">
                      {interviewPrep.technical_questions?.map((q: string, i: number) => <li key={i}>{q}</li>)}
                    </ul>
                  </div>
                  <div>
                    <div className="text-muted mb-1">Behavioral Questions</div>
                    <ul className="list-disc list-inside space-y-1">
                      {interviewPrep.behavioral_questions?.map((q: string, i: number) => <li key={i}>{q}</li>)}
                    </ul>
                  </div>
                  <div>
                    <div className="text-muted mb-1">Role-Specific Questions</div>
                    <ul className="list-disc list-inside space-y-1">
                      {interviewPrep.role_specific_questions?.map((q: string, i: number) => <li key={i}>{q}</li>)}
                    </ul>
                  </div>
                </div>
              )}
            </section>
          </FadeInItem>

          {/* Portfolio + GitHub */}
          <FadeInItem>
            <section className="card mb-6">
              <h2 className="h2 mb-3">Portfolio &amp; GitHub</h2>

              {(!links || links.length === 0) && (
                <button
                  onClick={() => extractLinksMutation.mutate()}
                  disabled={extractLinksMutation.isPending}
                  className="btn-primary text-sm mb-3"
                >
                  {extractLinksMutation.isPending ? "Extracting..." : "Extract Links from Resume"}
                </button>
              )}

              {links && links.length > 0 && (
                <div className="text-sm space-y-2 mb-4">
                  {links.map((link: any, i: number) => (
                    <div key={i} className="flex items-center gap-2">
                      <span className="badge">{link.type}</span>
                      <a href={link.url} target="_blank" className="link break-all">
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
                  className="btn-primary text-sm"
                >
                  {githubMutation.isPending ? "Analyzing..." : "Run GitHub Analysis"}
                </button>
              )}

              {githubData && (
                <div className="text-sm space-y-2 mt-3">
                  <div className="score-display">{githubData.technical_signal_score}/100</div>
                  <div className="text-muted">Technical Signal Score</div>
                  {githubData.profile && (
                    <div>
                      <span className="text-muted">Public repos:</span> {githubData.profile.public_repos} ·{" "}
                      <span className="text-muted">Followers:</span> {githubData.profile.followers} ·{" "}
                      <span className="text-muted">Top languages:</span> {githubData.profile.top_languages?.join(", ")}
                    </div>
                  )}
                  <div className="space-y-2 mt-2">
                    {githubData.repositories?.map((repo: any, i: number) => (
                      <div key={i} className="card-alt">
                        <div className="font-medium">{repo.repo_name}</div>
                        <div className="text-faint text-xs">{repo.description}</div>
                        <div className="text-xs mt-1">
                          ⭐ {repo.stars} · {repo.languages?.join(", ")} · {repo.has_readme ? "Has README" : "No README"}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </section>
          </FadeInItem>

          {/* Email Outreach — company accounts only */}
          {accountType === "company" && (
            <FadeInItem>
              <section className="card">
                <h2 className="h2 mb-3">Email Outreach</h2>
                <p className="text-xs text-faint mb-3">
                  Sent from your own connected Gmail account.
                </p>

                {!gmailStatus?.connected && (
                  <p className="text-sm status-warning mb-3">
                    Gmail not connected.{" "}
                    <a href={getGmailConnectUrl()} target="_blank" className="link">
                      Connect Gmail
                    </a>{" "}
                    to enable sending.
                  </p>
                )}

                <select
                  value={emailTemplate}
                  onChange={(e) => {
                    setEmailTemplate(e.target.value);
                    setPreviewed(false);
                  }}
                  className="input mb-3"
                >
                  <option value="invite_interview">Invite to Interview</option>
                  <option value="next_round">Move to Next Round</option>
                  <option value="reject">Reject</option>
                </select>

                {!previewed && (
                  <button
                    onClick={() => previewMutation.mutate()}
                    disabled={previewMutation.isPending || !gmailStatus?.connected}
                    className="btn-secondary mr-2"
                  >
                    {previewMutation.isPending ? "Loading..." : "Preview Email"}
                  </button>
                )}

                {previewed && (
                  <div className="card-alt mt-4 text-sm">
                    <label className="text-muted block mb-1">To</label>
                    <input
                      value={toEmail}
                      onChange={(e) => setToEmail(e.target.value)}
                      className="input mb-3"
                    />

                    <label className="text-muted block mb-1">Subject</label>
                    <input
                      value={subject}
                      onChange={(e) => setSubject(e.target.value)}
                      className="input mb-3"
                    />

                    <label className="text-muted block mb-1">Body</label>
                    <textarea
                      value={body}
                      onChange={(e) => setBody(e.target.value)}
                      rows={8}
                      className="input mb-4"
                    />

                    <button
                      onClick={() => sendMutation.mutate()}
                      disabled={sendMutation.isPending || !gmailStatus?.connected}
                      className="btn-success"
                    >
                      {sendMutation.isPending ? "Sending..." : "Confirm & Send"}
                    </button>
                  </div>
                )}

                {sendResult && (
                  <p className={`text-sm mt-3 ${sendResult.status === "sent" ? "status-success" : "status-danger"}`}>
                    Status: {sendResult.status}
                  </p>
                )}
              </section>
            </FadeInItem>
          )}
        </FadeInStagger>
      </main>
    </AuthGuard>
  );
}