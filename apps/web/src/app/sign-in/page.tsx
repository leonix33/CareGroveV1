"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { api, saveSession, type User } from "@/lib/api";

export default function SignInPage() {
  const router = useRouter();
  const [email, setEmail] = useState("maya.chen@caregrove.demo");
  const [password, setPassword] = useState("CareGrove-demo-12");
  const [show, setShow] = useState(false);
  const [error, setError] = useState("");

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    try {
      const result = await api<{ token: string; user: User }>("/api/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      saveSession(result.token, result.user);
      router.push(result.user.role === "provider" ? "/provider" : result.user.role === "admin" ? "/admin" : "/family");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not sign in");
    }
  }

  return (
    <main className="auth-page">
      <img src="/brand/logo.png" alt="CareGrove" style={{ height: 64 }} />
      <h1>Welcome to CareGrove</h1>
      <p className="lede">Create a free family account to search, save and request verified providers.</p>
      <form onSubmit={submit}>
        <label>Email address</label>
        <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Enter Email" />
        <label>Password</label>
        <div className="row">
          <input style={{ flex: 1 }} type={show ? "text" : "password"} value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Enter Password" />
          <button type="button" className="ghost" onClick={() => setShow(!show)}>{show ? "Hide" : "Show"}</button>
        </div>
        <div className="row" style={{ marginTop: 12 }}>
          <label style={{ fontWeight: 500 }}><input type="checkbox" style={{ width: "auto", marginRight: 8 }} /> Remember me</label>
          <Link href="/recover">Forgot Password?</Link>
        </div>
        {error && <p className="field-error">{error}</p>}
        <button className="btn full" style={{ marginTop: 16 }} type="submit">Login</button>
      </form>
      <p>Don&apos;t have an account? <Link href="/">Sign up</Link></p>
      <p className="meta">Demo password for every sample account is CareGrove-demo-12. Family maya.chen@caregrove.demo · Provider oak@caregrove.demo · Staff admin@caregrove.demo</p>
    </main>
  );
}
