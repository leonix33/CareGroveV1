"use client";

import { useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";
import { api, type Recipient } from "@/lib/api";

type RequestRow = {
  id: number;
  provider_id: number;
  provider_name: string;
  recipient_alias: string;
  service: string;
  status: string;
  disclosure: string;
  met_need: boolean | null;
};

function Requests() {
  const params = useSearchParams();
  const preset = Number(params.get("provider") || 0);
  const [rows, setRows] = useState<RequestRow[]>([]);
  const [recipients, setRecipients] = useState<Recipient[]>([]);
  const [recipientId, setRecipientId] = useState<number>(0);
  const [service, setService] = useState("respite");
  const [includeHealth, setIncludeHealth] = useState(false);
  const [message, setMessage] = useState("");

  function load() {
    api<{ results: RequestRow[] }>("/api/requests").then((data) => setRows(data.results));
  }
  useEffect(() => {
    load();
    api<{ recipients: Recipient[] }>("/api/family/profile").then((profile) => {
      const active = profile.recipients.filter((row) => !row.archived);
      setRecipients(active);
      if (active[0]) setRecipientId(active[0].id);
    });
  }, []);

  async function send(e: React.FormEvent) {
    e.preventDefault();
    if (!preset) return;
    const created = await api<RequestRow>("/api/requests", {
      method: "POST",
      body: JSON.stringify({ provider_id: preset, recipient_id: recipientId, service, include_health: includeHealth }),
    });
    setMessage(`Request ${created.status}. The provider will see: ${created.disclosure}`);
    load();
  }

  async function outcome(id: number, met_need: boolean) {
    await api(`/api/requests/${id}/outcome`, { method: "POST", body: JSON.stringify({ met_need }) });
    load();
  }

  return (
    <main className="page">
      <h1>Connection requests</h1>
      {preset > 0 && (
        <form className="card" onSubmit={send}>
          <h2>Request a connection</h2>
          <label>Recipient</label>
          <select value={recipientId} onChange={(e) => setRecipientId(Number(e.target.value))}>
            {recipients.map((row) => <option key={row.id} value={row.id}>{row.alias}</option>)}
          </select>
          <label>Service</label>
          <select value={service} onChange={(e) => setService(e.target.value)}>
            <option value="respite">Respite</option>
            <option value="personal_care">Personal care</option>
            <option value="autism_services">Autism services</option>
            <option value="therapy">Therapy</option>
          </select>
          <label><input type="checkbox" style={{ width: "auto" }} checked={includeHealth} onChange={(e) => setIncludeHealth(e.target.checked)} /> Include diagnosis and support needs</label>
          <button className="btn" type="submit">Send request</button>
          {message && <p>{message}</p>}
        </form>
      )}
      <div className="list" style={{ marginTop: 16 }}>
        {rows.map((row) => (
          <article key={row.id} className="card">
            <strong>{row.provider_name}</strong>
            <p className="meta">{row.recipient_alias} · {row.service} · {row.status}</p>
            <p>{row.disclosure}</p>
            {row.status === "accepted" && (
              <div className="actions">
                <button className="btn" onClick={() => outcome(row.id, true)}>Service received, need met</button>
                <button className="btn secondary" onClick={() => outcome(row.id, false)}>Service received, need not met</button>
              </div>
            )}
          </article>
        ))}
      </div>
    </main>
  );
}

export default function RequestsPage() {
  return <Suspense><Requests /></Suspense>;
}
