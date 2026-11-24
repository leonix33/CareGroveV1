"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

type Row = { id: number; display_name: string; membership: string; payment_status: string; paid_through: string | null; score: number | null; email: string };

export default function Subscriptions() {
  const [rows, setRows] = useState<Row[]>([]);
  useEffect(() => { api<{ results: Row[] }>("/api/admin/providers").then((data) => setRows(data.results)); }, []);
  return (
    <main className="page">
      <h1>Provider subscriptions</h1>
      <p className="lede">Staff can inspect subscription state. Billing never changes Trust Score.</p>
      {rows.map((row) => (
        <article key={row.id} className="card row">
          <div>
            <strong>{row.display_name}</strong>
            <p className="meta">{row.email} · {row.membership} · {row.payment_status} · through {row.paid_through || "—"}</p>
          </div>
          <span>Score {row.score ?? "—"}</span>
        </article>
      ))}
    </main>
  );
}
