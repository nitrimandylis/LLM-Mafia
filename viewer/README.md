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

On load it calls `/api/log`, which reads the engine's `../game_log.json` and
falls back to the bundled `public/logs/sample.json` if no game has been played.
The header shows the source (`● latest game` / `○ bundled sample`); **↻ Latest
game** re-reads the file after a new run, **Load a log…** drops in any
`game_log.json` by hand, and **Settings** sets the default style and playback
speed (saved in your browser).

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

`/selftest` renders all three skins against the full sample log (server-side),
so the real components can be smoke-tested headlessly (`curl` it) and eyeballed
in one page.

## How it fits together

```
mafia/events.py ─▶ ../game_log.json ─▶ app/api/log ─▶ lib/useReplay.ts ─▶ skin
```

`lib/useReplay.ts` is the shared engine (event cursor, pacing, play/pause,
derived alive/dead). The three skins in `components/skins/` are pure
presentation over the same engine — see `docs/superpowers/specs/` for the design.
