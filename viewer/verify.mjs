// Headless logic check for the replay data + engine reduction.
// Mirrors the reducer in lib/useReplay.ts and the event types the skins render.
// Run: node verify.mjs
import { readFileSync } from "node:fs";
import assert from "node:assert/strict";

const log = JSON.parse(readFileSync(new URL("./public/logs/sample.json", import.meta.url)));
const events = log.events;
assert(Array.isArray(events) && events.length > 0, "events[] present");

// Event types every skin's render switch handles (game_start carries data, not a row).
const RENDERED = new Set([
  "game_start", "phase", "statement", "question", "answer", "accusation",
  "vote", "elimination", "night_kill", "detective_will", "save", "mafia_chat",
  "investigation", "game_over",
]);

// 1. Boundaries.
assert.equal(events[0].type, "game_start", "first event is game_start");
assert.equal(events.at(-1).type, "game_over", "last event is game_over");

// 2. Every event type is renderable (else content silently vanishes in the UI).
const unknown = [...new Set(events.map((e) => e.type))].filter((t) => !RENDERED.has(t));
assert.deepEqual(unknown, [], `all event types renderable (unknown: ${unknown})`);

// 3. Reduce alive/deaths/winner exactly as useReplay does.
const players = events[0].players.map((p) => p.name);
const alive = new Set(players);
const deaths = new Map();
let winner;
for (const e of events) {
  if (e.type === "elimination") { alive.delete(e.target); deaths.set(e.target, e.role); }
  else if (e.type === "night_kill" && !e.saved) { alive.delete(e.target); deaths.set(e.target, e.role); }
  else if (e.type === "game_over") winner = e.winner;
}

// 4. Cross-check against the game_over survivor list.
const survivors = events.at(-1).survivors;
assert.deepEqual([...alive].sort(), [...survivors].sort(), "reduced alive == game_over survivors");
assert.equal(alive.size + deaths.size, players.length, "everyone is alive xor dead");
assert(["town", "mafia", "timeout"].includes(winner), `valid winner: ${winner}`);

// 5. Referential integrity: actors/targets must be real players.
const known = new Set(players);
for (const e of events) {
  if ("actor" in e) assert(known.has(e.actor), `actor ${e.actor} is a player`);
  if ("target" in e && e.target != null && e.type !== "save")
    assert(known.has(e.target), `target ${e.target} is a player`);
}

const counts = events.reduce((m, e) => ((m[e.type] = (m[e.type] || 0) + 1), m), {});
console.log("OK:", events.length, "events;", deaths.size, "deaths; winner =", winner);
console.log("types:", counts);
