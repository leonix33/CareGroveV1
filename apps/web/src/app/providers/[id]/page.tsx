"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { api, photoSrc, SERVICE_LABELS } from "@/lib/api";

type Detail = {
  id: number;
  display_name: string;
  photo: string;
  description: string;
  state: string;
  zip_code: string;
  services: string[];
  accepting: string;
  capacity: number | null;
  coverage_programs: string[];
  rates: { service: string; amount: number; unit: string }[];
  qualifications: string;
  verified: boolean;
  membership: string;
  score: number | null;
  score_label: string | null;
  score_state: string;
  score_breakdown: { categories?: Record<string, number>; weights?: Record<string, number>; disclaimer?: string };
  reviews: { id: number; rating: number; body: string; alias: string }[];
};

export default function ProviderProfilePage() {
  const params = useParams<{ id: string }>();
  const [provider, setProvider] = useState<Detail | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api<Detail>(`/api/providers/${params.id}`).then(setProvider).catch((err) => setError(err.message));
  }, [params.id]);

  if (error) return <main className="page"><p className="field-error">{error}</p></main>;
  if (!provider) return <main className="page">Loading profile…</main>;
  const categories = provider.score_breakdown.categories || {};

  return (
    <main className="page">
      <article className="card provider">
        {provider.photo && <img className="shot" src={photoSrc(provider.photo)} alt="" />}
        <div>
          <h1 style={{ fontSize: 32 }}>{provider.display_name}</h1>
          <p className="meta">{provider.state} {provider.zip_code} · {provider.accepting.replaceAll("_", " ")} · capacity {provider.capacity ?? "Not specified"}</p>
          <p>{provider.description || "Not specified"}</p>
          <div className="pills">
            {provider.services.map((id) => <span key={id} className="pill">{SERVICE_LABELS[id] || id}</span>)}
          </div>
          <p>Coverage: {provider.coverage_programs.join(", ") || "Not specified"}</p>
          <p>Qualifications: {provider.qualifications}</p>
          {provider.rates.map((rate) => (
            <p key={rate.service}>${rate.amount} / {rate.unit} · {SERVICE_LABELS[rate.service] || rate.service}</p>
          ))}
          <Link className="btn" href={`/family/requests?provider=${provider.id}`}>Request connection</Link>
        </div>
        <div className="ring" id="score">
          <strong>{provider.score ?? "—"}</strong>
          <span>{provider.score_label || provider.score_state}</span>
        </div>
      </article>
      <section className="card" style={{ marginTop: 16 }}>
        <h2>Trust Score</h2>
        <p>{provider.score_breakdown.disclaimer}</p>
        <div className="bars">
          {Object.entries(categories).map(([name, value]) => (
            <div key={name}>
              <div className="row"><span>{name}</span><span>{value}</span></div>
              <div className="bar"><i style={{ width: `${Math.min(100, value)}%` }} /></div>
            </div>
          ))}
        </div>
      </section>
      <section style={{ marginTop: 16 }}>
        <h2>Published reviews</h2>
        {provider.reviews.map((review) => (
          <article key={review.id} className="card">
            <strong>{review.alias}</strong> · {review.rating} / 5
            <p>{review.body}</p>
          </article>
        ))}
        {provider.reviews.length === 0 && <p>No published reviews yet.</p>}
      </section>
    </main>
  );
}
