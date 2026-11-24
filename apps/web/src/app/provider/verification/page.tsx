"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

type Item = { id: number; category: string; status: string; expires_on: string | null; file_name: string | null; note: string };

export default function VerificationPage() {
  const [items, setItems] = useState<Item[]>([]);
  const [fileName, setFileName] = useState("license.pdf");
  const [message, setMessage] = useState("");

  function load() {
    api<{ evidence: Item[] }>("/api/provider/profile").then((profile) => setItems(profile.evidence));
  }
  useEffect(load, []);

  async function upload(e: React.FormEvent) {
    e.preventDefault();
    await api("/api/provider/evidence", {
      method: "POST",
      body: JSON.stringify({ category: "license", subject: "company", file_name: fileName }),
    });
    setMessage("Upload recorded as submitted. It is not verified until staff review it.");
    load();
  }

  return (
    <main className="page">
      <h1>Verification</h1>
      <p className="lede">Supply company, owner, and assigned-staff evidence. Staff review it manually. A file upload alone never awards the badge.</p>
      {items.map((item) => (
        <article key={item.id} className="card row">
          <div>
            <strong>{item.category.replaceAll("_", " ")}</strong>
            <p className="meta">{item.file_name || "No file"} {item.expires_on ? `· expires ${item.expires_on}` : ""}</p>
          </div>
          <span className="badge">{item.status}</span>
        </article>
      ))}
      <form className="card" onSubmit={upload}>
        <label>File name (PDF, JPG, or PNG)</label>
        <input value={fileName} onChange={(e) => setFileName(e.target.value)} />
        <button className="btn" style={{ marginTop: 12 }} type="submit">Submit evidence</button>
        {message && <p>{message}</p>}
      </form>
    </main>
  );
}
