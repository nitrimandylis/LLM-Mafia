"""Self-check for the two gamelog-driven fixes in mafia/game.py.

Run: python tools/test_fixes.py
"""
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mafia.game import MafiaGame

# ponytail: bare instance, only the attrs the two methods under test touch
g = object.__new__(MafiaGame)
g.players = [
    SimpleNamespace(name=n)
    for n in ["RICO", "DR. VANCE", "CHEN", "SAGE", "MARSHAL", "PIP"]
]

targets = ["RICO", "CHEN", "SAGE"]

# parse_mafia_choice: a named target wins over incidental "no one"/"pass" words
assert g.parse_mafia_choice("CHEN — no one suspects her right now.", targets) == "CHEN"
assert g.parse_mafia_choice("I'll pass judgement on SAGE tonight.", targets) == "SAGE"
# real no-kill still works
assert g.parse_mafia_choice("NO_KILL", targets) == "no_kill"
assert g.parse_mafia_choice("I'd rather skip tonight.", targets) == "no_kill"
# "passes"/"nonetheless" no longer trip the markers, garbage yields None
assert g.parse_mafia_choice("Nonetheless he passes for now, no target.", targets) is None

# sanitize_response: honorifics don't count as sentence ends when clipping >5 sentences
player = g.players[0]  # RICO
long_text = (
    "One. Two. Three. I want to revisit DR. VANCE's votes. Five. Six. Seven."
)
cleaned = g.sanitize_response(player, long_text)
assert "DR. VANCE" in cleaned, cleaned
assert not cleaned.endswith("DR."), cleaned

# role-leak patterns: catch the real day-1 leak, spare persona speech
from mafia.events import EventLog
from mafia.player import Role

leak = MafiaGame.ROLE_LEAK_PATTERNS
assert leak[Role.MAFIA].search("As a Mafia member, I need to deflect suspicion.")
assert leak[Role.MAFIA].search("SOCRATES (my fellow Mafia) is under fire.")
assert not leak[Role.MAFIA].search("I'm not mafia, and HOLMES knows it.")
assert not leak[Role.MAFIA].search("They keep calling me mafia without evidence.")
assert leak[Role.DETECTIVE].search("As the detective, I scanned DR. VANCE.")
assert leak[Role.DOCTOR].search("As a doctor, I recommend caution.")
# patterns are role-scoped: a non-doctor saying "as a doctor" is never checked
assert Role.VILLAGER not in leak

# (YOU) marker: own lines tagged at line start, not when named as a target
g.day = 1
g.day_summaries = {}
g.private_notes = {}
g.events = EventLog()
g.events.emit("statement", day=1, actor="RICO", text="SAGE is too quiet.")
g.events.emit("question", day=1, actor="CHEN", target="RICO", text="Why so fast, RICO?")
ctx = g.build_context_for_player(player, "facts")
assert "RICO (YOU):" in ctx, ctx
assert "CHEN → RICO:" in ctx, ctx  # RICO as target stays untagged

# unterminated <think> (truncated reasoning) must never reach the transcript
assert g.sanitize_response(player, "SAGE is lying. <think>I'm mafia so I should") == "SAGE is lying."
assert g.sanitize_response(player, "<think>I am the mafia, plan: deflect") == ""

# extract_vote: reversed vote phrasing beats "last name mentioned" fallback
assert g.extract_vote("CHEN is my vote — that call-out of HOLMES reeked of setup.", targets) == "CHEN"
assert g.extract_vote("SAGE gets my vote today, not RICO.", targets) == "SAGE"
assert g.extract_vote("My vote is for RICO because CHEN cleared himself.", targets) == "RICO"

# new night events pass schema validation
g.events.emit("protection", day=1, actor="SAGE", target="CHEN")
g.events.emit("night_no_kill", day=1)

print("ok")
