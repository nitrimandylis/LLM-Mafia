# LLM Mafia — Replay Viewer

A web interface that dramatizes a finished LLM Mafia game. It reads the
`events[]` stream from a game log and plays it back with dramatic pacing in one
of four switchable designs: **Group Chat** (a messaging thread), **Case File**
(a noir detective board with redacted mafia intercepts), **Transcript** (a
line-numbered court deposition), or **Signal** (a live suspicion-network panel).

## Run

```bash
cd viewer
npm install
npm run dev          # http://localhost:3000
```

`http://localhost:3000` is the landing page; the replay viewer lives at
`/watch` (or click **▸ Watch a replay**).

On load it calls `/api/log`, which reads the engine's `../game_log.json` and
falls back to the bundled `public/logs/sample.json` if no game has been played.
The menu bar shows the source (`● latest game` / `○ bundled sample`) and which
backend/model(s) played the game (hover for the per-seat list); **↻ Latest
game** re-reads the file after a new run, **Load a log…** drops in any
`game_log.json` by hand, and the dropdown at the right end switches between the
four designs.

Logs stamped by the engine carry `provider` and a per-player `model` in their
`game_start` event: homepage episode cards show the provider in its signature
neon (NVIDIA green, Claude clay orange), and Group Chat message headers tag
each speaker with the model that played them. Older logs without the stamps
simply don't show the tags.

## Generate a log to watch

From the repo root, play a real game (writes `game_log.json`, which the viewer
reads automatically):

```bash
python main.py --reveal-secrets
```

…or generate the sample fixture (no LLM needed):

```bash
python tools/make_sample_log.py --write
```

`--reveal-secrets` includes the private mafia whispers and detective results in
the stream; without it the viewer only shows what the town could see.

## Checks

```bash
npm run build     # type-check + compile
node verify.mjs   # validate the sample log + replay reduction logic
```

`/selftest` renders all four skins against the full sample log (server-side),
so the real components can be smoke-tested headlessly (`curl` it) and eyeballed
in one page.

## How it fits together

```
mafia/events.py ─▶ ../game_log.json ─▶ app/api/log ─▶ lib/useReplay.ts ─▶ skin
```

`lib/useReplay.ts` is the shared engine (event cursor, pacing, play/pause,
derived alive/dead). The four skins in `components/skins/` are pure
presentation over the same engine — see `docs/superpowers/specs/` for the design.
