"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import { PRIVATE_TYPES, type GameEvent } from "@/lib/events";
import { useReplay } from "@/lib/useReplay";
import { SKINS as SKIN_META, type SkinId } from "@/lib/settings";
import type { EpisodeCard, EpisodeMeta } from "@/lib/episodes";
import { caseNumber } from "@/lib/episodes";
import { sting, unlockAudio, soundMuted, setSoundMuted } from "@/lib/sound";
import Controls from "@/components/Controls";
import SkinMenu from "@/components/SkinMenu";
import ChatSkin from "@/components/skins/ChatSkin";
import CaseFileSkin from "@/components/skins/CaseFileSkin";
import TranscriptSkin from "@/components/skins/TranscriptSkin";
import SignalSkin from "@/components/skins/SignalSkin";

export const SKIN_COMPONENTS = {
  chat: ChatSkin,
  casefile: CaseFileSkin,
  transcript: TranscriptSkin,
  signal: SignalSkin,
};

type Props = {
  events: GameEvent[];
  episode: EpisodeMeta;
  roles: Record<string, string>; // final roles by name, from the log's stats
  card: EpisodeCard;
  next?: EpisodeCard;
};

// A death lands as a full-stage card riding the event's existing dwell time
// (useReplay holds 2400ms on kills), so the beat costs no extra engine logic.
type DeathBeat = { name: string; role: string; how: "voted out" | "killed in the night" };

export default function EpisodePlayer({ events, episode, roles, card, next }: Props) {
  // Group Chat is the flagship episode experience; the other skins stay one
  // click away for the curious.
  const [skin, setSkin] = useState<SkinId>("chat");
  const [began, setBegan] = useState(false);
  const [beat, setBeat] = useState<DeathBeat | null>(null);
  const [recapDismissed, setRecapDismissed] = useState(false);
  const [muted, setMuted] = useState(true); // resolved from localStorage after mount
  // Revealed cases default to the honest whodunit; the cold open's second
  // button opts into the mafia's side-channel. Chosen once, before playback.
  const [secrets, setSecrets] = useState(false);
  const beatTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const shown = useMemo(
    () => (secrets ? events : events.filter((e) => !PRIVATE_TYPES.has(e.type))),
    [events, secrets]
  );

  // autoplay=began so that flipping `secrets` at the cold open (a new array,
  // which resets the engine) starts playing instead of stalling.
  const state = useReplay(shown, 1, began);
  const done = state.cursor >= state.total;

  useEffect(() => setMuted(soundMuted()), []);

  // Drama beats: react to the event that just revealed, only during live
  // playback (never while scrubbing or skipping).
  useEffect(() => {
    const e = state.current;
    if (!e || !state.playing || state.speed === "instant") return;
    if (e.type === "elimination" || (e.type === "night_kill" && !e.saved)) {
      sting("kill");
      setBeat({
        name: e.target,
        role: e.role,
        how: e.type === "elimination" ? "voted out" : "killed in the night",
      });
      if (beatTimer.current) clearTimeout(beatTimer.current);
      // hold just inside the 2400ms dwell so the card clears before the next event
      beatTimer.current = setTimeout(() => setBeat(null), 2100 / (state.speed as number));
    } else if (e.type === "phase" && e.phase === "night") {
      sting("night");
    } else if (e.type === "vote") {
      sting("vote");
    } else if (e.type === "save") {
      sting("save");
    } else if (e.type === "game_over") {
      sting("reveal");
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [state.cursor]);

  function begin(withSecrets: boolean) {
    unlockAudio();
    setSecrets(withSecrets);
    setBegan(true);
    state.controls.play();
    sting("begin");
  }

  function toggleMute() {
    const m = !muted;
    setMuted(m);
    setSoundMuted(m);
    if (!m) unlockAudio();
  }

  function watchAgain() {
    setRecapDismissed(false);
    setBeat(null);
    state.controls.restart();
  }

  const mafiaCount = Object.values(roles).filter((r) => r === "Mafia").length;
  const showRecap = began && done && !!state.winner && !recapDismissed;

  return (
    <div className="stage-wrap">
      <div className="menu">
        <Link href="/" className="brand">
          <span className="mark">MAFIA</span>
          <span className="rest">LLM REPLAY</span>
        </Link>
        <span className="ep-mark" title={episode.tagline}>
          <b>{caseNumber(card.slug)}</b> {episode.title}
        </span>

        <span className="menu-spacer" />

        <button
          className="menu-btn"
          onClick={toggleMute}
          aria-pressed={!muted}
          title={muted ? "Sound is off" : "Sound is on"}
        >
          {muted ? "sound off" : "sound on"}
        </button>
        {/* New tab: leaving the page would throw away the replay position. */}
        <a className="menu-btn" href="/rules" target="_blank" rel="noreferrer">
          rules
        </a>
        <a className="menu-btn" href="/about" target="_blank" rel="noreferrer">
          about
        </a>
        <a className="menu-btn ep-walls" href="/wallpapers" target="_blank" rel="noreferrer">
          wallpapers
        </a>
        <Link href="/" className="menu-btn ep-home">
          all cases
        </Link>
        <SkinMenu skin={skin} onChange={setSkin} />
      </div>

      {/* All four stay mounted so each keeps its own scroll position. */}
      {SKIN_META.map((m) => {
        const Skin = SKIN_COMPONENTS[m.id];
        const isActive = skin === m.id;
        return (
          <div key={m.id} className="skin-pane" style={{ display: isActive ? "flex" : "none" }}>
            <Skin state={state} active={isActive} title={episode.title} caseNo={caseNumber(card.slug)} />
          </div>
        );
      })}
      <Controls state={state} />

      {!began && (
        <div className="ep-open" role="dialog" aria-label="Episode intro">
          <div className="ep-open-inner">
            <div className="ep-open-kicker">
              LLM MAFIA · {caseNumber(card.slug)} · {card.days} DAYS ON RECORD
            </div>
            <h1 className="ep-open-title">{episode.title}</h1>
            <p className="ep-open-tagline">{episode.tagline}</p>

            <div className="ep-open-premise">
              <p>
                <b>{card.cast.length} players. All of them language models.</b>{" "}
                {mafiaCount > 0 && (
                  <>
                    <b className="red">{mafiaCount} are mafia</b>, and they know exactly who they are.
                  </>
                )}
              </p>
              <p>
                Each day the town votes somebody out. Each night the mafia kill. Every word
                you&apos;re about to read was written by an AI trying to win. Watch them lie.
              </p>
            </div>

            <div className="ep-open-cast" aria-label="Cast">
              {card.cast.map((p) => (
                <span key={p.name} className="ep-cast-chip">
                  <span className="dot" style={{ background: p.color }} />
                  {p.name}
                </span>
              ))}
            </div>

            <div className="ep-open-actions">
              <button className="ep-begin" onClick={() => begin(false)} autoFocus>
                ▸ BEGIN THE REPLAY
              </button>
              {card.revealed && (
                <button className="ep-begin ep-next" onClick={() => begin(true)}>
                  ▸ WITH SECRETS REVEALED
                </button>
              )}
            </div>
            {/* New tab on purpose: reading the rules must not throw away the replay. */}
            <a className="ep-open-rules" href="/rules" target="_blank" rel="noreferrer">
              new to Mafia? read the rules →
            </a>
            <div className="ep-open-hint">someone dies tonight</div>
          </div>
        </div>
      )}

      {beat && (
        <div className="ep-beat" aria-hidden>
          <div className="ep-beat-name">{beat.name}</div>
          <div className="ep-beat-how">{beat.how}</div>
          <div className={`ep-beat-role${beat.role === "Mafia" ? " mafia" : ""}`}>
            they were {beat.role.toUpperCase()}
          </div>
        </div>
      )}

      {showRecap && (
        <div
          className={`ep-open ep-recap${state.winner === "town" ? " town" : ""}`}
          role="dialog"
          aria-label="Episode recap"
        >
          <div className="ep-open-inner">
            <div className="ep-open-kicker">{caseNumber(card.slug)} · CLOSED</div>
            <h1 className={`ep-open-title${state.winner === "mafia" ? " red" : ""}`}>
              {state.winner === "town" ? "TOWN WINS" : "MAFIA WINS"}
            </h1>

            {episode.recap && <p className="ep-recap-text">{episode.recap}</p>}

            <div className="ep-recap-roles" aria-label="Final roles">
              {state.players.map((p) => {
                const dead = !state.alive.has(p.name);
                const role = roles[p.name] ?? p.role ?? "?";
                return (
                  <span key={p.name} className={`ep-role-chip${dead ? " dead" : ""}`}>
                    <span className="dot" style={{ background: p.color }} />
                    {p.name}
                    <b className={role === "Mafia" ? "mafia" : ""}>{role}</b>
                  </span>
                );
              })}
            </div>

            <div className="ep-recap-meta">
              {card.days} DAYS · {card.deaths} DEAD · {card.cast.length} PLAYED
            </div>

            <div className="ep-recap-actions">
              <button className="ep-begin" onClick={watchAgain}>↻ WATCH AGAIN</button>
              {next && (
                <Link href={`/watch/${next.slug}`} className="ep-begin ep-next">
                  NEXT: {next.title} →
                </Link>
              )}
              <button className="ep-dismiss" onClick={() => setRecapDismissed(true)}>
                read the thread
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
