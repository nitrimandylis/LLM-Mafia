"""
Contract guard for the structured event stream + sample-log generator.

Runs a full game with a stubbed model (no network), validates every emitted
event against the schema, checks the day-phase ordering, and writes a sample
log to viewer/public/logs/sample.json for the replay viewer.

    python test_events.py            # validate
    python test_events.py --write    # validate + (re)generate sample.json
"""
import json
import random
import sys
from pathlib import Path

from mafia.events import REQUIRED
from mafia.game import MafiaGame

# Flavorful canned lines. Each mentions {name} so extract_vote() resolves a
# target for votes/accusations/night choices — drives a real game to completion.
LINES = [
    "Something about {name} feels off — too calm when the pressure's on. My vote is {name}.",
    "I've been watching {name} dodge every direct question. I say we eliminate {name}.",
    "{name} flipped their story twice today. That's mafia behavior. Vote {name}.",
    "Honestly? {name}. The timing of their accusations is too convenient. {name}.",
    "I trust my gut and my gut says {name}. Let's vote out {name}.",
    "{name} has been awfully quiet, and quiet people are hiding something. {name}.",
]


def fake_query(game):
    def _q(player, prompt, context="", min_words=4):
        others = [p.name for p in game.get_alive_players() if p.name != player.name]
        if not others:
            return "I have nothing left to say."
        name = random.choice(others)
        if min_words <= 1:  # vote / night target — name only
            return name
        return random.choice(LINES).format(name=name)
    return _q


def run_game(reveal_secrets=True, seed=23):
    random.seed(seed)
    game = MafiaGame(
        reveal_secrets=reveal_secrets,
        player_count=8,        # 8 => mafia + detective + doctor all present
        gm_enabled=False,      # no narrator network calls
    )
    game.query_model = fake_query(game)
    game.run()
    return game


def validate(events):
    assert events, "no events emitted"
    assert events[0]["type"] == "game_start", "first event must be game_start"
    assert events[-1]["type"] == "game_over", "last event must be game_over"

    types = set()
    for ev in events:
        t = ev["type"]
        assert t in REQUIRED, f"unknown event type {t!r}"
        for field in REQUIRED[t]:
            assert field in ev, f"event {t!r} missing {field!r}"
        types.add(t)

    # A real game must produce a full day: phase -> statements -> votes -> elimination.
    assert "phase" in types and "statement" in types, "missing day discussion"
    assert "vote" in types and "elimination" in types, "missing voting outcome"

    # Ordering within the first day: phase(day) before first statement before
    # first vote before first elimination.
    def first(pred):
        return next(i for i, e in enumerate(events) if pred(e))

    i_phase = first(lambda e: e["type"] == "phase" and e["phase"] == "day")
    i_stmt = first(lambda e: e["type"] == "statement")
    i_vote = first(lambda e: e["type"] == "vote")
    i_elim = first(lambda e: e["type"] == "elimination")
    assert i_phase < i_stmt < i_vote < i_elim, "day-phase ordering wrong"


def main():
    game = run_game()
    events = game.events.to_list()
    validate(events)
    print(f"OK: {len(events)} events validated "
          f"({sum(1 for e in events if e['type']=='statement')} statements, "
          f"game_over winner={events[-1]['winner']})")

    if "--write" in sys.argv:
        out = Path(__file__).parent / "viewer" / "public" / "logs" / "sample.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "events": events,
            "game_log": game.game_log,
            "public_log": game.public_log,
            "day": game.day,
            "stats": game.compute_stats(),
        }
        out.write_text(json.dumps(payload, indent=2))
        print(f"wrote {out}")


if __name__ == "__main__":
    main()
