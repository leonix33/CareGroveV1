"use client";

import { useState } from "react";
import { api } from "@/lib/api";

export default function RecoverPage() {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    const result = await api<{ message: string }>("/api/auth/recover", {
      method: "POST",
      body: JSON.stringify({ email }),
    });
    setMessage(result.message);
  }

  return (
    <main className="auth-page">
      <img src="/brand/logo.png" alt="CareGrove" style={{ height: 64 }} />
      <h1>Recover account access</h1>
      <p className="lede">Start recovery using the email associated with the account.</p>
      <form onSubmit={submit}>
        <label>Email address</label>
        <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        <button className="btn full" style={{ marginTop: 16 }} type="submit">Send recovery link</button>
      </form>
      {message && <p className="note">{message}</p>}
    </main>
  );
}
