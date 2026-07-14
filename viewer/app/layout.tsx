import type { Metadata } from "next";
import { Bebas_Neue, JetBrains_Mono, Space_Grotesk } from "next/font/google";
import "./globals.css";

// Condensed display face for the wordmark + (in Signature) the chrome labels.
// Self-hosted by next/font; exposed to CSS as --font-display.
const bebas = Bebas_Neue({
  weight: "400",
  subsets: ["latin"],
  display: "swap",
  variable: "--font-display",
});

// Landing-page faces: mono body + grotesk headings. Exposed as CSS vars and
// only fetched when referenced, so the viewer pages don't pay for them.
const mono = JetBrains_Mono({ subsets: ["latin"], display: "swap", variable: "--font-mono" });
const grotesk = Space_Grotesk({ subsets: ["latin"], display: "swap", variable: "--font-grotesk" });

export const metadata: Metadata = {
  metadataBase: new URL("https://llm-mafia.vercel.app"),
  title: "LLM Mafia — Replay",
  description: "Dramatized replay of an all-LLM game of Mafia.",
  openGraph: {
    title: "LLM Mafia",
    description:
      "No humans. Pure model-vs-model deception. Watch AI players lie, accuse, and vote each other out.",
    siteName: "LLM Mafia",
    type: "website",
  },
  twitter: { card: "summary_large_image" },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${bebas.variable} ${mono.variable} ${grotesk.variable}`}>
      <body>
        <div className="shell">{children}</div>
      </body>
    </html>
  );
}
