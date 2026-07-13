"""
Sample-log generator + contract guard for the replay viewer.

Runs a full game with a stubbed model (no network), validates every emitted
event against the schema, checks the day-phase ordering, and confirms the
Python and TypeScript event schemas haven't drifted apart. With --write it
(re)generates the viewer's bundled sample log.

    python tools/make_sample_log.py            # validate engine + schema parity
    python tools/make_sample_log.py --write    # also (re)write the sample log
"""
import json
import pathlib
import random
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from mafia.events import REQUIRED  # noqa: E402
from mafia.game import MafiaGame  # noqa: E402

SAMPLE_LOG = ROOT / "viewer" / "public" / "logs" / "sample.json"
EVENTS_TS = ROOT / "viewer" / "lib" / "events.ts"

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
    def _q(player, prompt, context="", min_words=4, public_speech=False, max_tokens=2048):
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

    assert "phase" in types and "statement" in types, "missing day discussion"
    assert "vote" in types and "elimination" in types, "missing voting outcome"

    def first(pred):
        return next(i for i, e in enumerate(events) if pred(e))

    i_phase = first(lambda e: e["type"] == "phase" and e["phase"] == "day")
    i_stmt = first(lambda e: e["type"] == "statement")
    i_vote = first(lambda e: e["type"] == "vote")
    i_elim = first(lambda e: e["type"] == "elimination")
    assert i_phase < i_stmt < i_vote < i_elim, "day-phase ordering wrong"


def check_schema_parity():
    """The TS event union (viewer/lib/events.ts) must list the same event types
    as the Python schema. Catches the contract silently drifting apart."""
    # Only the GameEvent union counts — helper types below it (e.g. Ballot)
    # are viewer-side constructs, not wire events.
    ts = EVENTS_TS.read_text().split("export type GameLog")[0]
    ts_types = set(re.findall(r'type:\s*"([a-z_]+)"', ts))
    py_types = set(REQUIRED.keys())
    only_py = py_types - ts_types
    only_ts = ts_types - py_types
    assert not only_py, f"event types in mafia/events.py but missing from events.ts: {only_py}"
    assert not only_ts, f"event types in events.ts but missing from mafia/events.py: {only_ts}"


def main():
    game = run_game()
    events = game.events.to_list()
    validate(events)
    check_schema_parity()
    print(
        f"OK: {len(events)} events validated, schema parity holds "
        f"({len(REQUIRED)} event types; winner={events[-1]['winner']})"
    )

    if "--write" in sys.argv:
        SAMPLE_LOG.parent.mkdir(parents=True, exist_ok=True)
        SAMPLE_LOG.write_text(
            json.dumps(
                {
                    "events": events,
                    "game_log": game.game_log,
                    "public_log": game.public_log,
                    "day": game.day,
                    "stats": game.compute_stats(),
                },
                indent=2,
            )
        )
        print(f"wrote {SAMPLE_LOG.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
