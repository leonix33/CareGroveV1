"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

type Row = { id: number; provider_name: string; alias: string; rating: number; body: string; status: string };

export default function AdminReviews() {
  const [rows, setRows] = useState<Row[]>([]);
  function load() { api<{ results: Row[] }>("/api/admin/reviews").then((data) => setRows(data.results)); }
  useEffect(load, []);

  async function decide(id: number, status: string) {
    await api(`/api/admin/reviews/${id}`, { method: "POST", body: JSON.stringify({ status, reason: status === "published" ? "Meets publication rules" : "Does not meet publication rules" }) });
    load();
  }

  return (
    <main className="page">
      <h1>Review approval</h1>
      <p className="lede">Only approved family reviews can be published or contribute to a public score.</p>
      {rows.map((row) => (
        <article key={row.id} className="card">
          <strong>{row.provider_name}</strong> · {row.alias} · {row.rating}/5 · {row.status}
          <p>{row.body}</p>
          <div className="actions">
            <button className="btn" onClick={() => decide(row.id, "published")}>Approve</button>
            <button className="btn secondary" onClick={() => decide(row.id, "rejected")}>Reject</button>
          </div>
        </article>
      ))}
    </main>
  );
}
