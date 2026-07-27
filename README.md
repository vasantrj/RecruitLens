<div align="center">

# RecruitLensAI

</div>

An AI-powered recruiting platform that matches candidates to roles using a multi-stage retrieval and ranking pipeline — not keyword matching. Built end-to-end with dual account types (personal job seekers and hiring companies), structured resume/JD parsing, taxonomy-normalized skill matching, semantic reranking, GitHub-verified technical signal, explainable AI feedback, bulk screening, and real email outreach through a recruiter's own Gmail account.

## Why this exists

Most resume-screening demos compute one cosine-similarity number between a resume and a job description and call it a match score. That approach can't explain itself, can't handle synonyms or paraphrasing well, and gives no insight into *why* a candidate scored the way they did.

RecruitLensAI instead separates the problem into stages — extract structure, normalize skills against a taxonomy, embed and retrieve semantically, rerank with a cross-encoder, and combine everything into an explainable, weighted score with a full breakdown. An LLM then explains the score in plain language; it never sets the score itself.

## Who it's for

**Personal accounts** — job seekers who want to check how their resume matches a role, get AI feedback on gaps, and generate interview preparation questions. No email outreach section — it's not needed for this use case.

**Company accounts** — recruiters who want to screen one or many resumes against a job, shortlist top candidates, and send accept/reject emails in bulk, all from their own connected Gmail.

## Core features

### Matching engine
- Structured resume & JD parsing (LLM-based extraction, not keyword matching)
- Skill taxonomy normalization — "ML", "Machine Learning", "AI/ML" resolve to one canonical skill
- Two-stage semantic matching — bi-encoder retrieval + cross-encoder reranking
- Role-only matching — type a job title, no JD text required
- GitHub-verified technical signal, folded into the final score as a bonus
- Bias/fairness audit — recomputes the score with name/gendered-pronoun redaction and reports the delta

### AI feedback
- Explainable recruiter feedback (strengths, gaps, recommendation) grounded in the structured score, not hallucinated
- Interview preparation — 10+ technical, behavioral, and role-specific questions per candidate

### Screening workflows
- **Single resume** — upload one candidate, get an animated score reveal and full breakdown
- **Bulk resumes** (company accounts) — multi-file upload, automatic ranking, adjustable shortlist threshold, duplicate-application detection across your own jobs
- CSV export of shortlisted candidates

### Outreach
- Company accounts connect their own Gmail via OAuth2 — every email is sent from the recruiter's real address, never a shared system account
- Editable email preview before sending, both for single candidates and bulk batches
- Three templates: Invite to Interview, Move to Next Round, Reject

### Accounts & security
- JWT-based auth with Personal/Company account types
- Profile editing (display name, password)
- Forgot/reset password flow
- Inactivity auto-logout with a warning toast before logging out
- A working contact form that emails the developer directly (SMTP)

## Architecture
<div align="center">
```
                      ┌─────────────────┐
                      │   Next.js Web   │
                      └────────┬────────┘
                               │ REST + JWT
                      ┌────────▼─────────┐
                      │  FastAPI Backend │
                      └────────┬─────────┘
              ┌────────────────┼───────────────┐
     ┌────────▼────────┐  ┌────▼────┐  ┌───────▼───────┐
     │   PostgreSQL    │  │  MinIO  │  │ External APIs │
     │ (users, jobs,   │  │ (resume │  │ Groq (LLM)    │
     │ candidates,     │  │  files) │  │ GitHub API    │
     │ matches, tokens)│  └─────────┘  │ Gmail API     │
     └─────────────────┘               └───────────────┘
```
</div>

### Matching pipeline
<div align="center">
```
Resume/JD text
     │
     ▼
Structured extraction (LLM, JSON schema)
     │
     ▼
Skill taxonomy normalization
     │
     ▼
Multi-vector embeddings (skills / title / experience, separately)
     │
     ▼
Cross-encoder reranking (JD + resume evaluated jointly)
     │
     ▼
Weighted composite score + GitHub signal bonus
     │
     ▼
LLM explanation layer (strengths, gaps, recommendation, interview prep)
```
</div>

## Tech stack

<div align="center">
| Layer | Technology |
|---|---|
| Backend | FastAPI, SQLAlchemy, Alembic |
| Auth | JWT (python-jose), bcrypt password hashing |
| Database | PostgreSQL |
| File storage | MinIO (S3-compatible) |
| ML / NLP | sentence-transformers (bi-encoder + cross-encoder), spaCy |
| LLM | Groq (Llama 3.3) — extraction, feedback, role-profile synthesis, interview prep |
| Frontend | Next.js 14 (App Router), TypeScript, Tailwind CSS, TanStack Query |
| Integrations | GitHub REST API, Gmail API (OAuth2), Gmail SMTP (contact form) |
| Infrastructure | Docker, Docker Compose |
</div>

## Getting started

### Prerequisites
- Docker Desktop
- A [Groq API key](https://console.groq.com)
- A GitHub personal access token (no scopes needed — public data only)
- A Google Cloud OAuth client (Web application type) for Gmail sending
- A Gmail account with an App Password, for the contact form

### Setup

1. Clone the repo and create `infra/.env`:
```
GROQ_API_KEY=your_groq_key
GITHUB_TOKEN=your_github_token
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/integrations/gmail/callback
JWT_SECRET_KEY=a_long_random_secret
CONTACT_EMAIL_ADDRESS=your_contact_email@gmail.com
CONTACT_EMAIL_APP_PASSWORD=your_gmail_app_password
```

2. Start the stack:
```bash
cd infra
docker compose up -d
```

3. Run database migrations (first time only):
```bash
docker exec -it recruitlens_api alembic upgrade head
```

4. Open the app:
- Frontend: http://localhost:3000
- API docs: http://localhost:8000/docs
- MinIO console: http://localhost:9001 (`minioadmin` / `minioadmin`)

5. Register an account (Personal or Company), then, for Company accounts, connect Gmail from the candidate detail page or bulk screening page to enable email outreach.

### Everyday use

| Task | Command |
|---|---|
| Start everything | `cd infra && docker compose up -d` |
| Rebuild after code changes | `docker compose up --build -d` |
| Stop everything (keeps data) | `docker compose down` |
| View logs | `docker compose logs -f api` |
| Run a new migration | `docker exec -it recruitlens_api alembic upgrade head` |

## Known limitations

- **Taxonomy-based skill matching is exact/alias-based, not inferential.** A candidate with Scikit-learn experience and a Data Science internship title won't automatically be credited with "Machine Learning" unless it's stated explicitly or aliased in the taxonomy.
- **Match score weights are manually tuned, not learned.** A learning-to-rank model trained on labeled (resume, JD, human judgment) data would let these weights be learned rather than hand-set — a natural next step once labeled data exists.
- **GitHub technical signal score is a heuristic**, not a calibrated measure of skill — it rewards repo count, stars, language diversity, and README presence with hand-picked point values.
- **Bias audit covers name/pronoun/gender-word redaction only** — a starting point for fairness testing, not a certification of fairness.
- **Commit activity / issue resolution graphs on the Contact page are illustrative** — not connected to live GitHub data.
- **PDF parsing quality varies** with resume formatting — heavily designed, multi-column, or scanned/image-based resumes may extract text poorly.
- **Full-rankings export is CSV-only, and limited to shortlisted candidates in bulk screening** — a full-list export and a PDF option are on the roadmap.

## License

This is a personal project. Feel free to explore the code for learning purposes.

<div align="center">

**If this project helped you or you found it interesting, consider giving it a ⭐**

</div>