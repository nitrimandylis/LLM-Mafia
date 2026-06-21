"use client";

// Static render of all four skins against the full sample log — every event
// revealed at once. Doubles as headless verification (curl + grep this route)
// and a one-glance visual QA aid. Not part of the normal viewer flow.

import sample from "@/public/logs/sample.json";
import type { GameEvent } from "@/lib/events";
import { deriveState } from "@/lib/derive";
import type { ReplayState } from "@/lib/useReplay";
import ChatSkin from "@/components/skins/ChatSkin";
import CaseFileSkin from "@/components/skins/CaseFileSkin";
import TranscriptSkin from "@/components/skins/TranscriptSkin";
import SignalSkin from "@/components/skins/SignalSkin";

const events = (sample as unknown as { events: GameEvent[] }).events;

function stateAt(cursor: number): ReplayState {
  const noop = () => {};
  const revealed = events.slice(0, cursor);
  return {
    events,
    revealed,
    current: revealed[revealed.length - 1],
    pending: events[cursor],
    cursor,
    total: events.length,
    ...deriveState(revealed),
    playing: false,
    speed: "instant",
    controls: { toggle: noop, play: noop, pause: noop, setSpeed: noop, scrubTo: noop, restart: noop },
  };
}

export default function SelfTest() {
  const full = stateAt(events.length);
  // A mid-game cursor (just past the last accusation) exercises the in-progress
  // paths — live ballots, partial graph — that the final frame hides.
  const lastSpeechIdx = events.reduce(
    (acc, e, i) => (e.type === "accusation" ? i : acc),
    0
  );
  const mid = stateAt(lastSpeechIdx + 1);
  const skins: [string, React.ReactNode][] = [
    ["Group Chat", <ChatSkin key="c" state={full} active />],
    ["Case File", <CaseFileSkin key="cf" state={full} active />],
    ["Transcript", <TranscriptSkin key="tr" state={full} active />],
    ["Signal", <SignalSkin key="sg" state={full} active />],
    ["Signal (mid-game)", <SignalSkin key="sgm" state={mid} active />],
  ];
  return (
    <div style={{ padding: 18 }}>
      <p style={{ color: "var(--muted)", fontSize: 13 }}>
        Self-test: all three skins, full sample log revealed ({full.total} events,
        winner {full.winner}).
      </p>
      {skins.map(([name, node]) => (
        <section key={name} style={{ marginBottom: 24 }}>
          <h3 style={{ margin: "8px 0" }}>{name}</h3>
          <div style={{ height: 460, display: "flex", flexDirection: "column", border: "1px solid var(--line)", borderRadius: 10, overflow: "hidden" }}>
            {node}
          </div>
        </section>
      ))}
    </div>
  );
}
