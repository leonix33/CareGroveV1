"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export default function ScorePage() {
  const [profile, setProfile] = useState<{
    score: number | null;
    score_label: string | null;
    score_breakdown: { categories?: Record<string, number>; weights?: Record<string, number>; disclaimer?: string };
  } | null>(null);

  useEffect(() => {
    api<NonNullable<typeof profile>>("/api/provider/profile").then(setProfile);
  }, []);
  if (!profile) return <main className="page">Loading score…</main>;
  const categories = profile.score_breakdown.categories || {};
  const weights = profile.score_breakdown.weights || {};

  return (
    <main className="page">
      <h1>Trust Score</h1>
      <p className="lede">Platform standing and improvement guidance.</p>
      <section className="card" style={{ textAlign: "center" }}>
        <div className="score-ring" style={{ ["--p" as string]: profile.score ?? 0 }}>
          <div>
            <strong style={{ fontSize: 32 }}>{profile.score ?? "—"}</strong>
            <div>{profile.score_label || "Unavailable"}</div>
          </div>
        </div>
        <p>{profile.score_breakdown.disclaimer}</p>
      </section>
      <section className="card" style={{ marginTop: 16 }}>
        <h2>Category breakdown</h2>
        <div className="bars">
          {Object.entries(categories).map(([name, value]) => (
            <div key={name}>
              <div className="row">
                <span>{name} ({Math.round((weights[name] || 0) * 100)}%)</span>
                <span>{value}/100</span>
              </div>
              <div className="bar"><i style={{ width: `${Math.min(100, value)}%` }} /></div>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
