const entries = [
  {
    version: "v2.0",
    date: "2026",
    items: [
      "Personal and Company account types with dedicated flows",
      "Bulk resume screening with shortlist selection and bulk email outreach",
      "Interview preparation questions for personal accounts",
      "Duplicate application detection",
      "Bias/fairness auditing on match scores",
      "Inactivity auto-logout and password reset flow",
    ],
  },
  {
    version: "v1.0",
    date: "2026",
    items: [
      "Structured resume and job description parsing",
      "Skill taxonomy normalization",
      "Two-stage semantic matching (bi-encoder + cross-encoder reranker)",
      "Role-only matching without a job description",
      "GitHub and portfolio link verification",
      "Single-candidate email outreach via connected Gmail",
    ],
  },
];

export default function ChangelogPage() {
  return (
    <main className="page">
      <h1 className="h1 mb-6">What's New</h1>

      <div className="space-y-6">
        {entries.map((entry) => (
          <div key={entry.version} className="card">
            <div className="flex items-baseline gap-2 mb-3">
              <h2 className="h2">{entry.version}</h2>
              <span className="text-xs text-faint">{entry.date}</span>
            </div>
            <ul className="text-sm text-muted list-disc list-inside space-y-1">
              {entry.items.map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
          </div>
        ))}
      </div>
      <p className="text-xs text-faint text-center mt-8">
        Designed for transparency. Built with integrity. · Vasant Joshi · {new Date().getFullYear()}
      </p>
    </main>
  );
}