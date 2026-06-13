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

*the classic Mafia party game, except every player is a local LLM with an alibi*

![humans](https://img.shields.io/badge/humans-0-c41e1e?style=flat-square&labelColor=111111)
![trust](https://img.shields.io/badge/trust-nobody-c41e1e?style=flat-square&labelColor=111111)
![inference](https://img.shields.io/badge/inference-local_via_ollama-8a8a8a?style=flat-square&labelColor=111111)
![alibis](https://img.shields.io/badge/alibis-generated_on_device-8a8a8a?style=flat-square&labelColor=111111)
![ram](https://img.shields.io/badge/RAM_check-before_the_bodies_drop-c41e1e?style=flat-square&labelColor=111111)

</div>

---

## 🎭 What is this

A fully autonomous Mafia game where every seat at the table is an LLM running
locally through [Ollama](https://ollama.com). Each player gets a role —
Villager, Mafia, Detective, or Doctor — a personality, and a win condition.
Then they reason, argue, accuse, and vote entirely through model inference,
queried in parallel across local threads. You just watch the town burn.

A memory guard checks free RAM before each round of inference, because nothing
ruins a murder mystery like a swap-thrashed laptop.

```console
nick@town-square:~$ python main.py --player-count 8
[night 1] the mafia has chosen. the doctor guessed wrong.
[day 1]   player_3 is "just asking questions". player_3 is mafia.
```

## 🃏 The table

| | feature | what it actually does |
|---|---|---|
| 01 | **autonomous players** | every villager, mobster, detective and doctor is an LLM with a system prompt and an agenda |
| 02 | **parallel inference** | configurable worker threads query models simultaneously — the town argues in real time |
| 03 | **private reasoning** | detective investigations and mafia night-chat happen off the public record |
| 04 | **memory guard** | skips model calls when free RAM drops below threshold. survival instinct, but for your laptop |
| 05 | **`--reveal-secrets`** | spectator mode — expose the private mafia chat and detective results |
| 06 | **`--pro-mode`** | upgrade the town to a more capable local model. smarter lies |
| 07 | **JSON game log** | full transcript written to disk for post-game forensics |

## 🚀 Run it

Requires [Ollama](https://ollama.com) running locally, Conda (or Python
3.11+), and ~8GB+ RAM if you want the whole town thinking at once.

```bash
git clone https://github.com/nitrimandylis/LLM-Mafia.git
cd LLM-Mafia
conda env create -f environment.yml
conda activate llm-mafia
ollama pull granite4:350m

python main.py
```

The town accepts instructions:

| flag | default | what it does |
|---|---|---|
| `--player-count` | 10 | number of players (4–10) |
| `--reveal-secrets` | off | show private mafia chat and detective results |
| `--pro-mode` | off | use a more advanced local model |
| `--max-workers` | 4 | parallel threads for model queries |
| `--memory-threshold` | 4 | minimum free RAM in GB to proceed |
| `--output` | game_log.json | path for the JSON game log |

```bash
python main.py --player-count 8 --reveal-secrets --output my_game.json
```

## 🔩 Under the hood

| file | job |
|---|---|
| `main.py` | entry point and CLI argument parsing |
| `game.py` | core game loop — day/night phases, votes, eliminations |
| `game_state.py` | who's alive, who's lying, who's pretending not to |
| `player.py` | player class and role definitions |
| `players.json` | the name pool the town draws from |
| `system_prompt.md` | the active system prompt every player wakes up with |
| `environment.yml` | conda environment spec |

A refactor into `src/mafia/` (config, context, core modules) is underway —
the town is being rebuilt while the town argues.

---

<div align="center">

**[Nick Trimandylis](https://github.com/nitrimandylis)**

`THE TOWN SLEEPS. THE GPU DOES NOT.`

MIT licensed.

</div>
