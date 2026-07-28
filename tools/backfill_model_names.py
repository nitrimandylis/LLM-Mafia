"""Replace the Claude aliases in published logs with the build that actually played.

The `--claude` backend stamps whatever was passed to `claude --model`, which is an
alias ("sonnet", "opus"). Aliases move: two new opuses and one new sonnet shipped
while cases 005-020 were being recorded, so "sonnet" in case 005 and "sonnet" in
case 020 are different models. The viewer should name the real build, so this
rewrites the alias in each published log's game_start event.

One-off. Re-run it if the logs are ever regenerated from the raw games.
"""

import json
from pathlib import Path

LOGS = Path(__file__).resolve().parent.parent / "viewer" / "public" / "logs"

# Which build each Claude case actually ran on. Cases 001-004 were NVIDIA
# (minimax-m3) and already carry a real model name, so they are absent here.
CASE_MODEL = {
    "case-005": "sonnet-4.6",
    "case-006": "sonnet-4.6",
    "case-007": "sonnet-4.6",
    "case-008": "sonnet-4.6",
    "case-009": "sonnet-4.6",
    "case-010": "opus-4.7",
    "case-011": "opus-4.7",
    "case-012": "opus-4.7",
    "case-013": "opus-4.7",
    "case-014": "opus-4.7",
    "case-015": "opus-4.7",
    "case-016": "opus-4.7",
    "case-017": "opus-4.7",
    "case-018": "sonnet-5",
    "case-019": "opus-4.8",
    "case-020": "sonnet-5",
}


def backfill_one(path: Path, model_name: str) -> int:
    log = json.loads(path.read_text())
    start = log["events"][0]
    if start["type"] != "game_start":
        raise ValueError(f"{path.name}: first event is {start['type']}, not game_start")

    changed = 0
    for player in start["players"]:
        if player.get("model") != model_name:
            player["model"] = model_name
            changed += 1

    if changed:
        # indent=1 and no trailing newline, matching what publish_game.py writes
        path.write_text(json.dumps(log, indent=1))
    return changed


def main():
    for slug, model_name in sorted(CASE_MODEL.items()):
        path = LOGS / f"{slug}.json"
        changed = backfill_one(path, model_name)
        print(f"{slug}: {changed} seats -> {model_name}")


if __name__ == "__main__":
    main()
