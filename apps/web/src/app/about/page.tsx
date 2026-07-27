export default function AboutPage() {
  return (
    <main>
      {/* Hero */}
      <div
        className="relative"
        // style={{
        //   backgroundImage: "url('/auth-bg.png')",
        //   backgroundSize: "cover",
        //   backgroundPosition: "center",
        //   paddingTop: "3rem",
        //   paddingBottom: "3rem",
        // }}
      >
        <div className="relative z-10 text-center px-4">
          <h1 className="text-3xl font-bold mb-2" style={{ color: "var(--ink)" }}>
            About RecruitLens<span style={{ color: "var(--accent)" }}>AI</span>
          </h1>
          <p className="text-sm max-w-lg mx-auto" style={{ color: "var(--ink-soft)" }}>
            An AI-powered recruiting platform that matches candidates to roles using a
            multi-stage retrieval and ranking pipeline — not keyword matching.
          </p>
        </div>
      </div>

      <div style={{ maxWidth: "68rem", margin: "0 auto", padding: "2.5rem 1.5rem" }}>
        {/* 3-column info grid */}
        <div className="grid md:grid-cols-3 gap-5 mb-8">
          <div className="card">
            <h2 className="h2 mb-3">What this is</h2>
            <ul className="text-sm text-muted list-disc list-inside space-y-1">
              <li>AI-powered technical matching</li>
              <li>Multi-stage pipeline — resume &amp; JD parsing, skill normalization</li>
              <li>GitHub-verified technical signal</li>
              <li>Explainable match score, not a black box</li>
            </ul>
          </div>

          <div className="card">
            <h2 className="h2 mb-3">Core features</h2>
            <ul className="text-sm text-muted space-y-2">
              <li>
                <span className="font-medium" style={{ color: "var(--ink)" }}>Skill taxonomy</span> —
                maps similar skills precisely.
              </li>
              <li>
                <span className="font-medium" style={{ color: "var(--ink)" }}>Explainable feedback</span> —
                transparent reasoning per match.
              </li>
              <li>
                <span className="font-medium" style={{ color: "var(--ink)" }}>Bias auditing</span> —
                tests score stability under redaction.
              </li>
              <li>
                <span className="font-medium" style={{ color: "var(--ink)" }}>Bulk screening</span> —
                score and shortlist many candidates at once.
              </li>
              <li>
                <span className="font-medium" style={{ color: "var(--ink)" }}>GitHub verification</span> —
                confirms skills against real activity.
              </li>
            </ul>
          </div>

          <div className="card">
            <h2 className="h2 mb-3">Platform insights</h2>
            <ul className="text-sm text-muted list-disc list-inside space-y-1">
              <li>Structured resume &amp; JD parsing</li>
              <li>Two-stage semantic matching (bi-encoder + reranker)</li>
              <li>Role-only matching — no JD text required</li>
              <li>Portfolio &amp; GitHub verification</li>
              <li>Bulk screening &amp; shortlist management</li>
              <li>Duplicate application detection</li>
            </ul>
          </div>
        </div>

        {/* How it works */}
        <div className="card mb-8">
          <h2 className="h2 mb-4">How it works</h2>
          <div className="grid md:grid-cols-4 gap-4 text-sm">
            {[
              { step: "1", title: "Parse", desc: "Resume and JD are extracted into structured, comparable data." },
              { step: "2", title: "Normalize", desc: "Skills are mapped to a shared taxonomy — synonyms included." },
              { step: "3", title: "Match", desc: "Semantic embeddings and a cross-encoder reranker score fit." },
              { step: "4", title: "Explain", desc: "An LLM writes the reasoning behind the score in plain language." },
            ].map((s) => (
              <div key={s.step}>
                <div
                  className="w-8 h-8 rounded-full flex items-center justify-center font-semibold mb-2"
                  style={{ background: "var(--accent-bg)", color: "var(--accent)" }}
                >
                  {s.step}
                </div>
                <div className="font-medium mb-1" style={{ color: "var(--ink)" }}>{s.title}</div>
                <div className="text-muted">{s.desc}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Tech stack */}
        <div className="card mb-8">
          <h2 className="h2 mb-3">Built with</h2>
          <div className="flex flex-wrap gap-2">
            {[
              "FastAPI", "PostgreSQL", "Next.js", "TypeScript", "Sentence Transformers",
              "Groq LLM", "Docker", "GitHub API", "Gmail API",
            ].map((tech) => (
              <span key={tech} className="badge badge-accent">
                {tech}
              </span>
            ))}
          </div>
        </div>

        {/* Honesty note */}
        <div className="card mb-6">
          <h2 className="h2 mb-2">A note on honesty</h2>
          <p className="text-sm text-muted">
            This project documents its own limitations openly — including where matching is
            heuristic rather than perfectly calibrated, and where features are still evolving.
            We'd rather be upfront about what this tool does and doesn't do yet than oversell it.
          </p>
        </div>

        <p className="text-xs text-faint text-center">
          Designed for transparency. Built with integrity. · Vasant Joshi · {new Date().getFullYear()}
        </p>
      </div>
    </main>
  );
}