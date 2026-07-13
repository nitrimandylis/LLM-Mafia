"use client";

import type { GameEvent, Ballot } from "@/lib/events";
import { withBallots, tallyVotes } from "@/lib/events";
import { initials, useStageScroll, type SkinProps } from "./types";

// Noir investigation board: you're the detective reading the case as it builds.
// Signature move — intercepted mafia comms render as a DECLASSIFIED redaction
// memo, the dramatic irony of a spectator log made literal.
export default function CaseFileSkin({ state, active }: SkinProps) {
  const { players, revealed, alive, deaths, phase, day, winner } = state;
  const { ref: scroller, onScroll } = useStageScroll<HTMLElement>(active, state.cursor);

  const items = withBallots(revealed);
  const caseNo = String(1000 + (players.length || 0) * 7);

  return (
    <div className={`casefile ${phase}`}>
      <aside className="cf-suspects">
        <div className="cf-rail-head">SUSPECTS</div>
        {players.map((p) => {
          const dead = !alive.has(p.name);
          const role = deaths.get(p.name);
          const mafia = role === "Mafia";
          return (
            <div key={p.name} className={`cf-card${dead ? " closed" : ""}`}>
              <span className="cf-clip" />
              <div className="cf-mug" style={{ background: p.color }}>{initials(p.name)}</div>
              <div className="cf-id">
                <div className="cf-name">{p.name}</div>
                {p.model && <div className="cf-model">{p.model}</div>}
                {dead ? (
                  <div className={`cf-stamp-sm${mafia ? " mafia" : ""}`}>{role ?? "DECEASED"}</div>
                ) : (
                  <div className="cf-status">AT LARGE</div>
                )}
              </div>
            </div>
          );
        })}
      </aside>

      <main className="cf-file" ref={scroller} onScroll={onScroll}>
        <header className="cf-header">
          <div className="cf-no">CASE №{caseNo}</div>
          <div className="cf-title">THE TOWN MURDERS</div>
          <div className={`cf-sub ${phase}`}>
            {phase === "day" ? "▣ DAY" : "☾ NIGHT"} {day || 1} — {phase === "day" ? "IN SESSION" : "AFTER DARK"}
          </div>
        </header>

        <div className="cf-log">
          {items.map((e, i) => (
            <CaseRow key={i} e={e} />
          ))}
          {winner && (
            <div className="cf-closed-stamp">
              CASE CLOSED
              <span>{winner === "mafia" ? "MAFIA PREVAILED" : winner === "town" ? "TOWN PREVAILED" : "UNRESOLVED"}</span>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

function CaseRow({ e }: { e: GameEvent | Ballot }) {
  switch (e.type) {
    case "phase":
      return (
        <div className="cf-divider">
          {e.phase === "day" ? "▣ DAY" : "☾ NIGHT"} {e.day}
        </div>
      );
    case "statement":
      return <Testimony who={e.actor} text={e.text} />;
    case "question":
      return <Testimony who={e.actor} to={e.target} text={e.text} verb="ASKS" />;
    case "answer":
      return <Testimony who={e.actor} to={e.target} text={e.text} verb="REPLIES" />;
    case "accusation":
      return (
        <div className="cf-testimony accuse">
          <div className="cf-speaker">
            {e.actor} <span className="cf-points">NAMES {e.target ?? "—"}</span>
          </div>
          <p>{e.text}</p>
        </div>
      );
    case "mafia_chat":
      return (
        <div className="cf-intercept">
          <div className="cf-intercept-head">
            <span className="cf-declass">DECLASSIFIED</span> INTERCEPTED COMMS — {e.actor}
          </div>
          <p className="cf-redacted">{e.text}</p>
        </div>
      );
    case "ballot": {
      const tally = tallyVotes(e.votes);
      return (
        <div className="cf-tally">
          <span className="cf-tally-label">TALLY OF THE VOTE</span>
          {tally.map(([t, v]) => (
            <span key={t} className="cf-tally-row">
              {t} <b>{"|".repeat(v.length)}</b> {v.length}
            </span>
          ))}
        </div>
      );
    }
    case "investigation":
      return (
        <div className="cf-report">
          FIELD REPORT — {e.actor} examined {e.target}:{" "}
          <b className={e.result.toUpperCase() === "INNOCENT" ? "ok" : "bad"}>{e.result}</b>
        </div>
      );
    case "elimination":
      return <Verdict label="ELIMINATED BY VOTE" name={e.target} role={e.role} />;
    case "night_kill":
      return e.saved ? null : <Verdict label="FOUND SLAIN AT DAWN" name={e.target} role={e.role} />;
    case "save":
      return <div className="cf-report foiled">ATTEMPT ON {e.target} FOILED — subject survives</div>;
    default:
      return null;
  }
}

function Testimony({
  who,
  text,
  to,
  verb,
}: {
  who: string;
  text: string;
  to?: string;
  verb?: string;
}) {
  return (
    <div className="cf-testimony">
      <div className="cf-speaker">
        {who}
        {to && <span className="cf-to"> {verb} {to}</span>}
      </div>
      <p>{text}</p>
    </div>
  );
}

function Verdict({ label, name, role }: { label: string; name: string; role: string }) {
  return (
    <div className={`cf-verdict${role === "Mafia" ? " mafia" : ""}`}>
      <span className="cf-verdict-stamp">{label}</span>
      <span className="cf-verdict-name">{name}</span>
      <span className="cf-verdict-role">was {role}</span>
    </div>
  );
}
