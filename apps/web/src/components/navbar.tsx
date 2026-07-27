"use client";

import { useState, useMemo } from "react";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { getCurrentUser, listJobs } from "@/lib/api-client";

export function Navbar() {
  const router = useRouter();
  const [profileOpen, setProfileOpen] = useState(false);
  const [notifOpen, setNotifOpen] = useState(false);
  const [helpOpen, setHelpOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchFocused, setSearchFocused] = useState(false);

  const { data: user } = useQuery({
    queryKey: ["currentUser"],
    queryFn: getCurrentUser,
    retry: false,
  });

  const { data: jobs } = useQuery({
    queryKey: ["jobs"],
    queryFn: listJobs,
  });

  const filteredJobs = useMemo(() => {
    if (!searchQuery.trim() || !jobs) return [];
    return jobs
      .filter((j: any) => j.title.toLowerCase().includes(searchQuery.toLowerCase()))
      .slice(0, 6);
  }, [searchQuery, jobs]);

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("account_type");
    router.push("/login");
  };

  const initials = user?.email ? user.email.slice(0, 2).toUpperCase() : "?";

  return (
    <>
      <nav
        className="navbar flex items-center gap-6 px-6 py-3"
        style={{ background: "var(--paper-card)" }}
      >
        {/* Branding */}
        <a href="/" className="flex items-center gap-2 shrink-0">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="9" stroke="var(--accent)" strokeWidth="1.5" />
            <circle cx="12" cy="12" r="5.5" stroke="var(--accent-soft)" strokeWidth="1.5" />
            <circle cx="12" cy="12" r="2" fill="var(--accent)" />
          </svg>
          <span className="font-semibold" style={{ color: "var(--ink)" }}>
            RecruitLens<span style={{ color: "var(--accent)" }}>AI</span>
          </span>
        </a>

        {/* Nav links group */}
        <div className="hidden md:flex items-center gap-5">
          <a href="/docs" className="nav-link">Docs</a>
          <a href="/changelog" className="nav-link">What&apos;s New</a>
          <a href="/about" className="nav-link">About</a>
          <a href="/contact" className="nav-link">Contact</a>
        </div>

        {/* Search */}
        <div className="relative flex-1 max-w-sm ml-auto">
          <input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onFocus={() => setSearchFocused(true)}
            onBlur={() => setTimeout(() => setSearchFocused(false), 150)}
            placeholder="Search your jobs..."
            className="input text-sm"
          />
          {searchFocused && searchQuery.trim() && (
            <div
              className="absolute left-0 right-0 mt-1 rounded-lg border shadow-lg z-20 overflow-hidden"
              style={{ background: "var(--paper-card)", borderColor: "var(--paper-border)" }}
            >
              {filteredJobs.length === 0 && (
                <p className="text-sm text-faint p-3">No matching jobs.</p>
              )}
              {filteredJobs.map((job: any) => (
                <a
                  key={job.id}
                  href={`/jobs/${job.id}`}
                  onMouseDown={(e) => {
                    e.preventDefault();
                    setSearchQuery("");
                    setSearchFocused(false);
                    router.push(`/jobs/${job.id}`);
                  }}
                  className="block px-3 py-2 text-sm hover:opacity-80 cursor-pointer"
                  style={{ color: "var(--ink)" }}
                >
                  {job.title}
                </a>
              ))}
            </div>
          )}
        </div>

        {/* Utility icons + profile */}
        <div className="flex items-center gap-2 relative shrink-0">
          <button onClick={() => setHelpOpen(true)} className="icon-btn" aria-label="Help">
            ?
          </button>

          <div className="relative">
            <button
              onClick={() => setNotifOpen(!notifOpen)}
              className="icon-btn"
              aria-label="Notifications"
            >
              🔔
            </button>
            {notifOpen && (
              <div
                className="absolute right-0 mt-2 w-72 rounded-lg border p-3 text-sm shadow-lg z-10 space-y-3"
                style={{ background: "var(--paper-card)", borderColor: "var(--paper-border)" }}
              >
                <div>
                  <p className="font-medium mb-1">🔒 Privacy</p>
                  <p className="text-muted text-xs">
                    We never store your personal resume data beyond what's needed to run your matches.
                  </p>
                </div>
                <div>
                  <p className="font-medium mb-1">🚧 In development</p>
                  <p className="text-muted text-xs">
                    Full-rankings PDF export is still being built — CSV export of shortlisted candidates is available now.
                  </p>
                </div>
              </div>
            )}
          </div>

          <div className="relative">
            <button onClick={() => setProfileOpen(!profileOpen)} className="avatar-btn">
              {initials}
            </button>
            {profileOpen && (
              <div
                className="absolute right-0 mt-2 w-52 rounded-lg border shadow-lg z-10 overflow-hidden"
                style={{ background: "var(--paper-card)", borderColor: "var(--paper-border)" }}
              >
                <div className="px-4 py-2 text-xs text-faint border-b" style={{ borderColor: "var(--paper-border)" }}>
                  {user?.email}
                </div>
                <a
                  href="/profile"
                  className="block px-4 py-2 text-sm hover:opacity-80"
                  style={{ color: "var(--ink)" }}
                >
                  Edit Profile
                </a>
                <button
                  onClick={handleLogout}
                  className="block w-full text-left px-4 py-2 text-sm hover:opacity-80"
                  style={{ color: "var(--danger)" }}
                >
                  Logout
                </button>
              </div>
            )}
          </div>
        </div>
      </nav>

      {/* Help modal */}
      {helpOpen && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center"
          style={{ background: "rgba(0,0,0,0.3)" }}
          onClick={() => setHelpOpen(false)}
        >
          <div className="card max-w-md m-4" onClick={(e) => e.stopPropagation()}>
            <div className="flex justify-between items-center mb-3">
              <h2 className="h2">Quick Reference</h2>
              <button onClick={() => setHelpOpen(false)} className="text-sm text-faint">
                ✕
              </button>
            </div>
            <ul className="text-sm text-muted space-y-2">
              <li><span className="font-medium" style={{ color: "var(--ink)" }}>Create a job:</span> Home page → Full JD or Role Title Only</li>
              <li><span className="font-medium" style={{ color: "var(--ink)" }}>Single resume:</span> Open a job → Upload a Resume</li>
              <li><span className="font-medium" style={{ color: "var(--ink)" }}>Bulk screening:</span> Company accounts → Bulk Resumes on a job</li>
              <li><span className="font-medium" style={{ color: "var(--ink)" }}>Search:</span> Use the search bar to jump to any of your jobs</li>
              <li><span className="font-medium" style={{ color: "var(--ink)" }}>Full docs:</span> See the Docs link in the navbar</li>
            </ul>
          </div>
        </div>
      )}
    </>
  );
}