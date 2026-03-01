# LLM Mafia 🎭

A Python simulation of the classic Mafia party game, where every player is an LLM
running locally via Ollama. No humans. Pure model-vs-model deception.

## How It Works

Each player is assigned a role (Villager, Mafia, Detective, or Doctor) and given
a system prompt defining their personality and win condition. Players reason,
argue, accuse, and vote entirely through LLM inference — running in parallel
across local threads.

## Features

- Fully autonomous Mafia game with LLM-controlled players
- Parallel model querying with configurable worker count
- Detective and Doctor roles with private reasoning
- Memory-aware execution — skips model calls if RAM is too low
- `--reveal-secrets` flag to expose private mafia chat and detective results
- `--pro-mode` flag to upgrade to a more capable local model
- JSON game log output for post-game analysis

## Requirements

- [Ollama](https://ollama.com) installed and running locally
- Conda (recommended) or Python 3.11+
- ~8GB+ RAM for comfortable multi-player parallel inference

## Setup

### With Conda (recommended)

```bash
git clone https://github.com/nitrimandylis/LLM-Mafia.git
cd LLM-Mafia
conda env create -f environment.yml
conda activate llm-mafia
```

### Pull a model via Ollama

```bash
ollama pull llama3.2
```

## Usage

```bash
python main.py
```

### Flags

| Flag | Default | Description |
|---|---|---|
| `--player-count` | 10 | Number of players (4–10) |
| `--reveal-secrets` | off | Show private mafia chat and detective results |
| `--pro-mode` | off | Use a more advanced local model |
| `--max-workers` | 4 | Parallel threads for model queries |
| `--memory-threshold` | 4 | Minimum free RAM in GB to proceed |
| `--output` | game_log.json | Output path for the JSON game log |

### Example

```bash
python main.py --player-count 8 --reveal-secrets --output my_game.json
```

## Project Structure

```
LLM-Mafia/
├── main.py            # Entry point and CLI argument parsing
├── game.py            # Core game logic and phase management
├── player.py          # Player class and role definitions
├── players.json       # Player name pool
├── system_prompt.md   # Active system prompt for LLM players
└── environment.yml    # Conda environment
```

## License

MIT — see [LICENSE](LICENSE) for details.
