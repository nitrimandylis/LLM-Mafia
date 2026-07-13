// TypeScript mirror of the Python event schema (mafia/events.py) — the source
// of truth. `tools/make_sample_log.py` (check_schema_parity) fails if the
// event-type lists here and in events.py drift apart.

export type Player = {
  name: string;
  seat: number;
  color: string;
  model?: string; // absent in logs from before model stamping
  role?: string; // only present in spectator (reveal-secrets) logs
};

export type GameEvent =
  | { type: "game_start"; players: Player[]; player_count: number; provider?: string }
  | { type: "phase"; day: number; phase: "day" | "night" }
  | { type: "statement"; day: number; actor: string; text: string }
  | { type: "question"; day: number; actor: string; target: string; text: string }
  | { type: "answer"; day: number; actor: string; target: string; text: string }
  | { type: "accusation"; day: number; actor: string; target: string | null; text: string }
  | { type: "vote"; day: number; actor: string; target: string }
  | { type: "elimination"; day: number; target: string; role: string; tally: Record<string, number> }
  | { type: "night_kill"; day: number; target: string; role: string; saved: boolean }
  | { type: "night_no_kill"; day: number }
  | { type: "save"; day: number; target: string }
  | { type: "protection"; day: number; actor: string; target: string }
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

// A run of consecutive votes — skins render these as one tally, not N lines.
export type Ballot = { type: "ballot"; votes: { actor: string; target: string }[] };

// Collapse consecutive `vote` events into a single Ballot; pass everything else
// through unchanged. Shared by the Case File and Transcript skins.
export function withBallots(revealed: GameEvent[]): (GameEvent | Ballot)[] {
  const out: (GameEvent | Ballot)[] = [];
  for (const e of revealed) {
    const last = out[out.length - 1];
    if (e.type === "vote") {
      if (last && last.type === "ballot") last.votes.push({ actor: e.actor, target: e.target });
      else out.push({ type: "ballot", votes: [{ actor: e.actor, target: e.target }] });
    } else {
      out.push(e);
    }
  }
  return out;
}

// Tally a ballot's targets, most-voted first.
export function tallyVotes(votes: { actor: string; target: string }[]): [string, string[]][] {
  const m = new Map<string, string[]>();
  for (const v of votes) (m.get(v.target) ?? m.set(v.target, []).get(v.target)!).push(v.actor);
  return [...m.entries()].sort((a, b) => b[1].length - a[1].length);
}
