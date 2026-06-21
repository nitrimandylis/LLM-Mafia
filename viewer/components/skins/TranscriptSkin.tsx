"use client";

import type { GameEvent, Ballot } from "@/lib/events";
import { withBallots, tallyVotes } from "@/lib/events";
import { useStageScroll, type SkinProps } from "./types";

// A line-numbered court deposition. The typography is the design; votes become
// a typeset ballot exhibit and the eliminated are STRICKEN FROM THE RECORD.
export default function TranscriptSkin({ state, active }: SkinProps) {
  const { revealed, phase, winner } = state;
  const { ref: scroller, onScroll } = useStageScroll<HTMLDivElement>(active, state.cursor);

  const items = withBallots(revealed);
  let line = 0; // running deposition line number — only utterances get one

  return (
    <div className={`transcript ${phase}`} ref={scroller} onScroll={onScroll}>
      <div className="tr-page">
        <header className="tr-masthead">
          <div className="tr-court">IN THE MATTER OF THE TOWN</div>
          <div className="tr-record">OFFICIAL RECORD OF PROCEEDINGS · VERBATIM</div>
        </header>

        {items.map((e, i) => {
          if (isUtterance(e)) line += 1;
          return <Line key={i} e={e} no={isUtterance(e) ? line : undefined} />;
        })}

        {winner && (
          <div className="tr-verdict">
            <div className="tr-seal">⚖</div>
            <div className="tr-verdict-text">
              VERDICT — {winner === "mafia" ? "FOR THE MAFIA" : winner === "town" ? "FOR THE TOWN" : "NO RESOLUTION"}
            </div>
            <div className="tr-verdict-sub">So entered into the record. Proceedings adjourned.</div>
          </div>
        )}
      </div>
    </div>
  );
}

function isUtterance(e: GameEvent | Ballot): boolean {
  return e.type === "statement" || e.type === "question" || e.type === "answer" || e.type === "accusation";
}

function Line({ e, no }: { e: GameEvent | Ballot; no?: number }) {
  const num = <span className="tr-no">{no != null ? String(no).padStart(3, "0") : ""}</span>;

  switch (e.type) {
    case "phase":
      return (
        <div className="tr-section">
          {e.phase === "day" ? `DAY ${e.day} — CONVENED` : `NIGHT ${e.day} — THE COURT RECESSES`}
        </div>
      );
    case "statement":
      return (
        <div className="tr-line">
          {num}
          <span className="tr-body"><span className="tr-speaker">{e.actor}.</span> {e.text}</span>
        </div>
      );
    case "question":
      return (
        <div className="tr-line">
          {num}
          <span className="tr-body"><span className="tr-speaker">{e.actor}, to {e.target}.</span> {e.text}</span>
        </div>
      );
    case "answer":
      return (
        <div className="tr-line">
          {num}
          <span className="tr-body"><span className="tr-speaker">{e.actor}, in reply.</span> {e.text}</span>
        </div>
      );
    case "accusation":
      return (
        <div className="tr-line accuse">
          {num}
          <span className="tr-body">
            <span className="tr-speaker">{e.actor}.</span>{" "}
            <span className="tr-bracket">[accuses {e.target ?? "the room"}]</span> {e.text}
          </span>
        </div>
      );
    case "mafia_chat":
      return (
        <div className="tr-line sealed">
          {num}
          <span className="tr-body">
            <span className="tr-seal-tag">[SEALED · MAFIA CONFERENCE]</span>{" "}
            <span className="tr-speaker">{e.actor}.</span> {e.text}
          </span>
        </div>
      );
    case "ballot": {
      const tally = tallyVotes(e.votes);
      return (
        <div className="tr-exhibit">
          <div className="tr-exhibit-cap">EXHIBIT — BALLOT OF THE ASSEMBLY</div>
          <table>
            <tbody>
              {tally.map(([t, v]) => (
                <tr key={t}>
                  <td className="tr-ex-name">{t}</td>
                  <td className="tr-ex-dots">{"●".repeat(v.length)}</td>
                  <td className="tr-ex-n">{v.length}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
    }
    case "investigation":
      return (
        <div className="tr-finding">
          SEALED FINDING — {e.actor} examined {e.target}, returned <b>{e.result}</b>.
        </div>
      );
    case "elimination":
      return (
        <div className="tr-struck">
          STRICKEN FROM THE RECORD — <s>{e.target}</s>, found to be {e.role}, removed by vote of the assembly.
        </div>
      );
    case "night_kill":
      return e.saved ? null : (
        <div className="tr-struck night">
          FOUND DECEASED — <s>{e.target}</s>, {e.role}, entered into evidence at dawn.
        </div>
      );
    case "save":
      return <div className="tr-finding">NOTED — an attempt upon {e.target} was prevented.</div>;
    default:
      return null;
  }
}
