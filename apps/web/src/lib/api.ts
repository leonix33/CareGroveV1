function apiBase() {
  if (typeof window !== "undefined") {
    const host = window.location.hostname;
    if (host !== "localhost" && host !== "127.0.0.1") return "";
  }
  return process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
}

export type User = {
  id: number;
  name: string;
  email: string;
  role: "family" | "provider" | "admin";
  email_verified: boolean;
  status: string;
};

export type Recipient = {
  id: number;
  alias: string;
  age: number | null;
  diagnosis: string;
  needs: string;
  services: string[];
  coverage: string[];
  preferences: string[];
  archived: boolean;
};

export type ProviderCard = {
  id: number;
  display_name: string;
  provider_type: string;
  services: string[];
  state: string;
  city_zip?: string;
  distance_miles: number | null;
  distance_label: string | null;
  score: number | null;
  score_label: string | null;
  score_state: string;
  verified: boolean;
  membership: string;
  accepting: string;
  photo: string;
  match_reasons: string[];
  saved: boolean;
};

function token() {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("cg_token");
}

export async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  if (!(init.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  const auth = token();
  if (auth) headers.set("Authorization", `Bearer ${auth}`);
  const res = await fetch(`${apiBase()}${path}`, { ...init, headers });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) {
    const detail = body.detail;
    throw new Error(typeof detail === "string" ? detail : "Something went wrong");
  }
  return body as T;
}

export function saveSession(tokenValue: string, user: User) {
  localStorage.setItem("cg_token", tokenValue);
  localStorage.setItem("cg_user", JSON.stringify(user));
}

export function clearSession() {
  localStorage.removeItem("cg_token");
  localStorage.removeItem("cg_user");
}

export function photoSrc(photo: string) {
  return photo ? `/brand/${photo}` : "";
}

export const SERVICE_LABELS: Record<string, string> = {
  residential: "Residential",
  respite: "Respite",
  day_programs: "Day programs",
  behavioral_support: "Behavioral support",
  personal_care: "Personal care",
  employment: "Employment services",
  transportation: "Transportation",
  therapy: "Therapy",
  community: "Community activities",
  autism_services: "Autism services",
  supported_living: "Supported living",
};
