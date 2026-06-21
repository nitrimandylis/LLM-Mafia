"use client";

import type { GameEvent } from "@/lib/events";
import { useStageScroll, type SkinProps } from "./types";

// Instrument panel. A suspicion graph wires up every accusation and vote in
// real time; node size = how suspected you are. Mafia identities stay hidden
// until a death reveals them — and all of them ignite at the final verdict.
const R = 38; // graph radius in viewBox units (centre 50,50)

export default function SignalSkin({ state, active }: SkinProps) {
  const { players, revealed, alive, deaths, phase, day, winner } = state;
  const { ref: feedRef, onScroll } = useStageScroll<HTMLDivElement>(active, state.cursor);

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

  // Directed edges (actor → target) and incoming suspicion per target.
  const edges = new Map<string, number>();
  const incoming = new Map<string, number>();
  for (const e of revealed) {
    let from: string | undefined, to: string | null | undefined;
    if (e.type === "accusation") { from = e.actor; to = e.target; }
    else if (e.type === "vote") { from = e.actor; to = e.target; }
    if (!from || !to || !idx.has(from) || !idx.has(to)) continue;
    edges.set(`${from}>${to}`, (edges.get(`${from}>${to}`) ?? 0) + 1);
    incoming.set(to, (incoming.get(to) ?? 0) + 1);
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
          <em className="town" /> town <em className="mafia" /> mafia
        </span>
      </header>

      <div className="sg-graph">
        <svg viewBox="0 0 100 100" preserveAspectRatio="xMidYMid meet">
          {[...edges.entries()].map(([key, w]) => {
            const [from, to] = key.split(">");
            const a = pos(idx.get(from)!);
            const b = pos(idx.get(to)!);
            const hot = knownMafia.has(from);
            return (
              <line
                key={key}
                x1={a.x} y1={a.y} x2={b.x} y2={b.y}
                stroke={hot ? "var(--sg-mafia)" : "var(--sg-edge)"}
                strokeWidth={0.4 + Math.min(w, 4) * 0.45}
                strokeOpacity={hot ? 0.85 : 0.4}
                strokeLinecap="round"
              />
            );
          })}
          {players.map((p, i) => {
            const { x, y } = pos(i);
            const dead = !alive.has(p.name);
            const mafia = knownMafia.has(p.name);
            const r = 2.6 + Math.min(incoming.get(p.name) ?? 0, 6) * 0.55;
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
      </div>

      <aside className="sg-feed" ref={feedRef} onScroll={onScroll}>
        <div className="sg-feed-head">SIGNAL FEED</div>
        {revealed.slice(-40).map((e, i) => (
          <FeedLine key={i} e={e} />
        ))}
      </aside>
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
