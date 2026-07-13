import type { GameEvent, Player } from "./events";

export type DerivedState = {
  players: Player[];
  alive: Set<string>;
  deaths: Map<string, string>; // name -> role, in death-reveal order
  phase: "day" | "night";
  day: number;
  winner?: string;
  provider?: string;
};

// Fold the revealed events into the current game state. Pure — shared by the
// live engine (useReplay) and the static self-test page.
export function deriveState(revealed: GameEvent[]): DerivedState {
  let players: Player[] = [];
  const alive = new Set<string>();
  const deaths = new Map<string, string>();
  let phase: "day" | "night" = "day";
  let day = 0;
  let winner: string | undefined;
  let provider: string | undefined;

  for (const e of revealed) {
    switch (e.type) {
      case "game_start":
        players = e.players;
        provider = e.provider;
        for (const p of e.players) alive.add(p.name);
        break;
      case "phase":
        phase = e.phase;
        day = e.day;
        break;
      case "elimination":
        alive.delete(e.target);
        deaths.set(e.target, e.role);
        break;
      case "night_kill":
        if (!e.saved) {
          alive.delete(e.target);
          deaths.set(e.target, e.role);
        }
        break;
      case "game_over":
        winner = e.winner;
        break;
    }
  }
  return { players, alive, deaths, phase, day, winner, provider };
}
