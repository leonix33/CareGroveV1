"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";

type Saved = { id: number; display_name: string; state: string; score: number | null; score_label: string | null; available: boolean };

export default function SavedPage() {
  const [results, setResults] = useState<Saved[]>([]);

  function load() {
    api<{ results: Saved[] }>("/api/family/saved").then((data) => setResults(data.results));
  }
  useEffect(load, []);

  return (
    <main className="page">
      <h1>Saved providers</h1>
      <p className="lede">Only your family can see this list.</p>
      <div className="list">
        {results.map((row) => (
          <article key={row.id} className="card row">
            <div>
              <strong>{row.display_name}</strong>
              <p className="meta">{row.state} · {row.score ?? "Score unavailable"} {row.score_label || ""} · {row.available ? "Available" : "Unavailable"}</p>
            </div>
            <div className="actions">
              <Link className="btn secondary" href={`/providers/${row.id}`}>View profile</Link>
              <button className="ghost" onClick={async () => { await api(`/api/family/saved/${row.id}`, { method: "DELETE" }); load(); }}>Remove</button>
            </div>
          </article>
        ))}
        {results.length === 0 && <p>No saved providers yet.</p>}
      </div>
    </main>
  );
}
