"use client";

import { useRef, useState } from "react";
import type { GameEvent } from "@/lib/events";
import { useStageScroll, type SkinProps } from "./types";

// Instrument panel. An interaction graph wires up who engages whom: dialogue
// edges (questions & answers) show the conversation, suspicion edges
// (accusations & votes) the harder signal. Everything accumulates over the
// replay so the web only grows. Node size = attention aimed at a player,
// emphasised by suspicion. Mafia identities stay hidden until a death reveals
// them — and all of them ignite at the final verdict.
const R = 38; // graph radius in viewBox units (centre 50,50)

export default function SignalSkin({ state, active }: SkinProps) {
  const { players, revealed, alive, deaths, phase, day, winner } = state;
  const { ref: feedRef, onScroll } = useStageScroll<HTMLDivElement>(active, state.cursor);

  // Drag-to-resize the feed sidebar. Width drives a CSS var on the grid; the
  // mobile media query ignores it and stacks instead.
  const graphRef = useRef<HTMLDivElement>(null);
  const [feedW, setFeedW] = useState(272);
  const [dragging, setDragging] = useState(false);
  const onResize = (e: React.PointerEvent) => {
    e.preventDefault();
    setDragging(true);
    document.body.style.userSelect = "none";
    document.body.style.cursor = "col-resize";
    const move = (ev: PointerEvent) => {
      const rect = graphRef.current?.getBoundingClientRect();
      if (rect) setFeedW(Math.max(180, Math.min(560, rect.right - ev.clientX)));
    };
    const up = () => {
      setDragging(false);
      document.body.style.userSelect = "";
      document.body.style.cursor = "";
      window.removeEventListener("pointermove", move);
      window.removeEventListener("pointerup", up);
    };
    window.addEventListener("pointermove", move);
    window.addEventListener("pointerup", up);
  };

  const n = players.length || 1;
  const pos = (i: number) => {
    const a = (-90 + (i * 360) / n) * (Math.PI / 180);
    return { x: 50 + R * Math.cos(a), y: 50 + R * Math.sin(a) };
  };
  const idx = new Map(players.map((p, i) => [p.name, i]));

  // Mafia is revealed by death; at game_over the whole cell lights up.
  const knownMafia = new Set<string>();
  for (const [name, role] of deaths) if (role === "Mafia") knownMafia.add(name);
  if (winner) for (const p of players) if (p.role === "Mafia") knownMafia.add(p.name);

  // Directed interaction edges (actor → target). `dialogue` = questions/answers
  // (who's engaging whom), `suspicion` = accusations/votes (the hot signal).
  // Both accumulate across the whole replay, so adding statements never clears
  // the web — it only ever grows.
  type Edge = { dialogue: number; suspicion: number };
  const edges = new Map<string, Edge>();
  const incoming = new Map<string, number>();   // suspicion aimed at a player (→ MOST SUSPECTED)
  const attention = new Map<string, number>();  // any interaction aimed at a player (→ node size)
  const addEdge = (from: string, to: string | null | undefined, kind: keyof Edge) => {
    if (!from || !to || from === to || !idx.has(from) || !idx.has(to)) return;
    const key = `${from}>${to}`;
    const e = edges.get(key) ?? { dialogue: 0, suspicion: 0 };
    e[kind] += 1;
    edges.set(key, e);
    attention.set(to, (attention.get(to) ?? 0) + 1);
    if (kind === "suspicion") incoming.set(to, (incoming.get(to) ?? 0) + 1);
  };
  for (const e of revealed) {
    if (e.type === "question" || e.type === "answer") addEdge(e.actor, e.target, "dialogue");
    else if (e.type === "accusation") addEdge(e.actor, e.target, "suspicion");
    else if (e.type === "vote") addEdge(e.actor, e.target, "suspicion");
  }

  const mostSuspected = [...incoming.entries()].sort((a, b) => b[1] - a[1])[0];

  return (
    <div className={`signal ${phase}`}>
      <header className="sg-head">
        <span className="sg-readout">
          <b className={phase}>{phase === "day" ? "DAY" : "NIGHT"}</b> {String(day || 1).padStart(2, "0")}
        </span>
        <span className="sg-metric"><i>{alive.size}</i> ALIVE</span>
        <span className="sg-metric"><i>{deaths.size}</i> DOWN</span>
        <span className="sg-metric wide">
          MOST SUSPECTED <i>{mostSuspected ? mostSuspected[0] : "—"}</i>
        </span>
        <span className="sg-legend">
          <em className="line asks" /> asks <em className="line suspects" /> suspects <em className="mafia" /> mafia
        </span>
      </header>

      <div className="sg-graph" ref={graphRef} style={{ "--sg-feed-w": `${feedW}px` } as React.CSSProperties}>
        <svg viewBox="0 0 100 100" preserveAspectRatio="xMidYMid meet">
          {[...edges.entries()].map(([key, w]) => {
            const [from, to] = key.split(">");
            const a = pos(idx.get(from)!);
            const b = pos(idx.get(to)!);
            const total = w.dialogue + w.suspicion;
            const hot = knownMafia.has(from);   // confirmed mafia → red
            const suspicion = w.suspicion > 0;  // accused/voted → amber
            const stroke = hot ? "var(--sg-mafia)" : suspicion ? "var(--sg-susp)" : "var(--sg-edge)";
            return (
              <line
                key={key}
                x1={a.x} y1={a.y} x2={b.x} y2={b.y}
                stroke={stroke}
                strokeWidth={0.3 + Math.min(total, 5) * 0.34}
                strokeOpacity={hot ? 0.85 : suspicion ? 0.6 : 0.3}
                strokeLinecap="round"
              />
            );
          })}
          {players.map((p, i) => {
            const { x, y } = pos(i);
            const dead = !alive.has(p.name);
            const mafia = knownMafia.has(p.name);
            const susp = incoming.get(p.name) ?? 0;
            const r = 2.4 + Math.min(attention.get(p.name) ?? 0, 12) * 0.26 + Math.min(susp, 6) * 0.36;
            return (
              <g key={p.name} opacity={dead ? 0.4 : 1}>
                {mafia && <circle cx={x} cy={y} r={r + 1.6} fill="none" stroke="var(--sg-mafia)" strokeWidth={0.8} />}
                <circle cx={x} cy={y} r={r} fill={p.color} stroke="#0e1419" strokeWidth={0.5} />
                {dead && (
                  <text x={x} y={y + 1.1} textAnchor="middle" fontSize={r * 1.3} fill="#0e1419">✕</text>
                )}
                <text x={x} y={y + r + 3.4} textAnchor="middle" fontSize={2.6} fill="var(--sg-ink)" className="sg-node-label">
                  {p.name}
                </text>
              </g>
            );
          })}
        </svg>

        <div
          className={`sg-resizer${dragging ? " dragging" : ""}`}
          onPointerDown={onResize}
          role="separator"
          aria-orientation="vertical"
          title="Drag to resize the feed"
        />

        <aside className="sg-feed" ref={feedRef} onScroll={onScroll}>
          <div className="sg-feed-head">SIGNAL FEED</div>
          {revealed.map((e, i) => (
            <FeedLine key={i} e={e} />
          ))}
        </aside>
      </div>
    </div>
  );
}

function FeedLine({ e }: { e: GameEvent }) {
  const map: Partial<Record<GameEvent["type"], [string, string]>> = {
    statement: ["·", ""],
    question: ["?", ""],
    answer: ["»", ""],
    accusation: ["!", "accuse"],
    vote: ["▸", "vote"],
    mafia_chat: ["◆", "mafia"],
    investigation: ["◎", "probe"],
    elimination: ["✕", "down"],
    night_kill: ["☾", "down"],
    save: ["+", "save"],
    phase: ["—", "phase"],
    game_over: ["■", "end"],
  };
  const [glyph, cls] = map[e.type] ?? ["·", ""];
  return (
    <div className={`sg-line ${cls}`}>
      <span className="sg-glyph">{glyph}</span>
      <span className="sg-text">{summarize(e)}</span>
    </div>
  );
}

function summarize(e: GameEvent): string {
  switch (e.type) {
    case "phase": return `${e.phase === "day" ? "DAY" : "NIGHT"} ${e.day}`;
    case "statement": return `${e.actor}: ${e.text}`;
    case "question": return `${e.actor} → ${e.target}: ${e.text}`;
    case "answer": return `${e.actor} → ${e.target}: ${e.text}`;
    case "accusation": return `${e.actor} accuses ${e.target ?? "?"}`;
    case "vote": return `${e.actor} votes ${e.target}`;
    case "mafia_chat": return `${e.actor} [mafia]: ${e.text}`;
    case "investigation": return `${e.actor} probes ${e.target} → ${e.result}`;
    case "elimination": return `${e.target} eliminated — ${e.role}`;
    case "night_kill": return e.saved ? `attack on ${e.target} failed` : `${e.target} killed — ${e.role}`;
    case "save": return `${e.target} saved`;
    case "game_over": return `${e.winner.toUpperCase()} WINS`;
    default: return "";
  }
}
