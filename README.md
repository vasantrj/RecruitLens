# RecruitLens

An AI-powered recruiting platform that matches candidates to roles using a multi-stage retrieval and ranking pipeline — not keyword matching. Built end-to-end: structured resume/JD parsing, taxonomy-normalized skill matching, semantic embeddings, cross-encoder reranking, GitHub-verified technical signal, explainable AI recruiter feedback, and real email outreach through a recruiter's own Gmail account.

## Why this exists

Most resume-screening demos compute one cosine-similarity number between a resume and a job description and call it a match score. That approach can't explain itself, can't handle synonyms or paraphrasing well, and gives no insight into *why* a candidate scored the way they did.

RecruitLens instead separates the problem into stages — extract structure, normalize skills against a taxonomy, embed and retrieve semantically, rerank with a cross-encoder, and combine everything into an explainable, weighted score with a full breakdown. An LLM then explains the score in plain language; it never sets the score itself.

## Core features

- **Structured resume & JD parsing** — LLM-based extraction (skills, experience, education, titles) instead of raw keyword matching
- **Skill taxonomy normalization** — "ML", "Machine Learning", and "AI/ML" all resolve to one canonical skill
- **Two-stage semantic matching** — bi-encoder embeddings for fast comparison, cross-encoder reranking for precision
- **Role-only matching** — type just a job title (e.g. "Data Science Intern") and get a realistic, LLM-synthesized requirements profile with no JD text required
- **Explainable AI feedback** — strengths, gaps, a hire recommendation, and targeted interview questions, all grounded in the structured score breakdown
- **Portfolio & GitHub analysis** — extracts links (including hyperlinks hidden behind text like "GitHub") from resumes, and pulls live GitHub data (repos, languages, stars, README quality) into a technical signal score
- **Bias/fairness audit** — recomputes the match score with candidate name, gendered pronouns, and identity-signal words redacted, and reports the score delta
- **Real email outreach** — connects a recruiter's own Gmail via OAuth, with a mandatory preview-then-confirm step before any email is sent
- **Full-stack, containerized** — one `docker compose up` runs the entire system

## Architecture

```
                    ┌─────────────────┐
                    │   Next.js Web   │
                    └────────┬────────┘
                             │ REST
                    ┌────────▼────────┐
                    │  FastAPI Backend │
                    └────────┬────────┘
              ┌──────────────┼──────────────┐
     ┌────────▼───────┐ ┌────▼────┐ ┌───────▼──────┐
     │   PostgreSQL    │ │  MinIO  │ │ External APIs │
     │ (jobs, candi-   │ │ (resume │ │ Groq (LLM)    │
     │ dates, scores)  │ │  files) │ │ GitHub API    │
     └─────────────────┘ └─────────┘ │ Gmail API     │
                                     └──────────────┘
```

### Matching pipeline

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
LLM explanation layer (strengths, gaps, recommendation, interview questions)
```

## Tech stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, SQLAlchemy, Alembic |
| Database | PostgreSQL |
| File storage | MinIO (S3-compatible) |
| ML / NLP | sentence-transformers (bi-encoder + cross-encoder), spaCy |
| LLM | Groq (Llama 3.3) — structured extraction, feedback generation, role-profile synthesis |
| Frontend | Next.js 14 (App Router), TypeScript, Tailwind CSS, TanStack Query |
| Integrations | GitHub REST API, Gmail API (OAuth2) |
| Infrastructure | Docker, Docker Compose |

## Getting started

### Prerequisites
- Docker Desktop
- A [Groq API key](https://console.groq.com)
- A GitHub personal access token (no scopes needed — public data only)
- A Google Cloud OAuth client (Web application type) for Gmail sending

### Setup

1. Clone the repo and create `infra/.env`:
```
GROQ_API_KEY=your_groq_key
GITHUB_TOKEN=your_github_token
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/integrations/gmail/callback
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

5. (Optional) Connect Gmail for email outreach — visit http://localhost:8000/integrations/gmail/connect and follow the OAuth flow.

### Everyday use

| Task | Command |
|---|---|
| Start everything | `cd infra && docker compose up -d` |
| Rebuild after code changes | `docker compose up --build -d` |
| Stop everything (keeps data) | `docker compose down` |
| View logs | `docker compose logs -f api` |
| Run a new migration | `docker exec -it recruitlens_api alembic upgrade head` |

## Known limitations

- **Taxonomy-based skill matching is exact/alias-based, not inferential.** A candidate with Scikit-learn experience and a Data Science internship title won't automatically be credited with "Machine Learning" unless it's stated explicitly or aliased in the taxonomy. This is a deliberate simplification — a production system would add semantic skill inference (checking embedding similarity between candidate skills and required skills, not just exact/alias matches).
- **Match score weights are manually tuned, not learned.** The scoring formula combines skill overlap, experience match, title similarity, and reranker score with hand-set weights. A learning-to-rank model trained on labeled (resume, JD, human judgment) data would let these weights be learned rather than guessed — left as a natural next step once a labeled dataset exists.
- **GitHub technical signal score is a heuristic, not a rigorous metric.** It rewards repo count, stars, language diversity, and README presence with hand-picked point values. It's a useful directional signal, not a calibrated measure of skill.
- **Bias audit covers name/pronoun/gender-word redaction only.** It does not test for other protected characteristics (age, disability, etc.) and is a starting point for fairness testing, not a certification of fairness.
- **PDF parsing quality varies** with resume formatting — heavily designed, multi-column, or scanned/image-based resumes may extract text poorly.

## Roadmap / possible extensions

- Learning-to-rank model trained on recruiter feedback (thumbs up/down on rankings)
- Multi-tenant workspaces with authentication
- Async job processing (Celery + Redis) for bulk resume screening at scale
- Corpus-verified role profiles (cross-referencing real job postings, not just LLM-generated ones)
- Expanded skill taxonomy sourced from ESCO or O*NET

## License

This is a personal/portfolio project. Feel free to explore the code for learning purposes.