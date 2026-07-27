"use client";

import { useEffect, useState } from "react";

export function ScoreRing({ value, size = 140 }: { value: number; size?: number }) {
  const [animatedValue, setAnimatedValue] = useState(0);

  useEffect(() => {
    let frame: number;
    const duration = 900;
    const start = performance.now();

    const step = (now: number) => {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setAnimatedValue(eased * value);
      if (progress < 1) frame = requestAnimationFrame(step);
    };

    frame = requestAnimationFrame(step);
    return () => cancelAnimationFrame(frame);
  }, [value]);

  const radius = (size - 16) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (animatedValue / 100) * circumference;

  // Color shifts from pale mint (low score) to deep forest green (high score)
  const color = value >= 75 ? "var(--accent)" : value >= 45 ? "var(--accent-soft)" : "#a9c9b8";

  return (
    <div style={{ width: size, height: size, position: "relative" }}>
      <svg width={size} height={size} style={{ transform: "rotate(-90deg)" }}>
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="var(--paper-border)"
          strokeWidth={8}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={8}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{ transition: "stroke 0.3s ease" }}
        />
      </svg>
      <div
        style={{
          position: "absolute",
          inset: 0,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          flexDirection: "column",
        }}
      >
        <span style={{ fontSize: size * 0.22, fontWeight: 600, color: "var(--ink)" }}>
          {Math.round(animatedValue)}
        </span>
        <span style={{ fontSize: size * 0.09, color: "var(--ink-soft)" }}>/ 100</span>
      </div>
    </div>
  );
}