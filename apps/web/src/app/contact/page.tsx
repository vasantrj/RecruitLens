"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { submitContactForm } from "@/lib/api-client";
import { Mail, Globe } from "lucide-react";

export default function ContactPage() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [subject, setSubject] = useState("");
  const [message, setMessage] = useState("");

  const mutation = useMutation({
    mutationFn: () => submitContactForm({ name, email, subject, message }),
    onSuccess: () => {
      setName("");
      setEmail("");
      setSubject("");
      setMessage("");
    },
  });

  return (
    <main className="page-wide">
      <h1 className="h1 mb-1 text-center">Contact the RecruitLensAI Developer</h1>
      <p className="text-sm text-muted text-center mb-8">Inquire &amp; Collaborate</p>

      <div className="grid md:grid-cols-2 gap-6 mb-6">
        {/* Contact Form */}
        <div className="card">
          <h2 className="h2 mb-4">Contact Form</h2>

          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Your Name"
            className="input mb-3"
          />
          <input
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            type="email"
            placeholder="Your Email"
            className="input mb-3"
          />
          <input
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
            placeholder="Subject"
            className="input mb-3"
          />
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Message"
            rows={6}
            className="input mb-4"
          />

          <button
            onClick={() => mutation.mutate()}
            disabled={!name || !email || !message || mutation.isPending}
            className="btn-primary w-full"
          >
            {mutation.isPending ? "Sending..." : "Submit Message"}
          </button>

          {mutation.isSuccess && (
            <p className="text-sm status-success mt-3">Message sent. Thanks for reaching out!</p>
          )}
          {mutation.isError && (
            <p className="text-sm status-danger mt-3">
              Failed to send — please try emailing directly instead.
            </p>
          )}
        </div>

        {/* Developer Profile */}
        <div className="card">
          <h2 className="h2 mb-4">Developer Profile</h2>

          <div className="flex items-center gap-4 mb-2">
            <img
              src="/vasant-avatar.jpeg"
              alt="Vasant Joshi"
              className="w-16 h-16 rounded-full object-cover"
              style={{ border: "2px solid var(--accent-bg)" }}
            />
            <div>
              <div className="font-medium">Vasant Joshi</div>
              <div className="text-sm text-muted">Data Science Intern</div>
            </div>
          </div>

          <p className="text-xs mb-4" style={{ color: "var(--accent)" }}>
            Open to freelance work &amp; collaboration opportunities
          </p>

          <div className="text-sm mb-4">
            <div className="font-medium mb-2">Key Focus Areas</div>
            <ul className="list-disc list-inside space-y-1 text-muted">
              <li>Ranking pipeline design</li>
              <li>Resume data structuring &amp; analytics</li>
              <li>Bias auditing logic</li>
            </ul>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="card-alt">
              <div className="text-xs text-muted mb-2">Commit Activity</div>
              <div className="flex items-end gap-1 h-12">
                {[30, 55, 20, 70, 45, 80, 60].map((h, i) => (
                  <div
                    key={i}
                    style={{
                      height: `${h}%`,
                      width: "10px",
                      background: "var(--accent-soft)",
                      borderRadius: "2px",
                    }}
                  />
                ))}
              </div>
            </div>
            <div className="card-alt">
              <div className="text-xs text-muted mb-2">Issue Resolution</div>
              <div className="flex items-end gap-1 h-12">
                {[40, 65, 50, 30, 75, 55, 90].map((h, i) => (
                  <div
                    key={i}
                    style={{
                      height: `${h}%`,
                      width: "10px",
                      background: "var(--accent)",
                      borderRadius: "2px",
                    }}
                  />
                ))}
              </div>
            </div>
          </div>
          {/* <p className="text-xs text-faint mt-2">
            Illustrative activity graphs — not connected to live data yet.
          </p> */}
        </div>
      </div>

      {/* Additional contact info */}
      <div className="card">
        <h2 className="h2 mb-1">Additional Contact Info</h2>
        <p className="text-sm text-muted mb-4">Alternative outreach channels</p>

        <div className="flex flex-wrap gap-3">
          <a
            href="https://github.com/vasantrj"
            target="_blank"
            className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm transition-opacity hover:opacity-80"
            style={{ background: "var(--accent-bg)", color: "var(--ink)" }}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="var(--accent)">
    <path d="M12 0C5.37 0 0 5.37 0 12c0 5.3 3.44 9.8 8.21 11.39.6.11.82-.26.82-.58 0-.29-.01-1.04-.02-2.04-3.34.73-4.04-1.61-4.04-1.61-.55-1.39-1.34-1.76-1.34-1.76-1.09-.75.08-.73.08-.73 1.21.08 1.84 1.24 1.84 1.24 1.07 1.84 2.81 1.3 3.5.99.11-.78.42-1.3.76-1.6-2.67-.3-5.47-1.33-5.47-5.93 0-1.31.47-2.38 1.24-3.22-.12-.3-.54-1.52.12-3.18 0 0 1.01-.32 3.3 1.23a11.5 11.5 0 0 1 6 0c2.29-1.55 3.3-1.23 3.3-1.23.66 1.66.24 2.88.12 3.18.77.84 1.24 1.91 1.24 3.22 0 4.61-2.81 5.63-5.48 5.93.43.37.81 1.1.81 2.22 0 1.6-.01 2.89-.01 3.29 0 .32.21.7.83.58C20.56 21.79 24 17.3 24 12c0-6.63-5.37-12-12-12z" />
  </svg>
            GitHub
          </a>
          <a
            href="https://www.linkedin.com/in/vasantjoshi/"
            target="_blank"
            className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm transition-opacity hover:opacity-80"
            style={{ background: "var(--accent-bg)", color: "var(--ink)" }}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="var(--accent)">
    <path d="M20.45 20.45h-3.56v-5.57c0-1.33-.03-3.04-1.85-3.04-1.86 0-2.14 1.45-2.14 2.94v5.67H9.34V9h3.41v1.56h.05c.48-.9 1.64-1.85 3.38-1.85 3.61 0 4.28 2.38 4.28 5.47v6.27zM5.34 7.43a2.06 2.06 0 1 1 0-4.12 2.06 2.06 0 0 1 0 4.12zM7.12 20.45H3.56V9h3.56v11.45zM22.22 0H1.77C.79 0 0 .77 0 1.73v20.54C0 23.23.79 24 1.77 24h20.45c.98 0 1.78-.77 1.78-1.73V1.73C24 .77 23.2 0 22.22 0z" />
  </svg>
            LinkedIn
          </a>
          <a
            href="mailto:vasantjoshi2580@gmail.com"
            className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm transition-opacity hover:opacity-80"
            style={{ background: "var(--accent-bg)", color: "var(--ink)" }}
          >
            <Mail size={18} style={{ color: "var(--accent)" }} />
            Email
          </a>
          <a
            href="https://vasantportfolio.com"
            target="_blank"
            className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm transition-opacity hover:opacity-80"
            style={{ background: "var(--accent-bg)", color: "var(--ink)" }}
          >
            <Globe size={18} style={{ color: "var(--accent)" }} />
            Portfolio
          </a>
        </div>
      </div>

      <p className="text-xs text-faint text-center mt-8">
        Designed for transparency. Built with integrity. · Vasant Joshi · {new Date().getFullYear()}
      </p>
    </main>
  );
}