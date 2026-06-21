import type { Metadata } from "next";
import { Bebas_Neue } from "next/font/google";
import "./globals.css";
import TopBar from "./TopBar";

// Condensed display face for the wordmark + (in Signature) the chrome labels.
// Self-hosted by next/font; exposed to CSS as --font-display.
const bebas = Bebas_Neue({
  weight: "400",
  subsets: ["latin"],
  display: "swap",
  variable: "--font-display",
});

export const metadata: Metadata = {
  title: "LLM Mafia — Replay",
  description: "Dramatized replay of an all-LLM game of Mafia.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={bebas.variable}>
      <body>
        <div className="shell">
          <TopBar />
          {children}
        </div>
      </body>
    </html>
  );
}
