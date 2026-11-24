"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

type Plan = {
  membership: string;
  payment_status: string;
  paid_through: string | null;
  price_usd: string | null;
  price_set: boolean;
  note: string;
};

export default function MembershipPage() {
  const [plan, setPlan] = useState<Plan | null>(null);
  const [error, setError] = useState("");

  function load() {
    api<Plan>("/api/provider/membership").then(setPlan);
  }
  useEffect(load, []);

  async function activate() {
    setError("");
    try {
      setPlan(await api<Plan>("/api/provider/membership/activate", { method: "POST" }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Payment was not recorded");
    }
  }

  if (!plan) return <main className="page">Loading plan…</main>;

  return (
    <main className="page">
      <h1>Premium subscription</h1>
      <p className="lede">Web portal only. Monthly provider subscription is managed on the web with PayPal. The installed app has no checkout.</p>
      <section className="card">
        <p className="badge">{plan.membership}</p>
        <h2>Monthly Premium Plan</h2>
        <p style={{ fontSize: 28, margin: "8px 0" }}>{plan.price_set ? `$${plan.price_usd}` : "Price to be confirmed"}</p>
        <p>Pricing details are announced before paid enrollment opens. Purchased and managed on this website only.</p>
        <p>Paid-through date: {plan.paid_through || "Not started"} · Payment status: {plan.payment_status}</p>
        <div className="actions">
          <button className="btn" onClick={activate}>Record verified demo payment</button>
          <button className="btn secondary" onClick={async () => setPlan(await api<Plan>("/api/provider/membership/cancel", { method: "POST" }))}>Cancel subscription</button>
        </div>
        {error && <p className="field-error">{error}</p>}
        <p>{plan.note}</p>
      </section>
      <section className="card" style={{ marginTop: 16 }}>
        <h2>What membership changes</h2>
        <p>When a family’s criteria match your services, active premium providers are prioritized in Suggested matches. If none qualify, suitable free providers are shown. Families can always browse the full directory.</p>
        <p>Payment never alters Trust Score, ratings, or verification. Meet-and-greets and care payments stay offline.</p>
      </section>
    </main>
  );
}
