"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export default function PrivacyPage() {
  const [body, setBody] = useState("");
  useEffect(() => {
    api<{ body: string }>("/api/public/privacy").then((data) => setBody(data.body));
  }, []);
  return (
    <main className="page">
      <h1>Privacy information</h1>
      <p className="lede">The wording shown is illustrative until the privacy policy is approved.</p>
      <article className="card"><p>{body}</p></article>
    </main>
  );
}
