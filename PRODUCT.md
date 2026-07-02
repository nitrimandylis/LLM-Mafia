# Product

## Register

product

## Users

Nick (the developer) and anyone who runs an LLM-vs-LLM Mafia game and wants to watch the replay. Context: they just finished a game run from the terminal and open the viewer to see how the deception played out. Spectators, not operators — the primary job is *watching a story unfold*, with light controls (play/pause, speed, scrub, switch presentation style).

## Product Purpose

A replay viewer that dramatizes a finished LLM Mafia game log. It turns a JSON event stream into a paced, theatrical playback in one of four switchable skins: Group Chat, Case File, Transcript, and Signal. Success = a replay that is genuinely fun to watch and makes the model-vs-model deception legible (who accused whom, who lied, who died).

## Brand Personality

Noir, theatrical, self-aware. A crime-board aesthetic: near-black shell, blood-red `#c41e1e` brand, mono tracked labels, film grain, bracketed `[ text ]` buttons. Each skin is its own committed world (messaging thread, manila case file, court deposition, signal-intelligence panel) inside one consistent chrome. Playful pulp-fiction drama, executed with restraint.

## Anti-references

- **Sterile dev-tool minimal** — gray-on-gray Vercel/Linear clone with no personality.
- **Generic SaaS dashboard** — card grids, gradients, hero metrics, shadcn-default look.
- Also avoid drifting into kitsch: the noir is committed but dry, not Halloween.

## Design Principles

1. **Each skin is a world** — commit fully to its material (paper, terminal, chat app, courtroom); no half-themed compromises.
2. **The chrome recedes, the story leads** — shell UI stays quiet so the replay content carries the drama.
3. **Pacing is the product** — playback rhythm, typing indicators, and reveals are core UX, not decoration.
4. **Legibility of deception** — a viewer should always be able to tell who's alive, who accused whom, and what phase it is.
5. **Dry noir, not costume noir** — atmosphere through typography, texture, and restraint rather than clichés.

## Accessibility & Inclusion

WCAG AA throughout: ≥4.5:1 contrast for body text in every skin and chrome theme, full keyboard operability, visible focus states, and honored `prefers-reduced-motion` (both already scaffolded in globals.css — hold new work to the same bar).
