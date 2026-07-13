"use client";

import type { GameEvent } from "@/lib/events";
import { isSpeech } from "@/lib/events";
import { initials, useStageScroll, type SkinProps } from "./types";

// Fold the flat event stream into chat items: consecutive votes collapse into
// one ballot, everything else passes through. Speaker grouping (hiding a
// repeated avatar/header) is decided at render time against the previous item.
type Item =
  | { kind: "msg"; e: GameEvent; i: number }
  | { kind: "ballot"; votes: { actor: string; target: string }[]; i: number }
  | { kind: "phase"; e: Extract<GameEvent, { type: "phase" }>; i: number }
  | { kind: "system"; e: GameEvent; i: number };

// Stroke icons in the same vocabulary as the chrome's tab glyphs — color emoji
// render differently per platform, so the UI draws its own.
const ICON = {
  width: 14, height: 14, viewBox: "0 0 16 16", fill: "none",
  stroke: "currentColor", strokeWidth: 1.4,
  strokeLinecap: "round" as const, strokeLinejoin: "round" as const,
  "aria-hidden": true, style: { verticalAlign: "-2px" },
};
const LockIcon = () => (
  <svg {...ICON} width={16} height={16}>
    <rect x="3.5" y="7" width="9" height="6.5" rx="1" />
    <path d="M5.5 7V5.5a2.5 2.5 0 0 1 5 0V7" />
  </svg>
);
const BallotIcon = () => (
  <svg {...ICON}>
    <path d="M2.5 9.5h11v4h-11z" />
    <path d="M5.5 9.5 6.5 3h3l1 6.5M6.5 11.5h3" />
  </svg>
);
const SearchIcon = () => (
  <svg {...ICON}>
    <circle cx="7" cy="7" r="3.5" />
    <path d="m9.7 9.7 3.3 3.3" />
  </svg>
);

function fold(revealed: GameEvent[]): Item[] {
  const out: Item[] = [];
  for (let i = 0; i < revealed.length; i++) {
    const e = revealed[i];
    if (e.type === "vote") {
      const last = out[out.length - 1];
      if (last && last.kind === "ballot") last.votes.push({ actor: e.actor, target: e.target });
      else out.push({ kind: "ballot", votes: [{ actor: e.actor, target: e.target }], i });
    } else if (e.type === "phase") {
      out.push({ kind: "phase", e, i });
    } else if (isSpeech(e)) {
      out.push({ kind: "msg", e, i });
    } else {
      out.push({ kind: "system", e, i });
    }
  }
  return out;
}

export default function ChatSkin({ state, active }: SkinProps) {
  const { revealed, pending, players, phase, day, alive } = state;
  const { ref: scroller, onScroll } = useStageScroll<HTMLDivElement>(active, state.cursor);
  const colorOf = (name: string) => players.find((p) => p.name === name)?.color ?? "#888";
  // Short model tag ("deepseek-ai/deepseek-v4-pro" → "deepseek-v4-pro");
  // absent in logs from before model stamping.
  const modelOf = (name: string) =>
    players.find((p) => p.name === name)?.model?.split("/").pop();
  // Two-sided thread: odd seats speak from the right, even from the left, so
  // the conversation ping-pongs like a real group chat instead of a monologue.
  const flipOf = (name: string) =>
    ((players.find((p) => p.name === name)?.seat ?? 0) % 2) === 1;

  const items = fold(revealed);

  return (
    <div className={`chat ${phase}`}>
      <div className="chat-status">
        <span className={`chat-presence ${phase}`}>{phase === "day" ? "Daytime" : "Nightfall"}</span>
        <span className="chat-status-day">Day {day || 1}</span>
        <span className="chat-status-alive">{alive.size} still in the group</span>
      </div>

      <div className="chat-scroll" ref={scroller} onScroll={onScroll}>
        <div className="chat-inner">
          {items.map((it, idx) => {
            const prev = items[idx - 1];
            if (it.kind === "phase") return <PhaseDivider key={idx} day={it.e.day} phase={it.e.phase} />;
            if (it.kind === "ballot") return <Ballot key={idx} votes={it.votes} colorOf={colorOf} />;
            if (it.kind === "system") return <SystemRow key={idx} e={it.e} />;
            // Group consecutive plain messages from the same speaker.
            const grouped =
              prev?.kind === "msg" &&
              isSpeech(prev.e) &&
              isSpeech(it.e) &&
              prev.e.actor === it.e.actor &&
              it.e.type !== "accusation" &&
              it.e.type !== "mafia_chat" &&
              prev.e.type !== "mafia_chat";
            return (
              <Msg
                key={idx}
                e={it.e}
                color={colorOf(isSpeech(it.e) ? it.e.actor : "")}
                model={isSpeech(it.e) ? modelOf(it.e.actor) : undefined}
                grouped={grouped}
                flip={isSpeech(it.e) && flipOf(it.e.actor)}
              />
            );
          })}

          {pending && isSpeech(pending) && (
            <Msg
              key="typing"
              e={pending}
              color={colorOf(pending.actor)}
              model={modelOf(pending.actor)}
              grouped={false}
              flip={flipOf(pending.actor)}
              typing
            />
          )}
        </div>
      </div>
    </div>
  );
}

function PhaseDivider({ day, phase }: { day: number; phase: "day" | "night" }) {
  return (
    <div className="chat-divider">
      <span className="pill">
        {phase === "day" ? "☀︎ Day " : "☾︎ Night "}
        {day}
      </span>
    </div>
  );
}

function Msg({
  e,
  color,
  model,
  grouped,
  flip,
  typing,
}: {
  e: GameEvent;
  color: string;
  model?: string;
  grouped: boolean;
  flip?: boolean;
  typing?: boolean;
}) {
  if (!isSpeech(e)) return null;
  const whisper = e.type === "mafia_chat";
  const accuse = e.type === "accusation";
  const target = "target" in e ? e.target : undefined;

  return (
    <div className={`chat-row${whisper ? " side" : ""}${flip && !whisper ? " flip" : ""}${grouped ? " grouped" : ""}`}>
      <div className="chat-gutter">
        {!grouped && (
          <div className="avatar" style={{ background: whisper ? "transparent" : color }}>
            {whisper ? <LockIcon /> : initials(e.actor)}
          </div>
        )}
      </div>
      <div className="chat-stack">
        {!grouped && (
          <div className="who">
            {whisper ? `${e.actor} · mafia side-channel` : e.actor}
            {model && <span className="who-model">{model}</span>}
            {accuse && target && <span className="who-accuse"> accuses {target}</span>}
            {!accuse && !whisper && target && <span className="who-to"> → {target}</span>}
          </div>
        )}
        <div className={`bubble${accuse ? " accuse" : ""}${whisper ? " whisper" : ""}${typing ? " typing" : ""}`}>
          {typing ? <span className="dots"><i /><i /><i /></span> : e.text}
        </div>
      </div>
    </div>
  );
}

function Ballot({
  votes,
  colorOf,
}: {
  votes: { actor: string; target: string }[];
  colorOf: (n: string) => string;
}) {
  // Tally targets, most-voted first — the ballot reads like message reactions.
  const tally = new Map<string, string[]>();
  for (const v of votes) {
    if (!tally.has(v.target)) tally.set(v.target, []);
    tally.get(v.target)!.push(v.actor);
  }
  const sorted = [...tally.entries()].sort((a, b) => b[1].length - a[1].length);
  // Heat up the frontrunner's chip — only when they're strictly ahead.
  const leading =
    sorted.length > 0 && (sorted.length === 1 || sorted[0][1].length > sorted[1][1].length)
      ? sorted[0][0]
      : null;
  return (
    <div className="chat-ballot">
      <span className="ballot-label"><BallotIcon /> Ballot</span>
      {sorted.map(([target, voters]) => (
        <span
          key={target}
          className={`ballot-chip${target === leading ? " lead" : ""}`}
          title={voters.join(", ")}
        >
          <span className="dot" style={{ background: colorOf(target) }} />
          {target}
          <b>{voters.length}</b>
        </span>
      ))}
    </div>
  );
}

function SystemRow({ e }: { e: GameEvent }) {
  switch (e.type) {
    case "elimination":
      return (
        <div className="chat-event death">
          <b>{e.target}</b> was voted out — they were <span className="role">{e.role}</span>
        </div>
      );
    case "night_kill":
      return e.saved ? null : (
        <div className="chat-event death">
          <b>{e.target}</b> didn't survive the night — they were <span className="role">{e.role}</span>
        </div>
      );
    case "save":
      return <div className="chat-event save">The doctor saved <b>{e.target}</b></div>;
    case "detective_will":
      return (
        <div className="chat-event save">
          {e.actor}&apos;s final notes were found: investigated {e.target} — <b>{e.result}</b>
        </div>
      );
    case "investigation":
      return (
        <div className="chat-event secret">
          <SearchIcon /> {e.actor} investigated {e.target} — <b>{e.result}</b>
        </div>
      );
    case "game_over":
      return (
        <div className="chat-event gameover">
          {e.winner === "town" ? "TOWN WINS" : e.winner === "mafia" ? "MAFIA WINS" : "GAME OVER"}
        </div>
      );
    default:
      return null;
  }
}
