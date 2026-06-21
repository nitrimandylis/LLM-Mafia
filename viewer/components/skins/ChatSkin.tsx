"use client";

import { useEffect, useRef } from "react";
import type { GameEvent } from "@/lib/events";
import { isSpeech } from "@/lib/events";
import { initials, type SkinProps } from "./types";

export default function ChatSkin({ state }: SkinProps) {
  const { revealed, pending, players, phase } = state;
  const scroller = useRef<HTMLDivElement>(null);
  const colorOf = (name: string) =>
    players.find((p) => p.name === name)?.color ?? "#888";

  useEffect(() => {
    const el = scroller.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [revealed.length, pending]);

  return (
    <div className={`chat ${phase}`} ref={scroller}>
      <div className="chat-inner">
        {revealed.map((e, i) => (
          <Row key={i} e={e} color={isSpeech(e) ? colorOf(e.actor) : "#888"} />
        ))}
        {pending && isSpeech(pending) && (
          <div className="chat-row">
            <div className="avatar" style={{ background: colorOf(pending.actor) }}>
              {initials(pending.actor)}
            </div>
            <div className="bubble typing">
              <div className="who">{pending.actor}</div>
              typing…
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function Row({ e, color }: { e: GameEvent; color: string }) {
  switch (e.type) {
    case "statement":
    case "question":
    case "answer":
      return (
        <div className="chat-row">
          <div className="avatar" style={{ background: color }}>{initials(e.actor)}</div>
          <div className="bubble">
            <div className="who">
              {e.actor}
              {e.type !== "statement" && " → " + e.target}
            </div>
            {e.text}
          </div>
        </div>
      );
    case "accusation":
      return (
        <div className="chat-row">
          <div className="avatar" style={{ background: color }}>{initials(e.actor)}</div>
          <div className="bubble accuse">
            <div className="who">⚔️ {e.actor} accuses{e.target ? " " + e.target : ""}</div>
            {e.text}
          </div>
        </div>
      );
    case "mafia_chat":
      return (
        <div className="chat-row">
          <div className="avatar" style={{ background: color }}>{initials(e.actor)}</div>
          <div className="bubble whisper">
            <div className="who">🤫 {e.actor} (mafia whisper)</div>
            {e.text}
          </div>
        </div>
      );
    case "vote":
      return <div className="vote-line">🗳️ {e.actor} → {e.target}</div>;
    case "phase":
      return (
        <div className="divider">
          <span className="pill">{e.phase === "day" ? "☀️ Day " : "🌙 Night "}{e.day}</span>
        </div>
      );
    case "elimination":
      return (
        <div className="event-banner death">
          💀 The town voted out <b>{e.target}</b> — they were{" "}
          <span className="role">{e.role}</span>
        </div>
      );
    case "night_kill":
      return (
        <div className="event-banner death">
          🌙 <b>{e.target}</b> was killed in the night — they were{" "}
          <span className="role">{e.role}</span>
        </div>
      );
    case "save":
      return <div className="event-banner save">✨ The doctor saved <b>{e.target}</b>!</div>;
    case "investigation":
      return (
        <div className="event-banner secret">
          🔍 {e.actor} investigated {e.target}: <b>{e.result}</b>
        </div>
      );
    case "game_over":
      return (
        <div className="event-banner gameover">
          {e.winner === "town" ? "🎉 TOWN WINS" : e.winner === "mafia" ? "😈 MAFIA WINS" : "⏰ GAME OVER"}
        </div>
      );
    default:
      return null;
  }
}
