"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

type Row = { id: number; recipient_alias: string; service: string; status: string; disclosure: string };

export default function ProviderRequests() {
  const [rows, setRows] = useState<Row[]>([]);
  function load() {
    api<{ results: Row[] }>("/api/requests").then((data) => setRows(data.results));
  }
  useEffect(load, []);

  async function decide(id: number, action: "accept" | "decline") {
    await api(`/api/requests/${id}/${action}`, { method: "POST" });
    load();
  }

  return (
    <main className="page">
      <h1>Family requests</h1>
      {rows.map((row) => (
        <article key={row.id} className="card">
          <strong>{row.recipient_alias}</strong> · {row.service} · {row.status}
          <p>{row.disclosure}</p>
          {row.status === "pending" && (
            <div className="actions">
              <button className="btn" onClick={() => decide(row.id, "accept")}>Accept</button>
              <button className="btn secondary" onClick={() => decide(row.id, "decline")}>Decline</button>
            </div>
          )}
        </article>
      ))}
    </main>
  );
}
