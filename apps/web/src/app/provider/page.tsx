"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { api, photoSrc } from "@/lib/api";

type Profile = {
  display_name: string;
  photo: string;
  state: string;
  score: number | null;
  score_label: string | null;
  verified: boolean;
  membership: string;
  evidence: { category: string; status: string }[];
};

export default function ProviderHome() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [requests, setRequests] = useState<{ id: number; status: string; recipient_alias: string; service: string }[]>([]);

  useEffect(() => {
    api<Profile>("/api/provider/profile").then(setProfile).catch(() => setProfile(null));
    api<{ results: { id: number; status: string; recipient_alias: string; service: string }[] }>("/api/requests")
      .then((data) => setRequests(data.results))
      .catch(() => setRequests([]));
  }, []);

  if (!profile) return <main className="page">Loading provider home…</main>;
  const verifiedDocs = profile.evidence.filter((item) => item.status === "verified").length;

  return (
    <main className="page">
      <article className="card row">
        {profile.photo && <img src={photoSrc(profile.photo)} alt="" style={{ width: 72, height: 72, objectFit: "cover", borderRadius: 12 }} />}
        <div>
          <h1 style={{ fontSize: 28, margin: 0 }}>{profile.display_name}</h1>
          <p className="meta">{profile.state} · {profile.verified ? "Verified" : "Unverified"} · {profile.membership}</p>
        </div>
        <div className="ring"><strong>{profile.score ?? "—"}</strong><span>{profile.score_label || "SCORE"}</span></div>
      </article>
      <div className="role-grid">
        <div className="card"><strong>{requests.filter((row) => row.status === "pending").length}</strong><p>Open requests</p></div>
        <div className="card"><strong>{profile.score ?? "—"}</strong><p>Trust score</p></div>
      </div>
      <section className="card">
        <h2>Verification</h2>
        <p>{verifiedDocs} verified evidence items on file. Payment does not change this.</p>
        <Link className="btn" href="/provider/verification">Upload evidence</Link>
      </section>
      <section>
        <h2>Recent requests</h2>
        {requests.map((row) => (
          <article key={row.id} className="card row">
            <span>{row.recipient_alias} · {row.service}</span>
            <span>{row.status}</span>
          </article>
        ))}
      </section>
    </main>
  );
}
