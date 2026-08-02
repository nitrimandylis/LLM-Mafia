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

// 6. The landing page's record strip (lib/stats.ts) counts over every published
// log. This checks the invariants those counts rest on, not today's totals,
// which change every time a case is published. The failure it exists to catch:
// an event type gets renamed in the engine and a tile silently reads 0.
const SPEECH = ["statement", "question", "answer", "accusation", "mafia_chat"];
const manifest = JSON.parse(
  readFileSync(new URL("./public/logs/manifest.json", import.meta.url)),
);

let words = 0;
let bodies = 0;
let hangings = 0;
let innocentsHanged = 0;
const accusations = new Map();

for (const episode of manifest.episodes) {
  const url = new URL(`./public/logs/${episode.slug}.json`, import.meta.url);
  const caseEvents = JSON.parse(readFileSync(url)).events;
  const cast = new Set(caseEvents[0].players.map((p) => p.name));

  for (const e of caseEvents) {
    if (SPEECH.includes(e.type)) words += (e.text ?? "").split(/\s+/).filter(Boolean).length;
    else if (e.type === "elimination") {
      bodies += 1;
      hangings += 1;
      if (e.role !== "Mafia") innocentsHanged += 1;
    } else if (e.type === "night_kill") bodies += 1;

    // A handful of accusations carry target: null, where the engine could not
    // pull a name out of what the model actually said. They count as speech but
    // not as an accusation against anyone.
    if (e.type === "accusation" && e.target != null) {
      assert(cast.has(e.target), `${episode.slug}: accusation target ${e.target} is a player`);
      accusations.set(e.target, (accusations.get(e.target) ?? 0) + 1);
    }
  }
}

// The manifest's per-case death counts are written by tools/publish_game.py from
// the same logs; if these two disagree, one of them is counting the wrong events.
const manifestDeaths = manifest.episodes.reduce((sum, e) => sum + e.deaths, 0);
assert.equal(bodies, manifestDeaths, `bodies from events (${bodies}) == manifest (${manifestDeaths})`);

const mostAccused = Math.max(...accusations.values());
const wordsPerCorpse = Math.round(words / bodies);
for (const [name, value] of [
  ["words", words], ["bodies", bodies], ["hangings", hangings],
  ["innocentsHanged", innocentsHanged], ["wordsPerCorpse", wordsPerCorpse],
  ["mostAccused", mostAccused],
]) {
  assert(Number.isFinite(value) && value > 0, `stat ${name} is a positive number (got ${value})`);
}
assert(innocentsHanged <= hangings, "innocents hanged <= total hangings");

console.log(
  "stats OK:", manifest.episodes.length, "cases;", wordsPerCorpse, "words per corpse;",
  innocentsHanged, "of", hangings, "hanged were innocent;", mostAccused, "accusations against",
  [...accusations].find(([, v]) => v === mostAccused)[0],
);
