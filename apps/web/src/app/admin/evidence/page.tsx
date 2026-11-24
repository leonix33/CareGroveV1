"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

type Row = { id: number; provider_name: string; category: string; status: string; file_name: string | null };

export default function AdminEvidence() {
  const [rows, setRows] = useState<Row[]>([]);
  function load() { api<{ results: Row[] }>("/api/admin/evidence").then((data) => setRows(data.results)); }
  useEffect(load, []);

  async function decide(id: number, status: string) {
    await api(`/api/admin/evidence/${id}`, { method: "POST", body: JSON.stringify({ status, note: "Staff review recorded" }) });
    load();
  }

  return (
    <main className="page">
      <h1>Evidence review</h1>
      {rows.map((row) => (
        <article key={row.id} className="card row">
          <div>
            <strong>{row.provider_name}</strong>
            <p className="meta">{row.category} · {row.file_name || "no file"} · {row.status}</p>
          </div>
          <div className="actions">
            <button className="btn" onClick={() => decide(row.id, "verified")}>Verify</button>
            <button className="btn secondary" onClick={() => decide(row.id, "rejected")}>Reject</button>
          </div>
        </article>
      ))}
    </main>
  );
}
