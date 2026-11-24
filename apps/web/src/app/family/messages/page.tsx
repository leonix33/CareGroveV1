"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

type Thread = { id: number; provider_name: string; family_name: string };
type Msg = { id: number; body: string; mine: boolean; created_at: string };

export default function MessagesPage() {
  const [threads, setThreads] = useState<Thread[]>([]);
  const [current, setCurrent] = useState<number | null>(null);
  const [messages, setMessages] = useState<Msg[]>([]);
  const [text, setText] = useState("");

  useEffect(() => {
    api<{ results: Thread[] }>("/api/conversations").then((data) => {
      setThreads(data.results);
      if (data.results[0]) setCurrent(data.results[0].id);
    });
  }, []);

  useEffect(() => {
    if (!current) return;
    api<{ results: Msg[] }>(`/api/conversations/${current}/messages`).then((data) => setMessages(data.results));
  }, [current]);

  async function send(e: React.FormEvent) {
    e.preventDefault();
    if (!current || !text.trim()) return;
    const message = await api<Msg>(`/api/conversations/${current}/messages`, {
      method: "POST",
      body: JSON.stringify({ body: text }),
    });
    setMessages((items) => [...items, message]);
    setText("");
  }

  return (
    <main className="page" style={{ background: "#eef6f1", borderRadius: 16 }}>
      <h1>Messages</h1>
      <div className="row" style={{ alignItems: "stretch" }}>
        <div className="list" style={{ width: 240 }}>
          {threads.map((thread) => (
            <button key={thread.id} className={`card ${current === thread.id ? "role selected" : ""}`} onClick={() => setCurrent(thread.id)}>
              {thread.provider_name}
            </button>
          ))}
        </div>
        <div style={{ flex: 1 }}>
          {messages.map((message) => (
            <div key={message.id} style={{ textAlign: message.mine ? "right" : "left" }}>
              <span className="card" style={{ display: "inline-block", background: message.mine ? "#8d5a34" : "white", color: message.mine ? "white" : "inherit" }}>
                {message.body}
              </span>
            </div>
          ))}
          <form className="searchline" onSubmit={send}>
            <input value={text} onChange={(e) => setText(e.target.value)} placeholder="Enter..." maxLength={2000} />
            <button className="btn" type="submit">Send</button>
          </form>
        </div>
      </div>
    </main>
  );
}
