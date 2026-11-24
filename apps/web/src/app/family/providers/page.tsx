"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ProviderCard } from "@/components/ProviderCard";
import { api, type ProviderCard as Card } from "@/lib/api";

export default function AllProvidersPage() {
  const [results, setResults] = useState<Card[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api<{ results: Card[] }>("/api/family/providers")
      .then((data) => setResults(data.results))
      .catch((err) => setError(err.message));
  }, []);

  return (
    <main className="page">
      <div className="toolbar">
        <h1 style={{ fontSize: 28 }}>All providers</h1>
        <div className="nav">
          <Link href="/family/providers" className="active">All providers</Link>
          <Link href="/family">Suggested matches</Link>
        </div>
      </div>
      <p className="lede">The full directory includes every discoverable provider, free and premium. You choose whom to contact.</p>
      {error && <p className="field-error">{error}</p>}
      {results.map((provider) => <ProviderCard key={provider.id} provider={provider} />)}
    </main>
  );
}
