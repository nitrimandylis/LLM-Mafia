"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import type { GameEvent, Player } from "./events";
import { deriveState } from "./derive";

// Dwell time (ms) AFTER an event is shown, before the next reveals. This is the
// whole "drama" knob — kills/eliminations hang, votes snap by. Scaled by speed.
const DELAY: Record<GameEvent["type"], number> = {
  game_start: 500,
  phase: 1500,
  statement: 1700,
  question: 1400,
  answer: 1500,
  accusation: 1800,
  vote: 650,
  elimination: 2400,
  no_elimination: 2400,
  night_kill: 2400,
  detective_will: 2400,
  night_no_kill: 2000,
  save: 2000,
  protection: 1200,
  mafia_chat: 1500,
  investigation: 1500,
  game_over: 1000,
};

export type Speed = 1 | 2 | "instant";

export type ReplayState = {
  events: GameEvent[];
  revealed: GameEvent[];
  current?: GameEvent; // last revealed
  pending?: GameEvent; // next to reveal (drives typing indicators)
  cursor: number; // number of events revealed
  total: number;
  players: Player[];
  phase: "day" | "night";
  day: number;
  alive: Set<string>;
  deaths: Map<string, string>; // name -> role, in death order of reveal
  winner?: string;
  provider?: string;
  playing: boolean;
  speed: Speed;
  controls: {
    toggle: () => void;
    play: () => void;
    pause: () => void;
    setSpeed: (s: Speed) => void;
    scrubTo: (cursor: number) => void;
    restart: () => void;
  };
};

export function useReplay(
  events: GameEvent[],
  initialSpeed: Speed = 1,
  autoplay = true // false = wait for an explicit play() (episode cold open)
): ReplayState {
  const [cursor, setCursor] = useState(0);
  const [playing, setPlaying] = useState(autoplay);
  const [speed, setSpeed] = useState<Speed>(initialSpeed);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Reset when the log changes.
  useEffect(() => {
    setCursor(0);
    setPlaying(autoplay);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [events]);

  // Adopt the saved default speed once it resolves client-side.
  useEffect(() => {
    setSpeed(initialSpeed);
  }, [initialSpeed]);

  // Drive the cursor forward while playing.
  useEffect(() => {
    if (timer.current) clearTimeout(timer.current);
    if (!playing || cursor >= events.length) return;

    if (speed === "instant") {
      setCursor(events.length);
      return;
    }
    const justShown = events[cursor]; // event at index `cursor` becomes visible next
    const delay = (DELAY[justShown.type] ?? 1200) / speed;
    timer.current = setTimeout(() => setCursor((c) => Math.min(c + 1, events.length)), delay);
    return () => {
      if (timer.current) clearTimeout(timer.current);
    };
  }, [cursor, playing, speed, events]);

  const revealed = useMemo(() => events.slice(0, cursor), [events, cursor]);

  const derived = useMemo(() => deriveState(revealed), [revealed]);

  const controls = useMemo(
    () => ({
      toggle: () => setPlaying((p) => !p),
      play: () => setPlaying(true),
      pause: () => setPlaying(false),
      setSpeed: (s: Speed) => setSpeed(s),
      scrubTo: (c: number) => {
        setPlaying(false);
        setCursor(Math.max(0, Math.min(c, events.length)));
      },
      restart: () => {
        setCursor(0);
        setPlaying(true);
      },
    }),
    [events.length]
  );

  return {
    events,
    revealed,
    current: revealed[revealed.length - 1],
    pending: cursor < events.length ? events[cursor] : undefined,
    cursor,
    total: events.length,
    ...derived,
    playing,
    speed,
    controls,
  };
}
