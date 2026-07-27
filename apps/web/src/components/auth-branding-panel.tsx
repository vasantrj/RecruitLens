"use client";

export function AuthBrandingPanel() {
  return (
    <div
      className="hidden md:flex md:w-1/2 flex-col p-10 relative overflow-hidden"
      style={{
        backgroundImage: "url('/auth-bg.png')",
        backgroundSize: "cover",
        backgroundPosition: "center",
      }}
    >
      <div className="flex-1 flex flex-col items-center justify-center text-center relative z-10">
        <h1
          className="text-4xl font-bold mb-2"
          style={{ color: "#1c2624" }}
        >
          RecruitLens<span style={{ color: "var(--accent)" }}>AI</span>
        </h1>

        <div style={{ height: "9rem" }} />

        <p className="text-xl font-semibold" style={{ color: "#1c2624" }}>
          Focus on the right candidate.
        </p>
        <p className="text-sm mt-2 max-w-xs" style={{ color: "#5b6764" }}>
          AI-powered resume screening, matching, and recruiter outreach — built to cut through the noise.
        </p>
      </div>

      <div className="text-xs relative z-10" style={{ color: "#96a19d" }}>
        Built by Vasant Joshi · {new Date().getFullYear()}
      </div>
    </div>
  );
}