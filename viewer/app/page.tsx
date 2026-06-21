"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import type { GameEvent, GameLog } from "@/lib/events";
import { useReplay } from "@/lib/useReplay";
import { loadSettings, DEFAULTS, SKINS as SKIN_META, type SkinId } from "@/lib/settings";
import Controls from "@/components/Controls";
import ChatSkin from "@/components/skins/ChatSkin";
import CaseFileSkin from "@/components/skins/CaseFileSkin";
import TranscriptSkin from "@/components/skins/TranscriptSkin";
import SignalSkin from "@/components/skins/SignalSkin";

const SKIN_COMPONENTS = {
  chat: ChatSkin,
  casefile: CaseFileSkin,
  transcript: TranscriptSkin,
  signal: SignalSkin,
};

export default function Viewer() {
  // `mounted` gates localStorage reads so SSR and first client render match
  // (both use DEFAULTS), avoiding a hydration mismatch.
  const [mounted, setMounted] = useState(false);
  const settings = useMemo(() => (mounted ? loadSettings() : DEFAULTS), [mounted]);
  const [events, setEvents] = useState<GameEvent[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [source, setSource] = useState<"game" | "sample" | "upload" | null>(null);
  const [skin, setSkin] = useState<SkinId>(DEFAULTS.skin);
  const fileInput = useRef<HTMLInputElement>(null);

  useEffect(() => setMounted(true), []);

  useEffect(() => {
    setSkin(settings.skin);
  }, [settings.skin]);

  // Drive chrome theming from the root element: data-chrome picks the theme,
  // data-skin lets the Adaptive theme borrow the active design's accent. The
  // top bar lives in layout.tsx (outside this page), so the root is the one
  // node both can see — no context needed.
  useEffect(() => {
    const root = document.documentElement;
    root.dataset.chrome = settings.chromeTheme;
    root.dataset.skin = skin;
    return () => {
      delete root.dataset.chrome;
      delete root.dataset.skin;
    };
  }, [settings.chromeTheme, skin]);

  // Load whatever the engine last wrote (../game_log.json), else the sample.
  useEffect(() => {
    loadFromServer();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function loadFromServer() {
    fetch("/api/log", { cache: "no-store" })
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((data: { source: "game" | "sample"; log: GameLog }) => {
        setSource(data.source);
        applyLog(data.log);
      })
      .catch(() =>
        setError("No game log found. Run a game (python main.py) or generate the sample.")
      );
  }

  function applyLog(log: GameLog) {
    if (!Array.isArray(log.events) || log.events.length === 0) {
      setError(
        "This log has no structured events. Re-run the game with the updated version to generate an events[] stream."
      );
      setEvents(null);
      return;
    }
    setError(null);
    setEvents(log.events);
  }

  function onUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    file
      .text()
      .then((t) => {
        setSource("upload");
        applyLog(JSON.parse(t));
      })
      .catch(() => setError("That file isn't a valid game log JSON."));
  }

  const state = useReplay(events ?? [], settings.speed);

  return (
    <div className="stage-wrap">
      <div className="menu">
        <div className="skin-seg" role="tablist" aria-label="Presentation style">
          {SKIN_META.map((m) => (
            <button
              key={m.id}
              role="tab"
              aria-selected={skin === m.id}
              className={`skin-opt${skin === m.id ? " on" : ""}`}
              onClick={() => setSkin(m.id)}
              title={m.blurb}
            >
              <span className="skin-swatch" aria-hidden>
                {m.swatch.map((c, j) => (
                  <i key={j} style={{ background: c }} />
                ))}
              </span>
              <span className="skin-meta">
                <span className="nm">{m.name}</span>
                <span className="tg">{m.tag}</span>
              </span>
            </button>
          ))}
        </div>

        <span className="menu-spacer" />

        {source && (
          <span
            className={`source-badge${source === "game" ? " live" : ""}`}
            title="Where this replay came from"
          >
            <span className="dot" />
            {source === "game" ? "latest game" : source === "sample" ? "bundled sample" : "uploaded file"}
          </span>
        )}
        <button className="menu-btn" onClick={loadFromServer} title="Reload ../game_log.json from the engine">
          ↻ Latest game
        </button>
        <button className="menu-btn" onClick={() => fileInput.current?.click()}>
          Load a log…
        </button>
        <input
          ref={fileInput}
          type="file"
          accept="application/json,.json"
          onChange={onUpload}
          style={{ display: "none" }}
        />
      </div>

      {error ? (
        <div className="notice">
          <h2>No replay to show</h2>
          <p>{error}</p>
          <p>
            Generate one with <code>python test_events.py --write</code> or load a{" "}
            <code>game_log.json</code> above.
          </p>
        </div>
      ) : !events ? (
        <div className="notice">
          <p>Loading…</p>
        </div>
      ) : (
        <>
          {/* All four stay mounted so each keeps its own scroll position; only
              the selected design is shown. */}
          {SKIN_META.map((m) => {
            const Skin = SKIN_COMPONENTS[m.id];
            const isActive = skin === m.id;
            return (
              <div key={m.id} className="skin-pane" style={{ display: isActive ? "flex" : "none" }}>
                <Skin state={state} active={isActive} />
              </div>
            );
          })}
          <Controls state={state} />
        </>
      )}
    </div>
  );
}
