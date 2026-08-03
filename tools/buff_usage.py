"""Did the trusted-person buff actually fire? One line per buffed game.

Usage:
    python tools/buff_usage.py
    python tools/buff_usage.py --logs runs        # a batch of unpublished games

Win rate cannot answer this. At the batch sizes these games are run in, 33% and
50% are three wins versus four, which is noise. What the buff does to the
detective's behaviour is per-game and near-deterministic, so that is what the
delivery fix is judged on.

Two things are counted, both structural — they read the actor and target fields
rather than the text, because substring matching cannot tell a detective
defending their trusted person from one attacking them:

  attacked - the detective aimed a question or accusation at their own trusted
             person. This is the buff being spent backwards, and v2 filtered
             every site that can force it, so v2 should be 0. Under v1 it was
             2/7 (case-023 on days 1 and 4, case-026 on day 2).
  wasted   - the town lynched the trusted person while the detective was still
             alive to speak up. Under v1 this was case-023.

Whether the detective actually vouched is a judgement call no substring test
can make, so the quoted line is printed for the eye instead of scored.

Delete this script once the buff is confirmed to fire; it is a diagnostic for
one change, not part of the balance gate.
"""

import argparse
import json
from pathlib import Path

from balance_report import log_paths

REPO_ROOT = Path(__file__).resolve().parent.parent

# Aiming one of these at a player is an attack: a question is drawn from the
# "Challenge"/"Confront" templates, and an accusation is a call to lynch. A
# plain statement has no target field, so it cannot be scored this way.
ATTACK_TYPES = {"question", "accusation"}


def read_game(path):
    """Pull the buff story out of one log, or None if this game had no buff."""
    log = json.loads(path.read_text())
    detective = log.get("stats", {}).get("detective") or {}
    trusted_person = detective.get("trusted_person")
    if not trusted_person:
        return None

    detective_name = detective.get("name")
    events = log["events"]

    attacks = []
    wasted_day = None
    quotes = []
    detective_alive = True

    for event in events:
        event_type = event["type"]

        if event.get("actor") == detective_name:
            if event_type in ATTACK_TYPES and event.get("target") == trusted_person:
                attacks.append(event.get("day"))
            # Kept for the eye, not scored: whether this reads as vouching or as
            # pressure is a judgement no substring test can make.
            if event.get("text") and names(event["text"], trusted_person):
                quotes.append((event.get("day"), event["text"]))

        # The detective leaving play is what makes a later mislynch forgivable,
        # so track both ways they can die.
        if event_type in ("elimination", "night_kill") and event.get("target") == detective_name:
            detective_alive = False

        if event_type == "elimination" and event.get("target") == trusted_person:
            if detective_alive:
                wasted_day = event.get("day")

    return {
        "name": path.stem,
        "detective": detective_name,
        "trusted_person": trusted_person,
        "version": detective.get("trusted_person_v", 1),
        "attacks": attacks,
        "wasted_day": wasted_day,
        "quotes": quotes,
    }


def names(text, trusted_person):
    """Did this line say the trusted person's name?

    Matching on the first word handles the two-word names (AMBASSADOR SILVA,
    DR. VANCE), which players shorten in conversation.
    """
    return trusted_person.split()[0].lower() in text.lower()


def main():
    parser = argparse.ArgumentParser(description="Trusted-person buff usage per game")
    parser.add_argument(
        "--logs",
        default="viewer/public/logs",
        help="Directory of finished game logs (default: the published library)",
    )
    parser.add_argument(
        "--quotes",
        action="store_true",
        help="Print every line where the detective said the trusted person's name",
    )
    args = parser.parse_args()

    logs_dir = REPO_ROOT / args.logs
    games = []
    for path in log_paths(logs_dir):
        game = read_game(path)
        if game is not None:
            games.append(game)

    if not games:
        raise SystemExit(f"No buffed games in {logs_dir}")

    print(f"\n{len(games)} buffed game(s) in {args.logs}")
    print(f"{'game':<12} {'v':>2}  {'detective':<18} {'trusted':<18} {'attacked':>12}  {'wasted lynch':>13}")
    for game in games:
        if game["attacks"]:
            attacked = "days " + ",".join(str(day) for day in game["attacks"])
        else:
            attacked = "-"
        wasted = f"day {game['wasted_day']}" if game["wasted_day"] else "-"
        print(
            f"{game['name']:<12} {game['version']:>2}  {game['detective']:<18} "
            f"{game['trusted_person']:<18} {attacked:>12}  {wasted:>13}"
        )

    for version in sorted({game["version"] for game in games}):
        group = [game for game in games if game["version"] == version]
        attacked = sum(1 for game in group if game["attacks"])
        wasted = sum(1 for game in group if game["wasted_day"])
        print(
            f"\nv{version}: detective attacked their trusted person in "
            f"{attacked}/{len(group)} games, trusted person lynched with the "
            f"detective alive in {wasted}/{len(group)}"
        )

    if args.quotes:
        for game in games:
            print(f"\n--- {game['name']}: {game['detective']} on {game['trusted_person']}")
            for day, text in game["quotes"]:
                print(f"  day {day}: {text}")
    print()


if __name__ == "__main__":
    main()
