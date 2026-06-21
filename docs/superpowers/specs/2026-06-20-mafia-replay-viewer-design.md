# LLM Mafia — Replay Viewer (web interface)

**Date:** 2026-06-20
**Status:** Approved design

## Goal

A web interface that dramatizes an LLM Mafia game for viewer consumption. MVP is
**replay**: read a finished game's log and play it back with dramatic pacing and
animation. The same event stream is designed to drive a **live** mode later
(out of scope here).

The viewer offers **three presentation styles**, switchable on a settings page:

- **Group-chat** — players as avatars in a chat thread; statements as bubbles
  with typing indicators; accusations/votes styled inline; night dims the screen.
- **Table + spotlight** — players seated in a ring; day/night cycle; a spotlight
  swings to the speaker; deaths grey out the seat; vote tally appears center-table.
- **Broadcast** — reality-TV elimination show; "DAY 2" title cards, lower-third
  nameplates, suspense before vote reveals, a recap ticker.

All three render the **same structured event stream** — they are CSS/layout skins
over one shared replay engine, not three apps.

## Architecture

Two decoupled halves communicating through one JSON file:

```
Python game (existing) ──writes──▶ game_log.json { events: [...] } ──read──▶ Next.js viewer
```

### The event contract

The Python game currently logs emoji-prefixed strings (`game_log` / `public_log`).
The viewer cannot reliably dramatize prose, so we add a parallel **structured event
stream**: a flat, ordered `events[]` array, each entry one typed game action. The
existing string logs and `stats` stay in the JSON untouched (backward compatible).

Event types and shapes:

```jsonc
{ "type": "game_start", "players": [ { "name": "HOLMES", "seat": 0, "color": "#7cc4ff" } ], "player_count": 6 }
{ "type": "phase",       "day": 2, "phase": "day" }            // phase: "day" | "night"
{ "type": "statement",   "day": 2, "actor": "HOLMES", "text": "..." }
{ "type": "question",    "day": 2, "actor": "SOCRATES", "target": "PIP", "text": "..." }
{ "type": "answer",      "day": 2, "actor": "PIP", "target": "SOCRATES", "text": "..." }
{ "type": "accusation",  "day": 2, "actor": "HOLMES", "target": "ARIA", "text": "..." }
{ "type": "vote",        "day": 2, "actor": "MARSHAL", "target": "ARIA" }
{ "type": "elimination", "day": 2, "target": "ARIA", "role": "VILLAGER", "tally": {"ARIA":3,"HOLMES":1} }
{ "type": "night_kill",  "day": 2, "target": "SOCRATES", "role": "DETECTIVE", "saved": false }
{ "type": "save",        "day": 2, "target": "PIP" }
{ "type": "game_over",   "winner": "mafia", "survivors": ["..."] }
```

Two rules govern the stream:

1. **Private events respect `--reveal-secrets`.** Mafia night-chat and detective
   results appear in `events[]` only when the game was run with that flag — the
   same rule the console output already follows. The viewer renders whatever is
   present.
2. **Roles stay hidden until revealed.** `game_start` carries names/seats/colors
   but **not** roles (unless spectator mode). Roles arrive attached to
   `elimination` / `night_kill` events, enabling the dramatic "they were… MAFIA"
   reveal in the viewer.

This `events[]` array is the entire contract. Skins, pacing, and future live mode
all consume exactly this.

## Components

### Python (instrument the existing game)

- **`mafia/events.py`** — event constructor helpers + a tiny `EventLog` that
  appends dicts and validates `type` and required fields. Single source of the schema.
- **`mafia/game.py`** — gains `self.events = EventLog()` and `self.emit(...)` calls
  placed next to existing `self.log(...)` calls at each game action. `log()` is
  untouched; `emit()` runs beside it and checks `reveal_secrets` the same way for
  private events.
- **`main.py`** — writes `events` into the output JSON alongside the existing fields.

### Next.js viewer (`viewer/` subfolder)

- **`lib/events.ts`** — TypeScript types mirroring the schema (the contract, typed).
- **`lib/useReplay.ts`** — the shared engine. Owns the event cursor, play/pause,
  speed, and the synthetic timeline. Returns `{ visibleEvents, phase, alive, controls }`.
  All three skins use this — zero logic duplicated.
- **`components/skins/{ChatSkin,TableSkin,BroadcastSkin}.tsx`** — pure
  presentational, identical props `{ players, visibleEvents, phase, alive }`,
  differing only in markup/CSS.
- **`components/Controls.tsx`** — play/pause, speed (1×/2×/instant), scrubber, day jump.
- **`app/page.tsx`** — loads a log, runs `useReplay`, renders the active skin + controls.
- **`app/settings/page.tsx`** — skin picker (the three styles as cards) + default
  speed, persisted to `localStorage`.

## Data flow

```
events.py ─▶ game_log.json ─▶ viewer (public/logs/*.json or browser file upload)
                                 └─ useReplay ─▶ active skin
```

## Pacing (the drama)

The real game has no timestamps, so the replay engine **assigns** a delay per event
type: a statement reveals after a "typing" beat; a vote lands quickly;
`elimination` / `night_kill` get a held pause before the role reveal; `phase`
changes animate the day↔night transition. A speed multiplier scales all delays;
"instant" reveals everything at once. This logic lives once in `useReplay`; skins
animate whatever becomes visible.

## Log source

- Drop logs in `viewer/public/logs/` to pick from a list, **or**
- drag-and-drop / upload a `game_log.json` in the browser (no server round-trip
  needed for replay).

## Settings, errors

- **Settings:** active skin + default speed in `localStorage`. No accounts, no backend.
- **Errors:** a log with no `events[]` shows a friendly "re-run with the updated
  game to get a structured log" message rather than a blank screen. Unknown event
  types are skipped, not fatal — adding event types later never breaks an older viewer.

## Testing

- **Python:** one assert-based self-check — run a scripted game with a fake model
  (no live LLM), assert `events[]` is non-empty, every event validates against the
  schema, and a full day produces the expected type sequence
  (`phase → statement… → vote → elimination`). This is the contract guard, and it
  doubles as the sample-log generator for the viewer.
- **Next:** one small test on `useReplay` — given an events array, visible events
  appear in order and respect the cursor. Skins are presentational, not unit-tested.

## Scope / explicitly skipped

- **Live mode** — out of scope. The schema and `useReplay` are designed so live is
  a later add (a route handler streaming the same events over SSE into the same
  engine).
- Auth, database, multi-game library UI, real-time.
- The three skins are CSS skins over one engine. If a skin is unloved, delete its
  file and its settings option — nothing else depends on it.
