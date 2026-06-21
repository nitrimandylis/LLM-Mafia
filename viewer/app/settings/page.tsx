"use client";

import { useEffect, useState } from "react";
import {
  loadSettings,
  saveSettings,
  SKINS,
  CHROME_THEMES,
  type SkinId,
  type ChromeThemeId,
} from "@/lib/settings";
import type { Speed } from "@/lib/useReplay";

const SPEEDS: { id: Speed; label: string }[] = [
  { id: 1, label: "1× — full drama" },
  { id: 2, label: "2× — brisk" },
  { id: "instant", label: "Skip — no pacing" },
];

export default function SettingsPage() {
  const [skin, setSkin] = useState<SkinId>("chat");
  const [speed, setSpeed] = useState<Speed>(1);
  const [chromeTheme, setChromeTheme] = useState<ChromeThemeId>("signature");
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    const s = loadSettings();
    setSkin(s.skin);
    setSpeed(s.speed);
    setChromeTheme(s.chromeTheme);
  }, []);

  // Live-preview the frame: retint the top bar as the choice changes here.
  useEffect(() => {
    document.documentElement.dataset.chrome = chromeTheme;
  }, [chromeTheme]);

  function persist(next: { skin?: SkinId; speed?: Speed; chromeTheme?: ChromeThemeId }) {
    const merged = { skin, speed, chromeTheme, ...next };
    setSkin(merged.skin);
    setSpeed(merged.speed);
    setChromeTheme(merged.chromeTheme);
    saveSettings(merged);
    setSaved(true);
    setTimeout(() => setSaved(false), 1200);
  }

  return (
    <div style={{ maxWidth: 640, margin: "32px auto", padding: "0 20px" }}>
      <h1 style={{ fontSize: 20, letterSpacing: ".02em" }}>Settings</h1>
      <p style={{ color: "var(--shell-muted)", marginTop: 4 }}>
        Saved to your browser. {saved && <span style={{ color: "var(--green)" }}>✓ saved</span>}
      </p>

      <h3 style={{ marginTop: 28 }}>Chrome theme</h3>
      <p style={{ color: "var(--shell-muted)", fontSize: 13, marginTop: -6, marginBottom: 12 }}>
        Styles the frame around the replay — top bar, switcher, transport. Doesn&apos;t change the designs themselves.
      </p>
      <div style={{ display: "grid", gap: 12 }}>
        {CHROME_THEMES.map((c) => (
          <button
            key={c.id}
            onClick={() => persist({ chromeTheme: c.id })}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 14,
              textAlign: "left",
              background: chromeTheme === c.id ? "var(--shell-panel-2)" : "var(--shell-panel)",
              border: `1px solid ${chromeTheme === c.id ? "var(--brand)" : "var(--shell-line)"}`,
              borderRadius: 10,
              padding: "14px 16px",
              cursor: "pointer",
              color: "var(--shell-ink)",
            }}
          >
            <span style={{ display: "flex", borderRadius: 5, overflow: "hidden", flex: "0 0 auto", boxShadow: "0 0 0 1px rgba(255,255,255,.08)" }}>
              {c.swatch.map((col, j) => (
                <span key={j} style={{ width: 12, height: 34, background: col }} />
              ))}
            </span>
            <span>
              <span style={{ fontWeight: 700, display: "block" }}>
                {chromeTheme === c.id ? "● " : "○ "}
                {c.name}
              </span>
              <span style={{ color: "var(--shell-muted)", fontSize: 13, marginTop: 4, display: "block" }}>{c.blurb}</span>
            </span>
          </button>
        ))}
      </div>

      <h3 style={{ marginTop: 28 }}>Default presentation style</h3>
      <div style={{ display: "grid", gap: 12 }}>
        {SKINS.map((s) => (
          <button
            key={s.id}
            onClick={() => persist({ skin: s.id })}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 14,
              textAlign: "left",
              background: skin === s.id ? "var(--shell-panel-2)" : "var(--shell-panel)",
              border: `1px solid ${skin === s.id ? "var(--brand)" : "var(--shell-line)"}`,
              borderRadius: 10,
              padding: "14px 16px",
              cursor: "pointer",
              color: "var(--shell-ink)",
            }}
          >
            <span style={{ display: "flex", borderRadius: 5, overflow: "hidden", flex: "0 0 auto", boxShadow: "0 0 0 1px rgba(255,255,255,.08)" }}>
              {s.swatch.map((c, j) => (
                <span key={j} style={{ width: 12, height: 34, background: c }} />
              ))}
            </span>
            <span>
              <span style={{ fontWeight: 700, display: "block" }}>
                {skin === s.id ? "● " : "○ "}
                {s.name} <span style={{ color: "var(--shell-muted)", fontWeight: 400 }}>· {s.tag}</span>
              </span>
              <span style={{ color: "var(--shell-muted)", fontSize: 13, marginTop: 4, display: "block" }}>{s.blurb}</span>
            </span>
          </button>
        ))}
      </div>

      <h3 style={{ marginTop: 28 }}>Default playback speed</h3>
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        {SPEEDS.map((s) => (
          <button
            key={String(s.id)}
            onClick={() => persist({ speed: s.id })}
            style={{
              background: speed === s.id ? "var(--gold)" : "var(--shell-panel-2)",
              color: speed === s.id ? "#111" : "var(--shell-ink)",
              border: "1px solid var(--shell-line)",
              borderRadius: 7,
              padding: "8px 14px",
              cursor: "pointer",
              fontWeight: speed === s.id ? 700 : 400,
            }}
          >
            {s.label}
          </button>
        ))}
      </div>
    </div>
  );
}
