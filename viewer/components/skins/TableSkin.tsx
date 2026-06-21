"use client";

import type { GameEvent } from "@/lib/events";
import { isSpeech } from "@/lib/events";
import { initials, type SkinProps } from "./types";

export default function TableSkin({ state }: SkinProps) {
  const { players, revealed, current, alive, phase, day } = state;

  // Spotlight follows the most recent speaker.
  const lastSpeech = [...revealed].reverse().find(isSpeech);
  const speaker = lastSpeech?.actor;

  const n = players.length || 1;
  const rx = 40; // % radius
  const ry = 38;

  return (
    <div className={`table-skin ${phase}`}>
      <div className={`table-day ${phase}`}>
        {phase === "day" ? "☀️ DAY" : "🌙 NIGHT"} {day || 1}
      </div>
      <div className="felt" />

      {players.map((p, i) => {
        const angle = (-90 + (i * 360) / n) * (Math.PI / 180);
        const left = 50 + rx * Math.cos(angle);
        const top = 50 + ry * Math.sin(angle);
        const dead = !alive.has(p.name);
        return (
          <div
            key={p.name}
            className={`seat${p.name === speaker && !dead ? " spot" : ""}${dead ? " dead" : ""}`}
            style={{ left: `${left}%`, top: `${top}%` }}
          >
            <div className="disc" style={{ background: p.color }}>{initials(p.name)}</div>
            <div className="nm">{p.name}</div>
          </div>
        );
      })}

      <div className="center-card">{renderCenter(current, lastSpeech)}</div>
    </div>
  );
}

function renderCenter(current: GameEvent | undefined, lastSpeech: GameEvent | undefined) {
  if (current) {
    if (current.type === "elimination")
      return (
        <div className="big death">
          {current.target} voted out
          <div className="sub">they were {current.role}</div>
        </div>
      );
    if (current.type === "night_kill")
      return (
        <div className="big death">
          {current.target} killed
          <div className="sub">they were {current.role}</div>
        </div>
      );
    if (current.type === "save")
      return <div className="big save">{current.target} was saved!</div>;
    if (current.type === "game_over")
      return (
        <div className="big gameover">
          {current.winner === "town" ? "TOWN WINS" : current.winner === "mafia" ? "MAFIA WINS" : "GAME OVER"}
        </div>
      );
    if (current.type === "phase")
      return (
        <div className="big">
          {current.phase === "day" ? "☀️ DAY" : "🌙 NIGHT"} {current.day}
        </div>
      );
  }
  if (lastSpeech && "text" in lastSpeech)
    return (
      <div className="speech">
        <div className="who">{lastSpeech.actor}</div>
        {lastSpeech.text}
      </div>
    );
  return <div className="sub">The town gathers…</div>;
}
