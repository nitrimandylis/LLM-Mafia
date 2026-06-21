import type { Metadata } from "next";
import "./globals.css";
import TopBar from "./TopBar";

export const metadata: Metadata = {
  title: "LLM Mafia — Replay",
  description: "Dramatized replay of an all-LLM game of Mafia.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="shell">
          <TopBar />
          {children}
        </div>
      </body>
    </html>
  );
}
