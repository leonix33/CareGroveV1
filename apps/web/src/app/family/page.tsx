"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ProviderCard } from "@/components/ProviderCard";
import { api, SERVICE_LABELS, type ProviderCard as Card, type Recipient } from "@/lib/api";

export default function SuggestedPage() {
  const [recipients, setRecipients] = useState<Recipient[]>([]);
  const [recipientId, setRecipientId] = useState<number | null>(null);
  const [service, setService] = useState("respite");
  const [pool, setPool] = useState("");
  const [explanation, setExplanation] = useState("");
  const [results, setResults] = useState<Card[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api<{ recipients: Recipient[] }>("/api/family/profile")
      .then((profile) => {
        const active = profile.recipients.filter((row) => !row.archived);
        setRecipients(active);
        if (active[0]) setRecipientId(active[0].id);
      })
      .catch((err) => setError(err.message));
  }, []);

  useEffect(() => {
    if (!recipientId) return;
    api<{ pool: string; explanation: string; results: Card[] }>(
      `/api/family/suggestions?recipient_id=${recipientId}&service=${service}`,
    )
      .then((data) => {
        setPool(data.pool);
        setExplanation(data.explanation);
        setResults(data.results);
      })
      .catch((err) => setError(err.message));
  }, [recipientId, service]);

  return (
    <main className="page">
      <div className="toolbar">
        <label>
          Care for:
          <select value={recipientId ?? ""} onChange={(e) => setRecipientId(Number(e.target.value))}>
            {recipients.map((row) => (
              <option key={row.id} value={row.id}>{row.alias}</option>
            ))}
          </select>
        </label>
        <div className="nav">
          <Link href="/family/providers">All providers</Link>
          <Link href="/family" className="active">Suggested matches</Link>
        </div>
      </div>
      <form className="searchline" onSubmit={(e) => e.preventDefault()}>
        <input value={SERVICE_LABELS[service] || service} readOnly aria-label="Service" />
        <button className="btn" type="button">View Results</button>
      </form>
      <div className="pills">
        {["respite", "autism_services", "therapy", "personal_care"].map((id) => (
          <button key={id} className={`chip ${service === id ? "on" : ""}`} onClick={() => setService(id)}>
            {SERVICE_LABELS[id]}
          </button>
        ))}
        {pool === "premium" && <span className="chip on">Best Match</span>}
      </div>
      {explanation && (
        <div className="note">
          <span>{explanation}</span>
          <Link href="/family/providers">Switch to All providers →</Link>
        </div>
      )}
      {error && <p className="field-error">{error}</p>}
      <div style={{ marginTop: 16 }}>
        {results.map((provider) => <ProviderCard key={provider.id} provider={provider} />)}
        {results.length === 0 && !error && <p>No suitable providers for this service. Browse All providers without relaxing the criteria.</p>}
      </div>
      <p className="note" style={{ marginTop: 16 }}>Connect here, then arrange a meet-and-greet directly with the provider.</p>
    </main>
  );
}
