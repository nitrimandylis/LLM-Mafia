"""Checks for the one piece of ci_case.py that must never be wrong: the
validator standing between the reviewer and a merge. Everything else in that
file is subprocess plumbing that only a real run can exercise.

    python tools/test_ci_case.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.ci_case import parse_verdict, validate_verdict

CAST = ["Aria", "Marcus", "Vera"]
GM_TITLE = "The Doctor's Last Rounds"
GM_TAGLINE = "Three nights, one liar, and a town that counted wrong."


def good_verdict(**overrides):
    verdict = {
        "publish": True,
        "reasons": ["the mafia flipped the room on day 2"],
        "title": GM_TITLE,
        "tagline": GM_TAGLINE,
        "rewrote_metadata": False,
    }
    verdict.update(overrides)
    return verdict


def check(verdict, expected_problem_count, note):
    problems = validate_verdict(verdict, CAST, GM_TITLE, GM_TAGLINE)
    assert len(problems) == expected_problem_count, f"{note}: got {problems}"


# A well-formed approval passes.
check(good_verdict(), 0, "clean approval")

# A well-formed rejection is still a valid verdict — publish: false is an
# answer, not a malfunction.
check(good_verdict(publish=False), 0, "clean rejection")

# Each way of being malformed is caught.
check(good_verdict(publish="yes"), 1, "publish is a string")
check(good_verdict(reasons=[]), 1, "empty reasons")
check(good_verdict(reasons="one reason"), 1, "reasons is a string")
check(good_verdict(title=""), 1, "empty title")
check(good_verdict(tagline="   "), 1, "blank tagline")
check(good_verdict(rewrote_metadata=True), 1, "claimed a rewrite but changed nothing")

# The spoiler check: a tagline naming a cast member never ships.
check(good_verdict(tagline="Marcus knew all along."), 1, "tagline names a player")
# Titles are exempt, and a substring of a name is not a name.
check(good_verdict(title="Marcus and the long night"), 0, "title may name a player")
check(good_verdict(tagline="Aria's absence was always the point."), 1, "possessive still counts")
check(good_verdict(tagline="The verandah stayed empty."), 0, "Vera inside a word is not Vera")

# Nothing parseable is a rejection, not a crash.
check(None, 1, "verdict is None")
check("publish: true", 1, "verdict is a string")

# Fenced JSON is common enough that it must survive parsing.
assert parse_verdict('```json\n{"publish": true}\n```') == {"publish": True}
assert parse_verdict('Here you go:\n{"publish": false}') == {"publish": False}
assert parse_verdict("not json at all") is None
assert parse_verdict("") is None

print("✅ ci_case validator checks passed")
