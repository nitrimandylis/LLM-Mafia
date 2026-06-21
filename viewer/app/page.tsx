"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import type { GameEvent, GameLog } from "@/lib/events";
import { useReplay } from "@/lib/useReplay";
import { loadSettings, DEFAULTS, type SkinId } from "@/lib/settings";
import Controls from "@/components/Controls";
import ChatSkin from "@/components/skins/ChatSkin";
import TableSkin from "@/components/skins/TableSkin";
import BroadcastSkin from "@/components/skins/BroadcastSkin";

const SKINS = { chat: ChatSkin, table: TableSkin, broadcast: BroadcastSkin };

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
  const ActiveSkin = SKINS[skin];

  return (
    <div className="stage-wrap">
      <div
        style={{
          display: "flex",
          gap: 12,
          padding: "8px 18px",
          borderBottom: "1px solid var(--line)",
          alignItems: "center",
          fontSize: 12,
          color: "var(--muted)",
        }}
      >
        <span>Style:</span>
        {(["chat", "table", "broadcast"] as SkinId[]).map((s) => (
          <button
            key={s}
            onClick={() => setSkin(s)}
            style={{
              background: skin === s ? "var(--red)" : "var(--panel-2)",
              color: skin === s ? "#fff" : "var(--ink)",
              border: "1px solid var(--line)",
              borderRadius: 6,
              padding: "4px 10px",
              cursor: "pointer",
              textTransform: "capitalize",
            }}
          >
            {s}
          </button>
        ))}
        <span style={{ flex: 1 }} />
        {source && (
          <span title="Where this replay came from">
            {source === "game"
              ? "● latest game"
              : source === "sample"
              ? "○ bundled sample"
              : "○ uploaded file"}
          </span>
        )}
        <button
          onClick={loadFromServer}
          style={{
            background: "var(--panel-2)",
            color: "var(--ink)",
            border: "1px solid var(--line)",
            borderRadius: 6,
            padding: "4px 10px",
            cursor: "pointer",
          }}
          title="Reload ../game_log.json from the engine"
        >
          ↻ Latest game
        </button>
        <button
          onClick={() => fileInput.current?.click()}
          style={{
            background: "var(--panel-2)",
            color: "var(--ink)",
            border: "1px solid var(--line)",
            borderRadius: 6,
            padding: "4px 10px",
            cursor: "pointer",
          }}
        >
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
          <ActiveSkin state={state} />
          <Controls state={state} />
        </>
      )}
    </div>
  );
}
