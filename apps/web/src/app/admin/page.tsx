"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export default function AdminHome() {
  const [data, setData] = useState<{ families: number; providers: number; approved_providers: number; verified_providers: number; requests: Record<string, number> } | null>(null);
  useEffect(() => { api<NonNullable<typeof data>>("/api/admin/overview").then(setData); }, []);
  if (!data) return <main className="page">Loading staff overview…</main>;
  return (
    <main className="page">
      <h1>Staff workspace</h1>
      <div className="role-grid">
        <div className="card"><strong>{data.families}</strong><p>Families</p></div>
        <div className="card"><strong>{data.providers}</strong><p>Providers</p></div>
        <div className="card"><strong>{data.approved_providers}</strong><p>Approved listings</p></div>
        <div className="card"><strong>{data.verified_providers}</strong><p>Published scores</p></div>
      </div>
      <section className="card">
        <h2>Requests</h2>
        <p>Pending {data.requests.pending || 0} · Accepted {data.requests.accepted || 0} · Declined {data.requests.declined || 0} · Completed {data.requests.completed || 0}</p>
      </section>
    </main>
  );
}
