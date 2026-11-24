"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export default function ProviderReviews() {
  const [rows, setRows] = useState<{ id: number; alias: string; rating: number; body: string }[]>([]);
  useEffect(() => {
    api<{ results: typeof rows }>("/api/provider/reviews").then((data) => setRows(data.results));
  }, []);
  return (
    <main className="page">
      <h1>Published family reviews</h1>
      <p className="lede">You can read these reviews. You cannot edit, delete, or approve them.</p>
      {rows.map((row) => (
        <article key={row.id} className="card"><strong>{row.alias}</strong> · {row.rating}/5<p>{row.body}</p></article>
      ))}
      {rows.length === 0 && <p>No published reviews yet.</p>}
    </main>
  );
}
