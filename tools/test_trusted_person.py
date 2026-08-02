"""Self-check for the 3-mafia-gated detective trusted-person buff.

Run: python tools/test_trusted_person.py
"""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mafia.game import MafiaGame
from mafia.player import Player, Role

NAMES = ["RICO", "ARIA", "SAGE", "HOLMES", "MARSHAL",
         "SOCRATES", "DR. VANCE", "PIP", "CHEN", "SILVA"]


def run(mafia_count, seed):
    """ponytail: bare instance, assign_roles only touches these attrs."""
    random.seed(seed)
    g = object.__new__(MafiaGame)
    g.players = [Player(name=n) for n in NAMES]
    g.mafia_count = mafia_count
    g.trusted_person = None
    g.private_notes = {}
    g.log = lambda *a, **k: None
    g.assign_roles()
    return g


# 2 mafia: town already wins 5/5, no buff
for seed in range(20):
    g = run(2, seed)
    assert g.trusted_person is None, f"2-mafia leaked a buff (seed {seed})"
    assert g.private_notes == {}, g.private_notes

# 3 mafia: buff fires, names a real non-mafia player who isn't the detective
for seed in range(20):
    g = run(3, seed)
    det = next(p for p in g.players if p.role == Role.DETECTIVE)
    mafia = {p.name for p in g.players if p.role == Role.MAFIA}
    t = g.trusted_person
    assert t is not None, f"3-mafia buff missing (seed {seed})"
    assert t not in mafia, f"trusted person {t} is mafia (seed {seed})"
    assert t != det.name, f"detective trusted themselves (seed {seed})"
    assert t in NAMES, t
    # the detective, and only the detective, is told
    assert list(g.private_notes) == [det.name], g.private_notes
    assert t in g.private_notes[det.name][0]

# the buff picks a different name across seeds, i.e. it's not pinned to a seat
assert len({run(3, s).trusted_person for s in range(20)}) > 1

# The day points players at a target four separate ways (opening probe, daily
# "most suspicious", questioning rounds, final accusation), and this shortlist
# is what decides who each of them can be made to attack. Nobody should ever be
# handed a name they already know is on their own side.
for seed in range(20):
    game = run(3, seed)
    alive_names = [p.name for p in game.players]
    mafia_names = {p.name for p in game.players if p.role == Role.MAFIA}

    for player in game.players:
        candidates = game.probe_candidates(player, alive_names)

        assert player.name not in candidates, f"{player.name} can probe themselves (seed {seed})"
        assert candidates, f"empty shortlist for {player.name} (seed {seed})"

        if player.role == Role.MAFIA:
            partners = mafia_names - {player.name}
            overlap = partners & set(candidates)
            assert not overlap, f"wolf {player.name} offered partner {overlap} (seed {seed})"

        if player.role == Role.DETECTIVE:
            assert game.trusted_person not in candidates, (
                f"detective offered their trusted person "
                f"{game.trusted_person} (seed {seed})"
            )

# 2 mafia has no buff, so the detective's shortlist is everyone but themselves
for seed in range(20):
    game = run(2, seed)
    alive_names = [p.name for p in game.players]
    detective = next(p for p in game.players if p.role == Role.DETECTIVE)
    candidates = game.probe_candidates(detective, alive_names)
    assert len(candidates) == len(alive_names) - 1, f"2-mafia detective lost names (seed {seed})"

print("trusted-person gating OK")
print("probe shortlist exclusions OK")
