"""Run several Claude-backed Mafia games back to back, unattended.

Usage:
    caffeinate -i python tools/run_batch.py --games 10 --mafia 3

Writes raw logs to runs/ (gitignored) and publishes nothing. Read the summary,
then publish the keepers yourself:

    python tools/publish_game.py runs/2026-07-28-1930.json

Quota: there is no way to ask how much subscription quota is left before
spending it, so this checks the OAuth usage endpoint between games, measures
what one game actually costs, and sleeps until the window resets when there is
not enough headroom for another. If the endpoint will not answer, it runs
anyway and relies on mafia/game.py aborting a game whose backend has gone.
"""

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tools.claude_usage import read_usage

RUNS_DIR = REPO_ROOT / "runs"

# Game 1 has nothing measured yet, so it needs a fixed guard. Half a window is
# room for a game that turns out to be expensive without stranding quota.
FIRST_GAME_MAX_UTILIZATION = 50.0
# Start a game only with this much more headroom than the last one used —
# games vary in length, and running out mid-game wastes everything spent.
HEADROOM_MULTIPLIER = 1.5

EXIT_BACKEND_UNAVAILABLE = 2


def should_start_game(utilization, resets_at, now, last_cost, waited_so_far, max_wait):
    """go / wait / stop, from the numbers alone. Pure so it can be tested.

    utilization is percent used of the 5-hour window, or None when the usage
    endpoint would not answer. last_cost is percent used by the previous game,
    or None before any game has finished.
    """
    if utilization is None:
        return "go"  # cannot tell; the failure guard is the safety net

    if last_cost is None:
        needed = 100.0 - FIRST_GAME_MAX_UTILIZATION
    else:
        needed = last_cost * HEADROOM_MULTIPLIER

    if 100.0 - utilization >= needed:
        return "go"

    wait_seconds = max(0.0, resets_at - now)
    if waited_so_far + wait_seconds > max_wait:
        return "stop"
    return "wait"


def format_duration(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    if hours:
        return f"{hours}h{minutes:02d}m"
    return f"{minutes}m"


def log_path_for_now():
    return RUNS_DIR / f"{datetime.now().strftime('%Y-%m-%d-%H%M%S')}.json"


def smells_wrong(log_path):
    """Reasons not to publish a game that finished. Fallback text means players
    were failing to answer even though the run never tripped the abort."""
    log = json.loads(log_path.read_text())
    reasons = []

    fallback_lines = 0
    for event in log["events"]:
        text = event.get("text") or ""
        if "remains silent" in text or "mumbles something noncommittal" in text:
            fallback_lines += 1
    if fallback_lines:
        reasons.append(f"{fallback_lines} fallback line(s)")

    if not any(event["type"] == "game_over" for event in log["events"]):
        reasons.append("no game_over event")

    if (log.get("day") or 0) < 2:
        reasons.append("ended on day 1")

    return reasons


def run_one_game(log_path, args):
    """Play one game in a subprocess. Returns its exit code."""
    command = [
        sys.executable, str(REPO_ROOT / "main.py"),
        "--claude",
        "--mafia", str(args.mafia),
        "--player-count", str(args.player_count),
        "--output", str(log_path),
    ]
    if args.reveal_secrets:
        command.append("--reveal-secrets")
    return subprocess.run(command, cwd=REPO_ROOT).returncode


def main():
    parser = argparse.ArgumentParser(description="Run Claude-backed games back to back")
    parser.add_argument("--games", type=int, default=1, help="How many games to finish")
    parser.add_argument("--mafia", type=int, default=3, help="Mafia count (default: 3)")
    parser.add_argument("--player-count", type=int, default=10)
    parser.add_argument(
        "--no-reveal-secrets",
        dest="reveal_secrets", action="store_false",
        help="Omit mafia chat and night actions from the logs",
    )
    parser.add_argument(
        "--no-wait",
        dest="wait", action="store_false",
        help="Stop when quota runs low instead of sleeping until it resets",
    )
    parser.add_argument(
        "--max-wait-hours", type=float, default=12.0,
        help="Give up if total sleeping would exceed this (default: 12)",
    )
    args = parser.parse_args()

    # Redirected to a file, Python block-buffers, so the runner's own banners
    # land out of order among the game's output — unreadable in the log you
    # come back to after an overnight batch.
    sys.stdout.reconfigure(line_buffering=True)

    RUNS_DIR.mkdir(exist_ok=True)
    max_wait = args.max_wait_hours * 3600
    waited_so_far = 0.0
    last_cost = None
    finished = []
    aborted = []

    while len(finished) < args.games:
        usage = read_usage()
        utilization = usage["utilization"] if usage else None
        resets_at = usage["resets_at"] if usage else 0.0

        decision = should_start_game(
            utilization, resets_at, time.time(), last_cost, waited_so_far, max_wait
        )
        if decision == "stop":
            print(f"\n🛑 Not enough quota, and waiting would pass the "
                  f"{args.max_wait_hours:g}h cap. Stopping.")
            break
        if decision == "wait":
            if not args.wait:
                print("\n🛑 Not enough quota and --no-wait was passed. Stopping.")
                break
            wait_seconds = max(0.0, resets_at - time.time()) + 60
            print(f"\n⏳ {utilization:.0f}% of the window used. Sleeping "
                  f"{format_duration(wait_seconds)} until it resets.")
            time.sleep(wait_seconds)
            waited_so_far += wait_seconds
            last_cost = None  # a fresh window says nothing about the old one
            continue

        game_number = len(finished) + len(aborted) + 1
        where = "" if utilization is None else f"  |  window {utilization:.0f}% used"
        print(f"\n{'=' * 60}\n▶️  Game {game_number} "
              f"({len(finished)}/{args.games} finished){where}\n{'=' * 60}")

        log_path = log_path_for_now()
        exit_code = run_one_game(log_path, args)

        after = read_usage()
        if usage and after and after["utilization"] > utilization:
            last_cost = after["utilization"] - utilization
            print(f"💸 That game used {last_cost:.1f}% of the 5-hour window.")

        if exit_code == EXIT_BACKEND_UNAVAILABLE:
            aborted.append(log_path.name)
            print("⚠️  Backend went away mid-game — nothing saved.")
            if not args.wait:
                break
            # The quota reading is what decides whether to wait; loop back and
            # let should_start_game read it fresh.
            continue
        if exit_code != 0 or not log_path.exists():
            aborted.append(log_path.name)
            print(f"⚠️  Game failed (exit {exit_code}) — skipping.")
            continue

        finished.append(log_path)

    print(f"\n{'=' * 60}\n📦 Batch done: {len(finished)} finished, {len(aborted)} aborted")
    for log_path in finished:
        reasons = smells_wrong(log_path)
        if reasons:
            print(f"  ⚠️  {log_path.name}  — {', '.join(reasons)}")
        else:
            print(f"  ✅ {log_path.name}")
    if finished:
        print("\nPublish the keepers:  python tools/publish_game.py runs/<file>")
        print("Then check the split:  python tools/balance_report.py")


if __name__ == "__main__":
    main()
