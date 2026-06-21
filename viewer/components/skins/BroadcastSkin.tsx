"use client";

import { isSpeech } from "@/lib/events";
import type { SkinProps } from "./types";

export default function BroadcastSkin({ state }: SkinProps) {
  const { players, revealed, current, alive, deaths, phase, day } = state;
  const lastSpeech = [...revealed].reverse().find(isSpeech);

  const bigReveal =
    current &&
    (current.type === "elimination" || current.type === "night_kill" || current.type === "game_over")
      ? current
      : undefined;

  const tickerParts: string[] = [];
  for (const [name, role] of deaths) tickerParts.push(`${name} eliminated (${role})`);
  tickerParts.push(`${alive.size} alive`);
  if (state.winner) tickerParts.push(state.winner.toUpperCase() + " WINS");
  const ticker = tickerParts.join("  ▸  ");

  return (
    <div className={`cast ${phase}`}>
      <div className="cast-roster">
        {players.map((p) => (
          <span key={p.name} className={`chip ${alive.has(p.name) ? "" : "dead"}`}>
            {p.name}
          </span>
        ))}
      </div>

      <div className="cast-title">
        {bigReveal ? (
          bigReveal.type === "game_over" ? (
            <div className="cast-reveal win">
              {bigReveal.winner === "town" ? "TOWN WINS" : bigReveal.winner === "mafia" ? "MAFIA WINS" : "GAME OVER"}
            </div>
          ) : (
            <div className="cast-reveal">
              {bigReveal.target} <span className="role">— {bigReveal.role}</span>
            </div>
          )
        ) : (
          <>
            <div className={`day ${phase}`}>{phase === "day" ? "DAY" : "NIGHT"} {day || 1}</div>
            <div className="tagline">
              {phase === "day" ? "THE TOWN DELIBERATES" : "NIGHT FALLS ON THE TOWN"}
            </div>
          </>
        )}
      </div>

      {lastSpeech && !bigReveal && (
        <div className="lower-third">
          <div>
            <span className="nameplate">
              {lastSpeech.actor}
              {lastSpeech.type === "accusation" && <span className="tag">ACCUSING</span>}
              {lastSpeech.type === "mafia_chat" && <span className="tag">MAFIA</span>}
            </span>
          </div>
          <div className="third-text">{lastSpeech.text}</div>
        </div>
      )}

      <div className="ticker">
        <span>{ticker}　　▸　　{ticker}</span>
      </div>
    </div>
  );
}
