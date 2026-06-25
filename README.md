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
![inference](https://img.shields.io/badge/inference-lm--studio_|_nvidia--nim-8a8a8a?style=flat-square&labelColor=111111)
![alibis](https://img.shields.io/badge/alibis-generated_by_llms-8a8a8a?style=flat-square&labelColor=111111)

</div>

---

## 🎭 What is this

A fully autonomous Mafia game where every seat at the table is an LLM. Each player gets a role — Villager, Mafia, Detective, or Doctor — a personality, and a win condition. Then they reason, argue, accuse, and vote entirely through model inference, queried in parallel. You just watch the town burn.

Runs against any OpenAI-compatible endpoint: [LM Studio](https://lmstudio.ai) for local inference or [NVIDIA NIM](https://build.nvidia.com) for cloud models.

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
  the engine          structured events[]        web replay, 3 dramatized styles
  (python main.py)    + transcript + stats       (npm run dev)
```

The engine writes a structured `events[]` stream to `game_log.json`; the viewer
reads that same file and replays it as a tense group-chat, a spotlit table, or a
reality-TV elimination show. The event schema is defined once in
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
| 07 | **JSON game log** | full transcript + structured `events[]` + per-player vote accuracy and detective stats written to disk |
| 08 | **web replay viewer** | a Next.js app that dramatizes the log — group-chat, spotlit table, or broadcast styles ([`viewer/`](viewer/)) |

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

The town accepts instructions:

| flag | default | what it does |
|---|---|---|
| `--player-count` | 10 | number of players (4–10) |
| `--reveal-secrets` | off | show private mafia chat and detective results |
| `--nvidia` | off | use NVIDIA NIM instead of LM Studio |
| `--nvidia-key` | env | NVIDIA API key (or set `NVIDIA_API_KEY` in `.env`) |
| `--model` | auto | override the player model |
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
npm install            # first time only
npm run dev            # http://localhost:3000
```

Then:

1. In another terminal, play a game from the repo root: `python main.py` (writes `game_log.json`).
2. Open **http://localhost:3000**, click **▸ Watch a replay**, and hit **↻ Latest game** — the viewer loads what the engine just wrote.

No game yet? The viewer ships with a bundled sample so it works immediately. You
can also regenerate that sample without any LLM:

```bash
python tools/make_sample_log.py --write
```

Switch between the three styles in the header or set a default under **Settings**.
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
│   ├── components/skins/   the three dramatized styles
│   └── lib/                useReplay engine, events.ts (mirrors mafia/events.py)
├── tools/
│   └── make_sample_log.py  generates the viewer's sample log + checks schema parity
└── docs/                   design specs
```

---

<div align="center">

**[Nick Trimandylis](https://github.com/nitrimandylis)**

`LLMS LIE. PROVED IT.`

MIT licensed.

</div>
