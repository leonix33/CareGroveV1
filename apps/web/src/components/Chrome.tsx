"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { api, clearSession, type User } from "@/lib/api";

const FAMILY = [
  ["/family", "Home"],
  ["/family/saved", "Saved"],
  ["/family/requests", "Requests"],
  ["/family/messages", "Messages"],
  ["/family/profile", "Profile"],
];
const PROVIDER = [
  ["/provider", "Home"],
  ["/provider/profile", "Profile"],
  ["/provider/verification", "Verification"],
  ["/provider/requests", "Requests"],
  ["/provider/messages", "Messages"],
  ["/provider/reviews", "Reviews"],
  ["/provider/score", "Trust Score"],
  ["/provider/membership", "Premium subscription"],
];
const ADMIN = [
  ["/admin", "Overview"],
  ["/admin/evidence", "Evidence"],
  ["/admin/reviews", "Reviews"],
  ["/admin/subscriptions", "Subscriptions"],
];

export function Chrome({ children }: { children: React.ReactNode }) {
  const path = usePathname();
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const bare = path === "/" || path.startsWith("/sign-") || path === "/register" || path === "/recover";

  useEffect(() => {
    api<User>("/api/auth/me").then(setUser).catch(() => setUser(null));
  }, [path]);

  const links = user?.role === "provider" ? PROVIDER : user?.role === "admin" ? ADMIN : user ? FAMILY : [];

  return (
    <>
      <header className="topbar">
        <Link href={user ? (user.role === "family" ? "/family" : user.role === "provider" ? "/provider" : "/admin") : "/"} className="brand">
          <img src="/brand/logo.png" alt="CareGrove, verified care connections" />
        </Link>
        {!bare && (
          <nav className="nav">
            {links.map(([href, label]) => (
              <Link key={href} href={href} className={path === href ? "active" : ""}>
                {label}
              </Link>
            ))}
          </nav>
        )}
        <div className="row" style={{ gap: 8 }}>
          <Link href="/support" className="ghost" style={{ textDecoration: "none" }}>Support</Link>
          {user ? (
            <>
              <div className="avatar" title={user.name}>{user.name.slice(0, 2).toUpperCase()}</div>
              <button className="ghost" onClick={() => { clearSession(); setUser(null); router.push("/"); }}>Sign out</button>
            </>
          ) : (
            <Link href="/sign-in" className="btn" style={{ textDecoration: "none" }}>Login</Link>
          )}
        </div>
      </header>
      {children}
      <div className="page" style={{ paddingTop: 0 }}>
        <footer className="footer">
          <span>© Copyright 2026, CareGrove. All rights reserved. All family functionality is free.</span>
          <span>
            <Link href="/support">Terms of Service</Link>
            {" · "}
            <Link href="/privacy">Privacy Policy</Link>
            {" · "}
            <Link href="/screens">Design screens</Link>
          </span>
        </footer>
      </div>
    </>
  );
}
