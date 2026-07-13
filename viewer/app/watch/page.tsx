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

// One glyph per view: a speech bubble, a case folder, a deposition page, a
// suspicion network. Stroke uses currentColor so it follows the tab's state.
function SkinIcon({ id }: { id: SkinId }) {
  const p = {
    width: 18, height: 18, viewBox: "0 0 16 16", fill: "none",
    stroke: "currentColor", strokeWidth: 1.4,
    strokeLinecap: "round" as const, strokeLinejoin: "round" as const,
    "aria-hidden": true,
  };
  switch (id) {
    case "chat":
      return <svg {...p}><path d="M2.5 3.5h11v6.5h-7L4 12.5V10H2.5z" /></svg>;
    case "casefile":
      return <svg {...p}><path d="M2 4.5h4l1.3 1.5H14v6.5H2z" /></svg>;
    case "transcript":
      return <svg {...p}><path d="M4 2.2h5L12 5v8.8H4z" /><path d="M6 7.5h4M6 10h3" /></svg>;
    case "signal":
      return (
        <svg {...p}>
          <path d="M4.4 4.8 8 11M11.6 5.4 8 11" />
          <circle cx="3.5" cy="4" r="1.3" /><circle cx="12.5" cy="4.5" r="1.3" /><circle cx="8" cy="12" r="1.6" />
        </svg>
      );
  }
}

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

  // Drag-to-reorder the view tabs. Order is session-only; the tab list is
  // small so a plain HTML5 drag-and-drop reorder is plenty.
  const [tabOrder, setTabOrder] = useState<SkinId[]>(() => SKIN_META.map((m) => m.id));
  const [draggingTab, setDraggingTab] = useState<SkinId | null>(null);
  const dropTab = (target: SkinId) => {
    setDraggingTab(null);
    if (!draggingTab || draggingTab === target) return;
    setTabOrder((order) => {
      const next = order.filter((id) => id !== draggingTab);
      next.splice(next.indexOf(target), 0, draggingTab);
      return next;
    });
  };

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
          {tabOrder.map((id) => {
            const m = SKIN_META.find((s) => s.id === id)!;
            return (
            <button
              key={m.id}
              role="tab"
              aria-selected={skin === m.id}
              className={`skin-opt${skin === m.id ? " on" : ""}${draggingTab === m.id ? " dragging" : ""}`}
              onClick={() => setSkin(m.id)}
              title={m.blurb}
              draggable
              onDragStart={() => setDraggingTab(m.id)}
              onDragOver={(e) => e.preventDefault()}
              onDrop={(e) => { e.preventDefault(); dropTab(m.id); }}
              onDragEnd={() => setDraggingTab(null)}
            >
              <span className="skin-icon" aria-hidden>
                <SkinIcon id={m.id} />
              </span>
              <span className="skin-meta">
                <span className="nm">{m.name}</span>
                <span className="tg">{m.tag}</span>
              </span>
            </button>
            );
          })}
        </div>

        <span className="menu-spacer" />

        {state.provider && (
          <span
            className="provider-badge"
            title={state.players.map((p) => `${p.name}: ${p.model ?? "?"}`).join("\n")}
          >
            {state.provider} · {[...new Set(state.players.map((p) => p.model).filter(Boolean))].join(", ") || "unknown model"}
          </span>
        )}
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
