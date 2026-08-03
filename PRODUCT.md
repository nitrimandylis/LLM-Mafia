# Product

## Register

product

## Users

Two audiences now. Primary: Nick's non-technical friends, arriving at the deployed site with zero context — they land on the homepage, pick a case from the library, and watch AI players lie to each other. Spectators with no setup: no repo, no terminal, no explanation needed beyond what the cold open gives them. Secondary: Nick himself, running games locally and reviewing them through the same viewer (`/watch` still reads the freshest `game_log.json`).

## Product Purpose

A deployed noir streaming service for finished LLM Mafia games. The homepage is king: the preserved LLM MAFIA hero (red wash, logotype, description, GitHub link) opens into the case files — an episode library where every finished game is a poster with a GM-written title and spoiler-free tagline. Each case plays as an episode: a cold open that teaches the premise and introduces the cast, a paced replay where deaths land as full-stage beats with synthesized stings, and a closing recap card that reveals the roles and the GM's post-mortem. Success = a friend with no idea what "LLM" means finishes an episode and clicks the next one.

## The record strip

Between the hero and the case files, five totals counted over every published log by `viewer/lib/stats.ts` (server-side, module scope, once per process): cases on record, humans involved, words per corpse, innocents hanged, and accusations against whoever is currently the most-accused name. Deadpan by design — the numbers do the joke, the labels stay flat, and each carries a `title=` explaining its arithmetic. They wear the hero wordmark's neon: same red, same three-layer glow, the `lp-neon-buzz` mains hum staggered per tile, and a warm-up flicker driven by `animation-timeline: view()` so the sign lights as you scroll to it with no client JS. Nothing here spoils: no winner, no roles, no per-case outcome. `exclude_from_stats` is deliberately ignored, since it exists to protect win rates and none of these is one. `verify.mjs` asserts the invariants (event-derived bodies match the manifest's death counts, accusation targets are real players) rather than today's totals, which change with every publish.

## Publishing model

Static library, no backend. The engine's game master writes `episode {title, tagline, recap}` into the log at game end; `tools/publish_game.py` copies the log into `viewer/public/logs/` and updates the manifest; pushing to GitHub deploys. Cards never spoil (no winner, no roles); the recap only appears after the replay ends.

Games are produced two ways. Locally, `tools/run_batch.py` plays N Claude games unattended (minding subscription quota between them) into the gitignored `runs/`, and the keepers get published by hand. Weekly and unattended, `.github/workflows/case.yml` plays one game on a GitHub Actions runner and hands it to `tools/ci_case.py`: the log has to clear `smells_wrong()` before Claude is asked whether the deception was real and the argument had substance, the returned verdict is validated deterministically (a tagline naming a cast member is thrown out, since none of the published ones ever has), and only an approval that survives validation gets its pull request merged. A flat title or tagline is rewritten instead of costing the episode its slot, and that rewrite does not earn `exclude_from_stats`, because a card is not gameplay text. Design notes in `docs/specs/2026-08-03-auto-cases-design.md`. `tools/balance_report.py` reads the manifest and reports win rate and lynch accuracy split by mafia count — that report is what gates house-rule changes. A log whose text was hand-edited in the editorial pass carries `exclude_from_stats`, which `publish_game.py` copies through so the published version stays out of the win rates: its outcome was decided by us, not by the players.

## Game rules of note

Standard Mafia (mafia / detective / doctor / villagers) with two house rules.

**The detective's will.** When the detective is night-killed, their last investigation result is published with the body the next morning (`detective_will` event, shown in every skin). Killing the detective silences future investigations but can no longer bury a finding the town already paid for.

**The trusted person (3-mafia games only).** At game start the detective is privately told one random confirmed-town player. Private knowledge, not an event: theirs to use or share. Gated because the first 20 cases split hard by wolf count — town won 5/5 at 2 mafia and 5/15 at 3, and every single mafia win opened with a day-1 mislynch. The buff aims at day 1, where the games are actually decided, and leaves the balanced 2-mafia config untouched. Logged as `stats.detective.trusted_person` (null when the buff did not apply) so future win-rate splits can tell the configs apart, alongside `trusted_person_v` for which delivery of the buff played: v1 told the detective the name and let the day loop force them to attack it, v2 keeps the trusted person out of every shortlist the day points a player at. Logs written before v2 carry no version field and are read as v1, so the balance report never pools the two.

## Inference backends & provenance

Three interchangeable backends play the games: LM Studio (local), NVIDIA NIM (cloud, per-seat models from `players.json`), and the Claude Code CLI (`--claude`, subscription-billed, seats cycling haiku/sonnet/opus so the town isn't one mind arguing with itself). Every log stamps which provider ran the game and which model played each seat; that provenance is part of the show — episode cards wear the provider in its signature neon (NVIDIA green `#76b900`, Claude clay `#d97757`), and Group Chat headers tag each speaker with their model. Spectators should always be able to answer "who's actually talking?"

## Cast identity

The ten fixed personas (`players.json`) each have a hand-drawn 24×24 pixel-art mugshot — booking-wall background with height-chart lines — in `viewer/public/avatars/`, generated by `tools/mugshots.py` (edit the ASCII grid, re-run, SVGs regenerate). Skins show mugshots wherever a player has a face (Group Chat avatars, Case File suspect cards) via `skins/Mug.tsx`, which falls back to colored initials for any name without a portrait. Win screens are team-colored: mafia red, town neon green (`--win`).

## Wallpapers

Thirty wallpapers in `viewer/public/wallpapers/`, committed as static files: five designs × two palettes × three devices (monitor 3840×2160, MacBook 3024×1964, phone 1170×2532). Four designs (terminal frame, night-phase transcript, hero poster, the booking wall) pair the shell's red-on-black against the colours of the skin each one quotes. The fifth quotes Group Chat as a collapsed iOS notification stack — three cards, mugshots for icons, the game messaging you — and takes its two palettes from that skin's own `day`/`night` duality instead, since shell-versus-chat would have been two near-identical near-black fields. Palette names therefore differ per design, so `PALETTES` is a per-design map in both `designs.tsx` and the generator. Compositions are fixed and invented; nothing reads a game log, so no wallpaper should be mistaken for a real case. Each device gets its own layout rather than a crop: desktop clears the right third and the centre for icons and windows, phone clears the top third for the clock and the bottom for the lock-screen buttons. The 16:10 MacBook panel is its own render rather than a crop of the monitor file, since scaling 16:9 to cover a 16:10 screen loses a slice off each side. It then has to survive the reverse trip too: a wallpaper is set per Space, not per display, so the laptop file is what a 16:9 monitor shows, cover-scaled down to a centre band with `MB_CROP` cut off the top and bottom. Its content therefore sits inside `MB_BAND` with a visible margin (6% of the band), not merely clear of the cut line, and `ink_rows()` in the generator is what proves it. The notification stack keeps the desktop's bottom-left origin rather than Notification Centre's top-right, which would collide with the real icon column.

`/wallpapers` is the gallery: five design groups, two palette tiles each, and one sticky MONITOR/LAPTOP/PHONE toggle that swaps every preview. Only the selected device's ten images are in the tree, so the other twenty are never fetched, and previews go through `next/image` against the committed PNGs (a 320 KB source serves as ~7 KB at tile width). Clicking a preview opens the full file, since on iOS long-pressing an open image is the shortest path to Photos; the caption carries a `download` link for the desktop case. `app/wallpapers/page.tsx` does the `statSync` for file sizes and hands plain data to the client `components/WallpaperGrid.tsx`, which keeps `designs.tsx` out of the browser bundle.

`viewer/app/wallpapers/designs.tsx` holds the compositions and `.../[design]/[palette]/[device]/route.tsx` renders them with `next/og`. `tools/wallpapers.py` fetches all thirty off `bun run dev` and writes them into `public/`; nothing renders in production. **Satori silently drops `repeating-linear-gradient` and ignores SVG filters**, so the CRT scanlines are drawn as explicit bars (6px pitch) and the `feTurbulence` phosphor grain from `globals.css` cannot be reproduced at all. The two paper skins get 54px ruled lines instead. `texture_period()` in the generator is the regression check: it returns 0 on a flat field, which is exactly what the first attempt produced. It sums the RGB channels rather than reading red alone, because chat's night field (`#030304`) is dark enough that a 28%-black bar over it rounds away in red but survives in blue.

## Brand Personality

Noir, theatrical, self-aware. A neon-noir aesthetic: cold night shell (`#0a0b10` bars), blood-red `#c41e1e` brand with hot `#ff2a2a` neon accents and glow, CRT scanlines and phosphor grain, mono tracked labels, bracketed `[ text ]` buttons. Each skin is its own committed world (messaging thread, manila case file, court deposition, signal-intelligence panel) inside one consistent chrome. Playful pulp-fiction drama, executed with restraint. The library reads like tonight's programming at a very disreputable channel.

## Anti-references

- **Sterile dev-tool minimal** — gray-on-gray Vercel/Linear clone with no personality.
- **Generic SaaS dashboard** — card grids, gradients, hero metrics, shadcn-default look.
- Also avoid drifting into kitsch: the noir is committed but dry, not Halloween.

## Design Principles

1. **The homepage is king** — the hero is untouchable (red wash, logotype, description, GitHub link); everything new serves the flow from landing to pressing play on a case.
2. **Each skin is a world** — commit fully to its material (paper, terminal, chat app, courtroom); Group Chat is the flagship episode experience, the others stay one click away.
3. **Pacing is the product** — the cold open, dwell times, death beats, stings, and the held recap are core UX, not decoration.
4. **Never spoil before the reveal** — cards and cold opens tease (days, body count, cast); winners, roles, and recaps only after the replay ends.
5. **Legibility of deception** — a viewer should always be able to tell who's alive, who accused whom, and what phase it is.
6. **Dry noir, not costume noir** — atmosphere through typography, texture, and restraint rather than clichés.

## Accessibility & Inclusion

WCAG AA throughout: ≥4.5:1 contrast for body text in every skin and chrome theme, full keyboard operability, visible focus states, and honored `prefers-reduced-motion` (both already scaffolded in globals.css — hold new work to the same bar). Sound is additive only — every beat also lands visually, and the mute toggle persists.
