"use client";

import { useEffect, useState } from "react";
import { loadSettings, saveSettings, type SkinId } from "@/lib/settings";
import type { Speed } from "@/lib/useReplay";

const SKINS: { id: SkinId; name: string; blurb: string }[] = [
  { id: "chat", name: "Group-chat", blurb: "Avatars and bubbles in a thread. Easiest to follow who said what." },
  { id: "table", name: "Table + spotlight", blurb: "Players around a table; a spotlight follows the speaker; the dead grey out." },
  { id: "broadcast", name: "Broadcast", blurb: "Elimination-show treatment: title cards, lower-third nameplates, recap ticker." },
];

const SPEEDS: { id: Speed; label: string }[] = [
  { id: 1, label: "1× — full drama" },
  { id: 2, label: "2× — brisk" },
  { id: "instant", label: "Skip — no pacing" },
];

export default function SettingsPage() {
  const [skin, setSkin] = useState<SkinId>("chat");
  const [speed, setSpeed] = useState<Speed>(1);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    const s = loadSettings();
    setSkin(s.skin);
    setSpeed(s.speed);
  }, []);

  function persist(next: { skin?: SkinId; speed?: Speed }) {
    const merged = { skin, speed, ...next };
    setSkin(merged.skin);
    setSpeed(merged.speed);
    saveSettings(merged);
    setSaved(true);
    setTimeout(() => setSaved(false), 1200);
  }

  return (
    <div style={{ maxWidth: 640, margin: "32px auto", padding: "0 20px" }}>
      <h1 style={{ fontSize: 20 }}>Settings</h1>
      <p style={{ color: "var(--muted)", marginTop: 4 }}>
        Saved to your browser. {saved && <span style={{ color: "var(--green)" }}>✓ saved</span>}
      </p>

      <h3 style={{ marginTop: 28 }}>Default presentation style</h3>
      <div style={{ display: "grid", gap: 12 }}>
        {SKINS.map((s) => (
          <button
            key={s.id}
            onClick={() => persist({ skin: s.id })}
            style={{
              textAlign: "left",
              background: skin === s.id ? "#241015" : "var(--panel)",
              border: `1px solid ${skin === s.id ? "var(--red)" : "var(--line)"}`,
              borderRadius: 10,
              padding: "14px 16px",
              cursor: "pointer",
              color: "var(--ink)",
            }}
          >
            <div style={{ fontWeight: 700 }}>
              {skin === s.id ? "● " : "○ "}
              {s.name}
            </div>
            <div style={{ color: "var(--muted)", fontSize: 13, marginTop: 4 }}>{s.blurb}</div>
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
              background: speed === s.id ? "var(--gold)" : "var(--panel-2)",
              color: speed === s.id ? "#111" : "var(--ink)",
              border: "1px solid var(--line)",
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
