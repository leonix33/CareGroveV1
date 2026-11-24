"use client";

import { useEffect, useState } from "react";
import { api, photoSrc } from "@/lib/api";

export default function EditProfile() {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [zip, setZip] = useState("");
  const [state, setState] = useState("TX");
  const [photo, setPhoto] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    api<{ display_name: string; description: string; zip_code: string; state: string; photo: string; legal_name: string }>("/api/provider/profile").then((profile) => {
      setName(profile.display_name);
      setDescription(profile.description);
      setZip(profile.zip_code);
      setState(profile.state || "TX");
      setPhoto(profile.photo);
    });
  }, []);

  async function save(e: React.FormEvent) {
    e.preventDefault();
    const current = await api<Record<string, unknown>>("/api/provider/profile");
    await api("/api/provider/profile", {
      method: "PUT",
      body: JSON.stringify({ ...current, display_name: name, description, zip_code: zip, state }),
    });
    setMessage("Profile saved. Identity changes still go through verification.");
  }

  return (
    <main className="page">
      <h1>Business profile</h1>
      {photo && <img src={photoSrc(photo)} alt="" style={{ width: "100%", maxWidth: 480, borderRadius: 16 }} />}
      <form className="card" onSubmit={save}>
        <label>Display name</label>
        <input value={name} onChange={(e) => setName(e.target.value)} />
        <label>Description</label>
        <textarea value={description} onChange={(e) => setDescription(e.target.value)} rows={4} />
        <label>Base ZIP</label>
        <input value={zip} onChange={(e) => setZip(e.target.value)} />
        <label>State</label>
        <select value={state} onChange={(e) => setState(e.target.value)}><option>TX</option><option>IN</option></select>
        <button className="btn" style={{ marginTop: 12 }} type="submit">Save</button>
        {message && <p>{message}</p>}
      </form>
    </main>
  );
}
