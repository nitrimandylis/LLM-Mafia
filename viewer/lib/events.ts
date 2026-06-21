// TypeScript mirror of the Python event schema (mafia/events.py) — the source
// of truth. `tools/make_sample_log.py` (check_schema_parity) fails if the
// event-type lists here and in events.py drift apart.

export type Player = {
  name: string;
  seat: number;
  color: string;
  role?: string; // only present in spectator (reveal-secrets) logs
};

export type GameEvent =
  | { type: "game_start"; players: Player[]; player_count: number }
  | { type: "phase"; day: number; phase: "day" | "night" }
  | { type: "statement"; day: number; actor: string; text: string }
  | { type: "question"; day: number; actor: string; target: string; text: string }
  | { type: "answer"; day: number; actor: string; target: string; text: string }
  | { type: "accusation"; day: number; actor: string; target: string | null; text: string }
  | { type: "vote"; day: number; actor: string; target: string }
  | { type: "elimination"; day: number; target: string; role: string; tally: Record<string, number> }
  | { type: "night_kill"; day: number; target: string; role: string; saved: boolean }
  | { type: "save"; day: number; target: string }
  | { type: "mafia_chat"; day: number; actor: string; text: string }
  | { type: "investigation"; day: number; actor: string; target: string; result: string }
  | { type: "game_over"; winner: string; survivors: string[] };

export type GameLog = {
  events?: GameEvent[];
  day?: number;
  [k: string]: unknown;
};

// Events with a speech bubble (dialogue), used by skins to render text.
export const SPEECH_TYPES = new Set([
  "statement",
  "question",
  "answer",
  "accusation",
  "mafia_chat",
]);

export function isSpeech(
  e: GameEvent
): e is Extract<GameEvent, { actor: string; text: string }> {
  return SPEECH_TYPES.has(e.type);
}
