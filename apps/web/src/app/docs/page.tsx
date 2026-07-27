export default function DocsPage() {
  return (
    <main className="page">
      <h1 className="h1 mb-6">Docs &amp; Help</h1>

      <div className="card mb-6">
        <h2 className="h2 mb-3">Getting started (Personal accounts)</h2>
        <ol className="text-sm text-muted list-decimal list-inside space-y-1">
          <li>Register with the "Personal" account type</li>
          <li>Create a job — either paste a full job description or just type a role title</li>
          <li>Upload your resume to see your match score</li>
          <li>Generate AI feedback and interview preparation from the candidate detail page</li>
        </ol>
      </div>

      <div className="card mb-6">
        <h2 className="h2 mb-3">Getting started (Company accounts)</h2>
        <ol className="text-sm text-muted list-decimal list-inside space-y-1">
          <li>Register with the "Company" account type</li>
          <li>Create a job, then choose Single Resume or Bulk Resumes screening</li>
          <li>For bulk: upload multiple resumes, adjust the shortlist count, and preview before sending</li>
          <li>Connect your Gmail account once to enable email outreach</li>
          <li>Send accept/reject emails to your shortlisted and remaining candidates in one action</li>
        </ol>
      </div>

      <div className="card">
        <h2 className="h2 mb-3">Frequently asked questions</h2>
        <div className="text-sm space-y-3">
          <div>
            <p className="font-medium mb-1" style={{ color: "var(--ink)" }}>
              Why is my score lower than expected?
            </p>
            <p className="text-muted">
              Skill matching is taxonomy-based — it may not credit implied skills that aren't
              explicitly listed on your resume. Check the AI feedback for specific gaps.
            </p>
          </div>
          <div>
            <p className="font-medium mb-1" style={{ color: "var(--ink)" }}>
              Do you store my resume permanently?
            </p>
            <p className="text-muted">
              Resume data is stored only to power your own matches and is not shared with third
              parties.
            </p>
          </div>
          <div>
            <p className="font-medium mb-1" style={{ color: "var(--ink)" }}>
              Whose Gmail sends the outreach emails?
            </p>
            <p className="text-muted">
              Your own — each company account connects its own Gmail via OAuth. Emails are never
              sent from a shared system address.
            </p>
          </div>
        </div>
      </div>
      <p className="text-xs text-faint text-center mt-8">
        Designed for transparency. Built with integrity. · Vasant Joshi · {new Date().getFullYear()}
      </p>
    </main>
  );
}