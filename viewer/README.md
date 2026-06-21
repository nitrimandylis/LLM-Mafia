# LLM Mafia — Replay Viewer

A web interface that dramatizes a finished LLM Mafia game. It reads the
`events[]` stream from a game log and plays it back with dramatic pacing in one
of three switchable styles: **group-chat**, **table + spotlight**, or **broadcast**.

## Run

```bash
cd viewer
npm install
npm run dev          # http://localhost:3000
```

It loads `public/logs/sample.json` by default. Use **Load a log…** in the
header to drop in any `game_log.json`, and **Settings** to set the default
style and playback speed (saved in your browser).

## Generate a log to watch

From the repo root, either play a real game:

```bash
python main.py --reveal-secrets --output viewer/public/logs/sample.json
```

…or generate the deterministic-ish sample fixture (no LLM needed):

```bash
python test_events.py --write
```

`--reveal-secrets` includes the private mafia whispers and detective results in
the stream; without it the viewer only shows what the town could see.

## Checks

```bash
npm run build     # type-check + compile
node verify.mjs   # validate the sample log + replay reduction logic
```

`/selftest` renders all three skins against the full sample log (server-side),
so the real components can be smoke-tested headlessly (`curl` it) and eyeballed
in one page.

## How it fits together

```
mafia/events.py ─▶ game_log.json { events: [...] } ─▶ lib/useReplay.ts ─▶ skin
```

`lib/useReplay.ts` is the shared engine (event cursor, pacing, play/pause,
derived alive/dead). The three skins in `components/skins/` are pure
presentation over the same engine — see `docs/superpowers/specs/` for the design.
