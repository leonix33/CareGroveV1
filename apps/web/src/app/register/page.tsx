"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";
import { api, saveSession, type User } from "@/lib/api";

function Form() {
  const params = useSearchParams();
  const router = useRouter();
  const role = params.get("role") === "provider" ? "provider" : "family";
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    try {
      const result = await api<{ token: string; user: User }>("/api/auth/register", {
        method: "POST",
        body: JSON.stringify({ name, email, password, role }),
      });
      saveSession(result.token, result.user);
      router.push(role === "provider" ? "/provider/profile" : "/family/profile");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not register");
    }
  }

  return (
    <main className="auth-page">
      <img src="/brand/logo.png" alt="CareGrove" style={{ height: 64 }} />
      <h1>{role === "family" ? "Create a free family account" : "Register your provider account"}</h1>
      <p className="lede">Registration is free. Providers can add an optional monthly plan later on this website.</p>
      <form onSubmit={submit}>
        <label>Name</label>
        <input value={name} onChange={(e) => setName(e.target.value)} required />
        <label>Email address</label>
        <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        <label>Password</label>
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} minLength={12} required />
        {error && <p className="field-error">{error}</p>}
        <button className="btn full" style={{ marginTop: 16 }} type="submit">Create account</button>
      </form>
      <p>Already registered? <Link href="/sign-in">Login</Link></p>
    </main>
  );
}

export default function RegisterPage() {
  return <Suspense><Form /></Suspense>;
}
