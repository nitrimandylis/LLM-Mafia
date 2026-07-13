# Product

## Register

product

## Users

Two audiences now. Primary: Nick's non-technical friends, arriving at the deployed site with zero context — they land on the homepage, pick a case from the library, and watch AI players lie to each other. Spectators with no setup: no repo, no terminal, no explanation needed beyond what the cold open gives them. Secondary: Nick himself, running games locally and reviewing them through the same viewer (`/watch` still reads the freshest `game_log.json`).

## Product Purpose

A deployed noir streaming service for finished LLM Mafia games. The homepage is king: the preserved LLM MAFIA hero (red wash, logotype, description, GitHub link) opens into the case files — an episode library where every finished game is a poster with a GM-written title and spoiler-free tagline. Each case plays as an episode: a cold open that teaches the premise and introduces the cast, a paced replay where deaths land as full-stage beats with synthesized stings, and a closing recap card that reveals the roles and the GM's post-mortem. Success = a friend with no idea what "LLM" means finishes an episode and clicks the next one.

## Publishing model

Static library, no backend. The engine's game master writes `episode {title, tagline, recap}` into the log at game end; `tools/publish_game.py` copies the log into `viewer/public/logs/` and updates the manifest; pushing to GitHub deploys. Cards never spoil (no winner, no roles); the recap only appears after the replay ends.

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
