"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

export default function RolePage() {
  const router = useRouter();
  const [role, setRole] = useState<"family" | "provider">("family");

  return (
    <main className="auth-page">
      <div style={{ textAlign: "left" }}>
        <button className="ghost" onClick={() => router.push("/sign-in")}>← Back</button>
      </div>
      <h1>Choose your role</h1>
      <p className="lede">Select the option that best describes how you’ll use CareGrove.</p>
      <div className="role-grid">
        <div
          className={`role ${role === "family" ? "selected" : ""}`}
          role="button"
          tabIndex={0}
          onClick={() => setRole("family")}
          onKeyDown={(event) => { if (event.key === "Enter" || event.key === " ") setRole("family"); }}
        >
          <div className="mark">👪</div>
          <h2>Family</h2>
          <p>Select the option that best describes how you’ll use CareGrove.</p>
        </div>
        <div
          className={`role ${role === "provider" ? "selected" : ""}`}
          role="button"
          tabIndex={0}
          onClick={() => setRole("provider")}
          onKeyDown={(event) => { if (event.key === "Enter" || event.key === " ") setRole("provider"); }}
        >
          <div className="mark">🛡️</div>
          <h2>Provider</h2>
          <p>I provide care services and want to connect with families.</p>
        </div>
      </div>
      <button className="btn" style={{ minWidth: 280 }} onClick={() => router.push(`/register?role=${role}`)}>Continue</button>
    </main>
  );
}
