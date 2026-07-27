"use client";

import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import {
  getJob,
  uploadCandidatesBulk,
  bulkMatch,
  getCandidate,
  bulkSend,
  getGmailStatus,
  previewEmail,
  exportSelectedCandidates,
} from "@/lib/api-client";
import { AuthGuard } from "@/components/auth-guard";
import { FadeInStagger, FadeInItem } from "@/components/motion";
import { useToast } from "@/components/toast";

type RankedCandidate = {
  candidate_id: string;
  candidate_name: string | null;
  match_id: string;
  final_score: number;
  status: string;
  email?: string;
  duplicateCount?: number;
};

export default function BulkUploadPage() {
  const params = useParams();
  const jobId = params.id as string;
  const { showToast } = useToast();

  const [files, setFiles] = useState<File[]>([]);
  const [statusMessage, setStatusMessage] = useState("");
  const [ranked, setRanked] = useState<RankedCandidate[]>([]);
  const [shortlistCount, setShortlistCount] = useState(3);

  const [shortlistedTemplate, setShortlistedTemplate] = useState("invite_interview");
  const [rejectedTemplate, setRejectedTemplate] = useState("reject");

  const [shortlistedSubject, setShortlistedSubject] = useState("");
  const [shortlistedBody, setShortlistedBody] = useState("");
  const [rejectedSubject, setRejectedSubject] = useState("");
  const [rejectedBody, setRejectedBody] = useState("");

  const [previewed, setPreviewed] = useState(false);
  const [sendResult, setSendResult] = useState<any>(null);

  const { data: job } = useQuery({
    queryKey: ["job", jobId],
    queryFn: () => getJob(jobId),
  });

  const { data: gmailStatus } = useQuery({
    queryKey: ["gmailStatus"],
    queryFn: getGmailStatus,
  });

  const processMutation = useMutation({
    mutationFn: async () => {
      setStatusMessage(`Uploading ${files.length} resumes...`);
      const uploadResult = await uploadCandidatesBulk(files, jobId);

      const processedEntries = uploadResult.results.filter((r: any) => r.status === "processed");
      const processedIds = processedEntries.map((r: any) => r.candidate_id);

      setStatusMessage(`Scoring ${processedIds.length} candidates against job requirements...`);
      const matchResult = await bulkMatch(jobId, processedIds);

      setStatusMessage("Fetching candidate emails...");
      const withEmails = await Promise.all(
        matchResult.results
          .filter((r: any) => r.status === "matched")
          .map(async (r: any) => {
            const candidate = await getCandidate(r.candidate_id);
            const uploadEntry = processedEntries.find((e: any) => e.candidate_id === r.candidate_id);
            return {
              ...r,
              email: candidate.email,
              duplicateCount: uploadEntry?.duplicate_applications?.length || 0,
            };
          })
      );

      setStatusMessage("Done!");
      return withEmails;
    },
    onSuccess: (data) => {
      setRanked(data);
      setPreviewed(false);
      setSendResult(null);
      showToast(`${data.length} candidates scored successfully.`);
    },
  });

  const previewMutation = useMutation({
    mutationFn: async () => {
      const shortlistedSample = ranked[0];
      const rejectedSample = ranked[shortlistCount];

      const shortlistedPreview = shortlistedSample
        ? await previewEmail(shortlistedSample.candidate_id, shortlistedTemplate, job?.title || "the role")
        : null;
      const rejectedPreview = rejectedSample
        ? await previewEmail(rejectedSample.candidate_id, rejectedTemplate, job?.title || "the role")
        : null;

      return { shortlistedPreview, rejectedPreview };
    },
    onSuccess: (data) => {
      if (data.shortlistedPreview) {
        setShortlistedSubject(data.shortlistedPreview.subject);
        setShortlistedBody(data.shortlistedPreview.body);
      }
      if (data.rejectedPreview) {
        setRejectedSubject(data.rejectedPreview.subject);
        setRejectedBody(data.rejectedPreview.body);
      }
      setPreviewed(true);
    },
  });

  const sendMutation = useMutation({
    mutationFn: () => {
      const shortlisted = ranked.slice(0, shortlistCount).map((r) => ({
        candidate_id: r.candidate_id,
        to_email: r.email || "",
      }));
      const rejected = ranked.slice(shortlistCount).map((r) => ({
        candidate_id: r.candidate_id,
        to_email: r.email || "",
      }));
      return bulkSend({
        shortlisted,
        rejected,
        shortlisted_subject: shortlistedSubject,
        shortlisted_body: shortlistedBody,
        rejected_subject: rejectedSubject,
        rejected_body: rejectedBody,
      });
    },
    onSuccess: (data) => {
      setSendResult(data);
      const sentCount =
        data.shortlisted.filter((r: any) => r.status === "sent").length +
        data.rejected.filter((r: any) => r.status === "sent").length;
      showToast(`${sentCount} emails sent successfully.`);
    },
  });

  const getGmailConnectUrl = () => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : "";
    return `${apiUrl}/integrations/gmail/connect?token=${token}`;
  };

  const handleDownloadShortlist = async () => {
    const shortlistedIds = ranked.slice(0, shortlistCount).map((r) => r.candidate_id);
    const result = await exportSelectedCandidates(jobId, shortlistedIds);
    const blob = new Blob([result.csv], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = result.filename;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <AuthGuard>
      <main className="page-wide">
        <a href={`/jobs/${jobId}`} className="link text-sm mb-4 inline-block">
          Back to job
        </a>

        <h1 className="h1 mb-1">Bulk Screening</h1>
        <p className="text-sm text-muted mb-6">{job?.title}</p>

        <div className="card mb-6">
          <h2 className="h2 mb-3">Upload Resumes</h2>
          <input
            type="file"
            accept=".pdf,.docx"
            multiple
            onChange={(e) => setFiles(Array.from(e.target.files || []))}
            className="mb-3 text-sm"
          />
          <p className="text-sm text-muted mb-3">{files.length} file(s) selected</p>

          <button
            onClick={() => processMutation.mutate()}
            disabled={files.length === 0 || processMutation.isPending}
            className="btn-primary"
          >
            {processMutation.isPending ? "Processing..." : "Upload & Score All"}
          </button>

          {statusMessage && <p className="text-sm text-muted mt-3">{statusMessage}</p>}
        </div>

        {ranked.length > 0 && (
          <div className="card mb-6">
            <h2 className="h2 mb-3">Ranked Candidates</h2>

            <div className="flex items-center gap-2 mb-4">
              <label className="text-sm text-muted">Shortlist top</label>
              <input
                type="number"
                min={0}
                max={ranked.length}
                value={shortlistCount}
                onChange={(e) => {
                  setShortlistCount(Number(e.target.value));
                  setPreviewed(false);
                }}
                className="input w-20"
              />
              <span className="text-sm text-muted">candidates for next round</span>
            </div>

            <button onClick={handleDownloadShortlist} className="btn-secondary text-sm mb-4">
              Download Shortlisted Candidates (CSV)
            </button>

            <FadeInStagger>
              <div className="space-y-2">
                {ranked.map((r, i) => (
                  <FadeInItem key={r.candidate_id}>
                    <div
                      className={`card-alt flex justify-between items-center ${
                        i < shortlistCount ? "border-2" : ""
                      }`}
                      style={i < shortlistCount ? { borderColor: "var(--success)" } : {}}
                    >
                      <div>
                        <div className="font-medium">
                          #{i + 1} - {r.candidate_name || "Unnamed"}
                        </div>
                        <div className="text-xs text-muted">{r.email}</div>
                        {(r.duplicateCount ?? 0) > 0 && (
                          <div className="text-xs status-warning mt-1">
                            ⚠ Applied to {r.duplicateCount} other job{(r.duplicateCount ?? 0) > 1 ? "s" : ""}
                          </div>
                        )}
                      </div>
                      <div className="flex items-center gap-3">
                        <span className={`badge ${i < shortlistCount ? "badge-success" : "badge-danger"}`}>
                          {i < shortlistCount ? "Shortlisted" : "Reject"}
                        </span>
                        <div className="score-display">{r.final_score}</div>
                      </div>
                    </div>
                  </FadeInItem>
                ))}
              </div>
            </FadeInStagger>

            {!gmailStatus?.connected && (
              <p className="text-sm status-warning mt-4">
                Gmail not connected.{" "}
                <a href={getGmailConnectUrl()} target="_blank" className="link">
                  Connect Gmail
                </a>{" "}
                to send emails. Emails are sent from your own connected Gmail account.
              </p>
            )}

            <div className="mt-4 grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm text-muted block mb-1">Shortlisted candidates get</label>
                <select
                  value={shortlistedTemplate}
                  onChange={(e) => {
                    setShortlistedTemplate(e.target.value);
                    setPreviewed(false);
                  }}
                  className="input"
                >
                  <option value="invite_interview">Invite to Interview</option>
                  <option value="next_round">Move to Next Round</option>
                </select>
              </div>
              <div>
                <label className="text-sm text-muted block mb-1">Everyone else gets</label>
                <select
                  value={rejectedTemplate}
                  onChange={(e) => {
                    setRejectedTemplate(e.target.value);
                    setPreviewed(false);
                  }}
                  className="input"
                >
                  <option value="reject">Reject</option>
                </select>
              </div>
            </div>

            {!previewed && (
              <button
                onClick={() => previewMutation.mutate()}
                disabled={previewMutation.isPending || !gmailStatus?.connected}
                className="btn-secondary mt-4"
              >
                {previewMutation.isPending ? "Loading..." : "Preview & Edit Emails"}
              </button>
            )}

            {previewed && (
              <div className="mt-4 space-y-4">
                <div className="card-alt text-sm">
                  <div className="badge badge-success mb-2">
                    Sent to all {shortlistCount} shortlisted candidates
                  </div>
                  <label className="text-muted block mb-1">Subject</label>
                  <input
                    value={shortlistedSubject}
                    onChange={(e) => setShortlistedSubject(e.target.value)}
                    className="input mb-3"
                  />
                  <label className="text-muted block mb-1">Body</label>
                  <textarea
                    value={shortlistedBody}
                    onChange={(e) => setShortlistedBody(e.target.value)}
                    rows={6}
                    className="input"
                  />
                </div>

                <div className="card-alt text-sm">
                  <div className="badge badge-danger mb-2">
                    Sent to all {ranked.length - shortlistCount} other candidates
                  </div>
                  <label className="text-muted block mb-1">Subject</label>
                  <input
                    value={rejectedSubject}
                    onChange={(e) => setRejectedSubject(e.target.value)}
                    className="input mb-3"
                  />
                  <label className="text-muted block mb-1">Body</label>
                  <textarea
                    value={rejectedBody}
                    onChange={(e) => setRejectedBody(e.target.value)}
                    rows={6}
                    className="input"
                  />
                </div>

                <button
                  onClick={() => sendMutation.mutate()}
                  disabled={sendMutation.isPending || !gmailStatus?.connected}
                  className="btn-success"
                >
                  {sendMutation.isPending
                    ? "Sending..."
                    : `Confirm & Send to all ${ranked.length} candidates`}
                </button>
              </div>
            )}

            {sendResult && (
              <div className="mt-4 text-sm">
                <p className="status-success">
                  Sent to {sendResult.shortlisted.filter((r: any) => r.status === "sent").length} shortlisted
                  candidates.
                </p>
                <p className="status-danger">
                  Sent to {sendResult.rejected.filter((r: any) => r.status === "sent").length} rejected candidates.
                </p>
              </div>
            )}
          </div>
        )}
      </main>
    </AuthGuard>
  );
}