```
 ██╗     ██╗     ███╗   ███╗    ███╗   ███╗ █████╗ ███████╗██╗ █████╗
 ██║     ██║     ████╗ ████║    ████╗ ████║██╔══██╗██╔════╝██║██╔══██╗
 ██║     ██║     ██╔████╔██║    ██╔████╔██║███████║█████╗  ██║███████║
 ██║     ██║     ██║╚██╔╝██║    ██║╚██╔╝██║██╔══██║██╔══╝  ██║██╔══██║
 ███████╗███████╗██║ ╚═╝ ██║    ██║ ╚═╝ ██║██║  ██║██║     ██║██║  ██║
 ╚══════╝╚══════╝╚═╝     ╚═╝    ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝
```

<div align="center">

### `NO HUMANS. PURE MODEL-VS-MODEL DECEPTION.`

*the classic Mafia party game, except every player is an LLM with an alibi*

![humans](https://img.shields.io/badge/humans-0-c41e1e?style=flat-square&labelColor=111111)
![trust](https://img.shields.io/badge/trust-nobody-c41e1e?style=flat-square&labelColor=111111)
![inference](https://img.shields.io/badge/inference-lm--studio_|_nvidia--nim_|_claude-8a8a8a?style=flat-square&labelColor=111111)
![alibis](https://img.shields.io/badge/alibis-generated_by_llms-8a8a8a?style=flat-square&labelColor=111111)

</div>

---

## 🎭 What is this

A fully autonomous Mafia game where every seat at the table is an LLM. Each player gets a role — Villager, Mafia, Detective, or Doctor — a personality, and a win condition. Then they reason, argue, accuse, and vote entirely through model inference, queried in parallel. You just watch the town burn.

Runs against any OpenAI-compatible endpoint — [LM Studio](https://lmstudio.ai) for local inference or [NVIDIA NIM](https://build.nvidia.com) for cloud models — or against the [Claude Code CLI](https://claude.com/claude-code) (`--claude`), which bills your Claude subscription and mixes haiku, sonnet, and opus across the seats.

```console
$ python main.py --nvidia --reveal-secrets
☀️  DAY 2 - TOWN MEETING
🗣️  HOLMES: ARIA's defense of RICO on Day 1 was too rehearsed — I'm watching them.
🔍 SOCRATES → PIP: Why did you change your vote at the last second yesterday?
⚔️  MARSHAL: My vote is ARIA. The pattern doesn't add up.
```

It's **one pipeline, two halves**: a Python engine plays the game, and a Next.js
viewer dramatizes the result for spectators.

```
  mafia/  ──writes──▶  game_log.json  ──reads──▶  viewer/
  the engine          structured events[]        web replay, 4 dramatized skins
  (python main.py)    + transcript + stats       (bun run dev)
```

The engine writes a structured `events[]` stream to `game_log.json`; the viewer
reads that same file and replays it as a tense group chat, a noir case file, a
court transcript, or a live suspicion graph. The event schema is defined once in
`mafia/events.py` and mirrored in `viewer/lib/events.ts`, kept in lockstep by a
parity check.

## 🃏 The table

| | feature | what it actually does |
|---|---|---|
| 01 | **autonomous players** | every villager, mobster, detective and doctor is an LLM with a system prompt and an agenda |
| 02 | **parallel inference** | configurable worker threads query models simultaneously — the town argues in real time |
| 03 | **private reasoning** | detective investigations and mafia night-chat happen off the public record |
| 04 | **game master narrator** | a separate LLM narrates key moments and generates factual day summaries injected into player context |
| 05 | **`--reveal-secrets`** | spectator mode — expose the private mafia chat and detective results |
| 06 | **`--nvidia`** | run against NVIDIA NIM cloud models instead of a local LM Studio server |
| 07 | **`--claude`** | run against the Claude Code CLI on your subscription — seats cycle haiku/sonnet/opus for model-vs-model variety |
| 08 | **JSON game log** | full transcript + structured `events[]` + per-player vote accuracy, detective stats, and which model played each seat |
| 09 | **web replay viewer** | a Next.js app that dramatizes the log — group chat, case file, transcript, or suspicion graph ([`viewer/`](viewer/)) |

## ⚖️ Two house rules

Otherwise it's standard Mafia.

**The detective's will.** Night-kill the detective and their last investigation
result is published with the body the next morning (`detective_will`). Silencing
the detective no longer buries a finding the town already paid for.

**The trusted person** (`--mafia 3` only). At game start the detective is
privately told one random confirmed-town player. Private knowledge, not an
event — theirs to use or share. Gated to 3-mafia games because the first 20
cases split hard by wolf count: town won 5/5 at two mafia and 5/15 at three,
and every mafia win opened with a day-1 mislynch. Run
`python tools/balance_report.py` to see the current split.

## 🚀 Run it

**Install**

```bash
git clone https://github.com/nitrimandylis/LLM-Mafia.git
cd LLM-Mafia
pip install -r requirements.txt
```

**Option A — Local via LM Studio**

1. Install and launch [LM Studio](https://lmstudio.ai)
2. Load any model and start the local server (default port 1234)
3. Run:

```bash
python main.py
```

**Option B — NVIDIA NIM**

```bash
cp .env.example .env
# add your NVIDIA_API_KEY to .env

python main.py --nvidia
```

**Option C — Claude CLI**

Needs the [Claude Code CLI](https://claude.com/claude-code) installed and logged
in (`claude` on your PATH). Calls bill your Claude subscription — no API key.

```bash
python main.py --claude
```

By default the seats cycle **haiku / sonnet / opus** so the town isn't ten
copies of the same mind; pass `--model sonnet` (or `haiku`/`opus`) to force one
model everywhere. The Game Master narrates on sonnet.

The town accepts instructions:

| flag | default | what it does |
|---|---|---|
| `--player-count` | 10 | number of players (4–10) |
| `--mafia` | 2 | number of mafia (3 is "hard mode"; clamped below parity) |
| `--reveal-secrets` | off | show private mafia chat and detective results |
| `--nvidia` | off | use NVIDIA NIM instead of LM Studio |
| `--lm-studio-url` | `http://localhost:1234/v1` | LM Studio base URL |
| `--nvidia-key` | env | NVIDIA API key (or set `NVIDIA_API_KEY` in `.env`) |
| `--claude` | off | use the Claude CLI (subscription-billed); seats mix haiku/sonnet/opus |
| `--model` | auto | override the player model (with `--claude`, forces one model on every seat) |
| `--gm-model` | `qwen/qwen3.5-9b` | model used by the game master narrator |
| `--no-gm` | off | disable game master narration entirely |
| `--max-workers` | 4 | parallel threads for model queries |
| `--output` | `game_log.json` | path for the JSON game log |

```bash
python main.py --nvidia --player-count 8 --reveal-secrets --output my_game.json
```

## 📺 Watch the replay

The viewer dramatizes a finished game in the browser. It reads the engine's
latest `game_log.json` automatically — no copying, no config.

```bash
cd viewer
bun install            # first time only
bun run dev            # http://localhost:3000
```

Then:

1. In another terminal, play a game from the repo root: `python main.py` (writes `game_log.json`).
2. Open **http://localhost:3000**, click **▸ Watch a replay**, and hit **↻ Latest game** — the viewer loads what the engine just wrote.

No game yet? The viewer ships with a bundled sample so it works immediately. You
can also regenerate that sample without any LLM:

```bash
python tools/make_sample_log.py --write
```

Switch between the four designs with the dropdown at the right end of the menu
bar. Message headers tag each speaker with the model that played them, and the
menu shows which backend ran the game.
Use **`--reveal-secrets`** when running the game to include the private mafia
whispers and detective results in the replay. See [`viewer/README.md`](viewer/README.md) for details.

## 🔩 Under the hood

```
LLM-Mafia/
├── mafia/                  THE ENGINE
│   ├── game.py             core game loop — day/night/voting phases, roles, LLM queries
│   ├── game_master.py      AI narrator: day summaries, eliminations, night kills
│   ├── game_state.py       builds structured context summaries for player reasoning
│   ├── events.py           structured event schema — the contract with the viewer
│   └── player.py           Player dataclass, role enum, players.json loader
├── main.py                 CLI entry point; writes game_log.json
├── players.json            player roster with names and personality prompts
├── system_prompt.md        universal system prompt injected into every player
│
│   ── game_log.json ──     the bridge: structured events[] + transcript + stats
│
├── viewer/                 THE VIEWER (Next.js)
│   ├── app/                pages, /api/log (reads ../game_log.json), /selftest
│   │                       + /watch, /rules, /about, /wallpapers
│   ├── components/skins/   the four dramatized designs
│   ├── lib/                useReplay engine, events.ts (mirrors mafia/events.py)
│   └── public/             logs/ (published episodes + manifest), avatars/, wallpapers/
├── tools/
│   ├── make_sample_log.py  generates the viewer's sample log + checks schema parity
│   ├── publish_game.py     publishes a finished log as a homepage episode
│   ├── run_batch.py        plays N Claude games unattended, minding subscription quota
│   ├── balance_report.py   win rates + lynch accuracy across the library, split by wolf count
│   ├── mugshots.py         regenerates the pixel-art avatar SVGs from ASCII grids
│   ├── wallpapers.py       saves the wallpaper PNGs off a running viewer
│   ├── claude_usage.py     reads remaining Claude subscription quota
│   └── test_*.py           the engine's checks (`python tools/test_fixes.py`, …)
└── docs/                   design specs, the balance review, the editorial log
```

Published episodes live in `viewer/public/logs/` and are indexed by
`manifest.json`; that manifest, not the directory, defines the library. A log
hand-edited for the editorial pass carries `exclude_from_stats` so
`balance_report.py` leaves it out of the win rates.

---

<div align="center">

**[Nick Trimandylis](https://github.com/nitrimandylis)**

`LLMS LIE. PROVED IT.`

MIT licensed.

</div>
