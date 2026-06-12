import type { Metadata } from "next";
import type { ReactNode } from "react";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Job Tracker",
  description: "Local-first job search tracking dashboard",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <div className="app-frame">
          <header className="app-topbar">
            <Link href="/" className="topbar-brand">
              AI Job Tracker
            </Link>
            <nav className="topbar-nav">
              <Link href="/">Jobs</Link>
              <Link href="/dashboard">Dashboard</Link>
            </nav>
          </header>
          {children}
        </div>
      </body>
    </html>
  );
}
