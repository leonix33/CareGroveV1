"use client";

import { useState } from "react";
import { api } from "@/lib/api";

export default function SupportPage() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [body, setBody] = useState("");
  const [deleteEmail, setDeleteEmail] = useState("");
  const [role, setRole] = useState("family");
  const [message, setMessage] = useState("");

  return (
    <main className="page">
      <h1>CareGrove Platform Support & Legal</h1>
      <p className="lede">Official source for family members, care providers, and mobile application users. Access verified support channels, review privacy safeguards, or submit an account deletion request.</p>
      <form className="card" onSubmit={async (e) => {
        e.preventDefault();
        const result = await api<{ message: string }>("/api/public/support", { method: "POST", body: JSON.stringify({ name, email, body }) });
        setMessage(result.message);
      }}>
        <h2>Support & Contact</h2>
        <label>Your Name</label>
        <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Full Name" required />
        <label>Email Address</label>
        <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="name@example.com" required />
        <label>Message</label>
        <textarea value={body} onChange={(e) => setBody(e.target.value)} placeholder="Describe your inquiry or question..." required />
        <button className="btn" style={{ marginTop: 12 }} type="submit">Send Message</button>
      </form>
      <section className="card" style={{ marginTop: 16 }}>
        <h2>Privacy Safeguards</h2>
        <p><strong>Profiles:</strong> Provider business listings are public on the directory to facilitate discovery. Family members submit reviews and inquiries using their chosen public reviewer aliases.</p>
        <p><strong>Recipient Needs:</strong> Care preferences and service requirements are visible only between the requesting family and the recipient care provider.</p>
        <p><strong>Evidence & Credentials:</strong> Verification documents stay private for administrative verification.</p>
        <p><strong>Messages:</strong> Direct communications remain private between the corresponding accounts.</p>
        <p className="note">CareGrove is an introductory platform and directory. It does not provide clinical services, medical treatments, or direct caregiving. Actual service agreements and care delivery occur independently and offline.</p>
      </section>
      <form className="card" style={{ marginTop: 16 }} onSubmit={async (e) => {
        e.preventDefault();
        const result = await api<{ message: string }>("/api/public/deletion", { method: "POST", body: JSON.stringify({ email: deleteEmail, role }) });
        setMessage(result.message);
      }}>
        <h2>Request Account & Data Deletion</h2>
        <label>Account Email Address</label>
        <input value={deleteEmail} onChange={(e) => setDeleteEmail(e.target.value)} placeholder="name@example.com" required />
        <label>Account Type</label>
        <select value={role} onChange={(e) => setRole(e.target.value)}>
          <option value="family">Family / Care Recipient Account</option>
          <option value="provider">Provider Account</option>
        </select>
        <button className="btn" style={{ marginTop: 12 }} type="submit">Send Deletion Confirmation Email</button>
      </form>
      {message && <p className="note" style={{ marginTop: 16 }}>{message}</p>}
    </main>
  );
}
