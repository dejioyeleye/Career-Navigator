import "./globals.css";
import Link from "next/link";
import { ReactNode } from "react";

export const metadata = {
  title: "Skill-Bridge Career Navigator",
  description: "Gap analysis and learning roadmap for your dream role",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header className="border-b border-slate-200 bg-white">
          <div className="mx-auto max-w-6xl px-6 py-4 flex items-center justify-between">
            <Link href="/" className="text-xl font-semibold text-brand-700">Skill-Bridge</Link>
            <nav className="flex gap-5 text-sm text-slate-700">
              <Link href="/profiles/new">Create Profile</Link>
              <Link href="/search">Explore Market Data</Link>
            </nav>
          </div>
        </header>
        <main className="mx-auto max-w-6xl px-6 py-8">{children}</main>
      </body>
    </html>
  );
}
