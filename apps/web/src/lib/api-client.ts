import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// ---- Jobs ----
export const createJob = (data: { title: string; description?: string; is_role_only?: boolean }) =>
  apiClient.post("/jobs/", data).then((res) => res.data);

export const createRoleOnlyJob = (role_title: string) =>
  apiClient.post("/jobs/role-only", { role_title }).then((res) => res.data);

export const listJobs = () => apiClient.get("/jobs/").then((res) => res.data);

export const getJob = (jobId: string) => apiClient.get(`/jobs/${jobId}`).then((res) => res.data);

export const extractJobRequirements = (jobId: string) =>
  apiClient.post(`/jobs/${jobId}/extract`).then((res) => res.data);

// ---- Candidates ----
export const uploadCandidate = (file: File, jobId?: string) => {
  const formData = new FormData();
  formData.append("file", file);
  if (jobId) formData.append("job_id", jobId);

  return apiClient
    .post("/candidates/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    })
    .then((res) => res.data);
};

export const extractCandidateData = (candidateId: string) =>
  apiClient.post(`/candidates/${candidateId}/extract`).then((res) => res.data);

export const getCandidate = (candidateId: string) =>
  apiClient.get(`/candidates/${candidateId}`).then((res) => res.data);

// ---- Matching ----
export const matchCandidateToJob = (candidateId: string, jobId: string) =>
  apiClient.post(`/matching/${candidateId}/${jobId}`).then((res) => res.data);

// ---- Feedback ----
export const generateFeedback = (matchId: string) =>
  apiClient.post(`/feedback/${matchId}`).then((res) => res.data);

// ---- Portfolio ----
export const extractPortfolioLinks = (candidateId: string) =>
  apiClient.post(`/portfolio/${candidateId}/extract-links`).then((res) => res.data);

export const analyzeGithub = (candidateId: string) =>
  apiClient.post(`/portfolio/${candidateId}/analyze-github`).then((res) => res.data);


// ---- Feedback (additional) ----
export const getMatchDetails = (matchId: string) =>
  apiClient.get(`/matching/${matchId}`).then((res) => res.data).catch(() => null);

// ---- Portfolio (additional) ----
export const getPortfolioLinks = (candidateId: string) =>
  apiClient.get(`/portfolio/${candidateId}`).then((res) => res.data);

// ---- Outreach ----
export const previewEmail = (candidateId: string, templateKey: string, roleTitle: string) =>
  apiClient
    .post("/outreach/preview", { candidate_id: candidateId, template_key: templateKey, role_title: roleTitle })
    .then((res) => res.data);

export const sendEmail = (data: {
  candidate_id: string;
  to_email: string;
  subject: string;
  body: string;
  template_key?: string;
}) => apiClient.post("/outreach/send", data).then((res) => res.data);

export const getGmailStatus = () => apiClient.get("/integrations/gmail/status").then((res) => res.data);

export const getJobRankings = (jobId: string) =>
  apiClient.get(`/matching/job/${jobId}/rankings`).then((res) => res.data);