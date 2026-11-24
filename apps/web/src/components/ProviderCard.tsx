"use client";

import Link from "next/link";
import { useState } from "react";
import { api, photoSrc, SERVICE_LABELS, type ProviderCard as Card } from "@/lib/api";

export function ProviderCard({ provider, onChange }: { provider: Card; onChange?: () => void }) {
  const [saved, setSaved] = useState(provider.saved);
  const [busy, setBusy] = useState(false);
  const premium = provider.membership === "active" || provider.membership === "cancelling";
  const service = provider.match_reasons[0] || SERVICE_LABELS[provider.services[0]] || provider.services[0];

  async function toggleSave() {
    setBusy(true);
    try {
      if (saved) await api(`/api/family/saved/${provider.id}`, { method: "DELETE" });
      else await api(`/api/family/saved/${provider.id}`, { method: "POST" });
      setSaved(!saved);
      onChange?.();
    } finally {
      setBusy(false);
    }
  }

  return (
    <article className="card provider">
      {provider.photo ? (
        <img className="shot" src={photoSrc(provider.photo)} alt="" />
      ) : (
        <div className="shot" style={{ display: "grid", placeItems: "center", color: "#8a8175" }}>No photo</div>
      )}
      <div>
        <div className="badges">
          <h3>{provider.display_name}</h3>
          {provider.verified && <span className="badge">Verified</span>}
          {premium && <span className="badge gold">Premium Member</span>}
          {!premium && provider.membership === "free" && <span className="badge">Standard listing</span>}
        </div>
        <p className="meta">
          {provider.verified ? "Verified" : "Unverified"}
          {provider.distance_label ? ` · ${provider.distance_label}` : ""}
          {service ? ` · ${service}` : ""}
        </p>
        <div className="pills" style={{ margin: 0 }}>
          <span className="pill">Medicaid</span>
          <span className="pill">In-home</span>
        </div>
        <div className="actions">
          <button className="btn secondary" disabled={busy} onClick={toggleSave}>{saved ? "Saved" : "Save"}</button>
          <Link className="btn secondary" href={`/providers/${provider.id}`} style={{ textDecoration: "none" }}>View profile</Link>
          <Link className="btn secondary" href={`/providers/${provider.id}#score`} style={{ textDecoration: "none" }}>View Trust Score</Link>
          <Link className="btn" href={`/family/requests?provider=${provider.id}`} style={{ textDecoration: "none" }}>Request connection</Link>
        </div>
      </div>
      <div className="ring">
        {provider.score == null ? (
          <>
            <strong>—</strong>
            <span>UNAVAILABLE</span>
          </>
        ) : (
          <>
            <strong>{provider.score}</strong>
            <span>{(provider.score_label || "").toUpperCase()}</span>
          </>
        )}
      </div>
    </article>
  );
}
