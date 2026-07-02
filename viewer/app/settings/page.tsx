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
    <div className="settings">
      <h1>Settings</h1>
      <p className="hint">
        Saved to your browser. {saved && <span style={{ color: "var(--green)" }}>✓ saved</span>}
      </p>

      <h3>Chrome theme</h3>
      <p className="hint">
        Styles the frame around the replay — top bar, switcher, transport. Doesn&apos;t change the designs themselves.
      </p>
      <div className="opt-list">
        {CHROME_THEMES.map((c) => (
          <button
            key={c.id}
            className={`opt-card${chromeTheme === c.id ? " on" : ""}`}
            aria-pressed={chromeTheme === c.id}
            onClick={() => persist({ chromeTheme: c.id })}
          >
            <span className="swatch">
              {c.swatch.map((col, j) => (
                <span key={j} style={{ background: col }} />
              ))}
            </span>
            <span>
              <span className="opt-name">
                {chromeTheme === c.id ? "● " : "○ "}
                {c.name}
              </span>
              <span className="opt-blurb">{c.blurb}</span>
            </span>
          </button>
        ))}
      </div>

      <h3>Default presentation style</h3>
      <div className="opt-list">
        {SKINS.map((s) => (
          <button
            key={s.id}
            className={`opt-card${skin === s.id ? " on" : ""}`}
            aria-pressed={skin === s.id}
            onClick={() => persist({ skin: s.id })}
          >
            <span className="swatch">
              {s.swatch.map((c, j) => (
                <span key={j} style={{ background: c }} />
              ))}
            </span>
            <span>
              <span className="opt-name">
                {skin === s.id ? "● " : "○ "}
                {s.name} <span className="tag">· {s.tag}</span>
              </span>
              <span className="opt-blurb">{s.blurb}</span>
            </span>
          </button>
        ))}
      </div>

      <h3>Default playback speed</h3>
      <div className="speed-row">
        {SPEEDS.map((s) => (
          <button
            key={String(s.id)}
            className={`speed-btn${speed === s.id ? " on" : ""}`}
            aria-pressed={speed === s.id}
            onClick={() => persist({ speed: s.id })}
          >
            {s.label}
          </button>
        ))}
      </div>
    </div>
  );
}
