"use client";

import { useEffect, useRef, useState } from "react";
import type { GameEvent, GameLog } from "@/lib/events";
import { useReplay } from "@/lib/useReplay";
import { SKINS as SKIN_META, type SkinId } from "@/lib/settings";
import Controls from "@/components/Controls";
import SkinMenu from "@/components/SkinMenu";
import { SKIN_COMPONENTS } from "@/components/EpisodePlayer";

export default function Viewer() {
  const [events, setEvents] = useState<GameEvent[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [source, setSource] = useState<"game" | "sample" | "upload" | null>(null);
  const [skin, setSkin] = useState<SkinId>("chat");
  const fileInput = useRef<HTMLInputElement>(null);

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

  const state = useReplay(events ?? [], 1);

  return (
    <div className="stage-wrap">
      <div className="menu">
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
        <SkinMenu skin={skin} onChange={setSkin} />
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
