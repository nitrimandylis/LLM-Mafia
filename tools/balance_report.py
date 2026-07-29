"""Win rates and lynch accuracy across the published cases, split by mafia count.

Usage:
    python tools/balance_report.py
    python tools/balance_report.py --logs runs        # a batch of unpublished games

The question this answers: does town win often enough, and does the day-1
lynch decide the game? Split by mafia count because 2-mafia and 3-mafia are
effectively different games (see docs/potential-changes.md).
"""

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def log_paths(logs_dir):
    """Which files in a directory are real games. The published library has a
    manifest, and that manifest is the definition of what is in it — reading
    the directory instead would sweep up sample.json. A raw batch directory has
    no manifest, so every log counts."""
    manifest_path = logs_dir / "manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        return [logs_dir / f"{episode['slug']}.json" for episode in manifest["episodes"]]
    return sorted(logs_dir.glob("*.json"))


def read_game(path):
    """Pull the few numbers we care about out of one log, or None if the game
    never finished (no game_over event)."""
    log = json.loads(path.read_text())

    # Hand-edited logs carry this flag. Their winner was decided by us, not by
    # the players, so counting them would skew the win rate.
    if log.get("exclude_from_stats"):
        return None

    events = log["events"]

    winner = None
    for event in events:
        if event["type"] == "game_over":
            winner = event["winner"]
    if winner is None:
        return None

    # Roles live in stats for every log, revealed or not; game_start only
    # carries them on --reveal-secrets runs.
    players = log.get("stats", {}).get("players") or {}
    mafia_count = 0
    for player in players.values():
        if player.get("role") == "Mafia":
            mafia_count += 1

    lynches = []
    for event in events:
        if event["type"] == "elimination":
            lynches.append({"day": event.get("day"), "hit_mafia": event.get("role") == "Mafia"})

    detective = log.get("stats", {}).get("detective") or {}

    return {
        "name": path.stem,
        "winner": winner,
        "mafia_count": mafia_count,
        "lynches": lynches,
        "trusted_person": detective.get("trusted_person"),
    }


def summarise(games):
    """One row of the table: counts across a group of games."""
    town_wins = 0
    lynches_total = 0
    lynches_correct = 0
    day_one_total = 0
    day_one_correct = 0

    for game in games:
        if game["winner"] == "town":
            town_wins += 1
        for lynch in game["lynches"]:
            lynches_total += 1
            if lynch["hit_mafia"]:
                lynches_correct += 1
            if lynch["day"] == 1:
                day_one_total += 1
                if lynch["hit_mafia"]:
                    day_one_correct += 1

    return {
        "games": len(games),
        "town_wins": town_wins,
        "lynches_total": lynches_total,
        "lynches_correct": lynches_correct,
        "day_one_total": day_one_total,
        "day_one_correct": day_one_correct,
    }


def percent(part, whole):
    if whole == 0:
        return "  n/a"
    return f"{100 * part / whole:4.0f}%"


def print_table(title, groups):
    """groups is a list of (label, [games])."""
    print(f"\n{title}")
    print(f"{'split':<22} {'n':>3}  {'town win':>14}  {'lynch acc':>14}  {'day-1 acc':>14}")
    for label, games in groups:
        if not games:
            continue
        row = summarise(games)
        town = f"{row['town_wins']}/{row['games']} {percent(row['town_wins'], row['games'])}"
        lynch = f"{row['lynches_correct']}/{row['lynches_total']} {percent(row['lynches_correct'], row['lynches_total'])}"
        day_one = f"{row['day_one_correct']}/{row['day_one_total']} {percent(row['day_one_correct'], row['day_one_total'])}"
        print(f"{label:<22} {row['games']:>3}  {town:>14}  {lynch:>14}  {day_one:>14}")


def day_one_split(games):
    """Town's record when the day-1 lynch hit a wolf, versus when it missed.
    The 20-case review found this is where the game is decided."""
    hit = []
    missed = []
    for game in games:
        day_one_lynches = [lynch for lynch in game["lynches"] if lynch["day"] == 1]
        if not day_one_lynches:
            continue
        if day_one_lynches[0]["hit_mafia"]:
            hit.append(game)
        else:
            missed.append(game)
    return [("day-1 hit a wolf", hit), ("day-1 missed", missed)]


def main():
    parser = argparse.ArgumentParser(description="Balance report across game logs")
    parser.add_argument(
        "--logs",
        default="viewer/public/logs",
        help="Directory of finished game logs (default: the published library)",
    )
    args = parser.parse_args()

    logs_dir = REPO_ROOT / args.logs
    games = []
    for path in log_paths(logs_dir):
        game = read_game(path)
        if game is not None:
            games.append(game)

    if not games:
        raise SystemExit(f"No finished games in {logs_dir}")

    two_mafia = [g for g in games if g["mafia_count"] == 2]
    three_mafia = [g for g in games if g["mafia_count"] >= 3]

    print_table(
        f"{len(games)} finished game(s) in {args.logs}",
        [("2 mafia", two_mafia), ("3 mafia", three_mafia), ("all", games)],
    )

    print_table("Where the game is decided", day_one_split(games))

    # The trusted person only applies to 3-mafia games, so the comparison that
    # means anything is buffed vs unbuffed within that group.
    buffed = [g for g in three_mafia if g["trusted_person"]]
    unbuffed = [g for g in three_mafia if not g["trusted_person"]]
    print_table(
        "Trusted person (3-mafia only)",
        [("with trusted person", buffed), ("without", unbuffed)],
    )
    print()


if __name__ == "__main__":
    main()
