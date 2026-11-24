import type { Metadata } from "next";
import { Chrome } from "@/components/Chrome";
import "./globals.css";

export const metadata: Metadata = {
  title: "CareGrove",
  description: "Verified care connections for families and providers.",
  icons: { icon: "/brand/logo.png" },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Chrome>{children}</Chrome>
      </body>
    </html>
  );
}
