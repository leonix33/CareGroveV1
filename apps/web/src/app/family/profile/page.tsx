"use client";

import { useEffect, useState } from "react";
import { api, type Recipient } from "@/lib/api";

export default function FamilyProfilePage() {
  const [zip, setZip] = useState("");
  const [state, setState] = useState("TX");
  const [phone, setPhone] = useState("");
  const [recipients, setRecipients] = useState<Recipient[]>([]);
  const [alias, setAlias] = useState("");
  const [age, setAge] = useState("14");
  const [message, setMessage] = useState("");

  function load() {
    api<{ phone: string; zip_code: string; state: string; recipients: Recipient[] }>("/api/family/profile").then((profile) => {
      setPhone(profile.phone);
      setZip(profile.zip_code);
      setState(profile.state || "TX");
      setRecipients(profile.recipients);
    });
  }
  useEffect(load, []);

  async function saveProfile(e: React.FormEvent) {
    e.preventDefault();
    await api("/api/family/profile", { method: "PUT", body: JSON.stringify({ phone, zip_code: zip, state }) });
    setMessage("Profile saved.");
  }

  async function addRecipient(e: React.FormEvent) {
    e.preventDefault();
    await api("/api/family/recipients", {
      method: "POST",
      body: JSON.stringify({
        alias,
        age: Number(age),
        diagnosis: "autism",
        needs: "",
        services: ["respite"],
        coverage: ["medicaid"],
        preferences: [],
      }),
    });
    setAlias("");
    load();
  }

  return (
    <main className="page">
      <h1>Family profile</h1>
      <form className="card" onSubmit={saveProfile}>
        <label>Phone</label>
        <input value={phone} onChange={(e) => setPhone(e.target.value)} />
        <label>ZIP</label>
        <input value={zip} onChange={(e) => setZip(e.target.value)} />
        <label>State</label>
        <select value={state} onChange={(e) => setState(e.target.value)}>
          <option>TX</option>
          <option>IN</option>
        </select>
        <button className="btn" style={{ marginTop: 12 }} type="submit">Save</button>
        {message && <p>{message}</p>}
      </form>
      <h2>People receiving support</h2>
      {recipients.map((row) => (
        <article key={row.id} className="card">
          <strong>{row.alias}</strong>
          <p className="meta">Age {row.age ?? "—"} · {row.diagnosis || "Not specified"} · {row.archived ? "Archived" : "Active"}</p>
          {!row.archived && (
            <button className="ghost" onClick={async () => { await api(`/api/family/recipients/${row.id}/archive`, { method: "POST" }); load(); }}>Archive</button>
          )}
        </article>
      ))}
      <form className="card" onSubmit={addRecipient}>
        <h3>Add a recipient</h3>
        <label>Alias</label>
        <input value={alias} onChange={(e) => setAlias(e.target.value)} required />
        <label>Age</label>
        <input value={age} onChange={(e) => setAge(e.target.value)} />
        <button className="btn" style={{ marginTop: 12 }} type="submit">Add</button>
      </form>
    </main>
  );
}
